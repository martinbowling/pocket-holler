"""Input-only PyBoy driver for a receipt-paired PocketHoller full cartridge.

Memory is read only for debug assertions/navigation. No RAM fixture, emulator
state, teleport or progression injection is accepted. All save files are made
by ordinary camp interactions inside a fresh private evidence directory.
"""
from collections import deque
from pathlib import Path
from importlib.metadata import version
import copy, hashlib, json, math, re, shutil, tempfile

ROOT = Path(__file__).resolve().parents[1]
DIRECTIONS = {'down': 0, 'right': 1, 'up': 2, 'left': 3}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def events(value):
    if isinstance(value, dict):
        if 'command' in value:
            yield value
        for child in value.values():
            yield from events(child)
    elif isinstance(value, list):
        for child in value:
            yield from events(child)


def decode_collision(data):
    if isinstance(data, list):
        return data
    values = []; index = 0
    while index < len(data):
        value = int(data[index:index + 2], 16); index += 2
        if data[index] == '!':
            count = 1; index += 1
        else:
            stop = data.index('+', index)
            count = int(data[index:stop], 16); index = stop + 1
        values.extend([value] * count)
    return values


class Driver:
    ACTOR_SIZE = 56  # inspected pinned GBVM actor_t, farptr3/uword16 ABI

    def __init__(self, rom=None, receipt=None, label='full-route', sound=False):
        from pyboy import PyBoy
        self.PyBoy = PyBoy
        self.runtime={'name':'PyBoy','version':version('pyboy')}
        self.rom = Path(rom or ROOT/'dist/PocketHoller-full.gbc')
        self.receipt_path = Path(receipt or ROOT/'evidence/full-build.json')
        self.receipt = json.loads(self.receipt_path.read_text())
        self.identity = digest(self.rom)
        assert self.receipt['success'] and self.receipt['rom']['sha256'] == self.identity
        debug = self.receipt['debugArtifacts']
        assert debug['romSha256'] == self.identity, 'Debug ROM pairing is stale'
        self.debug_dir = Path(str(self.rom) + '.debug')
        for filename, key in [('symbols.noi', 'noiSha256'), ('globals.i', 'globalsSha256')]:
            assert digest(self.debug_dir/filename) == debug[key], 'Unpaired debug artifact: ' + filename
        assert debug['sourceDebugAbi']['layout'] == 'gbvm-farptr3-uword16-v1'
        symbols = (self.debug_dir/'symbols.noi').read_text()
        self.symbols = {name: int(address, 16) for name, address in
                        re.findall(r'^DEF (\S+) 0x([0-9A-Fa-f]+)$', symbols, re.M)}
        glob = (self.debug_dir/'globals.i').read_text()
        self.variables = {name: int(index) for name, index in
                          re.findall(r'VAR_(\w+)\s*=\s*(\d+)', glob)}
        variable_resource=json.loads((ROOT/'project/variables.gbsres').read_text())
        self.source_variables={v['id']:v['name'] for v in variable_resource['variables']}
        for required in ['_script_memory', '_actors', '_win_pos_y', '_win_dest_pos_y', '_text_drawn']:
            assert required in self.symbols, 'Missing paired symbol ' + required
        assert 'P12' in self.variables and 'ENDING_SEEN' in self.variables
        self.qa = Path(tempfile.mkdtemp(prefix=label+'-', dir=ROOT/'evidence'))
        self.cart = self.qa/self.rom.name; shutil.copy2(self.rom, self.cart)
        (self.qa/'frames').mkdir()
        self.journal = (self.qa/'events.jsonl').open('w')
        self.frames = 0; self.held = set(); self.sound = sound
        self.reading_frames=0
        self.checks = []; self.visited = set(); self.traversed_edges=set(); self.trace = []; self.boots = 0
        self.scenes = {}; self.scene_ids = {}
        self.custom_events={}
        for path in (ROOT/'project/custom_events').glob('*.gbsres'):
            data=json.loads(path.read_text());self.custom_events[data['id']]=data
        for path in (ROOT/'project/scenes').glob('*/scene.gbsres'):
            data = json.loads(path.read_text()); code = data['name'].split()[0]
            self.scene_ids[data['id']] = code
            if not re.fullmatch(r'R\d{2}', code):
                continue
            data['actors'] = []
            for actor_path in path.parent.glob('actors/*.gbsres'):
                actor = json.loads(actor_path.read_text())
                actor['_key'] = actor_path.stem
                data['actors'].append(actor)
            data['triggers'] = [json.loads(p.read_text()) for p in path.parent.glob('triggers/*.gbsres')]
            data['solid'] = decode_collision(data['collisions'])
            assert len(data['solid']) == data['width']*data['height'], (code, 'Invalid collision byte count')
            self.scenes[code] = data
        assert len(self.scenes) == 24, 'Full game requires 24 genuine source scenes'
        self.world_map=json.loads((ROOT/'evidence/full-world-map.json').read_text())
        self.emit({'kind': 'header', 'romSha256': self.identity, 'receipt': str(self.receipt_path),
            'runtime':self.runtime,
            'debugHashes': {k: debug[k] for k in ['noiSha256', 'globalsSha256']},
            'sourceDebugAbi': debug['sourceDebugAbi'], 'sourceProvenance': debug['sourceProvenance'],
            'startingCondition': 'Clean cartridge boot, no initial RAM or emulator state',
            'memoryWrites': False, 'soundEmulated': sound, 'physicalTested': False})
        self.boot()

    def emit(self, row):
        self.journal.write(json.dumps(row, separators=(',', ':'))+'\n'); self.journal.flush()

    def word(self, address, signed=False):
        value = self.p.memory[address] + 256*self.p.memory[address+1]
        return value - 65536 if signed and value >= 32768 else value

    def value(self, name):
        return self.word(self.symbols['_script_memory']+2*self.variables[name])

    def state(self, names=None):
        names = names or [n for n in self.variables if not n.startswith(('LOCAL_', 'TEMP_'))]
        return {name: self.value(name) for name in names}

    def source_value(self,value):
        if value['type']=='number':return value['value']
        if value['type']=='variable':return self.value(self.source_variables[value['value']])
        a,b=self.source_value(value['valueA']),self.source_value(value['valueB'])
        return {'eq':a==b,'ne':a!=b,'gt':a>b,'gte':a>=b,'lt':a<b,'lte':a<=b,
                'add':a+b,'sub':a-b,'mul':a*b,'max':max(a,b),'min':min(a,b),
                'and':bool(a and b),'or':bool(a or b)}[value['type']]

    def resolved_script(self,script,stack=(),actor_bindings=None):
        """Expand source custom calls for discovery, preserving IF branches.

        This is never submitted to the emulator. The cartridge executes its
        banked scripts normally; Python only locates menus and legal exits.
        """
        resolved=[]
        actor_bindings=actor_bindings or {}
        for event in script:
            if event['command']=='EVENT_CALL_CUSTOM_EVENT':
                custom_id=event['args']['customEventId']
                assert custom_id not in stack,('Recursive custom event discovery',stack,custom_id)
                assert custom_id in self.custom_events,('Unknown native custom event',custom_id)
                bound={}
                for key,actor_id in event['args'].items():
                    match=re.fullmatch(r'\$actor\[(\d+)\]\$',key)
                    if match:bound[match[1]]=actor_bindings.get(actor_id,actor_id)
                resolved+=self.resolved_script(self.custom_events[custom_id]['script'],stack+(custom_id,),bound)
            else:
                event=copy.deepcopy(event)
                for key,value in event.get('args',{}).items():
                    if key.lower().endswith('actorid') and isinstance(value,str):
                        event['args'][key]=actor_bindings.get(value,value)
                for branch,body in event.get('children',{}).items():
                    event['children'][branch]=self.resolved_script(body,stack,actor_bindings)
                resolved.append(event)
        return resolved

    def room(self):
        number = self.value('CURRENT_ROOM')
        return f'R{number:02}' if 1 <= number <= 24 else 'TITLE'

    def xy(self):
        base = self.symbols['_actors']
        return self.word(base+1)/256, self.word(base+3)/256

    def boot(self):
        self.boots += 1; self.held = set()
        self.p = self.PyBoy(str(self.cart), window='null', cgb=True, sound_emulated=self.sound)
        self.p.set_emulation_speed(0)
        self.emit({'kind': 'boot', 'boot': self.boots, 'frame': self.frames,
                   'ramPresent': Path(str(self.cart)+'.ram').exists()})
        self.step([], 180); self.photo('boot-'+str(self.boots))

    def step(self, buttons, frames):
        assert 0 < frames <= 600, 'Bounded ordinary inputs only'
        new = set(buttons)
        assert new <= {'up','down','left','right','a','b','start','select'}
        for button in self.held-new:
            self.p.button_release(button)
        for button in new-self.held:
            self.p.button_press(button)
        self.held = new
        self.emit({'kind':'action', 'frame':self.frames, 'buttons':sorted(new), 'frames':frames})
        for _ in range(frames):
            self.p.tick(1, True); self.frames += 1
            if self.frames % 120 == 0:
                self.sample()
        room = self.room()
        if room != 'TITLE':
            self.visited.add(room)

    def release(self, frames=12):
        self.step([], frames)

    def press(self, button, hold=4, settle=16):
        self.release(4); self.step([button], hold); self.release(settle)

    def sample(self, filename=None):
        frame = self.p.screen.image.convert('RGBA')
        sha = hashlib.sha256(frame.tobytes()).hexdigest()
        row = {'kind':'frame', 'frame':self.frames, 'boot':self.boots,
               'rgbaSha256':sha, 'nativeDimensions':list(frame.size), 'room':self.room(), 'xy':self.xy()}
        if filename:
            frame.save(self.qa/filename); row['file'] = filename
        self.emit(row)

    def photo(self, label):
        self.sample('frames/'+re.sub(r'[^A-Za-z0-9_-]', '_', label)+'.png')

    def ui_open(self):
        return min(self.p.memory[self.symbols['_win_pos_y']],
                   self.p.memory[self.symbols['_win_dest_pos_y']]) < 144

    def menu_cursor(self):
        if not self.ui_open():
            return None
        # VWF text can reuse tile0xCB for an ordinary glyph. The inspected
        # compiler's native menu text starts with its font/position controls;
        # ordinary EVENT_TEXT pages do not. Require both signals.
        text_base=self.symbols['_ui_text_data']
        if bytes(self.p.memory[text_base:text_base+7])!=b'\x01\x01\x03\x03\x02\x02\x01':
            return None
        base = 0x9C00 if self.p.memory[0xFF40] & 0x40 else 0x9800
        visible_rows = max(0, math.ceil((144-self.p.memory[self.symbols['_win_pos_y']])/8))
        for y in range(min(visible_rows, 18)):
            for x in range(20):
                if self.p.memory[base+y*32+x] == 0xCB:
                    return x, y
        return None

    def drain_dialogue(self, stop_at_menu=True, max_presses=500):
        """Advance actual on-screen text; never selects a menu as dialogue."""
        stable = 0
        for _ in range(max_presses):
            self.release(12)
            if self.menu_cursor() is not None:
                if stop_at_menu:
                    return 'menu'
                self.press('b'); stable = 0; continue
            if self.ui_open():
                stable = 0
                if self.reading_frames and self.p.memory[self.symbols['_text_drawn']]:
                    self.release(self.reading_frames)
                self.press('a'); self.release(60); continue
            stable += 12
            if stable >= 120:
                return 'closed'
        self.photo('dialogue-limit')
        raise AssertionError(('Dialogue did not settle', self.room(), self.xy(), self.state()))

    def settle(self):
        return self.drain_dialogue(stop_at_menu=False)

    def wait_menu(self):
        self.release(90)
        assert self.drain_dialogue() == 'menu', ('Expected real menu', self.room(), self.xy())

    def choose_menu(self, index):
        # Menu scripts draw asynchronously and wait for the opening button to
        # release. Let that native wait finish before reading the cursor.
        self.wait_menu(); self.release(30); self.photo('menu-'+str(self.frames))
        if self.reading_frames:self.release(self.reading_frames)
        if index == 0:
            self.press('b')
        else:
            row=self.menu_cursor()[1]
            # The native list's cursor rows start at y=1, one tile apart.
            current=row
            for _ in range(abs(index-current)):
                self.press('down' if index>current else 'up')
            self.press('a')
        self.release(24)

    def new_game(self):
        self.press('start'); self.choose_menu(1)
        self.settle(); assert self.room() == 'R01'
        assert self.value('BUILD_SAVE_EPOCH') == 2

    def cold_continue(self, expected_names=None):
        before = self.state(expected_names) if expected_names else None
        self.p.stop(save=True)
        ram = Path(str(self.cart)+'.ram'); assert ram.exists()
        shutil.copy2(ram, self.qa/('checkpoint-'+str(self.boots)+'.ram.fixture'))
        self.boot(); self.press('start'); self.choose_menu(2); self.settle()
        if before is not None:
            after = self.state(expected_names)
            assert before == after, ('Cold Continue changed saved values', before, after)
        self.photo('continued-'+str(self.boots))

    @staticmethod
    def key_matches(actor, key):
        normalize = lambda s: re.sub(r'[^a-z0-9]+', '_', s.lower()).strip('_')
        return normalize(actor['_key']) == normalize(key) or normalize(actor['name']) == normalize(key)

    def actor(self, key, code=None):
        code = code or self.room()
        matches = [a for a in self.scenes[code]['actors'] if self.key_matches(a,key)]
        assert len(matches) == 1, (code, key, 'Actor not uniquely found', [a['name'] for a in matches])
        return matches[0]

    def actor_runtime(self, actor):
        base = self.symbols['_actors'] + self.ACTOR_SIZE*(int(actor['_index'])+1)
        flags = self.p.memory[base]
        return {'hidden': bool(flags & (0x02|0x40)), 'collision': bool(flags & 0x08), 'disabled':bool(flags & 0x40),
                'xy': (self.word(base+1)/256,self.word(base+3)/256),
                'bounds':tuple(self.word(base+offset,signed=True)/256 for offset in [6,8,10,12])}

    def collision_bounds(self):
        base = self.symbols['_actors']
        return tuple(self.word(base+offset, signed=True)/256 for offset in [6,8,10,12])

    def occupied(self, x, y):
        left, right, top, bottom = self.collision_bounds()
        return {(xx,yy) for yy in range(math.floor(y+top),math.floor(y+bottom)+1)
                for xx in range(math.floor(x+left),math.floor(x+right)+1)}

    def path(self, goal, permit_trigger=None):
        code = self.room(); scene = self.scenes[code]
        start = tuple(round(n) for n in self.xy())
        assert all(abs(a-b)<0.02 for a,b in zip(start,self.xy())), ('Player not tile-aligned', self.xy())
        blocked = {(x,y) for y in range(scene['height']) for x in range(scene['width'])
                   if scene['solid'][y*scene['width']+x]}
        for actor in scene['actors']:
            runtime = self.actor_runtime(actor)
            # Active followers explicitly have collisions disabled; hidden
            # solved markers and dormant protagonist NPCs must not block BFS.
            if runtime['disabled'] or not runtime['collision']:
                continue
            x,y = runtime['xy']
            left,right,top,bottom=runtime['bounds']
            blocked |= {(xx,yy) for yy in range(math.floor(y+top),math.floor(y+bottom)+1)
                        for xx in range(math.floor(x+left),math.floor(x+right)+1)}
        forbidden = set()
        for trigger in scene['triggers']:
            if permit_trigger and trigger['id'] == permit_trigger['id']:
                continue
            forbidden |= {(x,y) for y in range(trigger['y'],trigger['y']+trigger['height'])
                          for x in range(trigger['x'],trigger['x']+trigger['width'])}
        def valid(point):
            x,y=point; cells=self.occupied(x,y)
            return all(0<=xx<scene['width'] and 0<=yy<scene['height'] for xx,yy in cells) and not cells & blocked and not cells & forbidden
        queue=deque([start]);parent={start:None}
        while queue:
            point=queue.popleft()
            if point == goal:
                route=[]
                while parent[point] is not None:
                    previous, direction=parent[point];route.append(direction);point=previous
                return list(reversed(route))
            x,y=point
            for direction,point in [('left',(x-1,y)),('right',(x+1,y)),('up',(x,y-1)),('down',(x,y+1))]:
                if point not in parent and valid(point):
                    parent[point]=(x,y),direction;queue.append(point)
        raise AssertionError(('No legal walking path',code,start,goal,self.collision_bounds()))

    def move_one(self, direction):
        before=self.xy(); code=self.room(); self.release(3); self.step([direction],2)
        moved=False
        for _ in range(120):
            self.release(1)
            if self.room()!=code:
                return 'transition'
            now=self.xy()
            if now != before:
                moved=True
            if moved and all(abs(n-round(n))<0.02 for n in now):
                return 'moved'
            if self.ui_open():
                return 'dialogue'
        raise AssertionError(('Ordinary walking input blocked',code,direction,before,self.xy()))

    def walk(self, x, y, permit_trigger=None):
        code=self.room(); goal=(x,y)
        for direction in self.path(goal,permit_trigger):
            outcome=self.move_one(direction)
            if outcome=='transition':
                self.settle();return
            if outcome=='dialogue':
                self.settle();return self.walk(x,y,permit_trigger)
        if permit_trigger:
            # CURRENT_ROOM updates in the destination on-enter script, after
            # the fade and the native player position switch have begun.
            self.release(120);self.settle()
            if self.room()!=code:return
        assert tuple(round(n) for n in self.xy())==goal,(code,goal,self.xy())

    def walk_to_actor(self, key, target=False):
        actor=self.actor(key);runtime=self.actor_runtime(actor)
        x,y=(actor['x'],actor['y']) if runtime['hidden'] else runtime['xy']
        candidates=[(round(x),round(y)+2,'up'),(round(x)-2,round(y),'right'),
                    (round(x)+2,round(y),'left'),(round(x),round(y)-2,'down')]
        for xx,yy,direction in candidates:
            try:
                route=self.path((xx,yy))
            except AssertionError:
                continue
            self.walk(xx,yy)
            # A visible actor prevents this facing tap from moving into it.
            # Hidden ability markers accept both one and two tile distances.
            self.press(direction,hold=2,settle=20)
            assert self.p.memory[self.symbols['_actors']+5]==DIRECTIONS[direction]
            return actor
        raise AssertionError(('No accessible interaction station',self.room(),key,candidates))

    def interact(self, key, choices=()):
        self.walk_to_actor(key)
        self.press('b' if 'SWAP_BUTTONS' in self.variables and self.value('SWAP_BUTTONS') else 'a')
        for choice in choices:
            self.choose_menu(choice)
        return self.drain_dialogue()

    def ability(self, key):
        self.walk_to_actor(key,target=True)
        self.press('a' if 'SWAP_BUTTONS' in self.variables and self.value('SWAP_BUTTONS') else 'b')
        self.settle()

    def edge_enabled(self, trigger):
        # The trigger's IF tree is evaluated for reachability only. Native
        # progression still happens exclusively by walking into the trigger.
        def destinations(script):
            out=[]
            for event in script:
                if event['command']=='EVENT_SWITCH_SCENE':out.append(event['args']['sceneId'])
                elif event['command']=='EVENT_IF':out+=destinations(event.get('children',{}).get('true' if self.source_value(event['args']['condition']) else 'false',[]))
                elif 'children' in event:
                    for child in event['children'].values():out+=destinations(child)
            return out
        return destinations(self.resolved_script(trigger.get('script',[])))

    def selected_menu_options(self,script,first_label):
        """Resolve native conditional menu labels using read-only quest values.

        This selects an ordinary UI row, never executes game effects in Python.
        Recruited-only companion menus grow, so their numeric row is not stable.
        """
        def find(body):
            found=[]
            for event in body:
                if event['command']=='EVENT_MENU' and event['args'].get('option1','').upper()==first_label:
                    a=event['args'];found.append([a['option'+str(i)] for i in range(1,a['items']+1)])
                elif event['command']=='EVENT_IF':
                    found+=find(event.get('children',{}).get('true' if self.source_value(event['args']['condition']) else 'false',[]))
            return found
        candidates=find(self.resolved_script(script))
        assert len(candidates)==1,('Current conditional menu not unique',first_label,candidates)
        return candidates[0]

    def go_room(self, destination):
        for _ in range(40):
            current=self.room()
            if current==destination:return
            queue=deque([current]);parent={current:None}
            while queue and destination not in parent:
                code=queue.popleft()
                links=[{'kind':'trigger','source':trigger} for trigger in self.scenes[code]['triggers']]
                for edge in self.world_map['edges']:
                    if edge['from']==code and 'actor' in edge:
                        actor=self.actor(edge['actor'],code)
                        assert actor['id']==edge['actorId'],('Portal manifest/source mismatch',edge)
                        links.append({'kind':'actor','source':actor})
                for link in links:
                    for sceneid in self.edge_enabled(link['source']):
                        other=self.scene_ids[sceneid]
                        if other in self.scenes and other not in parent:
                            parent[other]=(code,link);queue.append(other)
            assert destination in parent,('Destination is gated/unreachable',current,destination,self.state())
            next_room=destination
            while parent[next_room][0]!=current:next_room=parent[next_room][0]
            link=parent[next_room][1];trigger=link['source']
            self.traverse_link(link,next_room)
        raise AssertionError(('Room traversal limit',destination))

    def traverse_link(self,link,destination):
        current=self.room();source=link['source']
        assert self.scenes[destination]['id'] in self.edge_enabled(source),('Native edge is gated',current,destination)
        if link['kind']=='actor':
            self.interact(source['_key']);self.settle()
        else:
            x=min(max(source['x'],1),self.scenes[current]['width']-2)
            y=min(max(source['y'],1),self.scenes[current]['height']-2)
            self.walk(x,y,permit_trigger=source);self.settle()
        assert self.room()==destination,('Exit did not transition',current,destination,source['name'],self.xy())
        self.traversed_edges.add((current,source['id'],destination))
        self.emit({'kind':'edge','frame':self.frames,'from':current,'to':destination,
                   'sourceId':source['id'],'inputKind':link['kind']})
        self.photo('entered-'+destination+'-'+str(self.frames))

    def cover_world_edges(self):
        """Walk every native trigger and manifest actor portal after the ending."""
        assert self.value('ENDING_SEEN')==1 and self.value('P12')==1
        permanent=self.state([f'P{i:02}' for i in range(1,13)]+['ENDING_SEEN','PHASE'])
        native_edges=list(self.world_map['edges'])
        manifest_ids={e.get('actorId',e.get('triggerId')) for e in native_edges}
        for code,scene in self.scenes.items():
            for trigger in scene['triggers']:
                if trigger['id'] in manifest_ids:continue
                destinations={self.scene_ids[sid] for sid in self.edge_enabled(trigger)}
                assert len(destinations)==1,('Unmanifested native exit has ambiguous destinations',code,trigger['name'],destinations)
                native_edges.append({'from':code,'to':destinations.pop(),'triggerId':trigger['id']})
        for edge in native_edges:
            source_id=edge.get('actorId',edge.get('triggerId'))
            if (edge['from'],source_id,edge['to']) in self.traversed_edges:continue
            self.go_room(edge['from'])
            if 'actor' in edge:
                source=self.actor(edge['actor']);kind='actor'
            else:
                found=[t for t in self.scenes[self.room()]['triggers'] if t['id']==source_id]
                assert len(found)==1,('Missing manifest trigger',edge)
                source=found[0];kind='trigger'
            self.traverse_link({'kind':kind,'source':source},edge['to'])
            assert self.state(permanent)==permanent,('Revisit lost permanent progression',edge)
        expected={(e['from'],e.get('actorId',e.get('triggerId')),e['to']) for e in native_edges}
        assert expected<=self.traversed_edges,('Uncovered directed native exits',expected-self.traversed_edges)
        self.emit({'kind':'directedExitCoverage','frame':self.frames,'manifestEdges':len(self.world_map['edges']),'actualSourceConnections':len(expected),
                   'actualSourceTriggers':sum(len(s['triggers']) for s in self.scenes.values()),'passed':True})

    def open_camp(self):
        actors=[a for a in self.scenes[self.room()]['actors']
                if not self.actor_runtime(a)['hidden'] and any(
                    event['command']=='EVENT_MENU' and event['args'].get('option1','').upper()=='COMPANION'
                    for event in events(self.resolved_script(a.get('script',[]))))]
        assert actors,('No visible native camp actor',self.room())
        self.camp_actor=actors[0]
        self.interact(actors[0]['_key']);self.wait_menu()

    def companion(self,label):
        self.open_camp();self.choose_menu(1);self.wait_menu()
        labels=self.selected_menu_options(self.camp_actor['script'],'MOTH')
        assert label.upper() in [s.upper() for s in labels],('Unrecruited companion absent from menu',label,labels)
        self.choose_menu([s.upper() for s in labels].index(label.upper())+1);self.settle()
        return labels

    def companion_options(self):
        self.open_camp();self.choose_menu(1);self.wait_menu()
        labels=self.selected_menu_options(self.camp_actor['script'],'MOTH')
        self.choose_menu(0);self.settle();return labels

    def character(self,index):
        self.open_camp();self.choose_menu(2);self.choose_menu(index);self.settle()

    def save(self):
        self.open_camp();self.choose_menu(4);self.choose_menu(1);self.settle()
        self.photo('saved-'+self.room()+'-'+str(self.frames))

    def settings(self,index,subindex=None):
        self.press('start');self.choose_menu(2);self.choose_menu(index)
        if subindex is not None:self.choose_menu(subindex)
        self.settle()

    def assert_values(self, **values):
        actual=self.state(values)
        assert actual==values,('Quest assertion failed',self.room(),self.xy(),values,actual)
        self.checks.append({'frame':self.frames,'room':self.room(),'values':actual})
        self.emit({'kind':'check',**self.checks[-1]})

    def finish(self, passed=False, error=None):
        report={'passed':passed,'romSha256':self.identity,'qa':str(self.qa),
                'runtime':self.runtime,
                'frames':self.frames,'boots':self.boots,'visitedRooms':sorted(self.visited),
                'directedEdgesTraversed':[list(e) for e in sorted(self.traversed_edges)],
                'state':self.state(),'checks':self.checks,'error':error,
                'scope':'Ordinary-input file-backed PyBoy regression on receipt-paired ROM',
                'memoryWrites':False,'saveFixtureInjection':False,'physicalTested':False,
                'audioListeningTested':False,'firstTimeHumanPacingTested':False}
        self.photo('final' if passed else 'failure')
        (self.qa/'report.json').write_text(json.dumps(report,indent=2)+'\n')
        self.p.stop(save=False);self.journal.close();return report
