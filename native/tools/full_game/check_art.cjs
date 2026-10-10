/* Check authored native art/resources without building or driving the game. */
const fs=require('fs'),path=require('path'),assert=require('assert');
const vendor=process.argv[2] || '/Users/martinbowling/Library/Application Support/modretro-chromatic/toolchain/.local/vendor/gb-studio';
require(vendor+'/node_modules/ts-node').register({transpileOnly:true,skipProject:true,compilerOptions:{module:'CommonJS',moduleResolution:'node',esModuleInterop:true,target:'es2019',jsx:'react'}});
require(vendor+'/node_modules/tsconfig-paths').register({baseUrl:vendor+'/src',paths:{'*':['*']}});
const schemas=require(vendor+'/src/shared/lib/resources/types.ts');
const {Value}=require(vendor+'/node_modules/@sinclair/typebox/value');
const {decompress8bitNumberString}=require(vendor+'/src/shared/lib/resources/compression.ts');
const {loadUGESong}=require(vendor+'/src/shared/lib/uge/ugeHelper.ts');
const root=path.resolve(__dirname,'../..');
const read=p=>JSON.parse(fs.readFileSync(p));
let scenes=0,actors=0,events=0;const eventIds=new Set();
function checkEventIds(v){
  if(Array.isArray(v))for(const x of v)checkEventIds(x);
  else if(v&&typeof v==='object'){
    if(v.command){assert(!eventIds.has(v.id),'Duplicate event '+v.id);eventIds.add(v.id);events++;}
    for(const [k,x]of Object.entries(v))if(k!=='id')checkEventIds(x);
  }
}
const manifest=read(path.join(__dirname,'integrated-art-manifest.json'));
assert(!manifest.geometryOnly);
for(const row of manifest.rooms){
  const folder=path.join(root,row.scenePath);const scene=read(folder+'/scene.gbsres');
  assert(Value.Check(schemas.CompressedSceneResource,scene),JSON.stringify([...Value.Errors(schemas.CompressedSceneResource,scene)]));
  const solid=decompress8bitNumberString(scene.collisions);assert.equal(solid.length,360);
  for(let y=3;y<16;y++)for(let x=2;x<18;x++)assert.equal(solid[y*20+x],0);
  const af=fs.readdirSync(folder+'/actors').filter(x=>x.endsWith('.gbsres'));assert(af.length<=20);let companion=0;
  for(const filename of af){
    const actor=read(folder+'/actors/'+filename);
    assert(Value.Check(schemas.ActorResource,actor),JSON.stringify([...Value.Errors(schemas.ActorResource,actor)]));
    checkEventIds(actor);actors++;
    if(filename==='companion.gbsres'){
      assert.equal(actor.collisionGroup,'');
      assert(actor.startScript.some(e=>e.command==='EVENT_ACTOR_COLLISIONS_DISABLE'));
      assert(actor.updateScript.length>0);companion++;
    }
  }
  assert.equal(companion,1);checkEventIds(scene);scenes++;
}
let backgrounds=0,sprites=0,music=0;
for(const folder of ['backgrounds','sprites','music'])for(const filename of fs.readdirSync(root+'/assets/'+folder).filter(x=>x.endsWith('.gbsres'))){
  const data=read(root+'/assets/'+folder+'/'+filename);
  const schema=folder==='backgrounds'?schemas.CompressedBackgroundResource:folder==='sprites'?schemas.SpriteResource:schemas.MusicResource;
  assert(Value.Check(schema,data),filename+JSON.stringify([...Value.Errors(schema,data)]));
  if(folder==='backgrounds')backgrounds++;
  else if(folder==='sprites')sprites++;
  else{loadUGESong(fs.readFileSync(root+'/assets/music/'+data.filename));music++;}
}
const result={newScenes:scenes,newActors:actors,uniqueNewEventIds:events,totalRegisteredAssets:{backgrounds,sprites,music},
  officialSchemas:true,centralWalkableFloors:true,oneExplicitlyNoncollidingFollowerPerScene:true,
  allSongsOfficialParser:true,compiled:false,runtimeVerified:false};
fs.writeFileSync(path.join(__dirname,'native-art-check.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
