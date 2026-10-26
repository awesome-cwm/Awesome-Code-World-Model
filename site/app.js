/* Query grammar shared by the command UI and regression tests. */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.CWM_QUERY = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  const aliases = {generate:'generation', understand:'understanding', related:'adjacent'};
  const trackValue = value => ({generation:'generate', understanding:'understand', adjacent:'related'}[value] || value);
  const tokenize = text => [...text.matchAll(/(?:[^\s"']+|"[^"\n]*"|'[^'\n]*')+/g)].map(match => ({raw:match[0], start:match.index, end:match.index + match[0].length}));
  const unquote = value => value.replace(/^(["'])(.*)\1$/, '$2');

  function fields(taxonomy, papers) {
    return {
      track: [{value:'generate', label:taxonomy.tracks.find(t => t.id === 'generation').name}, {value:'understand', label:taxonomy.tracks.find(t => t.id === 'understanding').name}, {value:'related', label:taxonomy.tracks.find(t => t.id === 'adjacent').name}],
      cat: taxonomy.categories.map(c => ({value:c.id, label:c.name})),
      scope: Object.entries(taxonomy.scopes).map(([value,label]) => ({value,label})),
      dim: taxonomy.dimensions.flatMap(d => Object.entries(d.values).map(([v,label]) => ({value:`${d.id}=${v}`, label:`${d.name} / ${label}`}))),
      collection: [...taxonomy.collection_sections, ...taxonomy.collections].map(c => ({value:c.id, label:c.name})),
      month: [...new Set(papers.filter(p => p.published).map(p => p.published.slice(0,7)))].sort().reverse().map(value => ({value,label:value})).concat({value:'unknown',label:'Date unconfirmed'}),
      code: [{value:'yes',label:'Code resource available'}, {value:'no',label:'No code resource found'}],
      classic: [{value:'yes',label:'Representative works'}, {value:'no',label:'Other works'}],
      resource: [{value:'available',label:'Any public resource'}, {value:'not_found',label:'No public resources found'}],
      sort: [{value:'newest',label:'Newest first'}, {value:'oldest',label:'Oldest first'}, {value:'title',label:'Title A-Z'}]
    };
  }

  function parse(text, taxonomy, papers) {
    const allowed = fields(taxonomy, papers);
    const state = {q:'', track:'all', category:'all', scope:'all', collection:'all', month:'all', code:'all', classic:'all', tag:'all', sort:'newest'};
    taxonomy.dimensions.forEach(d => { state[d.id] = 'all'; });
    const errors = [], tokens = [], free = [];
    for (const token of tokenize(text)) {
      const match = token.raw.match(/^([a-z_]+):(.*)$/i);
      if (!match) { free.push(unquote(token.raw)); continue; }
      let key = match[1].toLowerCase(), value = unquote(match[2]).toLowerCase();
      if (key === 'category') key = 'cat';
      if (key === 'dim') {
        const parts = value.match(/^([a-z_]+)[=:](.+)$/);
        if (parts && taxonomy.dimensions.some(d => d.id === parts[1])) { key = parts[1]; value = parts[2]; }
      }
      const dimension = taxonomy.dimensions.find(d => d.id === key);
      let valid = false, field = key;
      if (dimension) valid = Object.hasOwn(dimension.values, value);
      else if (key === 'track') { value = aliases[value] || value; valid = taxonomy.tracks.some(t => t.id === value); }
      else if (key === 'cat') { field = 'category'; valid = allowed.cat.some(c => c.value === value); }
      else if (key === 'resource') { field = 'tag'; valid = allowed.resource.some(c => c.value === value); }
      else if (allowed[key] && key !== 'dim') valid = allowed[key].some(c => c.value === value);
      if (!valid) errors.push(`Unknown filter: ${token.raw}. Use the suggestions or Query syntax.`);
      else { state[field] = value; tokens.push({...token, field, value}); }
    }
    state.q = free.join(' ');
    return {state, errors, tokens, terms:free};
  }

  function set(text, key, value, taxonomy, papers) {
    const field = key === 'cat' ? 'category' : key === 'resource' ? 'tag' : key;
    const parsed = parse(text, taxonomy, papers);
    const removed = new Set(parsed.tokens.filter(t => t.field === field).map(t => t.start));
    let result = tokenize(text).filter(token => {
      if (removed.has(token.start)) return false;
      const rawKey = token.raw.split(':')[0].toLowerCase();
      return !(rawKey === key || (key === 'cat' && rawKey === 'category') ||
        (rawKey === 'dim' && token.raw.slice(4).startsWith(`${key}=`)));
    }).map(token => token.raw).join(' ');
    if (value && value !== 'all' && !(key === 'sort' && value === 'newest')) {
      const dimension = taxonomy.dimensions.some(d => d.id === key);
      const command = dimension ? `dim:${key}=${value}` : `${key}:${key === 'track' ? trackValue(value) : value}`;
      result += `${result ? ' ' : ''}${command}`;
    }
    return result;
  }

  function complete(text, caret, taxonomy, papers) {
    const start = text.lastIndexOf(' ', Math.max(0,caret - 1)) + 1;
    let end = text.indexOf(' ', caret);
    if (end < 0) end = text.length;
    const fragment = text.slice(start,caret).toLowerCase();
    const options = fields(taxonomy,papers);
    const match = fragment.match(/^([a-z_]+):(.*)$/);
    let items = [];
    if (match) {
      const key = match[1] === 'category' ? 'cat' : match[1];
      const direct = taxonomy.dimensions.find(d => d.id === key);
      const list = direct ? Object.entries(direct.values).map(([value,label]) => ({value,label})) : options[key];
      if (list) items = list.filter(item => item.value.startsWith(match[2]) || item.label.toLowerCase().includes(match[2])).map(item => ({text:`${key}:${item.value}`, label:item.label}));
    } else if (fragment && /^[a-z_]+$/.test(fragment)) {
      items = Object.keys(options).filter(key => key.startsWith(fragment)).map(key => ({text:`${key}:`, label:`Filter by ${key}`}));
    }
    return {start,end,items};
  }

  function fromParams(params, taxonomy, papers) {
    let query = params.get('q') || '';
    for (const key of ['track','category','cat','scope','collection','month','code','classic','sort',...taxonomy.dimensions.map(d => d.id)]) {
      if (params.has(key)) query = set(query, key === 'category' ? 'cat' : key, params.get(key), taxonomy, papers);
    }
    const tag = params.get('tag');
    if (tag === 'classic') query = set(query,'classic','yes',taxonomy,papers);
    if (tag === 'code' || tag === 'no-code') query = set(query,'code',tag === 'code' ? 'yes' : 'no',taxonomy,papers);
    if (tag === 'available' || tag === 'not_found') query = set(query,'resource',tag,taxonomy,papers);
    return query;
  }
  return {parse, set, complete, fields, fromParams, tokenize};
});

/* 数据来自统一目录；所有动态文本在插入 HTML 前转义。 */
(() => {
  'use strict';
  if (typeof document === 'undefined') return;
  const {papers, taxonomy, curated_at} = window.CWM_CATALOG;
  const $ = s => document.querySelector(s);
  const commandHome = document.body.classList.contains('command-home');
  const query = window.CWM_QUERY;
  const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const byId = new Map(papers.map(p => [p.id, p]));
  const cat = id => taxonomy.categories.find(c => c.id === id);
  const dim = id => taxonomy.dimensions.find(d => d.id === id);
  const collection = id => taxonomy.collections.find(c=>c.id===id) || taxonomy.collection_sections.find(c=>c.id===id);
  const inCollection = (p,id) => id==='all' || p.collections.includes(id) || p.collections.some(c=>collection(c).section===id);
  const labels = (p, id) => p.dimensions[id].map(v => dim(id).values[v]);
  const selected = new Set();
  const defaults = {q:'', track:'all', category:'all', collection:'all', scope:'all', month:'all', tag:'all', code:'all', classic:'all', sort:'newest', view:'list', path:'all'};
  taxonomy.dimensions.forEach(d => { defaults[d.id] = 'all'; });
  let state = {...defaults};
  let toastTimer;
  let commandText = '', queryErrors = [], queryTerms = [], homeMonthTargets = [], homeScrollRows = [], monthFrame = 0, commandTimer;

  function loadState() {
    const params = new URLSearchParams(location.search);
    if (commandHome) {
      commandText = query.fromParams(params, taxonomy, papers);
      const parsed = query.parse(commandText, taxonomy, papers);
      state = {...defaults, ...parsed.state};
      queryErrors = parsed.errors;
      queryTerms = parsed.terms;
      if (['list','categories','benchmarks','matrix','timeline'].includes(params.get('view'))) state.view = params.get('view');
      if (taxonomy.reading_paths.some(p => p.id === params.get('path'))) state.path = params.get('path');
      return;
    }
    state = {...defaults};
    for (const key of Object.keys(defaults)) if (params.has(key)) state[key] = params.get(key);
    const options = {track:['all',...taxonomy.tracks.map(t=>t.id)],category:['all',...taxonomy.categories.map(c=>c.id)],collection:['all',...taxonomy.collections.map(c=>c.id),...taxonomy.collection_sections.map(c=>c.id)],scope:['all',...Object.keys(taxonomy.scopes)],month:['all','unknown',...new Set(papers.filter(p=>p.published).map(p=>p.published.slice(0,7)))],tag:['all','classic','available','not_found'],code:['all','yes','no'],classic:['all','yes','no'],sort:['newest','oldest','title'],view:['list','categories','benchmarks','matrix','timeline'],path:['all',...taxonomy.reading_paths.map(p=>p.id)]};
    taxonomy.dimensions.forEach(d => {options[d.id]=['all',...Object.keys(d.values)];});
    for (const [key, values] of Object.entries(options)) if (!values.includes(state[key])) state[key]=defaults[key];
  }
  function writeState() {
    const params = new URLSearchParams();
    for (const [key, val] of Object.entries(state)) if (val !== defaults[key]) params.set(key, val);
    history.replaceState(null,'',location.pathname+(params.size?'?'+params:'')+location.hash);
  }
  function update(patch, reset=false) {
    if (commandHome) {
      commandText = $('#search').value;
      if (reset) { commandText = ''; state = {...defaults,view:state.view}; }
      for (const [key,value] of Object.entries(patch)) {
        if (key === 'view' || key === 'path') state[key] = value;
        else commandText = query.set(commandText, key === 'category' ? 'cat' : key === 'tag' ? 'resource' : key, value, taxonomy, papers);
      }
      commitCommand(commandText);
      return;
    }
    state = {...(reset?defaults:state),...patch};
    writeState(); syncControls(); render();
  }
  function syncControls() {
    if (commandHome) return syncCommandControls();
    $('#search').value=state.q;
    ['sort','scope','month',...taxonomy.dimensions.map(d=>d.id)].forEach(id=>{const el=$('#'+id);if(el)el.value=state[id];});
    if(taxonomy.dimensions.some(d=>state[d.id]!=='all')) $('#dimension-filters').closest('details').open=true;
    document.querySelectorAll('[data-view]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.view===state.view)));
    document.querySelectorAll('[data-tag]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.tag===state.tag)));
    document.querySelectorAll('[data-category]').forEach(b=>{const active=b.dataset.category===state.category && state.track==='all';b.classList.toggle('active',active);b.setAttribute('aria-pressed',String(active));});
    document.querySelectorAll('.track-filter').forEach(b=>{const active=b.dataset.track===state.track;b.classList.toggle('active',active);b.setAttribute('aria-pressed',String(active));});
    document.querySelectorAll('[data-collection]').forEach(b=>{const active=b.dataset.collection===state.collection;b.classList.toggle('active',active);b.setAttribute('aria-pressed',String(active));});
    const unrestricted=state.category==='all'&&state.track==='all';
    const otherFilters=Object.entries(state).some(([key,value])=>!['category','track','sort','view'].includes(key)&&value!==defaults[key]);
    $('#category-status').textContent=(unrestricted?'Research direction: All.':'Research direction filtered.')+(otherFilters?' Other filters also apply.':'');
  }
  function filtered() {
    if (commandHome && queryErrors.length) return [];
    const terms = commandHome ? queryTerms.map(t=>t.toLocaleLowerCase()) : state.q.toLocaleLowerCase().trim().split(/\s+/).filter(Boolean);
    const path = taxonomy.reading_paths.find(p=>p.id===state.path);
    const result = papers.filter(p=>{
      const haystack = [p.title,p.short_title,...p.authors,p.summary,p.abstract,...p.collections.map(c=>collection(c).name),...p.benchmarks.flatMap(b=>[b.name,b.input,b.artifact,b.checks]),...p.cross_categories.map(c=>cat(c).name),cat(p.category).name,...taxonomy.dimensions.flatMap(d=>labels(p,d.id))].join(' ').toLocaleLowerCase();
      return terms.every(t=>haystack.includes(t)) &&
        (state.track==='all'||p.track===state.track) &&
        (state.category==='all'||p.category===state.category||p.cross_categories.includes(state.category)) &&
        inCollection(p,state.collection) &&
        (state.view!=='benchmarks'||p.benchmarks.length>0) &&
        (state.scope==='all'||p.scope===state.scope) &&
        (state.code==='all'||p.resources.some(r=>r.kind==='code')===(state.code==='yes')) &&
        (state.classic==='all'||p.classic===(state.classic==='yes')) &&
        (state.tag==='all'||(state.tag==='classic'?p.classic:p.resource_status.status===state.tag)) &&
        (state.month==='all'||(p.published?p.published.slice(0,7):'unknown')===state.month) &&
        (!path||path.papers.includes(p.id)) &&
        taxonomy.dimensions.every(d=>state[d.id]==='all'||p.dimensions[d.id].includes(state[d.id]));
    });
    result.sort((a,b)=>{
      if(path) return path.papers.indexOf(a.id)-path.papers.indexOf(b.id);
      if(state.sort==='title') return a.title.localeCompare(b.title);
      if(!a.published && !b.published) return a.title.localeCompare(b.title);
      if(!a.published)return 1;if(!b.published)return -1;
      return (state.sort==='oldest'?1:-1)*a.published.localeCompare(b.published)||a.title.localeCompare(b.title);
    });
    return result;
  }
  function date(p) { return p.published || 'Date unconfirmed'; }
  function trackName(p) { return p.track==='generation'?'GENERATION':p.track==='understanding'?'UNDERSTANDING':'RELATED'; }
  function badge(p) {return `<span class="track-label ${esc(p.track)}">${trackName(p)}</span>`;}
  function icon(kind) {return `<svg class="status-icon" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><path d="${{available:'m5 12 4 4L19 6',not_found:'m6 6 12 12M6 18 18 6',classic:'m12 3 3 6 7 1-5 5 1 7-6-3-6 3 1-7-5-5 7-1Z'}[kind]}"/></svg>`;}
  function resourceBadge(p) {return `<span class="resource-badge ${p.resource_status.status}" title="${esc(p.resource_status.basis)}">${icon(p.resource_status.status)} ${p.resource_status.status==='available'?'Public resources':'Resources not found'}</span>${p.classic?`<span class="classic-badge" title="${esc(p.classic_note)}">${icon('classic')} Representative</span>`:''}`;}
  function resourceLabel(r) {return {paper:'Paper',code:'Code',project:'Project',data:'Data',weights:'Weights'}[r.kind]||r.kind;}
  function links(p, all=false, cardLinks=false) {
    const ordered=cardLinks?[...p.resources].sort((a,b)=>(a.kind==='paper'?0:a.kind==='code'?1:2)-(b.kind==='paper'?0:b.kind==='code'?1:2)):p.resources;
    const list = all?ordered:ordered.slice(0,cardLinks?3:2);
    return list.map(r=>`<a href="${esc(r.url)}" data-resource="${esc(r.kind)}" target="_blank" rel="noopener noreferrer" aria-label="${esc(resourceLabel(r))} for ${esc(p.short_title)} (opens in a new tab)">${esc(resourceLabel(r))} <span aria-hidden="true">↗</span></a>`).join('');
  }
  function compareButton(p) {return `<button class="compare-toggle" data-compare="${esc(p.id)}" aria-pressed="${selected.has(p.id)}" aria-label="${selected.has(p.id)?'Remove':'Add'} ${esc(p.short_title)} ${selected.has(p.id)?'from':'to'} comparison">${selected.has(p.id)?'✓ Selected':'+ Compare'}</button>`;}
  function card(p) {
    if (commandHome) return worldCard(p);
    return `<article class="paper-card${p.classic?' is-classic':''}" data-paper="${esc(p.id)}" data-track="${esc(p.track)}"><div class="paper-meta"><time${p.published?` datetime="${esc(p.published)}"`:''}>${esc(date(p))}</time>${badge(p)}<span>${esc(cat(p.category).name)}</span>${resourceBadge(p)}</div><h3><button data-detail="${esc(p.id)}">${esc(p.title)}</button></h3><p class="paper-summary">${esc(p.summary)}</p>${p.benchmarks.length?`<p class="benchmark-label">BENCHMARK · ${p.benchmarks.map(b=>esc(b.name)).join(' · ')}</p>`:''}<div class="paper-footer"><div class="paper-tags">${[...labels(p,'code_role').slice(0,2),...labels(p,'interaction').slice(0,1)].map(t=>`<span class="tag">${esc(t)}</span>`).join('')}</div><div class="paper-actions">${links(p,false,true)}${compareButton(p)}</div></div></article>`;
  }
  function categoryList(items) {
    return taxonomy.categories.map(c=>{
      const group=items.filter(p=>p.category===c.id||p.cross_categories.includes(c.id));
      if(!commandHome)group.sort((a,b)=>Number(b.classic)-Number(a.classic)||(b.published||'').localeCompare(a.published||'')||b.id.localeCompare(a.id));
      if(!group.length)return '';
      return `<section class="category-block"><h3>${esc(c.name)}</h3><p class="muted">${esc(c.question)}</p>${group.map(p=>`<p class="category-entry${p.classic?' is-classic':''}" data-category-paper="${esc(p.id)}"><span class="entry-month">[${p.published?p.published.slice(0,7):'Date TBC'}]</span> ${icon(p.resource_status.status)}${p.classic?icon('classic'):''}${p.classic?`<span class="entry-note">(${esc(p.classic_note)})</span> `:''}<button data-detail="${esc(p.id)}">${esc(p.title)}</button> <span class="entry-links">${links(p)}</span></p>`).join('')}</section>`;
    }).join('');
  }
  function matrix(items) {
    const columns=['code_role','dynamics','interaction','delivery','evaluation'];
    return `<div class="table-scroll" tabindex="0" aria-label="Paper mechanism matrix"><table><thead><tr><th>Research record</th>${columns.map(k=>`<th>${esc(dim(k).name)}</th>`).join('')}</tr></thead><tbody>${items.map(p=>`<tr><td><button class="matrix-title" data-detail="${esc(p.id)}">${esc(p.short_title)}</button><br><span class="muted">${esc(date(p))}</span><br>${compareButton(p)}</td>${columns.map(k=>`<td>${labels(p,k).map(v=>`<span class="tag">${esc(v)}</span>`).join(' ')}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;
  }
  function benchmarkAtlas(items) {
    return `<p class="atlas-intro">Compare the task and evidence of success. Each row is a named suite within a research record. <a href="benchmarks.html">Reading guide ↗</a></p><div class="table-scroll" tabindex="0" aria-label="Benchmark protocol comparison"><table class="benchmark-table"><thead><tr><th>Benchmark / paper</th><th>Input → artifact</th><th>Evaluation evidence</th><th>Boundary / version</th></tr></thead><tbody>${items.flatMap(p=>p.benchmarks.map(b=>`<tr data-benchmark="${esc(p.id)}"><td><button class="matrix-title" data-detail="${esc(p.id)}">${esc(b.name)}</button><p class="muted">${esc(date(p))}</p>${compareButton(p)}</td><td><p>${esc(b.input)}</p><p class="artifact-arrow">↓ ${esc(b.artifact)}</p></td><td>${esc(b.checks)}</td><td>${esc(b.caveat)}<p><a href="${esc(b.source)}" target="_blank" rel="noopener noreferrer">Protocol ↗</a></p></td></tr>`)).join('')}</tbody></table></div>`;
  }
  function render() {
    const items=filtered();
    if (commandHome) return renderCommandResults(items);
    $('#result-count').innerHTML=`<b>${items.length}</b> of ${papers.length} research records`;
    const path=taxonomy.reading_paths.find(p=>p.id===state.path);
    $('#result-context').hidden=!path;
    $('#result-context').innerHTML=path?`<div><p class="eyebrow">READING PATH</p><h2>${esc(path.title)}</h2><p>${esc(path.description)}</p></div><a href="index.html#reading">All reading paths <span aria-hidden="true">↗</span></a>`:'';
    const active = Object.entries(state).filter(([k,v])=>v!==defaults[k]&&!['sort','view'].includes(k));
    $('#filter-label').textContent=active.length?`Filters · ${active.length}`:'Filters';
    $('#active-filters').innerHTML=active.map(([k,v])=>{
      let title=v;
      if(k==='category')title=cat(v).name;
      if(k==='collection')title=collection(v).name;
      if(k==='track')title=taxonomy.tracks.find(t=>t.id===v).name;
      if(k==='scope')title=taxonomy.scopes[v];
      if(k==='tag')title={classic:'Representative',available:'Public resources',not_found:'Resources not found'}[v];
      if(k==='path')title=taxonomy.reading_paths.find(p=>p.id===v).title;
      if(dim(k))title=dim(k).values[v];
      return `<button class="active-chip" data-remove="${esc(k)}" aria-label="Remove ${esc(k)} filter: ${esc(title)}">${esc(title)} ×</button>`;
    }).join('');
    if(!items.length) $('#paper-list').innerHTML='<div class="empty-state"><span class="eyebrow">NO MATCHES</span><h3>Try a different research question.</h3><p>Search a shorter title, or remove a mechanism filter.</p><button data-reset class="button primary">Reset filters</button></div>';
    else if(state.view==='matrix') $('#paper-list').innerHTML=matrix(items);
    else if(state.view==='categories') $('#paper-list').innerHTML=categoryList(items);
    else if(state.view==='benchmarks') $('#paper-list').innerHTML=benchmarkAtlas(items);
    else if(state.view==='timeline') {
      const groups=new Map();
      items.forEach(p=>{const key=p.published?p.published.slice(0,7):'Publication date unconfirmed';if(!groups.has(key))groups.set(key,[]);groups.get(key).push(p);});
      $('#paper-list').innerHTML=[...groups].map(([month,list])=>`<h3 class="timeline-heading">${esc(month)} <span class="muted">${list.length} records</span></h3>${list.map(card).join('')}`).join('');
    } else $('#paper-list').innerHTML=items.map(card).join('');
    $('#compare-tray').hidden=selected.size===0;
    $('#compare-count').textContent=`${selected.size} / 4 selected`;
    $('#compare-open').disabled=selected.size<2;
  }
  function bibtex(p) {
    const tex=s=>String(s).replace(/[\\{}%&#_$]/g,c=>({'\\':'\\textbackslash{}','{':'\\{','}':'\\}','%':'\\%','&':'\\&','#':'\\#','_':'\\_','$':'\\$'}[c]));
    const r=p.resources.find(r=>r.kind==='paper')||p.resources[0];
    return `@misc{${p.id.replace(/-/g,'')},\n  title = {${tex(p.title)}},\n${p.authors.length?`  author = {${p.authors.map(tex).join(' and ')}},\n`:''}${p.published?`  year = {${p.published.slice(0,4)}},\n`:''}${p.arxiv?`  eprint = {${p.arxiv}},\n  archivePrefix = {arXiv},\n`:''}  url = {${tex(r.url)}}\n}`;
  }
  function detail(id) {
    const p=byId.get(id);if(!p)return;
    $('#detail-content').innerHTML=`<div class="paper-meta">${badge(p)}<span>${esc(date(p))} · ${esc(p.type)}</span></div><h2 id="dialog-title">${esc(p.title)}</h2><p class="authors">${esc(p.authors.join(', ')||'See the official project for attribution.')}</p><div class="link-group">${links(p,true)}</div><h3>Why this work belongs here</h3><p class="detail-summary">${esc(p.summary)}</p><p class="muted">Primary: ${esc(cat(p.category).name)}${p.cross_categories.length?' · Also relevant to: '+p.cross_categories.map(c=>esc(cat(c).name)).join(', '):''}</p>${p.performance_note?`<p class="detail-note">${esc(p.performance_note)}</p>`:''}<dl class="dimensions-grid">${taxonomy.dimensions.map(d=>`<div><dt>${esc(d.name)}</dt><dd>${esc(labels(p,d.id).join(' · '))}</dd></div>`).join('')}</dl>${p.abstract?`<details><summary>Read the source abstract</summary><p class="abstract">${esc(p.abstract)}</p></details>`:''}<h3>Citation <button class="text-link" id="copy-citation">Copy BibTeX ↗</button></h3><pre class="bibtex" id="citation-text">${esc(bibtex(p))}</pre><p class="provenance">Source checked ${esc(p.verification.checked)} · ${p.verification.basis==='primary_abstract'?'arXiv metadata + abstract reviewed':'Official project reviewed'}. Classification is an editorial reading, not an independent reproduction. ${p.published?'Date = first arXiv submission.':'Publication date is unconfirmed; repository creation is not used as a publication date.'}<br><a href="${esc(p.verification.source)}" target="_blank" rel="noopener noreferrer">Source: ${esc(p.verification.source)}</a><br>Resource links are distinguished by type. A linked project or repository does not certify a runnable or open-source release.</p>`;
    $('#copy-citation').onclick=()=>copy(bibtex(p));
    const anchor=$('#detail-content .dimensions-grid');
    if(p.collections.length)anchor.insertAdjacentHTML('beforebegin',`<p class="muted">Indexes: ${p.collections.map(c=>esc(collection(c).name)).join(' · ')}</p>`);
    if(p.benchmarks.length)anchor.insertAdjacentHTML('beforebegin',`<section class="detail-benchmarks"><h3>Benchmark protocol</h3>${p.benchmarks.map(b=>`<h4>${esc(b.name)}</h4><dl><dt>Input</dt><dd>${esc(b.input)}</dd><dt>Submitted artifact</dt><dd>${esc(b.artifact)}</dd><dt>Evaluation evidence</dt><dd>${esc(b.checks)}</dd><dt>Boundary / version</dt><dd>${esc(b.caveat)}</dd></dl><a href="${esc(b.source)}" target="_blank" rel="noopener noreferrer">Protocol source ↗</a>`).join('')}</section>`);
    const basis={primary_abstract:'arXiv metadata + abstract reviewed',official_project:'Official project + available metadata reviewed',full_text:'Relevant full-text sections + metadata reviewed'};
    const provenance=$('#detail-content .provenance');
    provenance.innerHTML=`Source checked ${esc(p.verification.checked)} · ${esc(basis[p.verification.basis])}. Classification is an editorial reading, not an independent reproduction. ${p.published?'Date = first arXiv submission.':'Publication date is unconfirmed at day precision; repository creation is not used as a publication date.'}<br><a href="${esc(p.verification.source)}" target="_blank" rel="noopener noreferrer">Source: ${esc(p.verification.source)}</a><br>Resource links are distinguished by type. A linked project or repository does not certify a runnable or open-source release.`;
    $('#detail-dialog').showModal();
  }
  async function copy(text) {
    let fallback;
    try {
      if(navigator.clipboard && window.isSecureContext) await navigator.clipboard.writeText(text);
      else {fallback=document.createElement('textarea');fallback.value=text;(document.querySelector('dialog[open]')||document.body).append(fallback);fallback.select();if(!document.execCommand('copy'))throw new Error('copy');}
      toast('BibTeX copied.');
    } catch {toast('Select and copy the citation below.');}
    finally {fallback?.remove();}
  }
  function toast(message) {
    clearTimeout(toastTimer);
    if(commandHome)(document.querySelector('dialog[open]')||document.body).append($('#toast'));
    $('#toast').textContent=message;$('#toast').hidden=false;
    toastTimer=setTimeout(()=>{$('#toast').hidden=true;},3000);
  }
  function compare() {
    const items=[...selected].map(id=>byId.get(id));
    const rows=[['Research direction',p=>taxonomy.tracks.find(t=>t.id===p.track).name],['Primary question',p=>cat(p.category).question],...taxonomy.dimensions.map(d=>[d.name,p=>labels(p,d.id).join(' · ')]),...['name','input','artifact','checks','caveat'].map(k=>[{name:'Benchmark',input:'Benchmark input',artifact:'Submitted artifact',checks:'Evaluation evidence',caveat:'Evaluation boundary'}[k],p=>p.benchmarks.map(b=>b[k]).join(' · ')||'No named benchmark protocol indexed.']),['Reported runtime context',p=>p.performance_note||'No runtime comparison recorded.'],['Editorial insight',p=>p.summary]];
    $('#compare-content').innerHTML=`<p class="muted">Evaluation targets describe what the source measures. They are not pass/fail certifications. Timing claims require matching hardware, resolution and latency definitions.</p><div class="table-scroll" tabindex="0"><table><thead><tr><th>Dimension</th>${items.map(p=>`<th>${esc(p.short_title)}</th>`).join('')}</tr></thead><tbody>${rows.map(([name,fn])=>`<tr><th>${esc(name)}</th>${items.map(p=>`<td>${esc(fn(p))}</td>`).join('')}</tr>`).join('')}<tr><th>Source</th>${items.map(p=>`<td><div class="link-group">${links(p)}</div></td>`).join('')}</tr></tbody></table></div>`;
    $('#compare-dialog').showModal();
  }
  function highlighted(value) {
    const text = String(value || '');
    const terms = queryTerms.filter(Boolean).sort((a,b)=>b.length-a.length);
    if (!terms.length) return esc(text);
    const pattern = terms.map(t=>t.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')).join('|');
    return text.split(new RegExp(`(${pattern})`,'gi')).map((part,i)=>i%2?`<mark>${esc(part)}</mark>`:esc(part)).join('');
  }
  function worldActionIcon(kind) {
    const paths={detail:'<circle cx="12" cy="12" r="9"/><path d="M12 11v6m0-10v1"/>',compare:'<path d="M3 5h7v14H3zM14 5h7v14h-7z"/>',cite:'<path d="M9 4H5v16h4m6-16h4v16h-4M10 9l-3 3 3 3m4-6 3 3-3 3"/>'};
    return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true">${paths[kind]}</svg>`;
  }
  function worldCard(p) {
    const primary = p.resources.find(r=>r.kind==='paper') || p.resources[0];
    const resourceIcons = {
      paper:'<path d="M6 3h8l4 4v14H6zM13 3v5h5M9 12h6m-6 4h6"/>',
      project:'<circle cx="12" cy="12" r="9"/><ellipse cx="12" cy="12" rx="4" ry="9"/><path d="M3 12h18M5 6h14M5 18h14"/>',
      code:'<path d="m8 6-6 6 6 6m8-12 6 6-6 6M14 3l-4 18"/>'
    };
    const resources = ['paper','project','code'].flatMap(kind=>p.resources.filter(r=>r.kind===kind));
    const hasCode=p.resources.some(r=>r.kind==='code');
    const signature = (key,value,label=value) => `<button data-signature="${esc(key)}" data-value="${esc(value)}" aria-pressed="${state[key]===value}" aria-label="Filter ${esc(dim(key).name)}: ${esc(dim(key).values[value])}">${esc(label)}</button>`;
    const representation = p.dimensions.representation.slice(0,1).map(v=>signature('representation',v));
    const domain = p.dimensions.domain.slice(0,1).map(v=>signature('domain',v));
    const feedback = p.dimensions.feedback.slice(0,1).map(v=>signature('feedback',v,`feedback:${v}`));
    const delivery = p.dimensions.delivery.filter(v=>v!=='unknown').slice(0,1).map(v=>signature('delivery',v));
    return `<article class="paper-card" data-paper="${esc(p.id)}" data-track="${esc(p.track)}" data-month="${p.published?p.published.slice(0,7):'unknown'}">
      <div class="world-card-top"><div class="world-heading"><div class="world-heading-line"><time${p.published?` datetime="${esc(p.published)}"`:''}>${esc(p.published||'DATE TBC')}</time><span class="track-dot" role="img" aria-label="${esc(taxonomy.tracks.find(t=>t.id===p.track).name)}"></span><h3>${p.classic?`<span class="classic-star" role="img" aria-label="Classic: ${esc(p.classic_note)}">&#9734;</span>`:''}<a href="${esc(primary.url)}" target="_blank" rel="noopener noreferrer">${highlighted(p.title)}</a></h3></div></div>
      <div class="world-actions"><button data-detail="${esc(p.id)}" title="Paper details" aria-label="Details for ${esc(p.short_title)}">${worldActionIcon('detail')}</button><button class="compare-toggle" data-compare="${esc(p.id)}" aria-pressed="${selected.has(p.id)}" title="Compare paper" aria-label="${selected.has(p.id)?'Remove':'Add'} ${esc(p.short_title)} ${selected.has(p.id)?'from':'to'} comparison">${worldActionIcon('compare')}</button><button data-cite="${esc(p.id)}" title="Copy BibTeX" aria-label="Copy BibTeX for ${esc(p.short_title)}">${worldActionIcon('cite')}</button></div></div>
      <div class="world-record-meta"><p class="world-authors">${p.authors.length?p.authors.slice(0,3).map(highlighted).join(', ')+(p.authors.length>3?' et al.':''):'See official project for attribution'}</p><span class="code-status ${hasCode?'has-code':'no-code'}" data-code-status="${hasCode?'available':'not_found'}" title="${hasCode?'Public code link indexed; license has not been verified.':'No public code link is recorded. This does not confirm closed-source status.'}">${icon(hasCode?'available':'not_found')}${hasCode?'Public code':'No public code found'}</span></div>
      <p class="paper-summary">${highlighted(p.summary)}</p><div class="world-signature" role="group" aria-label="Filter by paper tags">${[...representation,...domain,...feedback,...delivery].join('')}</div>
      <div class="world-card-bottom"><div class="world-resources">${resources.map(r=>`<a href="${esc(r.url)}" data-resource="${esc(r.kind)}" target="_blank" rel="noopener noreferrer" aria-label="${esc(resourceLabel(r))} for ${esc(p.short_title)} (opens in a new tab)"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true">${resourceIcons[r.kind]}</svg><span>${esc(resourceLabel(r))}</span></a>`).join('')}</div><span class="world-card-note">${esc(taxonomy.tracks.find(t=>t.id===p.track).name)}</span></div></article>`;
  }
  function syncCommandControls() {
    if ($('#search').value !== commandText) $('#search').value = commandText;
    $('#search-clear').hidden = !commandText;
    const active = Object.entries(state).filter(([key,value])=>value!==defaults[key]&&!['q','view','path','sort'].includes(key));
    $('#filter-count').textContent = String(active.length);
    $('#filter-count').hidden = !active.length;
    $('#filter-open').classList.toggle('has-filters',active.length>0);
    document.querySelectorAll('[data-command]').forEach(button=>{
      const key=button.dataset.command;
      const value=key==='track'?({generate:'generation',understand:'understanding',related:'adjacent'}[button.dataset.value]||button.dataset.value):button.dataset.value;
      button.setAttribute('aria-pressed',String(state[key]===value));
    });
    const topicTrack=state.track!=='all'?state.track:(taxonomy.categories.find(c=>c.id===state.category)?.track||'all');
    $('#direction-topics').hidden=topicTrack==='all';
    document.querySelectorAll('[data-topic-track]').forEach(button=>{button.hidden=button.dataset.topicTrack!==topicTrack;});
    document.querySelectorAll('[data-view]').forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.view===state.view)));
    document.querySelectorAll('[data-facet]').forEach(select=>{
      const key=select.dataset.facet;
      select.value=state[key==='cat'?'category':key==='resource'?'tag':key];
    });
  }
  function commitCommand(text, push=true) {
    clearTimeout(commandTimer);
    commandText = text;
    const parsed = query.parse(text,taxonomy,papers);
    const {view,path} = state;
    state = {...defaults,...parsed.state,view,path};
    queryErrors=parsed.errors; queryTerms=parsed.terms;
    const params=new URLSearchParams();
    if(text.trim())params.set('q',text.trim());
    if(view!=='list')params.set('view',view);
    if(path!=='all')params.set('path',path);
    const next=location.pathname+(params.size?'?'+params:'');
    if(next!==location.pathname+location.search+location.hash)history[push?'pushState':'replaceState'](null,'',next);
    syncControls(); render();
    const top=$('.command-header').offsetHeight;
    if(window.scrollY>top)window.scrollTo(0,top);
  }
  function renderCommandResults(items) {
    $('#result-count').textContent=`${items.length} papers`;
    $('#query-status').textContent=queryErrors.join(' ');
    $('#filter-done').textContent=`Show ${items.length} results`;
    const active=Object.entries(state).filter(([key,value])=>value!==defaults[key]&&!['q','view'].includes(key));
    $('#active-filters').innerHTML=active.map(([key,value])=>{
      let label=value;
      if(key==='category')label=cat(value)?.name||value;
      else if(key==='track')label=taxonomy.tracks.find(t=>t.id===value).name;
      else if(key==='collection')label=collection(value).name;
      else if(key==='scope')label=taxonomy.scopes[value];
      else if(dim(key))label=`${key}:${value}`;
      else if(key==='path')label=taxonomy.reading_paths.find(p=>p.id===value).title;
      else label=`${key}:${value}`;
      return `<button data-home-remove="${esc(key)}" aria-label="Remove ${esc(key)} filter: ${esc(label)}">${esc(label)} <span aria-hidden="true">&times;</span></button>`;
    }).join('')+(commandText||state.path!=='all'?'<button data-reset class="reset-query">Clear query</button>':'');
    const path=taxonomy.reading_paths.find(p=>p.id===state.path);
    $('#result-context').hidden=!path;
    $('#result-context').innerHTML=path?`<h2>${esc(path.title)}</h2><p>${esc(path.description)}</p>`:'';
    if(!items.length)$('#paper-list').innerHTML=`<div class="empty-state"><span class="eyebrow">NO MATCHING WORLDS</span><h3>${queryErrors.length?'Finish or correct the command.':'Try another way into the world.'}</h3><p>Use fewer words, remove a filter, or try <code>track:generate</code>.</p><button data-reset class="button primary">Clear query</button></div>`;
    else if(state.view==='matrix')$('#paper-list').innerHTML=matrix(items);
    else if(state.view==='categories')$('#paper-list').innerHTML=categoryList(items);
    else if(state.view==='benchmarks')$('#paper-list').innerHTML=benchmarkAtlas(items);
    else if(state.view==='timeline') {
      const groups=new Map();
      [...items].sort((a,b)=>state.sort==='oldest'?(a.published||'9999').localeCompare(b.published||'9999'):(b.published||'').localeCompare(a.published||'')).forEach(p=>{const m=p.published?.slice(0,7)||'unknown';if(!groups.has(m))groups.set(m,[]);groups.get(m).push(p);});
      $('#paper-list').innerHTML=[...groups].map(([month,list])=>`<section><h3 class="timeline-heading">${esc(month==='unknown'?'Date unconfirmed':month)} <span class="muted">${list.length} commits</span></h3>${list.map(card).join('')}</section>`).join('');
    } else $('#paper-list').innerHTML=items.map(card).join('');
    $('#compare-tray').hidden=selected.size===0;
    $('#compare-count').textContent=`${selected.size} / 4 selected`;
    $('#compare-open').disabled=selected.size<2;
    renderCommitLog(items);
  }
  function renderCommitLog(items) {
    const months=new Map();
    items.forEach(p=>{const month=p.published?.slice(0,7)||'unknown';if(!months.has(month))months.set(month,[]);months.get(month).push(p.id);});
    const ordered=[...months].sort(([a],[b])=>a==='unknown'?1:b==='unknown'?-1:state.sort==='oldest'?a.localeCompare(b):b.localeCompare(a));
    homeMonthTargets=[];
    $('#month-nav').innerHTML=ordered.map(([month,ids])=>{
      let target=null;
      // All five renderers already expose detail IDs; annotate their first match.
      for(const id of ids) {
        target=$(`#paper-list [data-paper="${id}"]`)||$(`#paper-list [data-category-paper="${id}"]`)||$(`#paper-list [data-detail="${id}"]`)?.closest('tr');
        if(target)break;
      }
      if(!target)return '';
      target.id=`commit-${month}`;
      homeMonthTargets.push({month,target});
      return `<a href="#commit-${month}" data-month-link="${month}"><span>${month==='unknown'?'DATE TBC':month}</span><span>${ids.length.toString().padStart(2,'0')}</span></a>`;
    }).join('');
    $('#month-total').textContent=String(months.size).padStart(2,'0');
    homeMonthTargets.sort((a,b)=>a.target.getBoundingClientRect().top-b.target.getBoundingClientRect().top);
    const rows=[...document.querySelectorAll('#paper-list [data-paper], #paper-list [data-category-paper], #paper-list tr')];
    homeScrollRows=rows.flatMap(target=>{
      const id=target.dataset.paper||target.dataset.categoryPaper||target.querySelector('[data-detail]')?.dataset.detail;
      const p=byId.get(id);return p?[{month:p.published?.slice(0,7)||'unknown',target}]:[];
    });
    updateCommitLog();
  }
  function updateCommitLog() {
    monthFrame=0;
    if(!homeMonthTargets.length||!matchMedia('(min-width:1100px)').matches)return;
    const threshold=$('.command-toolbar').getBoundingClientRect().bottom+50;
    const rows=homeScrollRows.length?homeScrollRows:homeMonthTargets;
    let active=rows[0];
    for(const entry of rows)if(entry.target.getBoundingClientRect().top<=threshold)active=entry;
    if(window.scrollY+innerHeight>=document.documentElement.scrollHeight-2)active=rows.at(-1);
    $('#month-nav').querySelectorAll('a').forEach(link=>{
      if(link.dataset.monthLink===active.month)link.setAttribute('aria-current','location');
      else link.removeAttribute('aria-current');
    });
    const current=$('#month-nav [aria-current]'), container=$('.commit-sticky');
    if(current&&(current.offsetTop<container.scrollTop||current.offsetTop+current.offsetHeight>container.scrollTop+container.clientHeight))container.scrollTop=current.offsetTop-container.clientHeight/2;
  }
  function initCommandHome() {
    $('#catalog-count').innerHTML=`${papers.length} <span>worlds indexed</span>`;
    $('#checked-date').textContent=`// curated ${curated_at}`;
    if(window.CWM_CATALOG.repository)$('#github-link').href=`https://github.com/${window.CWM_CATALOG.repository}`;
    // Keep the curated track/category hierarchy; expose other facets in Filters.
    const groups=[
      {id:'resources',label:'Classic works and public code',tags:[
        {key:'classic',value:'yes',label:'Classic Work',emoji:'\u2b50',description:'Representative works'},
        {key:'code',value:'yes',label:'Public code',emoji:'\ud83d\udcbb',description:'Public code link available; license has not been verified'}
      ]},
      {id:'tracks',label:'Direction',tags:[
        {key:'track',value:'all',label:'All',description:'All research directions'},
        {key:'track',value:'generate',label:'Generate',description:taxonomy.tracks.find(t=>t.id==='generation').question,className:'generate-chip'},
        {key:'track',value:'understand',label:'Understand',description:taxonomy.tracks.find(t=>t.id==='understanding').question,className:'understand-chip'},
        {key:'track',value:'related',label:'Related',description:taxonomy.tracks.find(t=>t.id==='adjacent').question}
      ]}
    ];
    $('#browse-tags').innerHTML=groups.map(group=>`<div class="tag-group" data-tag-group="${esc(group.id)}" role="group" aria-labelledby="tag-group-${esc(group.id)}"><h3 id="tag-group-${esc(group.id)}"${group.id==='resources'?' class="sr-only"':''}>${esc(group.label)}</h3><div class="tag-group-options">${group.tags.map(t=>`<button type="button" class="${esc(t.className||'')}" data-command="${esc(t.key)}" data-value="${esc(t.value)}" aria-pressed="false" title="${esc(t.description)}">${t.emoji?`<span class="filter-emoji" aria-hidden="true">${esc(t.emoji)}</span>`:''}${esc(t.label)}</button>`).join('')}</div></div>`).join('');
    $('#direction-topics').innerHTML='<span class="topic-label">Topics</span>'+taxonomy.categories.map(c=>`<button type="button" data-command="category" data-value="${esc(c.id)}" data-topic-track="${esc(c.track)}" aria-pressed="false" title="${esc(c.question)}" hidden>${esc(c.name)}</button>`).join('');
    const fields=query.fields(taxonomy,papers);
    const names={track:'Research track',cat:'Category',scope:'Collection scope',collection:'Research index',month:'Published month',code:'Code resources',classic:'Classic works',resource:'Public resources',sort:'Sort results'};
    const select=(key,label,options)=>`<label>${esc(label)}<select data-facet="${esc(key)}" id="${esc(key)}"><option value="${key==='sort'?'newest':'all'}">${key==='sort'?'Newest first':'Any / all'}</option>${options.filter(o=>key!=='sort'||o.value!=='newest').map(o=>`<option value="${esc(o.value)}">${esc(o.label)}</option>`).join('')}</select></label>`;
    $('#home-facets').innerHTML=Object.keys(names).map(key=>select(key,names[key],fields[key])).join('')+'<h3>COMPARE MECHANISMS / DIMENSIONS</h3>'+taxonomy.dimensions.map(d=>select(d.id,d.name,Object.entries(d.values).map(([value,label])=>({value,label})))).join('');
    const descriptions={track:'generate | understand | related',cat:'Category IDs from the taxonomy',scope:'core | foundation | adjacent',dim:'dimension=value, e.g. feedback=training. Each dimension can also be a key.',collection:'Benchmark and infrastructure index IDs',month:'YYYY-MM | unknown',code:'yes | no (requires an actual code resource)',classic:'yes | no',resource:'available | not_found (includes projects, data and weights)',sort:'newest | oldest | title'};
    $('#syntax-reference').innerHTML=Object.entries(descriptions).map(([key,label])=>`<dt>${key}:</dt><dd>${esc(label)}</dd>`).join('');
    let suggestions={items:[]}, suggestionIndex=0, composing=false;
    const input=$('#search'), popup=$('#completions');
    function hideSuggestions() {popup.hidden=true;input.setAttribute('aria-expanded','false');input.removeAttribute('aria-activedescendant');}
    function showSuggestions() {
      suggestions=query.complete(input.value,input.selectionStart??input.value.length,taxonomy,papers);
      suggestionIndex=0;
      if(!suggestions.items.length)return hideSuggestions();
      popup.innerHTML=suggestions.items.map((item,i)=>`<div id="suggestion-${i}" role="option" aria-selected="${i===0}" data-suggestion="${i}"><code>${esc(item.text)}</code><span>${esc(item.label)}</span></div>`).join('');
      popup.hidden=false;input.setAttribute('aria-expanded','true');input.setAttribute('aria-activedescendant','suggestion-0');
    }
    function acceptSuggestion(index) {
      const item=suggestions.items[index];if(!item)return;
      const next=input.value.slice(0,suggestions.start)+item.text+(item.text.endsWith(':')?'':' ')+input.value.slice(suggestions.end).trimStart();
      const cursor=suggestions.start+item.text.length+(item.text.endsWith(':')?0:1);
      commitCommand(next);input.focus();input.setSelectionRange(cursor,cursor);
      if(item.text.endsWith(':'))showSuggestions();else hideSuggestions();
    }
    input.addEventListener('input',()=>{
      clearTimeout(commandTimer);
      if(composing)return;
      showSuggestions(); commandTimer=setTimeout(()=>commitCommand(input.value),150);
    });
    input.addEventListener('compositionstart',()=>{composing=true;clearTimeout(commandTimer);hideSuggestions();});
    input.addEventListener('compositionend',()=>{composing=false;showSuggestions();commandTimer=setTimeout(()=>commitCommand(input.value),150);});
    input.addEventListener('click',showSuggestions);
    input.addEventListener('focus',showSuggestions);
    input.addEventListener('blur',()=>{
      hideSuggestions();
      // Keep unchanged results in place so blur does not swallow a card click.
      if(!composing&&input.value!==commandText)commitCommand(input.value);
    });
    input.addEventListener('keydown',event=>{
      if(event.isComposing)return;
      if(!popup.hidden&&['ArrowDown','ArrowUp'].includes(event.key)) {
        event.preventDefault();suggestionIndex=(suggestionIndex+(event.key==='ArrowDown'?1:-1)+suggestions.items.length)%suggestions.items.length;
        popup.querySelectorAll('[role="option"]').forEach((option,i)=>option.setAttribute('aria-selected',String(i===suggestionIndex)));
        input.setAttribute('aria-activedescendant',`suggestion-${suggestionIndex}`);$(`#suggestion-${suggestionIndex}`).scrollIntoView({block:'nearest'});
      } else if(!popup.hidden&&['Enter','Tab'].includes(event.key)) {event.preventDefault();acceptSuggestion(suggestionIndex);}
      else if(event.key==='Enter') {event.preventDefault();commitCommand(input.value);hideSuggestions();}
    });
    popup.addEventListener('pointerdown',event=>{
      const option=event.target.closest('[data-suggestion]');if(!option)return;
      event.preventDefault();acceptSuggestion(Number(option.dataset.suggestion));
    });
    $('#search-clear').onclick=()=>{update({},true);input.focus();hideSuggestions();};
    $('#filter-open').onclick=()=>{commitCommand(input.value);hideSuggestions();$('#filter-dialog').showModal();};
    $('#filter-done').onclick=()=>$('#filter-dialog').close();
    $('#syntax-open').onclick=()=>$('#syntax-dialog').showModal();
    $('#detail-dialog').addEventListener('close',()=>{
      const url=new URL(location.href);
      if(url.searchParams.has('paper')){url.searchParams.delete('paper');history.replaceState(history.state,'',url);}
    });
    $('#home-facets').addEventListener('change',event=>{if(event.target.matches('[data-facet]'))update({[event.target.dataset.facet]:event.target.value});});
    $('#result-sort').addEventListener('change',event=>update({sort:event.target.value}));
    $('#compare-open').onclick=compare;
    $('#compare-clear').onclick=()=>{selected.clear();render();};
    document.addEventListener('click',event=>{
      const b=event.target.closest('button');if(!b)return;
      if(b.hasAttribute('data-command')) {
        const field=b.dataset.command;const active=b.getAttribute('aria-pressed')==='true';
        update({...(field==='track'?{category:'all'}:{}),[field]:active?'all':b.dataset.value});hideSuggestions();
      }
      if(b.hasAttribute('data-signature')){update({[b.dataset.signature]:b.dataset.value});input.focus({preventScroll:true});hideSuggestions();}
      if(b.hasAttribute('data-view'))update({view:b.dataset.view});
      if(b.hasAttribute('data-home-remove'))update({[b.dataset.homeRemove]:defaults[b.dataset.homeRemove]});
      if(b.hasAttribute('data-reset'))update({},true);
      if(b.hasAttribute('data-detail'))detail(b.dataset.detail);
      if(b.hasAttribute('data-cite'))copy(bibtex(byId.get(b.dataset.cite)));
      if(b.hasAttribute('data-compare')) {
        const id=b.dataset.compare;
        if(selected.has(id))selected.delete(id);else if(selected.size<4)selected.add(id);else toast('Compare up to four records at a time.');
        // Keep the focused action in the DOM while updating selection and tray.
        document.querySelectorAll(`[data-compare="${id}"]`).forEach(button=>{
          button.setAttribute('aria-pressed',String(selected.has(id)));
          button.setAttribute('aria-label',`${selected.has(id)?'Remove':'Add'} ${byId.get(id).short_title} ${selected.has(id)?'from':'to'} comparison`);
          button.innerHTML=button.closest('.world-actions')?worldActionIcon('compare'):(selected.has(id)?'Selected':'+ Compare');
        });
        $('#compare-tray').hidden=selected.size===0;$('#compare-count').textContent=`${selected.size} / 4 selected`;$('#compare-open').disabled=selected.size<2;
      }
      if(b.classList.contains('close-dialog'))b.closest('dialog').close();
    });
    document.querySelectorAll('dialog').forEach(dialog=>dialog.addEventListener('click',event=>{
      if(event.target!==dialog)return;const rect=dialog.getBoundingClientRect();
      if(event.clientX<rect.left||event.clientX>rect.right||event.clientY<rect.top||event.clientY>rect.bottom)dialog.close();
    }));
    document.addEventListener('keydown',event=>{
      if(event.isComposing||document.querySelector('dialog[open]'))return;
      const editing=event.target.closest('input,textarea,select,[contenteditable="true"]');
      if((event.key==='/'&&!editing)||((event.ctrlKey||event.metaKey)&&event.key.toLowerCase()==='k')) {event.preventDefault();input.focus();}
      if(event.key==='Escape'&&(!editing||event.target===input)) {event.preventDefault();update({},true);hideSuggestions();input.focus();}
    });
    $('#month-nav').addEventListener('click',event=>{
      const link=event.target.closest('[data-month-link]');if(!link)return;event.preventDefault();
      const target=document.getElementById(`commit-${link.dataset.monthLink}`);
      const offset=$('.command-toolbar').offsetHeight+20;
      if(target)window.scrollTo({top:window.scrollY+target.getBoundingClientRect().top-offset,behavior:'instant'});
      updateCommitLog();
    });
    window.addEventListener('scroll',()=>{if(!monthFrame)monthFrame=requestAnimationFrame(updateCommitLog);},{passive:true});
    new ResizeObserver(()=>{document.body.style.setProperty('--toolbar-height',`${$('.command-toolbar').offsetHeight}px`);updateCommitLog();}).observe($('.command-toolbar'));
    window.addEventListener('popstate',()=>{clearTimeout(commandTimer);hideSuggestions();loadState();syncControls();render();});
    loadState();syncControls();render();
    const paperId=new URLSearchParams(location.search).get('paper');if(paperId)detail(paperId);
  }
  function init() {
    if (commandHome) return initCommandHome();
    const mobileLayout=window.matchMedia('(max-width:800px)');
    $('.library-options').open=!mobileLayout.matches;
    // Keep one set of resource controls, adjacent to results on desktop and inside Filters on mobile.
    function placeResourceFilters() {
      $(mobileLayout.matches?'#mobile-resource-filters':'#desktop-resource-filters').append($('.library-badges'));
    }
    placeResourceFilters();
    function revealBenchmarkEntry() {
      if(location.hash!=='#benchmark-entry')return;
      $('.library-options').open=true;
      requestAnimationFrame(()=>$('#benchmark-entry').scrollIntoView({behavior:'instant',block:'start'}));
    }
    mobileLayout.addEventListener('change',()=>{
      $('.library-options').open=!mobileLayout.matches;
      placeResourceFilters();
      revealBenchmarkEntry();
    });
    window.addEventListener('hashchange',revealBenchmarkEntry);
    $('#checked-date').textContent=`Checked ${curated_at}`;
    $('#research-total').textContent=papers.length;
    $('#collection-filters').innerHTML=taxonomy.collection_sections.map(s=>`<section class="category-group" aria-labelledby="collection-heading-${esc(s.id)}"><h4 class="category-track" id="collection-heading-${esc(s.id)}">${esc(s.name)}</h4><button class="category-button category-parent" data-collection="${esc(s.id)}" aria-pressed="false"><span>All ${s.id==='benchmarks'?'benchmarks':'infrastructure'}</span><span>${papers.filter(p=>inCollection(p,s.id)).length}</span></button>${taxonomy.collections.filter(c=>c.section===s.id).map(c=>`<button class="category-button category-child" data-collection="${esc(c.id)}" aria-pressed="false"><span>${esc(c.name)}</span><span>${papers.filter(p=>inCollection(p,c.id)).length}</span></button>`).join('')}</section>`).join('');
    $('#categories').innerHTML=taxonomy.tracks.map(t=>`<section class="category-group" aria-labelledby="track-heading-${esc(t.id)}"><h4 class="category-track" id="track-heading-${esc(t.id)}">${esc(t.subtitle)}</h4><button class="category-button category-parent track-filter" data-track="${esc(t.id)}" aria-pressed="false"><span>All ${esc(t.id==='adjacent'?t.name.toLowerCase():t.name)}</span><span>${papers.filter(p=>p.track===t.id).length}</span></button>${taxonomy.categories.filter(c=>c.track===t.id).map(c=>`<button class="category-button category-child" data-category="${esc(c.id)}" aria-pressed="false"><span>${esc(c.name)}</span><span>${papers.filter(p=>p.category===c.id||p.cross_categories.includes(c.id)).length}</span></button>`).join('')}</section>`).join('');
    const months=[...new Set(papers.filter(p=>p.published).map(p=>p.published.slice(0,7)))].sort().reverse();
    $('#month').innerHTML='<option value="all">All dates</option>'+months.map(m=>`<option value="${esc(m)}">${esc(m)}</option>`).join('')+'<option value="unknown">Date unconfirmed</option>';
    $('#dimension-filters').innerHTML=taxonomy.dimensions.map(d=>`<label class="facet-label">${esc(d.name)}<select id="${esc(d.id)}"><option value="all">Any ${esc(d.name.toLowerCase())}</option>${Object.entries(d.values).filter(([value])=>papers.some(p=>p.dimensions[d.id].includes(value))).map(([value,label])=>`<option value="${esc(value)}">${esc(label)}</option>`).join('')}</select></label>`).join('');
    $('#search').addEventListener('input',e=>update({q:e.target.value}));
    ['sort','scope','month',...taxonomy.dimensions.map(d=>d.id)].forEach(id=>$('#'+id).addEventListener('change',e=>update({[id]:e.target.value})));
    $('#clear').onclick=()=>update({},true);
    $('#compare-open').onclick=compare;
    $('#compare-clear').onclick=()=>{selected.clear();render();};
    document.addEventListener('click',e=>{
      const b=e.target.closest('button');if(!b)return;
      if(b.hasAttribute('data-category'))update({category:b.dataset.category,track:'all',path:'all'});
      if(b.hasAttribute('data-collection')){const c=collection(b.dataset.collection);update({collection:b.dataset.collection,view:c.id==='benchmarks'||c.section==='benchmarks'?'benchmarks':'list'},true);$('#library').scrollIntoView();}
      if(b.hasAttribute('data-track'))update({track:b.dataset.track,category:'all',path:'all'});
      if(b.hasAttribute('data-view'))update({view:b.dataset.view});
      if(b.hasAttribute('data-tag')){update({tag:b.dataset.tag});$('#library').scrollIntoView();}
      if(b.hasAttribute('data-detail'))detail(b.dataset.detail);
      if(b.hasAttribute('data-remove'))update({[b.dataset.remove]:defaults[b.dataset.remove]});
      if(b.hasAttribute('data-reset'))update({},true);
      if(b.hasAttribute('data-compare')){const id=b.dataset.compare;if(selected.has(id))selected.delete(id);else if(selected.size<4)selected.add(id);else toast('Compare up to four records at a time.');render();}
      if(b.classList.contains('close-dialog'))b.closest('dialog').close();
    });
    document.querySelectorAll('dialog').forEach(d=>d.addEventListener('click',e=>{if(e.target===d){const r=d.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)d.close();}}));
    $('#detail-dialog').addEventListener('close',()=>{
      const url=new URL(location.href);
      if(!url.searchParams.has('paper'))return;
      url.searchParams.delete('paper');
      history.replaceState(history.state,'',url.href);
    });
    document.addEventListener('keydown',e=>{if(e.key==='/'&&!['INPUT','TEXTAREA','SELECT'].includes(document.activeElement.tagName)&&!document.querySelector('dialog[open]')){e.preventDefault();$('#search').focus();}});
    window.addEventListener('popstate',()=>{loadState();syncControls();render();});
    loadState();syncControls();render();
    revealBenchmarkEntry();
    // 首页的近期论文使用稳定 ID 打开详情，不改变原有筛选参数。
    const paperId=new URLSearchParams(location.search).get('paper');
    if(paperId)detail(paperId);
  }
  init();
})();
