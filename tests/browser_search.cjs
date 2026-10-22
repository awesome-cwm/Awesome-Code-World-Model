/* 可选浏览器验收：npm install --prefix test-results/browser-tools playwright */
const {chromium}=require(process.env.CWM_PLAYWRIGHT_MODULE||'../test-results/browser-tools/node_modules/playwright');
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {pathToFileURL}=require('node:url');
const engine=require('../site/search.js');
const root=path.resolve(__dirname,'..'),out=path.join(root,'test-results');
const catalog=JSON.parse(fs.readFileSync(path.join(root,'data/papers.json'),'utf8'));
const taxonomy=JSON.parse(fs.readFileSync(path.join(root,'data/taxonomy.json'),'utf8'));
const base=process.env.CWM_TEST_URL||'http://127.0.0.1:8000';
fs.mkdirSync(out,{recursive:true});
(async()=>{
  const installedChrome='C:/Program Files/Google/Chrome/Application/chrome.exe';
  const browser=await chromium.launch({headless:true,executablePath:process.env.CWM_BROWSER_PATH||(fs.existsSync(installedChrome)?installedChrome:undefined),args:['--disable-background-networking']});
  const checks=[],errors=[];
  try{
    const page=await browser.newPage({viewport:{width:1440,height:1080},reducedMotion:'reduce'});
    page.on('pageerror',e=>errors.push(String(e)));
    const ids=()=>page.locator('.paper-card').evaluateAll(nodes=>nodes.map(n=>n.dataset.paper).sort());
    const expected=selected=>catalog.papers.filter(p=>engine.matchesTopics(engine.topicsFor(p,taxonomy.topics),{include:selected})).map(p=>p.id).sort();
    const topic=id=>page.locator(`#topic-options input[value="${id}"]`);
    await page.goto(base,{waitUntil:'networkidle'});
    assert.equal(await page.locator('.paper-card').count(),catalog.papers.length);
    assert.equal(await page.locator('#topic-options input[type="checkbox"]').count(),10);
    assert.equal(await page.locator('.index-hero,.advanced-panel,.match-switch,.compare-tray,dialog').count(),0);
    await page.screenshot({path:path.join(out,'simple-desktop.png')});
    checks.push('Simple reference-style list: 58 papers, 10 checkboxes, no extra panels');

    await topic('physics').check();await topic('reconstruction').check();
    assert.deepEqual(await ids(),expected(['physics','reconstruction']));
    const intersectionURL=page.url();
    await page.screenshot({path:path.join(out,'simple-intersection.png')});
    await page.reload({waitUntil:'networkidle'});
    assert.ok(await topic('physics').isChecked());assert.ok(await topic('reconstruction').isChecked());
    assert.deepEqual(await ids(),expected(['physics','reconstruction']));
    await topic('physics').uncheck();assert.deepEqual(await ids(),expected(['reconstruction']));
    await page.goBack();assert.equal(page.url(),intersectionURL);assert.ok(await topic('physics').isChecked());
    await page.goForward();assert.ok(!await topic('physics').isChecked());
    checks.push('Multi-select intersection, deselection, refresh and browser history');

    await page.locator('#clear').click();
    const latestMonth=catalog.papers.filter(p=>p.published).map(p=>p.published.slice(0,7)).sort().reverse()[0];
    const monthButton=month=>page.locator(`#month-options [data-month="${month}"]`);
    await monthButton(latestMonth).click();
    assert.deepEqual(await ids(),catalog.papers.filter(p=>p.published?.startsWith(latestMonth)).map(p=>p.id).sort());
    await topic('physics').check();
    assert.deepEqual(await ids(),expected(['physics']).filter(id=>catalog.papers.find(p=>p.id===id).published?.startsWith(latestMonth)));
    assert.equal(Number(await monthButton('all').locator('.month-count').innerText()),expected(['physics']).length);
    await page.reload({waitUntil:'networkidle'});
    assert.equal(await monthButton(latestMonth).getAttribute('aria-pressed'),'true');
    assert.ok(await topic('physics').isChecked());
    await page.locator('#clear').click();await monthButton('undated').click();
    assert.deepEqual(await ids(),catalog.papers.filter(p=>!p.published).map(p=>p.id).sort());
    await page.locator('#clear').click();
    assert.equal(await monthButton('all').getAttribute('aria-pressed'),'true');
    checks.push('Month navigation composes with topics, updates counts, restores URLs and includes undated work');

    await page.locator('#all-topics').click();
    assert.equal(await page.locator('.paper-card').count(),catalog.papers.length);
    await topic('physics').focus();await page.keyboard.press('Space');assert.ok(await topic('physics').isChecked());
    await page.keyboard.press('Space');assert.ok(!await topic('physics').isChecked());
    await page.locator('.paper-topics [data-topic="physics"]').first().click();assert.ok(await topic('physics').isChecked());
    await page.locator('#clear').click();
    checks.push('All-topics reset, keyboard checkboxes and clickable paper topic labels');

    await topic('physics').check();await page.locator('[data-badge="available"]').click();
    const intersection=expected(['physics']).filter(id=>catalog.papers.find(p=>p.id===id).resource_status.status==='available');
    assert.deepEqual(await ids(),intersection);
    await page.locator('#search').fill('World');
    assert.ok((await ids()).every(id=>{const p=catalog.papers.find(p=>p.id===id);return [p.title,p.short_title,...p.authors].join(' ').toLowerCase().includes('world');}));
    await page.locator('#clear').click();
    await page.locator('#search').fill(catalog.papers[0].authors[0]);
    assert.ok((await ids()).includes(catalog.papers[0].id));
    await page.locator('#clear').click();await page.locator('[data-badge="classic"]').click();
    assert.equal(await page.locator('.paper-card').count(),catalog.papers.filter(p=>p.classic).length);
    await page.locator('#clear').click();
    checks.push('Search by title / author composes with topic and badge filters');

    await page.locator('#search').fill('<img src=x onerror=alert(1)>no-paper');
    assert.equal(await page.locator('.empty-state').count(),1);assert.equal(await page.locator('#paper-list img').count(),0);
    await page.locator('[data-reset]').click();
    assert.equal(await page.locator('.paper-card').count(),catalog.papers.length);
    await page.goto(base+'/?topics=unknown,physics,physics,reconstruction&exclude=physics&match=any',{waitUntil:'networkidle'});
    assert.deepEqual(await ids(),expected(['physics','reconstruction']));
    await page.locator('#clear').click();
    assert.equal(await page.locator('.paper-card h2 a[target="_blank"][rel="noopener noreferrer"]').count(),catalog.papers.length);
    checks.push('Empty-state reset, safe text, direct paper links and no invisible legacy filters');

    await page.setViewportSize({width:390,height:844});
    assert.ok(!await page.evaluate('document.documentElement.scrollWidth>innerWidth'));
    assert.ok(await page.locator('#month-options').evaluate(nav=>nav.scrollWidth>nav.clientWidth));
    await monthButton(latestMonth).click();
    assert.deepEqual(await ids(),catalog.papers.filter(p=>p.published?.startsWith(latestMonth)).map(p=>p.id).sort());
    await page.locator('#clear').click();
    await page.screenshot({path:path.join(out,'simple-mobile.png')});
    await topic('physics').check();await topic('reconstruction').check();
    assert.deepEqual(await ids(),expected(['physics','reconstruction']));
    assert.ok(!await page.evaluate('document.documentElement.scrollWidth>innerWidth'));
    checks.push('390px phone layout has no horizontal overflow and supports multi-selection');

    await page.goto(pathToFileURL(path.join(root,'site/index.html')).href,{waitUntil:'load'});
    assert.equal(await page.locator('.paper-card').count(),catalog.papers.length);
    await topic('physics').check();assert.deepEqual(await ids(),expected(['physics']));
    await page.goto(base+'/readme.html',{waitUntil:'networkidle'});
    assert.ok(await page.locator('a').filter({hasText:'Open the research website'}).count()>0);
    assert.ok(!await page.evaluate('document.documentElement.scrollWidth>innerWidth'));
    checks.push('Offline file opening and generated README website entry');
    assert.deepEqual(errors,[]);
    fs.writeFileSync(path.join(out,'browser-search.json'),JSON.stringify({checks,errors},null,2)+'\n');
    console.log(JSON.stringify({checks,errors},null,2));
  }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
