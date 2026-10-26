/* 数据来自统一目录；所有动态文本在插入 HTML 前转义。 */
(() => {
  'use strict';
  const {papers, taxonomy, curated_at, repository, news} = window.CWM_CATALOG;
  const $ = s => document.querySelector(s);
  const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const byId = new Map(papers.map(p => [p.id, p]));
  const cat = id => taxonomy.categories.find(c => c.id === id);
  const dim = id => taxonomy.dimensions.find(d => d.id === id);
  const collection = id => taxonomy.collections.find(c=>c.id===id) || taxonomy.collection_sections.find(c=>c.id===id);
  const inCollection = (p,id) => id==='all' || p.collections.includes(id) || p.collections.some(c=>collection(c).section===id);
  const labels = (p, id) => p.dimensions[id].map(v => dim(id).values[v]);
  const selected = new Set();
  const defaults = {q:'', track:'all', category:'all', collection:'all', scope:'all', month:'all', tag:'all', sort:'newest', view:'list', path:'all'};
  taxonomy.dimensions.forEach(d => { defaults[d.id] = 'all'; });
  let state = {...defaults};
  let toastTimer;

  function loadState() {
    const params = new URLSearchParams(location.search);
    state = {...defaults};
    for (const key of Object.keys(defaults)) if (params.has(key)) state[key] = params.get(key);
    const options = {track:['all',...taxonomy.tracks.map(t=>t.id)],category:['all',...taxonomy.categories.map(c=>c.id)],collection:['all',...taxonomy.collections.map(c=>c.id),...taxonomy.collection_sections.map(c=>c.id)],scope:['all',...Object.keys(taxonomy.scopes)],month:['all','unknown',...new Set(papers.filter(p=>p.published).map(p=>p.published.slice(0,7)))],tag:['all','classic','available','not_found'],sort:['newest','oldest','title'],view:['list','categories','benchmarks','matrix','timeline'],path:['all',...taxonomy.reading_paths.map(p=>p.id)]};
    taxonomy.dimensions.forEach(d => {options[d.id]=['all',...Object.keys(d.values)];});
    for (const [key, values] of Object.entries(options)) if (!values.includes(state[key])) state[key]=defaults[key];
  }
  function writeState() {
    const params = new URLSearchParams();
    for (const [key, val] of Object.entries(state)) if (val !== defaults[key]) params.set(key, val);
    history.replaceState(null,'',location.pathname+(params.size?'?'+params:'')+location.hash);
  }
  function update(patch, reset=false) {
    state = {...(reset?defaults:state),...patch};
    writeState(); syncControls(); render();
  }
  function syncControls() {
    $('#search').value=state.q;
    ['sort','scope','month',...taxonomy.dimensions.map(d=>d.id)].forEach(id=>{const el=$('#'+id);if(el)el.value=state[id];});
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
    const terms = state.q.toLocaleLowerCase().trim().split(/\s+/).filter(Boolean);
    const path = taxonomy.reading_paths.find(p=>p.id===state.path);
    const result = papers.filter(p=>{
      const haystack = [p.title,p.short_title,...p.authors,p.summary,...p.collections.map(c=>collection(c).name),...p.benchmarks.flatMap(b=>[b.name,b.input,b.artifact,b.checks]),...p.cross_categories.map(c=>cat(c).name),cat(p.category).name,...taxonomy.dimensions.flatMap(d=>labels(p,d.id))].join(' ').toLocaleLowerCase();
      return terms.every(t=>haystack.includes(t)) &&
        (state.track==='all'||p.track===state.track) &&
        (state.category==='all'||p.category===state.category||p.cross_categories.includes(state.category)) &&
        inCollection(p,state.collection) &&
        (state.view!=='benchmarks'||p.benchmarks.length>0) &&
        (state.scope==='all'||p.scope===state.scope) &&
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
  function resourceBadge(p) {return `<span class="resource-badge ${p.resource_status.status}" title="${esc(p.resource_status.basis)}">${p.resource_status.status==='available'?'✅ Public resources':'❌️ Resources not found'}</span>${p.classic?`<span class="classic-badge" title="${esc(p.classic_note)}">🌟 Representative</span>`:''}`;}
  function resourceLabel(r) {return {paper:'Paper',code:'Code',project:'Project',data:'Data',weights:'Weights'}[r.kind]||r.kind;}
  function links(p, all=false) {
    const list = all?p.resources:p.resources.slice(0,2);
    return list.map(r=>`<a href="${esc(r.url)}" target="_blank" rel="noopener noreferrer">${esc(resourceLabel(r))} ↗</a>`).join('');
  }
  function compareButton(p) {return `<button class="compare-toggle" data-compare="${esc(p.id)}" aria-pressed="${selected.has(p.id)}" aria-label="${selected.has(p.id)?'Remove':'Add'} ${esc(p.short_title)} ${selected.has(p.id)?'from':'to'} comparison">${selected.has(p.id)?'✓ Selected':'+ Compare'}</button>`;}
  function card(p) {
    return `<article class="paper-card${p.classic?' is-classic':''}" data-paper="${esc(p.id)}"><div class="paper-meta"><time${p.published?` datetime="${esc(p.published)}"`:''}>${esc(date(p))}</time>${badge(p)}<span>${esc(cat(p.category).name)}</span>${resourceBadge(p)}</div><h3><button data-detail="${esc(p.id)}">${esc(p.title)}</button></h3><p class="paper-summary">${esc(p.summary)}</p>${p.benchmarks.length?`<p class="benchmark-label">BENCHMARK · ${p.benchmarks.map(b=>esc(b.name)).join(' · ')}</p>`:''}<div class="paper-footer"><div class="paper-tags">${[...labels(p,'code_role').slice(0,2),...labels(p,'interaction').slice(0,1)].map(t=>`<span class="tag">${esc(t)}</span>`).join('')}</div><div class="paper-actions">${links(p)}${compareButton(p)}</div></div></article>`;
  }
  function categoryList(items) {
    return taxonomy.categories.map(c=>{
      const group=items.filter(p=>p.category===c.id||p.cross_categories.includes(c.id)).sort((a,b)=>Number(b.classic)-Number(a.classic)||(b.published||'').localeCompare(a.published||'')||b.id.localeCompare(a.id));
      if(!group.length)return '';
      return `<section class="category-block"><h3>${esc(c.name)}</h3><p class="muted">${esc(c.question)}</p>${group.map(p=>`<p class="category-entry${p.classic?' is-classic':''}" data-category-paper="${esc(p.id)}"><span class="entry-month">[${p.published?p.published.slice(0,7):'Date TBC'}]</span> ${p.resource_status.status==='available'?'✅':'❌️'}${p.classic?'🌟 ':''}${p.classic?`<span class="entry-note">(${esc(p.classic_note)})</span> `:''}<button data-detail="${esc(p.id)}">${esc(p.title)}</button> <span class="entry-links">${links(p)}</span></p>`).join('')}</section>`;
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
    $('#result-count').innerHTML=`<b>${items.length}</b> of ${papers.length} research records`;
    const active = Object.entries(state).filter(([k,v])=>v!==defaults[k]&&!['sort','view'].includes(k));
    $('#active-filters').innerHTML=active.map(([k,v])=>{
      let title=v;
      if(k==='category')title=cat(v).name;
      if(k==='collection')title=collection(v).name;
      if(k==='track')title=taxonomy.tracks.find(t=>t.id===v).name;
      if(k==='scope')title=taxonomy.scopes[v];
      if(k==='tag')title={classic:'🌟 Representative',available:'✅ Public resources',not_found:'❌️ Resources not found'}[v];
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
    try {
      if(navigator.clipboard && window.isSecureContext) await navigator.clipboard.writeText(text);
      else {const el=document.createElement('textarea');el.value=text;document.body.append(el);el.select();if(!document.execCommand('copy'))throw new Error('copy');el.remove();}
      toast('BibTeX copied.');
    } catch {toast('Select and copy the citation below.');}
  }
  function toast(message) {clearTimeout(toastTimer);$('#toast').textContent=message;$('#toast').hidden=false;toastTimer=setTimeout(()=>{$('#toast').hidden=true;},3000);}
  function compare() {
    const items=[...selected].map(id=>byId.get(id));
    const rows=[['Research direction',p=>taxonomy.tracks.find(t=>t.id===p.track).name],['Primary question',p=>cat(p.category).question],...taxonomy.dimensions.map(d=>[d.name,p=>labels(p,d.id).join(' · ')]),...['name','input','artifact','checks','caveat'].map(k=>[{name:'Benchmark',input:'Benchmark input',artifact:'Submitted artifact',checks:'Evaluation evidence',caveat:'Evaluation boundary'}[k],p=>p.benchmarks.map(b=>b[k]).join(' · ')||'No named benchmark protocol indexed.']),['Reported runtime context',p=>p.performance_note||'No runtime comparison recorded.'],['Editorial insight',p=>p.summary]];
    $('#compare-content').innerHTML=`<p class="muted">Evaluation targets describe what the source measures. They are not pass/fail certifications. Timing claims require matching hardware, resolution and latency definitions.</p><div class="table-scroll" tabindex="0"><table><thead><tr><th>Dimension</th>${items.map(p=>`<th>${esc(p.short_title)}</th>`).join('')}</tr></thead><tbody>${rows.map(([name,fn])=>`<tr><th>${esc(name)}</th>${items.map(p=>`<td>${esc(fn(p))}</td>`).join('')}</tr>`).join('')}<tr><th>Source</th>${items.map(p=>`<td><div class="link-group">${links(p)}</div></td>`).join('')}</tr></tbody></table></div>`;
    $('#compare-dialog').showModal();
  }
  function init() {
    $('#stats').innerHTML=`<div class="stat"><strong>${papers.length}</strong><span>curated records</span></div><div class="stat"><strong>02</strong><span>core directions</span></div><div class="stat"><strong>${taxonomy.dimensions.length.toString().padStart(2,'0')}</strong><span>comparison dimensions</span></div>`;
    $('#checked-date').textContent=`Checked ${curated_at}`;
    $('#benchmark-total').textContent=papers.reduce((n,p)=>n+p.benchmarks.length,0);
    $('#research-total').textContent=papers.length;
    $('#collection-filters').innerHTML=taxonomy.collection_sections.map(s=>`<section class="category-group" aria-labelledby="collection-heading-${esc(s.id)}"><h4 class="category-track" id="collection-heading-${esc(s.id)}">${esc(s.name)}</h4><button class="category-button category-parent" data-collection="${esc(s.id)}" aria-pressed="false"><span>All ${s.id==='benchmarks'?'benchmarks':'infrastructure'}</span><span>${papers.filter(p=>inCollection(p,s.id)).length}</span></button>${taxonomy.collections.filter(c=>c.section===s.id).map(c=>`<button class="category-button category-child" data-collection="${esc(c.id)}" aria-pressed="false"><span>${esc(c.name)}</span><span>${papers.filter(p=>inCollection(p,c.id)).length}</span></button>`).join('')}</section>`).join('');
    $('#news-list').innerHTML=news.map(n=>`<article class="news-item"><p><span>${esc(n.icon)} [${esc(n.date)}]</span> <strong>${esc(n.title)}</strong></p><p>${esc(n.body)}</p></article>`).join('');
    const latest=[...papers].filter(p=>p.published).sort((a,b)=>b.published.localeCompare(a.published)||b.id.localeCompare(a.id)).slice(0,20);
    $('#recent-updates').innerHTML=latest.map(p=>`<p><time datetime="${esc(p.published)}">[${esc(p.published)}]</time> ${p.resource_status.status==='available'?'✅':'❌️'}<button data-detail="${esc(p.id)}">${esc(p.title)}</button></p>`).join('');
    if(repository){$('#source-link').href=`https://github.com/${repository}`;$('#source-link').textContent='GitHub ↗';}
    $('#categories').innerHTML=taxonomy.tracks.map(t=>`<section class="category-group" aria-labelledby="track-heading-${esc(t.id)}"><h4 class="category-track" id="track-heading-${esc(t.id)}">${esc(t.subtitle)}</h4><button class="category-button category-parent track-filter" data-track="${esc(t.id)}" aria-pressed="false"><span>All ${esc(t.id==='adjacent'?t.name.toLowerCase():t.name)}</span><span>${papers.filter(p=>p.track===t.id).length}</span></button>${taxonomy.categories.filter(c=>c.track===t.id).map(c=>`<button class="category-button category-child" data-category="${esc(c.id)}" aria-pressed="false"><span>${esc(c.name)}</span><span>${papers.filter(p=>p.category===c.id||p.cross_categories.includes(c.id)).length}</span></button>`).join('')}</section>`).join('');
    const months=[...new Set(papers.filter(p=>p.published).map(p=>p.published.slice(0,7)))].sort().reverse();
    $('#month').innerHTML='<option value="all">All dates</option>'+months.map(m=>`<option value="${esc(m)}">${esc(m)}</option>`).join('')+'<option value="unknown">Date unconfirmed</option>';
    $('#dimension-filters').innerHTML=taxonomy.dimensions.map(d=>`<label class="facet-label">${esc(d.name)}<select id="${esc(d.id)}"><option value="all">Any ${esc(d.name.toLowerCase())}</option>${Object.entries(d.values).filter(([value])=>papers.some(p=>p.dimensions[d.id].includes(value))).map(([value,label])=>`<option value="${esc(value)}">${esc(label)}</option>`).join('')}</select></label>`).join('');
    $('#reading-paths').innerHTML=taxonomy.reading_paths.map((p,i)=>`<button class="reading-card" data-path="${esc(p.id)}"><span class="path-index">0${i+1} / READING PATH</span><h3>${esc(p.title)}</h3><p>${esc(p.description)}</p><span class="path-count">${p.papers.length} WORKS <span aria-hidden="true">↗</span></span></button>`).join('');
    $('#search').addEventListener('input',e=>update({q:e.target.value}));
    ['sort','scope','month',...taxonomy.dimensions.map(d=>d.id)].forEach(id=>$('#'+id).addEventListener('change',e=>update({[id]:e.target.value})));
    $('#clear').onclick=()=>update({},true);
    $('#mobile-filters').onclick=()=>{const open=$('#research-filters').classList.toggle('is-open');$('#mobile-filters').setAttribute('aria-expanded',String(open));$('#mobile-filters span').textContent=open?'−':'＋';};
    $('#compare-open').onclick=compare;
    $('#compare-clear').onclick=()=>{selected.clear();render();};
    document.addEventListener('click',e=>{
      const b=e.target.closest('button');if(!b)return;
      if(b.hasAttribute('data-category'))update({category:b.dataset.category,track:'all',path:'all'});
      if(b.hasAttribute('data-collection')){const c=collection(b.dataset.collection);update({collection:b.dataset.collection,view:c.id==='benchmarks'||c.section==='benchmarks'?'benchmarks':'list'},true);$('#library').scrollIntoView();}
      if(b.hasAttribute('data-track')){update({track:b.dataset.track,category:'all',path:'all'});if(b.classList.contains('track-card'))$('#library').scrollIntoView();}
      if(b.hasAttribute('data-view'))update({view:b.dataset.view});
      if(b.hasAttribute('data-tag')){update({tag:b.dataset.tag});$('#library').scrollIntoView();}
      if(b.hasAttribute('data-detail'))detail(b.dataset.detail);
      if(b.hasAttribute('data-path')){update({path:b.dataset.path},true);$('#library').scrollIntoView();}
      if(b.hasAttribute('data-remove'))update({[b.dataset.remove]:defaults[b.dataset.remove]});
      if(b.hasAttribute('data-reset'))update({},true);
      if(b.hasAttribute('data-compare')){const id=b.dataset.compare;if(selected.has(id))selected.delete(id);else if(selected.size<4)selected.add(id);else toast('Compare up to four records at a time.');render();}
      if(b.classList.contains('close-dialog'))b.closest('dialog').close();
    });
    document.querySelectorAll('dialog').forEach(d=>d.addEventListener('click',e=>{if(e.target===d){const r=d.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)d.close();}}));
    document.addEventListener('keydown',e=>{if(e.key==='/'&&!['INPUT','TEXTAREA','SELECT'].includes(document.activeElement.tagName)&&!document.querySelector('dialog[open]')){e.preventDefault();$('#search').focus();}});
    window.addEventListener('popstate',()=>{loadState();syncControls();render();});
    loadState();syncControls();render();
  }
  init();
})();
