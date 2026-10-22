/* Optional browser acceptance: npm install --prefix test-results/browser-tools playwright */
const {chromium}=require(process.env.CWM_PLAYWRIGHT_MODULE||'../test-results/browser-tools/node_modules/playwright');
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {pathToFileURL}=require('node:url');
const engine=require('../site/search.js');
const root=path.resolve(__dirname,'..'),out=path.join(root,'test-results');
const catalog=JSON.parse(fs.readFileSync(path.join(root,'data/papers.json'),'utf8'));
const taxonomy=JSON.parse(fs.readFileSync(path.join(root,'data/taxonomy.json'),'utf8'));
const base=(process.env.CWM_TEST_URL||'http://127.0.0.1:8000').replace(/\/$/,'');
fs.mkdirSync(out,{recursive:true});
(async()=>{
  const installedChrome='C:/Program Files/Google/Chrome/Application/chrome.exe';
  const browser=await chromium.launch({headless:true,executablePath:process.env.CWM_BROWSER_PATH||(fs.existsSync(installedChrome)?installedChrome:undefined),args:['--disable-background-networking']});
  const checks=[],errors=[];
  try{
    const page=await browser.newPage({viewport:{width:1440,height:1080},reducedMotion:'reduce'});
    page.on('pageerror',e=>errors.push(String(e)));
    const ids=()=>page.locator('.paper-card').evaluateAll(nodes=>nodes.map(n=>n.dataset.paper).sort());
    const expected=(state={})=>catalog.papers.filter(p=>engine.matchesClassification(p.classification,{area:'all',direction:'all',tags:[],...state})).map(p=>p.id).sort();
    const area=id=>page.locator(`#area-options input[value="${id}"]`);
    const tag=id=>page.locator(`#auxiliary-options input[value="${id}"]`);
    const monthButton=id=>page.locator(`#month-options [data-month="${id}"]`);
    const openTags=async()=>{if(!await page.locator('#auxiliary-filters').evaluate(n=>n.open))await page.locator('#auxiliary-filters>summary').click();};
    await page.goto(base+'/',{waitUntil:'networkidle'});
    assert.equal(await page.locator('.paper-card').count(),catalog.papers.length);
    assert.equal(await page.locator('#area-options input[type="radio"]').count(),7);
    assert.equal(await page.locator('#area-options input:checked').count(),1);
    assert.ok(await area('all').isChecked());
    assert.equal(await page.locator('#auxiliary-options fieldset').count(),8);
    assert.equal(await page.locator('#auxiliary-options input[type="checkbox"]').count(),engine.tagOptions(taxonomy).length);
    assert.deepEqual(await page.locator('#auxiliary-options legend').allTextContents(),taxonomy.tag_dimensions.map(d=>d.name));
    assert.equal(await page.locator('.paper-primary [data-area]').count(),catalog.papers.length);
    await page.screenshot({path:path.join(out,'taxonomy-v2-desktop.png')});
    checks.push('58 records, six primary areas plus All, eight auxiliary dimensions, one primary label per paper');

    for(const a of taxonomy.research_areas){
      await area(a.id).check();
      assert.equal(await page.locator('#area-options input:checked').count(),1);
      assert.deepEqual(await ids(),expected({area:a.id}));
    }
    await area('all').check();await page.locator('#direction').selectOption('reconstruction');
    assert.ok(await area('world-construction').isChecked());
    assert.deepEqual(await ids(),expected({area:'world-construction',direction:'reconstruction'}));
    await area('resources-analysis').check();
    assert.equal(await page.locator('#direction').inputValue(),'all');
    assert.deepEqual(await ids(),expected({area:'resources-analysis'}));
    checks.push('Every primary area is exclusive; direction selection synchronizes its parent and changing area clears direction');

    await area('world-construction').check();await openTags();
    await tag('physical-consistency').check();await tag('program-synthesis').check();
    const composite={area:'world-construction',tags:['physical-consistency','program-synthesis']};
    assert.ok(expected(composite).length>0);
    assert.deepEqual(await ids(),expected(composite));
    const intersectionURL=page.url();
    assert.equal(await page.locator('#selected-tags button').count(),2);
    await page.screenshot({path:path.join(out,'taxonomy-v2-intersection.png')});
    await page.locator('#auxiliary-filters>summary').click();
    assert.equal(await page.locator('#selected-tags button:visible').count(),2);
    await page.reload({waitUntil:'networkidle'});
    assert.ok(await area('world-construction').isChecked());
    assert.ok(await tag('physical-consistency').isChecked());assert.ok(await tag('program-synthesis').isChecked());
    assert.deepEqual(await ids(),expected(composite));
    await page.locator('#selected-tags [data-aux-tag="physical-consistency"]').click();
    assert.deepEqual(await ids(),expected({area:'world-construction',tags:['program-synthesis']}));
    await page.goBack();assert.equal(page.url(),intersectionURL);assert.deepEqual(await ids(),expected(composite));
    await page.goForward();assert.ok(!await tag('physical-consistency').isChecked());
    await openTags();await page.locator('#clear-tags').click();
    assert.ok(await area('world-construction').isChecked());assert.deepEqual(await ids(),expected({area:'world-construction'}));
    checks.push('Auxiliary tags intersect across dimensions; selected chips, independent tag reset, refresh and browser history work');

    await page.locator('#clear').click();
    const latestMonth=catalog.papers.filter(p=>p.published).map(p=>p.published.slice(0,7)).sort().reverse()[0];
    await monthButton(latestMonth).click();await area('world-construction').check();await tag('physical-consistency').check();
    const monthState={area:'world-construction',tags:['physical-consistency']};
    assert.deepEqual(await ids(),expected(monthState).filter(id=>catalog.papers.find(p=>p.id===id).published?.startsWith(latestMonth)));
    assert.equal(Number(await monthButton('all').locator('.month-count').innerText()),expected(monthState).length);
    await page.reload({waitUntil:'networkidle'});
    assert.equal(await monthButton(latestMonth).getAttribute('aria-pressed'),'true');
    assert.ok(await area('world-construction').isChecked());assert.ok(await tag('physical-consistency').isChecked());
    await openTags();await page.locator('#clear-tags').click();
    assert.equal(await monthButton(latestMonth).getAttribute('aria-pressed'),'true');
    await page.locator('#clear').click();await monthButton('undated').click();
    assert.deepEqual(await ids(),catalog.papers.filter(p=>!p.published).map(p=>p.id).sort());
    await page.locator('#clear').click();
    checks.push('Month filtering composes with area and tags, updates counts and restores unknown dates and URLs');

    await openTags();await tag('physical-consistency').focus();await page.keyboard.press('Space');
    assert.ok(await tag('physical-consistency').isChecked());await page.keyboard.press('Space');
    assert.ok(!await tag('physical-consistency').isChecked());
    await page.locator('.paper-primary [data-area="world-construction"]').first().click();
    assert.ok(await area('world-construction').isChecked());
    const cardTag=page.locator('.paper-tags [data-aux-tag]').first(),tagId=await cardTag.getAttribute('data-aux-tag');
    await cardTag.click();assert.ok(await tag(tagId).isChecked());
    await page.locator('#clear').click();
    const more=page.locator('.more-tags').first();await more.locator('summary').click();
    assert.ok(await more.evaluate(n=>n.open));
    const extra=more.locator('[data-aux-tag]').first(),extraId=await extra.getAttribute('data-aux-tag');
    await extra.click();assert.ok(await tag(extraId).isChecked());
    await page.locator('#clear').click();
    checks.push('Keyboard checkboxes and clickable primary, auxiliary and expanded paper labels work');

    await tag('physical-consistency').check();await page.locator('[data-badge="available"]').click();
    const available=expected({tags:['physical-consistency']}).filter(id=>catalog.papers.find(p=>p.id===id).resource_status.status==='available');
    assert.deepEqual(await ids(),available);
    await page.locator('#search').fill('World');
    assert.deepEqual(await ids(),available.filter(id=>{const p=catalog.papers.find(p=>p.id===id);return [p.title,p.short_title,...p.authors].join(' ').toLowerCase().includes('world');}));
    await page.locator('#clear').click();await page.locator('#search').fill(catalog.papers[0].authors[0]);
    assert.ok((await ids()).includes(catalog.papers[0].id));
    await page.locator('#clear').click();await page.locator('[data-badge="classic"]').click();
    assert.equal(await page.locator('.paper-card').count(),catalog.papers.filter(p=>p.classic).length);
    await page.locator('#clear').click();
    checks.push('Title and author search composes with auxiliary tags and resource badges');

    await page.locator('#search').fill('<img src=x onerror=alert(1)>no-paper');
    assert.equal(await page.locator('.empty-state').count(),1);assert.equal(await page.locator('#paper-list img').count(),0);
    await page.locator('[data-reset]').click();assert.equal(await page.locator('.paper-card').count(),catalog.papers.length);
    await page.goto(base+'/?area=resources-analysis&direction=reconstruction&tags=unknown&topics=physics&exclude=physics&match=any',{waitUntil:'networkidle'});
    assert.deepEqual(await ids(),expected({area:'resources-analysis'}));
    assert.equal(await page.locator('#direction').inputValue(),'all');
    await page.locator('#clear').click();
    assert.equal(await page.locator('.paper-card h2 a[target="_blank"][rel="noopener noreferrer"]').count(),catalog.papers.length);
    checks.push('Invalid or legacy URL filters cannot constrain results; empty state, safe text and paper links work');

    await page.setViewportSize({width:390,height:844});
    assert.ok(!await page.evaluate('document.documentElement.scrollWidth>innerWidth'));
    assert.ok(await page.locator('#month-options').evaluate(nav=>nav.scrollWidth>nav.clientWidth));
    await page.screenshot({path:path.join(out,'taxonomy-v2-mobile.png')});
    await monthButton(latestMonth).click();
    assert.deepEqual(await ids(),catalog.papers.filter(p=>p.published?.startsWith(latestMonth)).map(p=>p.id).sort());
    await page.locator('#clear').click();await area('world-construction').check();await openTags();
    await tag('physical-consistency').check();await tag('program-synthesis').check();
    assert.deepEqual(await ids(),expected(composite));
    assert.ok(!await page.evaluate('document.documentElement.scrollWidth>innerWidth'));
    await page.screenshot({path:path.join(out,'taxonomy-v2-mobile-tags.png')});
    checks.push('390px mobile layout has no horizontal overflow, supports a scrolling month rail and multi-select tags');

    await page.goto(pathToFileURL(path.join(root,'site/index.html')).href,{waitUntil:'load'});
    assert.equal(await page.locator('.paper-card').count(),catalog.papers.length);
    await area('world-construction').check();await openTags();await tag('physical-consistency').check();
    assert.deepEqual(await ids(),expected({area:'world-construction',tags:['physical-consistency']}));
    await page.goto(base+'/readme.html',{waitUntil:'networkidle'});
    assert.ok(await page.locator('a').filter({hasText:'Open the research website'}).count()>0);
    assert.ok(!await page.evaluate('document.documentElement.scrollWidth>innerWidth'));
    checks.push('Offline file opening and the generated README website entry work');
    assert.deepEqual(errors,[]);
    fs.writeFileSync(path.join(out,'browser-search.json'),JSON.stringify({checks,errors},null,2)+'\n');
    console.log(JSON.stringify({checks,errors},null,2));
  }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
