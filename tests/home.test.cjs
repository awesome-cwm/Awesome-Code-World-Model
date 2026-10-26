const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const query = require('../site/app.js');
const load = name => JSON.parse(fs.readFileSync(path.join(__dirname,'../data',name),'utf8'));
const taxonomy = load('taxonomy.json');
const {papers} = load('papers.json');
const parse = text => query.parse(text,taxonomy,papers);
const set = (text,key,value) => query.set(text,key,value,taxonomy,papers);

test('free text and quoted phrases stay separate from structured commands', () => {
  const result = parse('"physical world" Newton track:understand code:yes classic:yes sort:title');
  assert.deepEqual(result.terms,['physical world','Newton']);
  assert.equal(result.state.track,'understanding');
  assert.equal(result.state.code,'yes');
  assert.equal(result.state.classic,'yes');
  assert.equal(result.state.sort,'title');
  assert.deepEqual(result.errors,[]);
});

test('all taxonomy categories, scopes, collections, months and dimension values are queryable', () => {
  for (const c of taxonomy.categories) assert.equal(parse(`cat:${c.id}`).state.category,c.id);
  for (const key of Object.keys(taxonomy.scopes)) assert.equal(parse(`scope:${key}`).state.scope,key);
  for (const c of [...taxonomy.collection_sections,...taxonomy.collections]) assert.equal(parse(`collection:${c.id}`).state.collection,c.id);
  for (const d of taxonomy.dimensions) {
    for (const v of Object.keys(d.values)) {
      for (const text of [`dim:${d.id}=${v}`,`dim:${d.id}:${v}`,`${d.id}:${v}`]) {
        assert.equal(parse(text).state[d.id],v,text);
        assert.deepEqual(parse(text).errors,[]);
      }
    }
  }
  assert.equal(parse('month:unknown').state.month,'unknown');
  assert.equal(parse('code:no classic:no resource:not_found').state.tag,'not_found');
});

test('commands on different dimensions intersect; a repeated field uses its final value', () => {
  const result = parse('track:generate track:understand dim:feedback=training dim:delivery=streaming');
  assert.equal(result.state.track,'understanding');
  assert.equal(result.state.feedback,'training');
  assert.equal(result.state.delivery,'streaming');
  assert.equal(parse('track:related').state.track,'adjacent');
  assert.equal(parse('track:generation').state.track,'generation');
});

test('invalid/incomplete commands produce actionable errors, not silently broad results', () => {
  for (const text of ['track:','track:bad','cat:fake','dim:feedback=bad','unknown:foo','month:1900-99','sort:bad','classic:maybe']) {
    assert.equal(parse(text).errors.length,1,text);
  }
});

test('setting a field preserves quoted text, removes old aliases, and repairs incomplete fields', () => {
  const input = '"physical  world" category:g_rendering code:yes';
  assert.equal(set(input,'cat','u_reasoning'),'"physical  world" code:yes cat:u_reasoning');
  assert.equal(set('track:understand track:generate code:yes','track','all'),'code:yes');
  assert.equal(set('physics track:','track','generate'),'physics track:generate');
  assert.equal(set('dim:feedback=training feedback:visual','feedback','execution'),'dim:feedback=execution');
  assert.equal(set('sort:oldest code:no','sort','newest'),'code:no');
});

test('completions replace the token at the caret without swallowing later commands', () => {
  const text = 'physics track:und code:yes';
  const result = query.complete(text,17,taxonomy,papers);
  assert.equal(result.start,8);
  assert.equal(result.end,17);
  assert.deepEqual(result.items.map(i=>i.text),['track:understand']);
  const dims = query.complete('dim:feedback=',13,taxonomy,papers);
  assert.ok(dims.items.length > 1);
  assert.ok(dims.items.every(i=>i.text.startsWith('dim:feedback=')));
  assert.ok(query.complete('coll',4,taxonomy,papers).items.some(i=>i.text==='collection:'));
});

test('legacy URLs migrate to the same query grammar and shareable q URLs roundtrip', () => {
  const params = new URLSearchParams('q=physics&track=understanding&category=u_reasoning&tag=classic&delivery=streaming&sort=oldest');
  const text = query.fromParams(params,taxonomy,papers);
  const state = parse(text).state;
  assert.equal(state.q,'physics');
  assert.equal(state.track,'understanding');
  assert.equal(state.category,'u_reasoning');
  assert.equal(state.classic,'yes');
  assert.equal(state.delivery,'streaming');
  assert.equal(state.sort,'oldest');
  const roundtrip = query.fromParams(new URLSearchParams({q:text}),taxonomy,papers);
  assert.equal(roundtrip,text);
  assert.equal(parse(query.fromParams(new URLSearchParams('tag=not_found'),taxonomy,papers)).state.tag,'not_found');
});
