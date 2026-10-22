const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const engine=require('../site/search.js');
const taxonomy=JSON.parse(fs.readFileSync(path.join(__dirname,'../data/taxonomy.json'),'utf8'));
const catalog=JSON.parse(fs.readFileSync(path.join(__dirname,'../data/papers.json'),'utf8'));

test('multiple checked topics match their intersection; an empty selection matches all',()=>{
  const query={include:['physics','reconstruction']};
  assert.equal(engine.matchesTopics(['physics','reconstruction','rendering'],query),true);
  assert.equal(engine.matchesTopics(['physics'],query),false);
  assert.equal(engine.matchesTopics([],query),false);
  assert.equal(engine.matchesTopics([],{include:[]}),true);
});
test('clicking a topic twice selects then deselects it and preserves the other selections',()=>{
  const original=['physics'];
  const selected=engine.toggleTopic(original,'reconstruction');
  assert.deepEqual(selected,['physics','reconstruction']);
  assert.deepEqual(engine.toggleTopic(selected,'reconstruction'),['physics']);
  assert.deepEqual(original,['physics']);
});
test('URL state deduplicates topics, ignores unknown and removed filters, and round-trips',()=>{
  const params=new URLSearchParams('q=robot&topics=physics,unknown,physics&topics=reconstruction&exclude=physics&match=any');
  const query=engine.readTopics(params,taxonomy.topics);
  assert.deepEqual(query,{include:['physics','reconstruction']});
  engine.writeTopics(params,query);
  assert.equal(params.get('q'),'robot');
  assert.equal(params.has('exclude'),false);assert.equal(params.has('match'),false);
  assert.deepEqual(engine.readTopics(params,taxonomy.topics),query);
  engine.writeTopics(params,{include:[]});assert.equal(params.toString(),'q=robot');
});
test('the ten topic definitions index all records without modifying paper metadata',()=>{
  const before=JSON.stringify(catalog),valid=new Set(taxonomy.topics.map(t=>t.id));
  assert.equal(valid.size,10);
  for(const paper of catalog.papers){
    const ids=engine.topicsFor(paper,taxonomy.topics);
    assert.equal(ids.length,new Set(ids).size);assert.ok(ids.every(id=>valid.has(id)));
    if(paper.benchmarks.length)assert.ok(ids.includes('evaluation'));
  }
  assert.equal(JSON.stringify(catalog),before);
});
test('reviewed per-paper topics override the provisional metadata mapping',()=>{
  const paper={...catalog.papers[0],topics:['physics','physics','unknown']};
  assert.deepEqual(engine.topicsFor(paper,taxonomy.topics),['physics']);
  assert.deepEqual(engine.topicsFor({...paper,topics:[]},taxonomy.topics),[]);
});
