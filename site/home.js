/* 首页仅展示目录概况；所有浏览入口指向独立论文库。 */
(() => {
  'use strict';
  const {papers, taxonomy, curated_at, news} = window.CWM_CATALOG;
  const params = new URLSearchParams(location.search);
  const libraryKeys = new Set(['q','track','category','collection','scope','month','tag','sort','view','path','paper',...taxonomy.dimensions.map(d=>d.id)]);
  function routeLegacyLibrary() {
    if ([...params.keys()].some(key=>libraryKeys.has(key)) || ['#library','#benchmark-entry'].includes(location.hash)) {
      location.replace(new URL('papers.html'+location.search+location.hash, location.href).href);
      return true;
    }
    return false;
  }
  // 保留旧首页上的筛选分享链接，以及 README 中已有的目录锚点。
  if (routeLegacyLibrary()) return;
  window.addEventListener('hashchange', routeLegacyLibrary);
  const $ = s=>document.querySelector(s);
  const esc = value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  $('#stats').innerHTML=`<div class="stat"><strong>${papers.length}</strong><span>curated records</span></div><div class="stat"><strong>02</strong><span>core directions</span></div><div class="stat"><strong>${taxonomy.dimensions.length.toString().padStart(2,'0')}</strong><span>comparison dimensions</span></div>`;
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  if (!motion.matches) {
    const numbers = [...document.querySelectorAll('.stat strong')].map(el=>[el,el.textContent]);
    let start;
    function count(now) {
      start ??= now;
      const t = motion.matches ? 1 : Math.min((now-start)/850,1);
      numbers.forEach(([el,value])=>{el.textContent=String(Math.round(Number(value)*(1-(1-t)**3))).padStart(value.length,'0');});
      if(t<1) requestAnimationFrame(count);
    }
    requestAnimationFrame(count);
  }
  document.querySelectorAll('.track-card').forEach(card=>{
    let frame=0, x, y;
    card.addEventListener('pointermove',event=>{
      if(motion.matches || event.pointerType==='touch')return;
      x=event.clientX; y=event.clientY;
      if(!frame)frame=requestAnimationFrame(()=>{
        const box=card.getBoundingClientRect();
        card.style.setProperty('--x',`${x-box.left}px`);
        card.style.setProperty('--y',`${y-box.top}px`);
        frame=0;
      });
    });
  });
  $('#checked-date').textContent=`Checked ${curated_at}`;
  const newsLabels = {'📚':'NEW','🧭':'MAP','📊':'BENCH','🔥':'NEW','🗂️':'MAP','🤖':'TOOL','📁':'DATA','🐱':'TOOL','🚩':'NEW'};
  const plainNews = text=>String(text).replace(/highlighted with 🌟/g,'identified by a Representative badge').replace(/[\p{Extended_Pictographic}\uFE0F\u200D]/gu,'').replace(/ +/g,' ').trim();
  const newsItem = n=>`<article class="news-item"><p class="news-meta"><span class="update-label">${esc(newsLabels[n.icon]||'UPDATE')}</span><time datetime="${esc(n.date)}">${esc(n.date)}</time></p><p><strong>${esc(plainNews(n.title))}</strong></p><p>${esc(plainNews(n.body))}</p></article>`;
  const updates=[...news].sort((a,b)=>b.date.localeCompare(a.date));
  $('#news-list').innerHTML=updates.slice(0,3).map(newsItem).join('');
  $('#news-archive').innerHTML=updates.slice(3).map(newsItem).join('');
  $('.news-archive').hidden=updates.length<=3;
  const latest=[...papers].filter(p=>p.published).sort((a,b)=>b.published.localeCompare(a.published)||b.id.localeCompare(a.id)).slice(0,6);
  $('#recent-updates').innerHTML=latest.map(p=>`<p><time datetime="${esc(p.published)}">${esc(p.published)}</time><a href="papers.html?paper=${encodeURIComponent(p.id)}">${esc(p.title)} <span aria-hidden="true">↗</span></a></p>`).join('');
  $('#reading-paths').innerHTML=taxonomy.reading_paths.map((p,i)=>`<a class="reading-card" href="papers.html?path=${encodeURIComponent(p.id)}"><span class="path-index">0${i+1} / READING PATH</span><h3>${esc(p.title)}</h3><p>${esc(p.description)}</p><span class="path-count">${p.papers.length} WORKS <span aria-hidden="true">↗</span></span></a>`).join('');
})();
