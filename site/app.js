/* Simple paper list with a single primary category and multi-select auxiliary tags. */
(() => {
  'use strict';
  const {papers,taxonomy,curated_at,repository}=window.CWM_CATALOG;
  const engine=window.CWM_SEARCH;
  const $=selector=>document.querySelector(selector);
  const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const areaById=new Map(taxonomy.research_areas.map(a=>[a.id,a]));
  const directionById=new Map(taxonomy.research_areas.flatMap(a=>a.directions.map(d=>[d.id,{...d,area:a.id}])));
  const tagById=new Map(engine.tagOptions(taxonomy).map(t=>[t.id,t]));
  const badges=['all','classic','available','not_found'];
  const monthFor=p=>p.published?p.published.slice(0,7):'undated';
  const months=[...new Set(papers.map(monthFor))].sort((a,b)=>a==='undated'?1:b==='undated'?-1:b.localeCompare(a));
  const defaults={q:'',badge:'all',area:'all',direction:'all',tags:[],month:'all'};
  let state={...defaults};

  function loadState(){
    const params=new URLSearchParams(location.search);
    const badge=params.get('badge')||params.get('tag')||'all';
    const month=params.get('month')||'all';
    state={q:params.get('q')||'',badge:badges.includes(badge)?badge:'all',month:months.includes(month)?month:'all',...engine.readFilters(params,taxonomy)};
  }
  function writeState(replace){
    const params=engine.writeFilters(new URLSearchParams(),state);
    if(state.q)params.set('q',state.q);
    if(state.badge!=='all')params.set('badge',state.badge);
    if(state.month!=='all')params.set('month',state.month);
    const query=params.toString();
    const target=location.pathname+(query?'?'+query:'')+location.hash;
    if(target!==location.pathname+location.search+location.hash){
      try{history[replace?'replaceState':'pushState'](null,'',target);}catch{/* Filtering also works when opened as a local file. */}
    }
  }
  function update(patch,replace=false){state={...state,...patch};writeState(replace);render();}
  function matches(ignoreMonth=false){
    const words=state.q.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
    return papers.filter(p=>{
      const haystack=[p.title,p.short_title,...p.authors].join(' ').toLocaleLowerCase();
      return words.every(word=>haystack.includes(word))&&engine.matchesClassification(p.classification,state)&&
        (state.badge==='all'||(state.badge==='classic'?p.classic:p.resource_status.status===state.badge))&&
        (ignoreMonth||state.month==='all'||monthFor(p)===state.month);
    }).sort((a,b)=>{
      if(!a.published&&!b.published)return a.title.localeCompare(b.title);
      if(!a.published)return 1;if(!b.published)return -1;
      return b.published.localeCompare(a.published)||a.title.localeCompare(b.title);
    });
  }
  function renderMonths(){
    const available=matches(true),counts=new Map();
    available.forEach(p=>counts.set(monthFor(p),(counts.get(monthFor(p))||0)+1));
    $('#month-options').innerHTML=['all',...months].map(month=>{
      const label=month==='all'?'All':month==='undated'?'Date TBC':month;
      const count=month==='all'?available.length:counts.get(month)||0,selected=state.month===month;
      return `<button type="button" data-month="${month}" aria-pressed="${selected}" aria-label="${esc(label)}, ${count} papers"${!count&&!selected?' disabled':''}><span>${label}</span><span class="month-count" aria-hidden="true">${count}</span></button>`;
    }).join('');
  }
  function tagButton(id){
    const tag=tagById.get(id);
    return `<button data-aux-tag="${id}" aria-pressed="${state.tags.includes(id)}" title="${esc(tag.dimensionName)}">${esc(tag.name)}</button>`;
  }
  function card(p){
    const c=p.classification,area=areaById.get(c.area),direction=directionById.get(c.direction);
    const primary=p.resources.find(r=>r.kind==='paper')?.url||p.verification.source;
    const resources=p.resources.filter(r=>r.kind!=='paper'),labels={code:'Code',project:'Project',data:'Data',weights:'Weights'};
    const stamp=p.published?p.published.slice(0,7):'Date TBC';
    const badge=p.resource_status.status==='available'?'<span class="badge badge-open">✅ Public resources</span>':'<span class="badge badge-closed">No resources found</span>';
    const tags=engine.tagIds(c).sort((a,b)=>Number(state.tags.includes(b))-Number(state.tags.includes(a)));
    return `<article class="paper-card${p.classic?' starred':''}" data-paper="${esc(p.id)}" data-research-area="${c.area}">
      <div class="paper-heading"><div class="paper-main"><div class="paper-badges">${p.classic?'<span class="badge badge-star" title="'+esc(p.classic_note)+'">🌟 Classic</span>':''}${badge}</div><h2><a href="${esc(primary)}" target="_blank" rel="noopener noreferrer">${esc(p.title)}</a></h2></div><time class="paper-date"${p.published?' datetime="'+esc(p.published)+'"':''}>${esc(stamp)}</time></div>
      <div class="paper-primary"><button data-area="${area.id}" title="Primary research area">${esc(area.name)}</button>${direction?`<button class="paper-direction" data-direction="${direction.id}">${esc(direction.name)}</button>`:''}</div>
      <p class="paper-description">${esc(p.summary)}</p>
      <div class="paper-tags">${tags.slice(0,4).map(tagButton).join('')}${tags.length>4?`<details class="more-tags"><summary>+${tags.length-4} tags</summary><div>${tags.slice(4).map(tagButton).join('')}</div></details>`:''}</div>
      ${resources.length?'<div class="paper-links">'+resources.map(r=>`<a href="${esc(r.url)}" target="_blank" rel="noopener noreferrer">${esc(labels[r.kind]||r.kind)} ↗</a>`).join('')+'</div>':''}
    </article>`;
  }
  function renderDirections(){
    const groups=state.area==='all'?taxonomy.research_areas:[areaById.get(state.area)];
    const options='<option value="all">All directions</option>'+groups.map(a=>`<optgroup label="${esc(a.name)}">${a.directions.map(d=>`<option value="${d.id}">${esc(d.name)}</option>`).join('')}</optgroup>`).join('');
    if($('#direction').innerHTML!==options)$('#direction').innerHTML=options;
    $('#direction').value=state.direction;
  }
  function render(){
    if($('#search').value!==state.q)$('#search').value=state.q;
    document.querySelectorAll('[data-badge]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.badge===state.badge)));
    document.querySelectorAll('input[name="research-area"]').forEach(input=>{input.checked=input.value===state.area;});
    document.querySelectorAll('#auxiliary-options input').forEach(input=>{input.checked=state.tags.includes(input.value);});
    renderDirections();renderMonths();
    $('#tag-selection-count').textContent=state.tags.length?`${state.tags.length} selected`:'Optional · select one or more';
    $('#selected-tags').innerHTML=state.tags.map(id=>`<button data-aux-tag="${id}" aria-label="Remove ${esc(tagById.get(id).name)}">${esc(tagById.get(id).name)} <span aria-hidden="true">×</span></button>`).join('');
    $('#clear-tags').disabled=!state.tags.length;
    $('#clear').disabled=!state.q&&state.badge==='all'&&state.area==='all'&&!state.tags.length&&state.month==='all';
    const found=matches();
    $('#result-count').textContent=`Showing ${found.length} of ${papers.length} papers & projects`;
    $('#paper-list').innerHTML=found.length?found.map(card).join(''):'<div class="empty-state"><p>No papers match these filters.</p><button data-reset>Clear filters</button></div>';
  }
  $('#area-options').innerHTML=[{id:'all',name:'All'},...taxonomy.research_areas].map(a=>`<label class="topic-option"><input type="radio" name="research-area" value="${a.id}"><span>${esc(a.name)}</span></label>`).join('');
  $('#auxiliary-options').innerHTML=taxonomy.tag_dimensions.map(d=>`<fieldset class="tag-dimension"><legend>${esc(d.name)}</legend>${Object.entries(d.values).map(([id,name])=>`<label class="topic-option"><input type="checkbox" value="${id}"><span>${esc(name)}</span></label>`).join('')}</fieldset>`).join('');
  $('#checked-date').textContent=`Sources checked ${curated_at}`;
  if(repository){$('#source-link').href=`https://github.com/${repository}`;$('#source-link').textContent='GitHub ↗';}
  $('#search').addEventListener('input',e=>update({q:e.target.value},true));
  $('#area-options').addEventListener('change',e=>{if(e.target.matches('input'))update({area:e.target.value,direction:'all'});});
  $('#direction').addEventListener('change',e=>{const direction=e.target.value;update({direction,...(direction!=='all'?{area:directionById.get(direction).area}:{})});});
  $('#auxiliary-options').addEventListener('change',e=>{if(e.target.matches('input'))update({tags:engine.toggleTag(state.tags,e.target.value)});});
  $('#clear-tags').onclick=()=>update({tags:[]});
  $('#clear').onclick=()=>update({...defaults});
  document.addEventListener('click',e=>{
    const b=e.target.closest('button');if(!b)return;
    if(b.hasAttribute('data-badge'))update({badge:b.dataset.badge});
    if(b.hasAttribute('data-month'))update({month:b.dataset.month});
    if(b.hasAttribute('data-area'))update({area:b.dataset.area,direction:'all'});
    if(b.hasAttribute('data-direction'))update({area:directionById.get(b.dataset.direction).area,direction:b.dataset.direction});
    if(b.hasAttribute('data-aux-tag'))update({tags:engine.toggleTag(state.tags,b.dataset.auxTag)});
    if(b.hasAttribute('data-reset'))update({...defaults});
  });
  document.addEventListener('keydown',e=>{if(e.key==='/'&&!['INPUT','TEXTAREA','SELECT'].includes(document.activeElement.tagName)){e.preventDefault();$('#search').focus();}});
  window.addEventListener('popstate',()=>{loadState();render();});
  loadState();render();
})();
