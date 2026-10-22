const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const engine=require('../site/search.js');
const taxonomy=JSON.parse(fs.readFileSync(path.join(__dirname,'../data/taxonomy.json'),'utf8'));
const catalog=JSON.parse(fs.readFileSync(path.join(__dirname,'../data/papers.json'),'utf8'));

const defaults={area:'all',direction:'all',tags:[]};
const sample={area:'world-construction',direction:'reconstruction',tags:{research_challenges:['physical-consistency'],memory_state:['explicit-state']}};

test('one primary area, its direction and all selected auxiliary tags must match together',()=>{
  assert.equal(engine.matchesClassification(sample,defaults),true);
  assert.equal(engine.matchesClassification(sample,{...defaults,area:'world-construction',direction:'reconstruction',tags:['physical-consistency','explicit-state']}),true);
  assert.equal(engine.matchesClassification(sample,{...defaults,area:'resources-analysis'}),false);
  assert.equal(engine.matchesClassification(sample,{...defaults,direction:'generation'}),false);
  assert.equal(engine.matchesClassification(sample,{...defaults,tags:['physical-consistency','streaming-output']}),false);
});
test('toggling an auxiliary tag preserves other choices and never mutates its input',()=>{
  const original=['physical-consistency'];
  const selected=engine.toggleTag(original,'explicit-state');
  assert.deepEqual(selected,['physical-consistency','explicit-state']);
  assert.deepEqual(engine.toggleTag(selected,'explicit-state'),original);
  assert.deepEqual(original,['physical-consistency']);
});
test('URLs deduplicate valid auxiliary tags, preserve other filters and remove legacy topics',()=>{
  const params=new URLSearchParams('q=robot&month=2026-10&area=world-construction&direction=reconstruction&tags=physical-consistency,unknown,physical-consistency&tags=explicit-state&topics=physics&exclude=physics&match=any');
  const state=engine.readFilters(params,taxonomy);
  assert.deepEqual(state,{area:'world-construction',direction:'reconstruction',tags:['physical-consistency','explicit-state']});
  engine.writeFilters(params,state);
  assert.equal(params.get('q'),'robot');assert.equal(params.get('month'),'2026-10');
  for(const key of ['topics','exclude','match'])assert.equal(params.has(key),false);
  assert.deepEqual(engine.readFilters(params,taxonomy),{...state,tags:[...state.tags].sort()});
  engine.writeFilters(params,defaults);assert.equal(params.toString(),'q=robot&month=2026-10');
});
test('a direction identifies one parent; mismatched or unknown values cannot add hidden filters',()=>{
  assert.deepEqual(engine.readFilters(new URLSearchParams('direction=reconstruction'),taxonomy),{...defaults,area:'world-construction',direction:'reconstruction'});
  assert.deepEqual(engine.readFilters(new URLSearchParams('area=resources-analysis&direction=reconstruction'),taxonomy),{...defaults,area:'resources-analysis'});
  assert.deepEqual(engine.readFilters(new URLSearchParams('area=unknown&direction=unknown&tags=unknown&topics=physics'),taxonomy),defaults);
  assert.deepEqual(engine.readFilters(new URLSearchParams('area=world-construction&area=resources-analysis'),taxonomy),{...defaults,area:'world-construction'});
});
test('eight auxiliary dimensions expose unique labels and index every record without mutation',()=>{
  const before=JSON.stringify(catalog),options=engine.tagOptions(taxonomy),valid=new Set(options.map(t=>t.id));
  assert.equal(taxonomy.research_areas.length,6);assert.equal(taxonomy.tag_dimensions.length,8);
  assert.equal(options.length,valid.size);
  for(const paper of catalog.papers){
    const ids=engine.tagIds(paper.classification);
    assert.ok(ids.length>=1);assert.equal(ids.length,new Set(ids).size);assert.ok(ids.every(id=>valid.has(id)));
    const matches=taxonomy.research_areas.filter(a=>engine.matchesClassification(paper.classification,{...defaults,area:a.id}));
    assert.deepEqual(matches.map(a=>a.id),[paper.classification.area]);
  }
  assert.equal(JSON.stringify(catalog),before);
});
