/* Standalone original song validation against official installed GB Studio code.
 * No native project is selected, changed, built, or launched by this check.
 * Pass the vendor GB Studio folder as the first argument.
 */
const fs = require('fs');
const path = require('path');
const assert = require('assert');
const vendor = path.resolve(process.argv[2]);
require(path.join(vendor, 'node_modules/ts-node')).register({
  transpileOnly: true,
  skipProject: true,
  compilerOptions: {module: 'CommonJS',moduleResolution: 'node',esModuleInterop: true,target: 'es2019',jsx: 'react'},
});
require(path.join(vendor, 'node_modules/tsconfig-paths')).register({
  baseUrl: path.join(vendor, 'src'), paths: {'*': ['*']},
});
const {loadUGESong, saveUGESong, exportToC} = require(path.join(vendor,'src/shared/lib/uge/ugeHelper.ts'));
const {decompress8bitNumberString} = require(path.join(vendor,'src/shared/lib/resources/compression.ts'));
const schemas=require(path.join(vendor,'src/shared/lib/resources/types.ts'));
const {Value}=require(path.join(vendor,'node_modules/@sinclair/typebox/value'));
const reports=[];
for(const name of ['porch','creek','ridge','hollow','dawn']) {
  const buffer=fs.readFileSync(path.join(__dirname,'music',name+'.uge'));
  const song=loadUGESong(buffer);
  const sequence=JSON.parse(fs.readFileSync(path.join(__dirname,'music',name+'.sequence.json')));
  assert.equal(song.patterns.length,sequence.patterns.length);
  assert.equal(song.sequence.length,sequence.orders[0].length);
  assert.equal(song.ticksPerRow,sequence.ticksPerRow);
  assert.equal(song.dutyInstruments[0].initialVolume,5);
  assert.equal(song.dutyInstruments[1].initialVolume,3);
  assert.equal(song.waveInstruments[0].volume,3);
  assert.equal(song.noiseInstruments[0].initialVolume,1);
  for(let p=0;p<sequence.patterns.length;p++)for(let r=0;r<64;r++) {
    const original=sequence.patterns[p][r]; const parsed=song.patterns[p][r];
    assert.equal(parsed.note,original[0]===90?null:original[0]);
    assert.equal(parsed.instrument,original[1]===0?null:original[1]-1);
  }
  const roundtrip=loadUGESong(saveUGESong(song));
  assert.deepEqual(roundtrip.patterns,song.patterns);
  assert.deepEqual(roundtrip.sequence,song.sequence);
  const c=exportToC(song,'pocketholler_'+name);
  assert(c.includes('const hUGESong_t pocketholler_'+name+'_Data'));
  reports.push({song:name,parser:'Official GB Studio loadUGESong',patterns:song.patterns.length,sequenceLength:song.sequence.length,
    matchedPatternCells:sequence.patterns.length*64,roundtrip:true,officialCExporter:true,bytes:buffer.length});
}
const art=JSON.parse(fs.readFileSync(path.join(__dirname,'art-manifest.json')));
for(const room of art.rooms) {
  const res=JSON.parse(fs.readFileSync(path.join(__dirname,room.background+'.gbsres')));
  assert(Value.Check(schemas.CompressedBackgroundResource,res),JSON.stringify([...Value.Errors(schemas.CompressedBackgroundResource,res)]));
  assert.deepEqual(decompress8bitNumberString(res.tileColors),room.slots);
}
for(const sprite of art.sprites) {
  const res=JSON.parse(fs.readFileSync(path.join(__dirname,sprite.image+'.gbsres')));
  assert(Value.Check(schemas.SpriteResource,res),JSON.stringify([...Value.Errors(schemas.SpriteResource,res)]));
}
for(const name of ['porch','creek','ridge','hollow','dawn']) {
  const res=JSON.parse(fs.readFileSync(path.join(__dirname,'music',name+'.uge.gbsres')));
  assert(Value.Check(schemas.MusicResource,res),JSON.stringify([...Value.Errors(schemas.MusicResource,res)]));
}
const report={music:reports,backgroundPaletteRunsChecked:18,nativeResourceSchemasChecked:{backgrounds:18,sprites:7,music:5},
  limitation:'Format validation and composition previews do not verify built-ROM playback, audio mixing or user pacing.'};
fs.writeFileSync(path.join(__dirname,'validation-report.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report));
