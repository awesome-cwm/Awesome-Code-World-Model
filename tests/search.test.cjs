const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const engine=require('../site/search.js');
const taxonomy=JSON.parse(fs.readFileSync(path.join(__dirname,'../data/taxonomy.json'),'utf8'));
const catalog=JSON.parse(fs.readFileSync(path.join(__dirname,'../data/papers.json'),'utf8'));

test('flat topic selection uses intersection and an empty selection includes every paper',()=>{
  const actual=Object.freeze(['general-world-model','memory','interactive']);
  assert.equal(engine.matchesTopics(actual,[]),true);
  assert.equal(engine.matchesTopics(actual,['memory']),true);
  assert.equal(engine.matchesTopics(actual,['memory','interactive']),true);
  assert.equal(engine.matchesTopics(actual,['memory','real-time']),false);
  assert.equal(engine.matchesTopics([],['memory']),false);
  assert.equal(engine.matchesTopics([],[]),true);
  assert.deepEqual(actual,['general-world-model','memory','interactive']);
});

test('toggling a topic adds or removes only that topic and never mutates the input',()=>{
  const original=Object.freeze(['memory']);
  const selected=engine.toggleTopic(original,'interactive');
  assert.deepEqual(selected,['memory','interactive']);
  assert.deepEqual(engine.toggleTopic(Object.freeze(selected),'interactive'),original);
  assert.deepEqual(engine.toggleTopic(original,'memory'),[]);
  assert.deepEqual(original,['memory']);
});

test('topic URLs merge repeated parameters and discard duplicate, empty and unknown values',()=>{
  const params=new URLSearchParams('topics=memory,unknown,memory,,&topics=interactive&topics=Memory&topics=real-time,interactive');
  assert.deepEqual(engine.readTopics(params,taxonomy.topics),['memory','interactive','real-time']);
  assert.deepEqual(engine.readTopics(new URLSearchParams('topics=unknown&topics='),taxonomy.topics),[]);
  assert.deepEqual(engine.readTopics(new URLSearchParams(),taxonomy.topics),[]);
});

test('legacy area, direction and auxiliary tag parameters cannot apply hidden topic filters',()=>{
  const legacy=new URLSearchParams('area=world-construction&direction=reconstruction&tags=physical-consistency&exclude=memory&match=any');
  assert.deepEqual(engine.readTopics(legacy,taxonomy.topics),[]);
  legacy.append('topics','physics,memory');
  assert.deepEqual(engine.readTopics(legacy,taxonomy.topics),['physics','memory']);
});

test('writing a canonical URL preserves search, month and resources while removing obsolete filters',()=>{
  const params=new URLSearchParams('q=robot+arm&month=2026-10&badge=available&topics=old&area=world-construction&direction=reconstruction&tags=old&exclude=physics&match=any');
  const selected=Object.freeze(['memory','interactive','memory']);
  assert.equal(engine.writeTopics(params,selected),params);
  assert.equal(params.get('q'),'robot arm');
  assert.equal(params.get('month'),'2026-10');
  assert.equal(params.get('badge'),'available');
  assert.equal(params.get('topics'),'interactive,memory');
  for(const key of ['area','direction','tags','exclude','match'])assert.equal(params.has(key),false);
  assert.deepEqual(engine.readTopics(params,taxonomy.topics),['interactive','memory']);
  assert.deepEqual(selected,['memory','interactive','memory']);
  const canonical=params.toString();
  engine.writeTopics(params,engine.readTopics(params,taxonomy.topics));
  assert.equal(params.toString(),canonical);
  engine.writeTopics(params,[]);
  assert.equal(params.has('topics'),false);
  assert.equal(params.toString(),'q=robot+arm&month=2026-10&badge=available');
});

test('all 58 records have one README topic but can match multiple peer website filters',()=>{
  const before=JSON.stringify(catalog);
  const valid=new Set(taxonomy.topics.map(topic=>topic.id));
  assert.equal(taxonomy.topics.length,22);
  assert.equal(valid.size,22);
  assert.equal(catalog.papers.length,58);
  let websiteMemberships=0;
  for(const paper of catalog.papers){
    const classification=paper.classification;
    assert.equal(typeof classification.readme_topic,'string');
    assert.ok(classification.topics.length>=1);
    assert.equal(classification.topics.length,new Set(classification.topics).size);
    assert.ok(classification.topics.every(topic=>valid.has(topic)));
    assert.ok(classification.topics.includes(classification.readme_topic));
    for(const topic of classification.topics){
      assert.equal(engine.matchesTopics(classification.topics,[topic]),true);
      websiteMemberships++;
    }
    assert.equal(engine.matchesTopics(classification.topics,classification.topics),true);
  }
  assert.ok(websiteMemberships>catalog.papers.length);
  const paper=catalog.papers.find(p=>p.classification.topics.length>1);
  const secondary=paper.classification.topics.find(topic=>topic!==paper.classification.readme_topic);
  assert.ok(secondary);
  assert.equal(engine.matchesTopics(paper.classification.topics,[secondary]),true);
  assert.equal(engine.matchesTopics(paper.classification.topics,[paper.classification.readme_topic,secondary]),true);
  const readmePlacements=taxonomy.topics.filter(topic=>topic.id===paper.classification.readme_topic);
  assert.equal(readmePlacements.length,1);
  assert.equal(JSON.stringify(catalog),before);
});
