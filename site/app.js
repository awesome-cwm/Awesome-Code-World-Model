/* One flat vocabulary: unique README placement and overlapping website topics. */
(()=>{
  'use strict';
  const {papers,taxonomy,curated_at,repository}=window.CWM_CATALOG;
  const engine=window.CWM_SEARCH;
  const $=selector=>document.querySelector(selector);
  const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const topicById=new Map(taxonomy.topics.map(t=>[t.id,t]));
  const badges=['all','available','not_found'];
  const monthFor=p=>p.published?p.published.slice(0,7):'undated';
  const months=[...new Set(papers.map(monthFor))].sort((a,b)=>a==='undated'?1:b==='undated'?-1:b.localeCompare(a));
  const defaults={q:'',badge:'all',topics:[],month:'all'};
  let state={...defaults};

  function loadState(){
    const params=new URLSearchParams(location.search);
    const badge=params.get('badge')||params.get('tag')||'all';
    const month=params.get('month')||'all';
    state={q:params.get('q')||'',badge:badges.includes(badge)?badge:'all',month:months.includes(month)?month:'all',topics:engine.readTopics(params,taxonomy.topics)};
  }
  function writeState(replace){
    const params=engine.writeTopics(new URLSearchParams(),state.topics);
    if(state.q)params.set('q',state.q);
    if(state.badge!=='all')params.set('badge',state.badge);
    if(state.month!=='all')params.set('month',state.month);
    const query=params.toString(),target=location.pathname+(query?'?'+query:'')+location.hash;
    if(target!==location.pathname+location.search+location.hash){
      try{history[replace?'replaceState':'pushState'](null,'',target);}catch{/* Local-file filtering also works without URL updates. */}
    }
  }
  function update(patch,replace=false){state={...state,...patch};writeState(replace);render();}
  function matches(ignoreMonth=false){
    const words=state.q.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
    return papers.filter(p=>{
      const haystack=[p.title,p.short_title,...p.authors].join(' ').toLocaleLowerCase();
      return words.every(word=>haystack.includes(word))&&engine.matchesTopics(p.classification.topics,state.topics)&&
        (state.badge==='all'||p.resource_status.status===state.badge)&&
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
  function topicButton(id){
    return `<button type="button" data-topic="${id}" aria-pressed="${state.topics.includes(id)}">${esc(topicById.get(id).name)}</button>`;
  }
  function card(p){
    const primary=p.resources.find(r=>r.kind==='paper')?.url||p.verification.source;
    const resources=p.resources.filter(r=>r.kind!=='paper'),labels={code:'Code',project:'Project',data:'Data',weights:'Weights'};
    const stamp=p.published?p.published.slice(0,7):'Date TBC';
    const badge=p.resource_status.status==='available'?'<span class="badge badge-open">✅ Open Source</span>':'<span class="badge badge-closed">❌️ Not Open Source</span>';
    return `<article class="paper-card" data-paper="${esc(p.id)}">
      <div class="paper-heading"><div class="paper-main"><div class="paper-badges">${badge}</div><h2><a href="${esc(primary)}" target="_blank" rel="noopener noreferrer">${esc(p.title)}</a></h2></div><time class="paper-date"${p.published?' datetime="'+esc(p.published)+'"':''}>${esc(stamp)}</time></div>
      <div class="paper-topics">${p.classification.topics.map(topicButton).join('')}</div>
      <p class="paper-description">${esc(p.summary)}</p>
      ${resources.length?'<div class="paper-links">'+resources.map(r=>`<a href="${esc(r.url)}" target="_blank" rel="noopener noreferrer">${esc(labels[r.kind]||r.kind)} ↗</a>`).join('')+'</div>':''}
    </article>`;
  }
  function render(){
    if($('#search').value!==state.q)$('#search').value=state.q;
    document.querySelectorAll('[data-badge]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.badge===state.badge)));
    document.querySelectorAll('#topic-options input').forEach(input=>{input.checked=state.topics.includes(input.value);});
    $('#all-topics').setAttribute('aria-pressed',String(!state.topics.length));
    $('#selected-topics').innerHTML=state.topics.map(id=>`<button type="button" data-topic="${id}" aria-label="Remove ${esc(topicById.get(id).name)}">${esc(topicById.get(id).name)} <span aria-hidden="true">×</span></button>`).join('');
    $('#clear').disabled=!state.q&&state.badge==='all'&&!state.topics.length&&state.month==='all';
    renderMonths();
    const found=matches();
    $('#result-count').textContent=`Showing ${found.length} of ${papers.length} papers & projects`;
    $('#paper-list').innerHTML=found.length?found.map(card).join(''):'<div class="empty-state"><p>No papers match these filters.</p><button type="button" data-reset>Clear filters</button></div>';
  }
  $('#topic-options').innerHTML=taxonomy.topics.map(t=>{
    const count=papers.filter(p=>p.classification.topics.includes(t.id)).length;
    return `<label class="topic-option" title="${esc(t.description)}"><input type="checkbox" value="${t.id}" aria-label="${esc(t.name)}, ${count} papers"><span>${esc(t.name)}</span><span class="topic-count" aria-hidden="true">${count}</span></label>`;
  }).join('');
  const reviewed=papers.map(p=>p.classification.checked).sort().at(-1)||curated_at;
  $('#checked-date').textContent=`Topics reviewed ${reviewed}`;
  if(repository){$('#source-link').href=`https://github.com/${repository}`;$('#source-link').textContent='GitHub ↗';}
  $('#search').addEventListener('input',e=>update({q:e.target.value},true));
  $('#topic-options').addEventListener('change',e=>{if(e.target.matches('input'))update({topics:engine.toggleTopic(state.topics,e.target.value)});});
  $('#all-topics').onclick=()=>update({topics:[]});
  $('#clear').onclick=()=>update({...defaults});
  document.addEventListener('click',e=>{
    const b=e.target.closest('button');if(!b)return;
    if(b.hasAttribute('data-badge'))update({badge:b.dataset.badge});
    if(b.hasAttribute('data-month'))update({month:b.dataset.month});
    if(b.hasAttribute('data-topic'))update({topics:engine.toggleTopic(state.topics,b.dataset.topic)});
    if(b.hasAttribute('data-reset'))update({...defaults});
  });
  document.addEventListener('keydown',e=>{if(e.key==='/'&&!['INPUT','TEXTAREA','SELECT'].includes(document.activeElement.tagName)){e.preventDefault();$('#search').focus();}});
  window.addEventListener('popstate',()=>{loadState();render();});
  loadState();render();
})();
