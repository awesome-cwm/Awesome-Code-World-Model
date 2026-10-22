/* 简洁论文清单：标签只在选中与未选中之间切换，多选取交集。 */
(() => {
  'use strict';
  const {papers, taxonomy, curated_at, repository} = window.CWM_CATALOG;
  const engine = window.CWM_SEARCH;
  const topics = taxonomy.topics;
  const $ = selector => document.querySelector(selector);
  const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const topicById = new Map(topics.map(topic => [topic.id, topic]));
  const indexed = papers.map(paper => ({paper, topics:engine.topicsFor(paper,topics)}));
  const badges = ['all','classic','available','not_found'];
  const monthFor = paper => paper.published ? paper.published.slice(0,7) : 'undated';
  const months = [...new Set(papers.map(monthFor))].sort((a,b)=>a==='undated'?1:b==='undated'?-1:b.localeCompare(a));
  const defaults = {q:'',badge:'all',include:[],month:'all'};
  let state = {...defaults};

  function loadState() {
    const params = new URLSearchParams(location.search);
    const badge = params.get('badge') || params.get('tag') || 'all';
    const month = params.get('month') || 'all';
    state = {q:params.get('q') || '',badge:badges.includes(badge)?badge:'all',month:months.includes(month)?month:'all',...engine.readTopics(params,topics)};
  }
  function writeState(replace) {
    const params = engine.writeTopics(new URLSearchParams(),state);
    if(state.q)params.set('q',state.q);
    if(state.badge!=='all')params.set('badge',state.badge);
    if(state.month!=='all')params.set('month',state.month);
    const query=params.toString();
    const target=location.pathname+(query?'?'+query:'')+location.hash;
    if(target!==location.pathname+location.search+location.hash) {
      try {history[replace?'replaceState':'pushState'](null,'',target);} catch { /* 离线打开时也可筛选。 */ }
    }
  }
  function update(patch,replace=false) {
    state={...state,...patch};writeState(replace);render();
  }
  function matches(ignoreMonth=false) {
    const words=state.q.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
    return indexed.filter(({paper:p,topics:ids})=>{
      const haystack=[p.title,p.short_title,...p.authors].join(' ').toLocaleLowerCase();
      return words.every(word=>haystack.includes(word)) && engine.matchesTopics(ids,state) &&
        (state.badge==='all'||(state.badge==='classic'?p.classic:p.resource_status.status===state.badge)) &&
        (ignoreMonth||state.month==='all'||monthFor(p)===state.month);
    }).sort(({paper:a},{paper:b})=>{
      if(!a.published&&!b.published)return a.title.localeCompare(b.title);
      if(!a.published)return 1;if(!b.published)return -1;
      return b.published.localeCompare(a.published)||a.title.localeCompare(b.title);
    });
  }
  function renderMonths() {
    const available=matches(true);
    const counts=new Map();
    available.forEach(({paper})=>{const month=monthFor(paper);counts.set(month,(counts.get(month)||0)+1);});
    $('#month-options').innerHTML=['all',...months].map(month=>{
      const label=month==='all'?'All':month==='undated'?'Date TBC':month;
      const count=month==='all'?available.length:counts.get(month)||0;
      const selected=state.month===month;
      return `<button type="button" data-month="${month}" aria-pressed="${selected}" aria-label="${esc(label)}, ${count} papers"${!count&&!selected?' disabled':''}><span>${label}</span><span class="month-count" aria-hidden="true">${count}</span></button>`;
    }).join('');
  }
  function card({paper:p,topics:ids}) {
    const primary=p.resources.find(r=>r.kind==='paper')?.url || p.verification.source;
    const resources=p.resources.filter(r=>r.kind!=='paper');
    const labels={code:'Code',project:'Project',data:'Data',weights:'Weights'};
    const stamp=p.published?p.published.slice(0,7):'Date TBC';
    const badge=p.resource_status.status==='available'?'<span class="badge badge-open">✅ Public resources</span>':'<span class="badge badge-closed">No resources found</span>';
    return `<article class="paper-card${p.classic?' starred':''}" data-paper="${esc(p.id)}">
      <div class="paper-heading"><div class="paper-main"><div class="paper-badges">${p.classic?'<span class="badge badge-star" title="'+esc(p.classic_note)+'">🌟 Classic</span>':''}${badge}</div><h2><a href="${esc(primary)}" target="_blank" rel="noopener noreferrer">${esc(p.title)}</a></h2></div><time class="paper-date"${p.published?' datetime="'+esc(p.published)+'"':''}>${esc(stamp)}</time></div>
      <div class="paper-topics">${ids.map(id=>`<button data-topic="${esc(id)}" aria-pressed="${state.include.includes(id)}" title="${esc(topicById.get(id).zh)}">${esc(topicById.get(id).name)}</button>`).join('')}</div>
      <p class="paper-description">${esc(p.summary)}</p>
      ${resources.length?'<div class="paper-links">'+resources.map(r=>`<a href="${esc(r.url)}" target="_blank" rel="noopener noreferrer">${esc(labels[r.kind]||r.kind)} ↗</a>`).join('')+'</div>':''}
    </article>`;
  }
  function render() {
    if($('#search').value!==state.q)$('#search').value=state.q;
    document.querySelectorAll('[data-badge]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.badge===state.badge)));
    document.querySelectorAll('#topic-options input').forEach(input=>{input.checked=state.include.includes(input.value);});
    $('#all-topics').setAttribute('aria-pressed',String(state.include.length===0));
    $('#clear').disabled=!state.q&&state.badge==='all'&&!state.include.length&&state.month==='all';
    renderMonths();
    const found=matches();
    $('#result-count').textContent=`Showing ${found.length} of ${papers.length} papers & projects`;
    $('#paper-list').innerHTML=found.length?found.map(card).join(''):'<div class="empty-state"><p>No papers match these filters.</p><button data-reset>Clear filters</button></div>';
  }
  $('#topic-options').innerHTML=topics.map(t=>`<label class="topic-option" title="${esc(t.zh+' · '+t.description)}"><input type="checkbox" value="${esc(t.id)}"><span>${esc(t.name)}</span></label>`).join('');
  $('#checked-date').textContent=`Sources checked ${curated_at}`;
  if(repository){$('#source-link').href=`https://github.com/${repository}`;$('#source-link').textContent='GitHub ↗';}
  $('#search').addEventListener('input',event=>update({q:event.target.value},true));
  $('#topic-options').addEventListener('change',event=>{
    if(event.target.matches('input[type="checkbox"]'))update({include:engine.toggleTopic(state.include,event.target.value)});
  });
  $('#all-topics').onclick=()=>update({include:[]});
  $('#clear').onclick=()=>update({...defaults});
  document.addEventListener('click',event=>{
    const button=event.target.closest('button');if(!button)return;
    if(button.hasAttribute('data-badge'))update({badge:button.dataset.badge});
    if(button.hasAttribute('data-month'))update({month:button.dataset.month});
    if(button.hasAttribute('data-topic'))update({include:engine.toggleTopic(state.include,button.dataset.topic)});
    if(button.hasAttribute('data-reset'))update({...defaults});
  });
  document.addEventListener('keydown',event=>{
    if(event.key==='/'&&!['INPUT','TEXTAREA','SELECT'].includes(document.activeElement.tagName)){
      event.preventDefault();$('#search').focus();
    }
  });
  window.addEventListener('popstate',()=>{loadState();render();});
  loadState();render();
})();
