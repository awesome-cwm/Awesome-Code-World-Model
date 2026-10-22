/* Optional browser acceptance: npm install --prefix test-results/browser-tools playwright */
const {chromium}=require(process.env.CWM_PLAYWRIGHT_MODULE||'../test-results/browser-tools/node_modules/playwright');
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {pathToFileURL}=require('node:url');
const root=path.resolve(__dirname,'..'),out=path.join(root,'test-results');
const catalog=JSON.parse(fs.readFileSync(path.join(root,'data/papers.json'),'utf8'));
const taxonomy=JSON.parse(fs.readFileSync(path.join(root,'data/taxonomy.json'),'utf8'));
const base=(process.env.CWM_TEST_URL||'http://127.0.0.1:8000').replace(/\/$/,'');
const sorted=items=>[...items].sort();
const monthFor=paper=>paper.published?paper.published.slice(0,7):'undated';
const defaults={q:'',badge:'all',topics:[],month:'all'};
const paperById=new Map(catalog.papers.map(p=>[p.id,p]));
const topicById=new Map(taxonomy.topics.map(t=>[t.id,t]));
// Use the catalog as an independent oracle instead of calling the frontend filter implementation.
function expectedPapers(filters={}){
  const state={...defaults,...filters};
  const words=state.q.trim().toLowerCase().split(/\s+/).filter(Boolean);
  return catalog.papers.filter(p=>{
    const titleAndAuthors=[p.title,p.short_title,...p.authors].join(' ').toLowerCase();
    return words.every(word=>titleAndAuthors.includes(word))&&
      state.topics.every(topic=>p.classification.topics.includes(topic))&&
      (state.badge==='all'||(state.badge==='classic'?p.classic:p.resource_status.status===state.badge))&&
      (state.month==='all'||monthFor(p)===state.month);
  });
}
const expectedIds=filters=>sorted(expectedPapers(filters).map(p=>p.id));
fs.mkdirSync(out,{recursive:true});
(async()=>{
  assert.equal(taxonomy.topics.length,22,'The agreed vocabulary contains 22 flat topics');
  const installedChrome='C:/Program Files/Google/Chrome/Application/chrome.exe';
  const browser=await chromium.launch({
    headless:true,
    executablePath:process.env.CWM_BROWSER_PATH||(fs.existsSync(installedChrome)?installedChrome:undefined),
    args:['--disable-background-networking']
  });
  const checks=[],errors=[],dialogs=[];
  try{
    const page=await browser.newPage({viewport:{width:1440,height:1080},reducedMotion:'reduce'});
    page.on('pageerror',error=>errors.push(String(error)));
    page.on('dialog',async dialog=>{dialogs.push(dialog.message());await dialog.dismiss();});
    const topic=id=>page.locator('#topic-options input[value="'+id+'"]');
    const monthButton=id=>page.locator('#month-options [data-month="'+id+'"]');
    const checkedTopics=async()=>sorted(await page.locator('#topic-options input:checked').evaluateAll(nodes=>nodes.map(n=>n.value)));
    const ids=async()=>sorted(await page.locator('.paper-card').evaluateAll(nodes=>nodes.map(n=>n.dataset.paper)));
    const assertResults=async(filters={})=>{
      const actual=await ids();
      assert.equal(new Set(actual).size,actual.length,'Each matching paper renders once');
      assert.deepEqual(actual,expectedIds(filters));
      assert.equal(await page.locator('#result-count').innerText(),
        'Showing '+actual.length+' of '+catalog.papers.length+' papers & projects');
    };
    const assertMonthCounts=async(filters={})=>{
      const pool=expectedPapers({...filters,month:'all'});
      const counts=new Map();
      for(const p of pool)counts.set(monthFor(p),(counts.get(monthFor(p))||0)+1);
      const actual=await page.locator('#month-options [data-month]').evaluateAll(nodes=>nodes.map(n=>({
        month:n.dataset.month,count:Number(n.querySelector('.month-count').textContent),disabled:n.disabled,selected:n.getAttribute('aria-pressed')==='true'
      })));
      assert.deepEqual(sorted(actual.map(n=>n.month)),sorted(['all',...new Set(catalog.papers.map(monthFor))]));
      for(const item of actual){
        const count=item.month==='all'?pool.length:(counts.get(item.month)||0);
        assert.equal(item.count,count,'Month count for '+item.month);
        assert.equal(item.disabled,count===0&&!item.selected,'Empty unselected months are disabled');
      }
    };
    const assertClear=async()=>{
      assert.deepEqual(await checkedTopics(),[]);
      assert.equal(await page.locator('#search').inputValue(),'');
      assert.equal(await page.locator('[data-badge="all"]').getAttribute('aria-pressed'),'true');
      assert.equal(await monthButton('all').getAttribute('aria-pressed'),'true');
      assert.equal(await page.locator('#all-topics').getAttribute('aria-pressed'),'true');
      assert.equal(await page.locator('#selected-topics button').count(),0);
      assert.ok(await page.locator('#clear').isDisabled());
      assert.equal(new URL(page.url()).search,'');
      await assertResults();
    };
    const clear=async()=>{if(await page.locator('#clear').isEnabled())await page.locator('#clear').click();};

    await page.goto(base+'/',{waitUntil:'networkidle'});
    await assertResults();
    assert.equal(await page.locator('#topic-options input[type="checkbox"]').count(),22);
    assert.equal(await page.locator('#topic-options input:disabled').count(),0,'Even empty topics remain selectable');
    assert.equal(await page.locator('input[type="radio"],#direction,#area-options,#auxiliary-options').count(),0);
    assert.deepEqual(await page.locator('#topic-options input').evaluateAll(nodes=>nodes.map(n=>n.value)),taxonomy.topics.map(t=>t.id));
    const labels=await page.locator('.paper-card').evaluateAll(nodes=>nodes.map(n=>({
      id:n.dataset.paper,topics:[...n.querySelectorAll('.paper-topics [data-topic]')].map(b=>b.dataset.topic)
    })));
    for(const card of labels)assert.deepEqual(card.topics,paperById.get(card.id).classification.topics);
    await assertMonthCounts();
    await page.screenshot({path:path.join(out,'topics-desktop.png')});
    checks.push('All records render once; 22 enabled flat native checkboxes and complete paper topic labels replace the hierarchy');

    for(const t of taxonomy.topics){
      await topic(t.id).check();
      assert.deepEqual(await checkedTopics(),[t.id]);
      await assertResults({topics:[t.id]});
      assert.equal(await page.locator('#selected-topics [data-topic="'+t.id+'"]').count(),1);
      const count=await topic(t.id).locator('..').locator('.topic-count').innerText();
      assert.equal(Number(count),expectedPapers({topics:[t.id]}).length);
      await page.locator('#all-topics').click();
      await assertResults();
    }
    checks.push('Every one of the 22 single-topic filters matches the reviewed catalog, including selectable empty topics');

    const pair=['memory','real-time'],triple=[...pair,'general-world-model'];
    assert.ok(expectedIds({topics:pair}).length>0,'Memory plus Real-Time needs a positive reviewed example');
    assert.ok(expectedIds({topics:triple}).length>0,'The integrated-model triple needs a positive example');
    await topic('memory').check();await topic('real-time').check();
    await assertResults({topics:pair});
    assert.equal(await page.locator('#selected-topics button').count(),2);
    assert.equal(await page.locator('#all-topics').getAttribute('aria-pressed'),'false');
    const pairURL=page.url();
    assert.deepEqual(new URL(pairURL).searchParams.get('topics').split(','),sorted(pair));
    await page.screenshot({path:path.join(out,'topics-intersection.png')});
    await topic('general-world-model').check();
    await assertResults({topics:triple});
    await topic('general-world-model').uncheck();
    await assertResults({topics:pair});
    await page.reload({waitUntil:'networkidle'});
    assert.deepEqual(await checkedTopics(),sorted(pair));
    await assertResults({topics:pair});
    await page.locator('#selected-topics [data-topic="memory"]').click();
    assert.deepEqual(await checkedTopics(),['real-time']);
    await assertResults({topics:['real-time']});
    await page.goBack();
    assert.equal(page.url(),pairURL);
    assert.deepEqual(await checkedTopics(),sorted(pair));
    await assertResults({topics:pair});
    await page.goForward();
    assert.deepEqual(await checkedTopics(),['real-time']);
    await assertResults({topics:['real-time']});
    checks.push('Two- and three-topic AND intersections, deselection, selected chips, canonical URLs, reload and browser history work');

    await clear();
    await topic('memory').focus();await page.keyboard.press('Space');
    assert.ok(await topic('memory').isChecked());
    await assertResults({topics:['memory']});
    await page.keyboard.press('Space');
    assert.ok(!await topic('memory').isChecked());
    await assertResults();
    const firstCardTopic=page.locator('.paper-topics [data-topic]').first();
    const cardTopic=await firstCardTopic.getAttribute('data-topic');
    await firstCardTopic.click();
    assert.ok(await topic(cardTopic).isChecked());
    await assertResults({topics:[cardTopic]});
    await page.locator('.paper-topics [data-topic="'+cardTopic+'"]').first().click();
    assert.ok(!await topic(cardTopic).isChecked());
    await assertResults();
    await page.locator('.page-header h1').click();await page.keyboard.press('/');
    assert.ok(await page.locator('#search').evaluate(n=>n===document.activeElement));
    checks.push('Native keyboard selection, paper-label toggling and the search keyboard shortcut work');

    await clear();
    await topic('memory').check();await topic('real-time').check();
    await assertMonthCounts({topics:pair});
    const datedMatch=expectedPapers({topics:pair}).filter(p=>p.published).sort((a,b)=>b.published.localeCompare(a.published))[0];
    assert.ok(datedMatch,'The compound filter has a dated paper');
    const selectedMonth=monthFor(datedMatch);
    await monthButton(selectedMonth).click();
    await assertResults({topics:pair,month:selectedMonth});
    await assertMonthCounts({topics:pair,month:selectedMonth});
    await page.reload({waitUntil:'networkidle'});
    assert.equal(await monthButton(selectedMonth).getAttribute('aria-pressed'),'true');
    assert.deepEqual(await checkedTopics(),sorted(pair));
    await assertResults({topics:pair,month:selectedMonth});
    await clear();
    const undated=catalog.papers.filter(p=>!p.published);
    if(undated.length){
      await monthButton('undated').click();
      await assertResults({month:'undated'});
      const unknownTopic=undated[0].classification.topics[0];
      await topic(unknownTopic).check();
      await assertResults({month:'undated',topics:[unknownTopic]});
      await assertMonthCounts({month:'undated',topics:[unknownTopic]});
      await page.reload({waitUntil:'networkidle'});
      assert.equal(await monthButton('undated').getAttribute('aria-pressed'),'true');
      await assertResults({month:'undated',topics:[unknownTopic]});
    }
    await clear();
    checks.push('Month navigation composes with topic AND filters, recomputes all month counts, and restores dated and Date TBC URLs');

    const anchor=datedMatch,query=anchor.short_title,badge=anchor.resource_status.status;
    const preserved={q:query,badge,month:monthFor(anchor)};
    await page.locator('#search').fill(query);
    await page.locator('[data-badge="'+badge+'"]').click();
    await monthButton(preserved.month).click();
    await topic('memory').check();await topic('real-time').check();
    await assertResults({...preserved,topics:pair});
    await page.locator('#all-topics').click();
    assert.deepEqual(await checkedTopics(),[]);
    assert.equal(await page.locator('#search').inputValue(),query);
    assert.equal(await page.locator('[data-badge="'+badge+'"]').getAttribute('aria-pressed'),'true');
    assert.equal(await monthButton(preserved.month).getAttribute('aria-pressed'),'true');
    await assertResults(preserved);
    const preservedURL=new URL(page.url());
    assert.equal(preservedURL.searchParams.get('q'),query);
    assert.equal(preservedURL.searchParams.get('badge'),badge);
    assert.equal(preservedURL.searchParams.get('month'),preserved.month);
    assert.ok(!preservedURL.searchParams.has('topics'));
    await page.locator('#clear').click();
    await assertClear();
    checks.push('All topics clears only the topic selection while preserving query, resources and month; Clear filters resets everything');

    for(const resource of ['classic','available','not_found']){
      await page.locator('[data-badge="'+resource+'"]').click();
      await assertResults({badge:resource});
      await assertMonthCounts({badge:resource});
      await clear();
    }
    await topic('physics').check();await page.locator('[data-badge="available"]').click();
    await page.locator('#search').fill('World');
    await assertResults({topics:['physics'],badge:'available',q:'World'});
    await assertMonthCounts({topics:['physics'],badge:'available',q:'World'});
    await clear();
    await page.locator('#search').fill(catalog.papers[0].authors[0]);
    await assertResults({q:catalog.papers[0].authors[0]});
    assert.ok((await ids()).includes(catalog.papers[0].id));
    await page.locator('#search').fill(catalog.papers[0].short_title);
    await assertResults({q:catalog.papers[0].short_title});
    await clear();
    assert.equal(await page.locator('.paper-card h2 a[target="_blank"][rel="noopener noreferrer"]').count(),catalog.papers.length);
    checks.push('All resource badges, title/author search and compound resource/topic/search queries match the independent oracle');

    await page.locator('#search').fill('<img src=x onerror=alert(1)>no-paper');
    assert.equal(await page.locator('.empty-state').count(),1);
    assert.equal(await page.locator('#paper-list img').count(),0);
    await assertResults({q:'<img src=x onerror=alert(1)>no-paper'});
    await page.locator('[data-reset]').click();
    await assertClear();
    await page.goto(base+'/?area=resources-analysis&direction=reconstruction&tags=physics&exclude=memory&match=any&topics=memory,unknown,real-time&topics=memory&badge=invalid&month=2099-99',{waitUntil:'networkidle'});
    assert.deepEqual(await checkedTopics(),sorted(pair));
    await assertResults({topics:pair});
    await topic('general-world-model').check();
    await assertResults({topics:triple});
    const sanitized=new URL(page.url()).searchParams;
    assert.deepEqual([...sanitized.keys()],['topics']);
    assert.deepEqual(sanitized.get('topics').split(','),sorted(triple));
    await page.goto(base+'/?area=world-construction&direction=reconstruction&tags=physics&exclude=memory&match=any',{waitUntil:'networkidle'});
    assert.deepEqual(await checkedTopics(),[]);
    await assertResults();
    checks.push('Invalid IDs and retired hierarchy/OR/exclusion parameters are ignored, valid repeated topics deduplicate, URLs normalize after interaction and empty results reset safely');

    await page.goto(base+'/',{waitUntil:'networkidle'});
    await page.setViewportSize({width:390,height:844});
    const assertNoOverflow=async()=>assert.ok(!await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),'No horizontal page overflow at 390px');
    await assertNoOverflow();
    assert.ok(await page.locator('#month-options').evaluate(nav=>nav.scrollWidth>nav.clientWidth));
    await page.screenshot({path:path.join(out,'topics-mobile.png')});
    await monthButton(selectedMonth).click();
    await assertResults({month:selectedMonth});
    await topic('memory').check();await topic('real-time').check();
    await assertResults({month:selectedMonth,topics:pair});
    await assertNoOverflow();
    await page.screenshot({path:path.join(out,'topics-mobile-selected.png')});
    await clear();await assertClear();
    checks.push('390px layout has no page overflow and retains a horizontal month rail, native multiselection and mobile clear controls');

    await page.goto(pathToFileURL(path.join(root,'site/index.html')).href,{waitUntil:'load'});
    await assertResults();
    await topic('memory').check();await topic('real-time').check();
    await assertResults({topics:pair});
    await monthButton(selectedMonth).click();
    await assertResults({topics:pair,month:selectedMonth});
    await clear();
    await assertResults();
    checks.push('Opening site/index.html directly from file:// supports topic intersections, months and reset');

    await page.goto(base+'/readme.html',{waitUntil:'networkidle'});
    const websiteEntry=page.locator('.prose a').filter({hasText:'Open the research website'});
    assert.ok(await websiteEntry.count()>0,'Generated README retains the website entry');
    const websiteHref=await websiteEntry.first().getAttribute('href');
    assert.ok(/^https:\/\/[^/]+\.github\.io\/[^/]+\//.test(websiteHref)||websiteHref==='index.html'||websiteHref==='./');
    const paperPlacements=await page.locator('.prose').evaluate((prose,titles)=>{
      const wanted=new Set(titles),found=[];
      let heading='';
      for(const element of prose.querySelectorAll('h2,a')){
        if(element.tagName==='H2')heading=element.textContent.trim();
        else if(wanted.has(element.textContent.trim()))found.push({title:element.textContent.trim(),heading});
      }
      return found;
    },catalog.papers.map(p=>p.title));
    assert.equal(paperPlacements.length,catalog.papers.length,'One bibliography link per record in generated README');
    for(const paper of catalog.papers){
      const entries=paperPlacements.filter(entry=>entry.title===paper.title);
      assert.equal(entries.length,1,'README lists '+paper.id+' exactly once');
      assert.equal(entries[0].heading,topicById.get(paper.classification.readme_topic).name,'README placement for '+paper.id);
    }
    assert.ok(await page.locator('.prose a[href="topic-review.html"]').count()>0);
    await assertNoOverflow();
    await page.goto(base+'/topic-review.html',{waitUntil:'networkidle'});
    assert.equal(await page.locator('.prose h1').innerText(),'Per-paper Topic Review');
    const reviewHeadings=await page.locator('.prose h2').allTextContents();
    assert.deepEqual(reviewHeadings,catalog.papers.map(p=>p.short_title));
    const reviewIds=await page.locator('.prose code').allTextContents();
    for(const paper of catalog.papers)assert.equal(reviewIds.filter(id=>id===paper.id).length,1);
    assert.ok((await page.locator('.prose').innerText()).includes('Sources actually consulted'));
    await assertNoOverflow();
    checks.push('Generated README lists each paper title exactly once under its chosen topic and links the website; review HTML covers every record and its sources');

    assert.deepEqual(errors,[]);
    assert.deepEqual(dialogs,[]);
    const report={papers:catalog.papers.length,topics:taxonomy.topics.length,checks,errors,dialogs};
    fs.writeFileSync(path.join(out,'browser-search.json'),JSON.stringify(report,null,2)+'\n');
    console.log(JSON.stringify(report,null,2));
  }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
