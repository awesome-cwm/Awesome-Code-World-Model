"""可选真实浏览器验收：需要 playwright 和 Chromium，不属于标准库单元测试。"""
import asyncio
import json
import os
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
from playwright.async_api import async_playwright, expect

ROOT=Path(__file__).resolve().parents[1]
BASE=os.environ.get('CWM_TEST_URL','http://127.0.0.1:8000')
LIBRARY=BASE.rstrip('/')+'/papers.html'


async def check_main_navigation(browser, out):
    expected=[{'href':name+'.html','text':label} for name,label in [('index','Home'),('papers','Papers'),('taxonomy','Taxonomy'),('research','Research notes'),('contributing','Contribute'),('readme','Repository guide')]]
    context=await browser.new_context(reduced_motion='reduce')
    # A deployed catalog must not turn the local guide into an external GitHub link.
    catalog_script=(ROOT/'site/catalog.js').read_text(encoding='utf-8')+'\nwindow.CWM_CATALOG.repository="example/repository";'
    await context.route('**/catalog.js',lambda route:route.fulfill(body=catalog_script,content_type='application/javascript'))
    page=await context.new_page()

    async def check_header(filename):
        await page.evaluate('document.fonts.ready')
        links=page.locator('.header nav a')
        assert await links.evaluate_all('(els) => els.map(el => ({href:el.getAttribute("href"),text:el.textContent.trim()}))')==expected
        assert await links.evaluate_all('els => els.every(el => el.getBoundingClientRect().width>0)')
        current=page.locator('a[aria-current="page"]')
        assert await current.count()==1
        assert await current.get_attribute('href')==filename
        assert await current.evaluate('el => getComputedStyle(el).textDecorationLine')=='underline'
        assert await page.locator('.header').evaluate('''header => {
            const brand=header.querySelector('.brand').getBoundingClientRect();
            const links=[...header.querySelectorAll('nav a')].map(el=>el.getBoundingClientRect());
            const theme=header.querySelector('.theme-toggle').getBoundingClientRect();
            return header.getBoundingClientRect().height===88 && brand.right<=links[0].left &&
                links.every((box,i)=>i===0 || links[i-1].right<=box.left) &&
                links[links.length-1].right<=theme.left;
        }'''),filename
        assert await page.evaluate('document.documentElement.scrollWidth<=innerWidth'),filename

    for theme in ['light','dark']:
        for width in [1440,1280,1024,900,801]:
            await page.set_viewport_size({'width':width,'height':900})
            await page.goto(BASE+'/index.html',wait_until='load')
            await page.evaluate('(theme) => localStorage.setItem("cwm-theme",theme)',theme)
            await page.reload(wait_until='load')
            await check_header('index.html')
            for filename in ['readme','contributing','readme','papers','taxonomy','research','index']:
                link=page.locator(f'.header nav a[href="{filename}.html"]')
                if filename=='contributing':
                    await link.focus()
                    assert await link.evaluate('el => getComputedStyle(el).outlineStyle')=='solid'
                    await page.keyboard.press('Enter')
                else:
                    await link.click()
                await page.wait_for_url('**/'+filename+'.html',wait_until='load')
                await check_header(filename+'.html')
                assert await page.locator('html').get_attribute('data-theme')==theme
                if filename=='contributing':
                    await page.locator('.header').screenshot(path=str(out/f'navigation-{theme}-contribute-{width}.png'))
                    if width==1440:
                        await page.go_back(wait_until='load')
                        await check_header('readme.html')
                        await page.go_forward(wait_until='load')
                        await check_header('contributing.html')
        await page.set_viewport_size({'width':1440,'height':900})
        for filename in ['benchmarks','deployment','crawler','agent-review','topic-review','frontend']:
            await page.goto(BASE+'/'+filename+'.html',wait_until='load')
            await check_header(filename+'.html')
            assert await page.locator('.header nav [aria-current="page"]').count()==0
            assert await page.locator('.document-context [aria-current="page"]').count()==1
    await context.close()


async def check_file_document_themes(playwright, out):
    candidates=[
        ('Chrome',playwright.chromium,os.environ.get('CWM_BROWSER_PATH','C:/Program Files/Google/Chrome/Application/chrome.exe')),
        ('Edge',playwright.chromium,os.environ.get('CWM_EDGE_PATH','C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe')),
        ('Firefox',playwright.firefox,os.environ.get('CWM_FIREFOX_PATH',playwright.firefox.executable_path)),
    ]
    reports=[]
    for name,engine,executable in candidates:
        if not Path(executable).exists():
            reports.append({'browser':name,'status':'not installed; skipped'})
            continue
        browser=await engine.launch(headless=True,executable_path=executable)
        context=await browser.new_context(color_scheme='light',reduced_motion='reduce')
        page=await context.new_page()
        errors=[]
        page.on('pageerror',lambda error:errors.append(str(error)))
        await page.goto((ROOT/'site/index.html').as_uri(),wait_until='load')
        await page.locator('.theme-toggle').click()
        await page.locator('.theme-toggle').click()
        assert await page.locator('html').get_attribute('data-theme')=='dark'
        await page.locator('.header nav a[href="taxonomy.html"]').click()
        async def check_document(filename):
            assert await page.locator('html').get_attribute('data-theme')=='dark',(name,filename)
            assert await page.locator('body').evaluate('(el) => getComputedStyle(el).backgroundColor')=='rgb(23, 30, 27)'
            current=page.locator('.document-page a[aria-current="page"]')
            assert await current.count()==1
            assert await current.get_attribute('href')==filename
            assert await current.evaluate('(el) => getComputedStyle(el).textDecorationLine')=='underline'
            assert await current.evaluate('(el) => getComputedStyle(el).fontWeight')=='600'
            assert await page.locator('.document-back').get_attribute('href')=='papers.html'
            assert await page.locator('.header .brand').get_attribute('href')=='index.html'
            assert await page.locator('.document .prose').evaluate('(el)=>getComputedStyle(el).fontSize')=='16px'
        await check_document('taxonomy.html')
        # Bypass the browser cache rather than relying on a headless keyboard shortcut.
        if engine==playwright.chromium:
            session=await context.new_cdp_session(page)
            async with page.expect_navigation(wait_until='load'):
                await session.send('Page.reload',{'ignoreCache':True})
        else:
            async with page.expect_navigation(wait_until='load'):
                await page.evaluate('location.reload(true)')
        await check_document('taxonomy.html')
        for filename in ['topic-review.html','readme.html']:
            await page.goto((ROOT/'site'/filename).as_uri(),wait_until='load')
            await check_document(filename)
        await page.goto((ROOT/'site/papers.html').as_uri()+'?q=VideoCoCo&paper=videococo#library',wait_until='load')
        assert await page.locator('#detail-dialog').is_visible()
        await page.keyboard.press('Escape')
        await page.wait_for_function("!new URLSearchParams(location.search).has('paper')")
        assert parse_qs(urlsplit(page.url).query)=={'q':['VideoCoCo']}
        assert urlsplit(page.url).fragment=='library'
        await page.set_viewport_size({'width':390,'height':844})
        await page.goto((ROOT/'site/index.html').as_uri()+'#benchmark-entry',wait_until='load')
        await page.wait_for_url('**/papers.html#benchmark-entry')
        assert await page.locator('.library-options').get_attribute('open') is not None
        assert await page.locator('#benchmark-entry').is_visible()
        assert not errors,(name,errors)
        reports.append({'browser':name,'version':browser.version,'status':'passed','file_dark_navigation':True,'taxonomy_current_page':True,'cache_bypass_refresh':True,'mobile_benchmark_anchor':True,'paper_close_preserves_query_hash':True})
        await browser.close()
    (out/'file-browser-results.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(reports,ensure_ascii=False,indent=2))


async def check_deep_links(page):
    await page.set_viewport_size({'width':390,'height':844})
    for url in [LIBRARY+'#benchmark-entry', BASE+'/#benchmark-entry']:
        await page.goto(url,wait_until='networkidle')
        await page.wait_for_url('**/papers.html#benchmark-entry')
        assert await page.locator('.library-options').get_attribute('open') is not None
        assert await page.locator('#benchmark-entry').is_visible()
        await page.wait_for_function('''() => {
            const box=document.querySelector('#benchmark-entry').getBoundingClientRect();
            const header=document.querySelector('.header').getBoundingClientRect();
            return box.top>=header.bottom && box.top<innerHeight && box.bottom<=innerHeight;
        }''')
        assert await page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    # Hash-only navigation on an already-loaded mobile page also reveals the target.
    await page.goto(LIBRARY,wait_until='networkidle')
    assert await page.locator('.library-options').get_attribute('open') is None
    await page.evaluate("location.hash='benchmark-entry'")
    await page.wait_for_function("document.querySelector('.library-options').open")

    await page.set_viewport_size({'width':1440,'height':1100})
    for method in ['escape','button','backdrop']:
        await page.goto(LIBRARY+'?q=VideoCoCo&sort=title&paper=videococo&utm_source=test#library',wait_until='networkidle')
        assert await page.locator('#detail-dialog').is_visible()
        if method=='escape':
            await page.keyboard.press('Escape')
        elif method=='button':
            await page.locator('#detail-dialog .close-dialog').click()
        else:
            await page.mouse.click(1,1)
        await page.wait_for_function("!new URLSearchParams(location.search).has('paper')")
        assert parse_qs(urlsplit(page.url).query)=={'q':['VideoCoCo'],'sort':['title'],'utm_source':['test']}
        assert urlsplit(page.url).fragment=='library'
        await page.reload(wait_until='networkidle')
        assert not await page.locator('#detail-dialog').is_visible()


async def check_themes(browser, out):
    context=await browser.new_context(color_scheme='dark',reduced_motion='reduce')
    page=await context.new_page()
    errors=[]
    page.on('pageerror',lambda error:errors.append(str(error)))
    await page.goto(LIBRARY,wait_until='networkidle')
    assert await page.locator('html').get_attribute('data-theme')=='dark'
    assert (await page.locator('.theme-toggle').get_attribute('aria-label')).startswith('Theme: System.')
    await page.emulate_media(color_scheme='light')
    await page.wait_for_function("document.documentElement.dataset.theme==='light'")
    await page.locator('.theme-toggle').focus()
    assert await page.locator('.theme-toggle').evaluate('(el) => getComputedStyle(el).outlineStyle')=='solid'
    await page.keyboard.press('Enter')
    assert await page.locator('html').get_attribute('data-theme-preference')=='light'
    await page.emulate_media(color_scheme='dark')
    assert await page.locator('html').get_attribute('data-theme')=='light'
    await page.keyboard.press('Enter')
    assert await page.locator('html').get_attribute('data-theme')=='dark'
    await page.reload(wait_until='networkidle')
    assert (await page.locator('.theme-toggle').get_attribute('aria-label')).startswith('Theme: Dark.')
    await page.goto(BASE+'/taxonomy.html',wait_until='networkidle')
    assert (await page.locator('.theme-toggle').get_attribute('aria-label')).startswith('Theme: Dark.')
    current=page.locator('.document-page .header nav a[aria-current="page"]')
    assert await current.get_attribute('href')=='taxonomy.html'
    assert await current.evaluate("(el) => getComputedStyle(el).textDecorationLine")=='underline'
    assert await current.evaluate("(el) => getComputedStyle(el).fontWeight")=='600'
    await page.locator('.theme-toggle').click()
    assert await page.locator('html').get_attribute('data-theme-preference')=='system'
    assert await page.locator('html').get_attribute('data-theme')=='dark'
    sibling=await context.new_page()
    await sibling.goto(LIBRARY,wait_until='networkidle')
    await page.locator('.theme-toggle').click()
    await sibling.wait_for_function("document.documentElement.dataset.theme==='light'")
    await sibling.close()

    for theme in ['light','dark']:
        await page.evaluate('(theme) => localStorage.setItem("cwm-theme",theme)',theme)
        for target in ['index.html','papers.html','taxonomy.html']:
            await page.goto(BASE+'/'+target,wait_until='networkidle')
            assert await page.locator('html').get_attribute('data-theme')==theme
            await page.evaluate('document.fonts.ready')
            assert await page.evaluate('document.fonts.check(\'400 20px "Newsreader"\')')
            assert await page.evaluate('document.fonts.check(\'400 17px "Source Sans 3"\')')
            for width in [1440,1024,768,390,320]:
                await page.set_viewport_size({'width':width,'height':1000})
                assert await page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(target,theme,width)
                assert await page.locator('.theme-toggle').is_visible()
                if width in [1440,1024,768,390]:
                    await page.screenshot(path=str(out/f'theme-{theme}-{target}-{width}.png'))
                if target=='taxonomy.html':
                    assert await page.locator('.header nav a[aria-current="page"]').is_visible()
                    assert await page.locator('.header nav a[href="papers.html"]').is_visible()
                    assert await page.locator('.document .prose').evaluate('(el)=>getComputedStyle(el).fontSize')=='16px'
                    assert await page.locator('.toc-desktop').is_visible()==(width>1100)
                    assert await page.locator('.toc-mobile').is_visible()==(width<=1100)
            if target=='papers.html':
                await page.locator('#search').fill('VideoCoCo: Code-as-CoT')
                assert await page.locator('.paper-card').count()==1
                await page.locator('.paper-card [data-detail]').click()
                assert await page.locator('#detail-dialog').is_visible()
                await page.keyboard.press('Escape')
    assert not errors,errors
    await context.close()

    restricted=await browser.new_context(color_scheme='dark',has_touch=True,is_mobile=True,viewport={'width':390,'height':844})
    await restricted.add_init_script("Object.defineProperty(window,'localStorage',{get(){throw new Error('Storage disabled')}})")
    restricted_page=await restricted.new_page()
    await restricted_page.goto(LIBRARY,wait_until='networkidle')
    assert await restricted_page.locator('html').get_attribute('data-theme')=='dark'
    await restricted_page.locator('.theme-toggle').click()
    await expect(restricted_page.locator('html')).to_have_attribute('data-theme','light')
    await restricted_page.locator('.library-options > summary').click()
    assert await restricted_page.locator('.resource-filters button').first.evaluate('(el) => el.getBoundingClientRect().height')>=44
    await restricted.close()

    offline=await browser.new_context(color_scheme='dark')
    offline_page=await offline.new_page()
    await offline_page.goto((ROOT/'site/papers.html').as_uri(),wait_until='load')
    assert await offline_page.locator('.theme-toggle').is_visible()
    assert await offline_page.locator('.paper-card').count()>0
    await offline.close()
    no_script=await browser.new_context(java_script_enabled=False,color_scheme='dark')
    no_script_page=await no_script.new_page()
    await no_script_page.goto(BASE+'/index.html',wait_until='networkidle')
    assert await no_script_page.locator('html').evaluate('(el) => getComputedStyle(el).colorScheme')=='dark'
    await no_script.close()


async def check_visual_enhancements(browser, out):
    context=await browser.new_context(viewport={'width':1440,'height':1000},color_scheme='light')
    page=await context.new_page()
    errors=[]
    page.on('pageerror',lambda error:errors.append(str(error)))
    await page.goto(BASE+'/index.html',wait_until='networkidle')
    await page.wait_for_function("[...document.querySelectorAll('.stat strong')].map(el=>el.textContent).join(',')===[String(CWM_CATALOG.papers.length),'02',String(CWM_CATALOG.taxonomy.dimensions.length).padStart(2,'0')].join(',')")
    assert await page.locator('link[rel="preload"][as="font"]').count()==2
    # The code panel must follow the drawing in normal flow, in either theme.
    for preference in ['light','dark']:
        await page.evaluate('(theme)=>localStorage.setItem("cwm-theme",theme)',preference)
        await page.reload(wait_until='networkidle')
        assert await page.evaluate('''() => document.querySelector('.code-strip').getBoundingClientRect().top>=document.querySelector('.world-svg').getBoundingClientRect().bottom''')
    await page.locator('.track-card').first.hover()
    await page.wait_for_function("document.querySelector('.track-card').style.getPropertyValue('--x')!==''")
    await page.screenshot(path=str(out/'direction-card-hover.png'))
    await page.evaluate('scrollTo(0,600)')
    assert await page.locator('.header').evaluate('(el)=>el.getBoundingClientRect().top')==0
    await page.evaluate('scrollTo(0,0)')
    if await page.evaluate('!!document.startViewTransition'):
        await page.locator('.theme-toggle').click()
        await page.wait_for_function("document.documentElement.dataset.themePreference==='system'")
        await page.wait_for_function("!document.querySelector('.theme-toggle').disabled")
        assert await page.evaluate("document.documentElement.style.getPropertyValue('--theme-x')!==''")
    # Unsupported View Transitions still switch themes synchronously.
    await page.evaluate('document.startViewTransition=undefined')
    await page.locator('.theme-toggle').click()
    assert await page.locator('html').get_attribute('data-theme-preference')=='light'
    await page.emulate_media(reduced_motion='reduce')
    assert await page.locator('.loop-path').evaluate('(el)=>getComputedStyle(el).animationName')=='none'
    await page.locator('.theme-toggle').click()
    assert await page.locator('html').get_attribute('data-theme')=='dark'
    await page.goto(BASE+'/taxonomy.html',wait_until='networkidle')
    anchors=await page.locator('.toc-desktop a').evaluate_all('(els)=>els.map(el=>decodeURIComponent(el.hash).slice(1))')
    assert len(anchors)>=4
    for anchor in anchors:
        assert await page.locator(f'[id="{anchor}"]').count()==1
    await page.locator('.toc-desktop a').last.click()
    await page.wait_for_function('''() => {
        const target=document.getElementById(decodeURIComponent(location.hash.slice(1)));
        return target.getBoundingClientRect().top>=document.querySelector('.header').getBoundingClientRect().bottom;
    }''')
    await page.set_viewport_size({'width':390,'height':844})
    await page.locator('.toc-mobile summary').click()
    await page.locator('.toc-mobile a').last.click()
    assert await page.locator(f'[id="{anchors[-1]}"]').is_visible()
    await page.goto(BASE+'/papers.html',wait_until='networkidle')
    assert await page.locator('.resource-filters svg').count()==3
    assert await page.locator('.paper-card .resource-badge svg').count()>0
    assert not errors,errors
    await context.close()


async def check_home_navigation(page, records, taxonomy, news, out):
    await page.goto(BASE+'/',wait_until='networkidle')
    assert await page.locator('.hero').count()==1
    assert await page.locator('#search, #paper-list, #research-filters').count()==0
    assert await page.locator('#news-list .news-item').count()==min(3,len(news))
    assert await page.locator('#news-archive .news-item').count()==max(0,len(news)-3)
    assert not await page.locator('#news-archive').is_visible()
    await page.locator('.news-archive > summary').focus()
    await page.keyboard.press('Enter')
    assert await page.locator('#news-archive').is_visible()
    assert await page.locator('.news-item, .updates-layout h2').evaluate_all("els => els.every(el => !/\\p{Extended_Pictographic}/u.test(el.textContent))")
    await page.keyboard.press('Enter')
    assert await page.locator('#recent-updates > p').count()==6
    assert await page.locator('#reading-paths a').count()==len(taxonomy['reading_paths'])
    assert await page.locator('.stat strong').first.inner_text()==str(len(records))
    for width in [1440,1024,768,390]:
        await page.set_viewport_size({'width':width,'height':1000})
        assert await page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        assert await page.get_by_role('navigation',name='Main navigation').get_by_role('link',name='Home',exact=True).is_visible()
        assert await page.get_by_role('navigation',name='Main navigation').get_by_role('link',name='Papers',exact=True).is_visible()
        await page.screenshot(path=str(out/f'home-{width}.png'),full_page=True)
    await page.set_viewport_size({'width':1440,'height':1100})
    await page.locator('.track-card.generation').click()
    assert urlsplit(page.url).path.endswith('/papers.html')
    assert await page.locator('.hero, #news-list, #reading-paths').count()==0
    assert await page.locator('.paper-card').count()==sum(p['track']=='generation' for p in records)
    await page.go_back(wait_until='networkidle')
    await page.locator('#reading-paths a[href="papers.html?path=render"]').click()
    path=next(p for p in taxonomy['reading_paths'] if p['id']=='render')
    assert await page.locator('.paper-card').count()==len(path['papers'])
    assert await page.locator('.paper-card').first.get_attribute('data-paper')==path['papers'][0]
    await page.go_back(wait_until='networkidle')
    recent=page.locator('#recent-updates a').first
    ident=parse_qs(urlsplit(await recent.get_attribute('href')).query)['paper'][0]
    await recent.click()
    assert await page.locator('#detail-dialog').is_visible()
    assert await page.locator('#dialog-title').inner_text()==next(p['title'] for p in records if p['id']==ident)
    await page.keyboard.press('Escape')
    await page.goto(BASE+'/?q=physics&track=generation&view=timeline#library',wait_until='networkidle')
    await page.wait_for_url('**/papers.html?**')
    assert parse_qs(urlsplit(page.url).query)=={'q':['physics'],'track':['generation'],'view':['timeline']}
    assert await page.locator('#search').input_value()=='physics'
    assert await page.locator('[data-view="timeline"]').get_attribute('aria-pressed')=='true'
    await page.goto(BASE+'/index.html#benchmark-entry',wait_until='networkidle')
    await page.wait_for_url('**/papers.html#benchmark-entry')
    assert await page.locator('#benchmark-entry').is_visible()
    await page.locator('nav[aria-label="Main navigation"] a[href="index.html"]').click()
    assert await page.locator('.hero').is_visible()


async def check_layout_polish(browser, out):
    context=await browser.new_context(reduced_motion='reduce')
    page=await context.new_page()
    for theme in ['light','dark']:
        await page.set_viewport_size({'width':1440,'height':900})
        await page.goto(LIBRARY,wait_until='networkidle')
        await page.evaluate('(theme) => document.documentElement.dataset.theme=theme',theme)
        await page.evaluate('document.fonts.ready')
        titles=await page.locator('.paper-card h3').evaluate_all('(els) => els.slice(0,3).map(el => el.getBoundingClientRect().bottom)')
        assert await page.locator('.paper-card').first.evaluate('el => el.getBoundingClientRect().top')<=420
        assert len(titles)==3 and max(titles)<=900,titles
        assert await page.locator('#desktop-resource-filters .resource-filters').count()==1
        assert await page.locator('#benchmark-entry a').count()==3
        assert await page.locator('#benchmark-entry button').count()==0
        assert await page.locator('[data-tag="all"]').get_attribute('aria-pressed')=='true'
        assert await page.locator('[data-tag="all"]').evaluate("el => getComputedStyle(el).backgroundColor!=='rgba(0, 0, 0, 0)'")
        for card in await page.locator('.paper-card').all():
            kinds=await card.locator('.paper-actions a').evaluate_all('els => els.map(el => el.dataset.resource)')
            assert len(kinds)<=3,kinds
            assert kinds==sorted(kinds,key=lambda kind:{'paper':0,'code':1,'project':2}.get(kind,3)),kinds
            if 'code' in kinds and 'project' in kinds:
                assert kinds.index('code')<kinds.index('project'),kinds
        await page.screenshot(path=str(out/f'polish-{theme}-papers-1440.png'))
        await page.goto(LIBRARY+'?path=render',wait_until='networkidle')
        assert 'From code to pixels' in await page.locator('#result-context').inner_text()
        assert await page.locator('#result-context a').get_attribute('href')=='index.html#reading'
        await page.locator('#result-context a').click()
        await page.wait_for_url('**/index.html#reading')
        await page.goto(BASE+'/',wait_until='networkidle')
        await page.evaluate('(theme) => document.documentElement.dataset.theme=theme',theme)
        await page.evaluate('document.fonts.ready')
        bottoms=await page.locator('.updates-layout > section').evaluate_all('(els) => els.map(el => el.lastElementChild.getBoundingClientRect().bottom)')
        assert abs(bottoms[0]-bottoms[1])<=60,bottoms
        await page.locator('.collection-updates').scroll_into_view_if_needed()
        await page.screenshot(path=str(out/f'polish-{theme}-home-updates-1440.png'))
        for width in [320,390,640,768]:
            await page.set_viewport_size({'width':width,'height':844})
            await page.goto(LIBRARY+'?track=generation&tag=available',wait_until='networkidle')
            await page.evaluate('(theme) => document.documentElement.dataset.theme=theme',theme)
            assert await page.locator('#filter-label').inner_text()=='Filters · 2'
            assert not await page.locator('#research-filters').is_visible()
            if width<=640:
                assert await page.locator('.header').evaluate('el => el.getBoundingClientRect().height')==64
                assert not await page.locator('.header .source-link').is_visible()
                assert await page.locator('h1').evaluate('el => el.getBoundingClientRect().top')>=64
            await page.locator('#mobile-filters').focus()
            await page.keyboard.press('Enter')
            assert await page.locator('#research-filters').is_visible()
            assert await page.locator('#mobile-resource-filters .resource-filters').count()==1
            await page.locator('[data-tag="classic"]').click()
            assert await page.locator('#filter-label').inner_text()=='Filters · 2'
            await page.locator('#clear').click()
            assert await page.locator('#filter-label').inner_text()=='Filters'
            await page.locator('#mobile-filters').click()
            await page.locator('#sort').select_option('title')
            await page.locator('[data-view="timeline"]').click()
            assert await page.locator('#filter-label').inner_text()=='Filters'
            await page.evaluate("document.querySelector('#library').scrollIntoView({behavior:'instant'})")
            assert await page.locator('h1').evaluate('el => el.getBoundingClientRect().top')>=64
            assert await page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            await page.screenshot(path=str(out/f'polish-{theme}-papers-{width}.png'))
    await context.close()

    touch=await browser.new_context(has_touch=True,is_mobile=True,viewport={'width':390,'height':844})
    page=await touch.new_page()
    await page.goto(LIBRARY,wait_until='networkidle')
    assert not await page.evaluate("matchMedia('(hover:hover)').matches")
    await page.locator('[data-view="benchmarks"]').tap()
    await page.locator('[data-view="list"]').tap()
    assert await page.locator('[data-view="benchmarks"]').get_attribute('aria-pressed')=='false'
    await expect(page.locator('[data-view="benchmarks"]')).to_have_css('background-color','rgba(0, 0, 0, 0)')
    await touch.close()


async def check_research_navigation(page, records, taxonomy, out):
    sidebar=page.locator('#research-filters')
    month_filter=page.locator('#month')
    assert await month_filter.locator('xpath=..').get_attribute('class')=='quick-filter'
    assert await month_filter.get_attribute('aria-label')=='Filter by published month'
    await month_filter.select_option('2026-10')
    assert '2026-10' in await page.locator('#active-filters').inner_text()
    await page.locator('#clear').click()
    assert await month_filter.input_value()=='all'
    all_research=sidebar.locator('[data-category="all"]')
    assert await sidebar.locator('.category-button').first.get_attribute('data-category')=='all'
    assert await all_research.count()==1
    assert await all_research.get_attribute('aria-pressed')=='true'
    assert await page.locator('#research-total').inner_text()==str(len(records))
    assert 'Other filters' not in await page.locator('#category-status').inner_text()
    for track in taxonomy['tracks']:
        button=sidebar.locator(f'[data-track="{track["id"]}"]')
        await button.click()
        assert await page.locator('.paper-card').count()==sum(p['track']==track['id'] for p in records)
        assert await button.get_attribute('aria-pressed')=='true'
        assert await all_research.get_attribute('aria-pressed')=='false'
        assert await sidebar.locator('.category-button[aria-pressed="true"]').count()==1
    for category in taxonomy['categories']:
        button=sidebar.locator(f'[data-category="{category["id"]}"]')
        expected=sum(p['category']==category['id'] or category['id'] in p['cross_categories'] for p in records)
        assert await button.locator('span').last.inner_text()==str(expected)
        await button.click()
        assert await page.locator('.paper-card').count()==expected
        assert await sidebar.locator('.category-button[aria-pressed="true"]').count()==1

    # All research resets direction/category/path, while independent filters remain.
    query='?q=physics&track=generation&month=2026-10&tag=available&scope=core&interaction=offline&sort=title'
    await page.goto(LIBRARY+query.replace('&track=generation',''),wait_until='networkidle')
    expected_ids=await page.locator('.paper-card').evaluate_all('(els) => els.map(el => el.dataset.paper)')
    assert expected_ids
    await page.goto(LIBRARY+query+'&path=render',wait_until='networkidle')
    await all_research.focus()
    assert await all_research.evaluate('(el) => getComputedStyle(el).outlineStyle')=='solid'
    await page.keyboard.press('Enter')
    params=parse_qs(urlsplit(page.url).query)
    assert params=={'q':['physics'],'month':['2026-10'],'tag':['available'],'scope':['core'],'interaction':['offline'],'sort':['title']}
    assert 'Other filters also apply' in await page.locator('#category-status').inner_text()
    assert await page.locator('.paper-card').evaluate_all('(els) => els.map(el => el.dataset.paper)')==expected_ids
    await page.reload(wait_until='networkidle')
    assert await all_research.get_attribute('aria-pressed')=='true'
    assert 'Other filters also apply' in await page.locator('#category-status').inner_text()
    await page.locator('#clear').click()
    assert await page.locator('.paper-card').count()==len(records)

    await sidebar.locator('[data-collection="d_streaming"]').click()
    await sidebar.locator('[data-track="generation"]').click()
    await all_research.click()
    assert parse_qs(urlsplit(page.url).query)=={'collection':['d_streaming']}
    assert await sidebar.locator('[data-collection="d_streaming"]').get_attribute('aria-pressed')=='true'
    assert 'Other filters also apply' in await page.locator('#category-status').inner_text()

    await page.goto(LIBRARY,wait_until='networkidle')
    await page.goto(LIBRARY+'?track=generation',wait_until='networkidle')
    await page.go_back(wait_until='networkidle')
    assert await all_research.get_attribute('aria-pressed')=='true'
    await page.go_forward(wait_until='networkidle')
    assert await sidebar.locator('[data-track="generation"]').get_attribute('aria-pressed')=='true'
    # Exercise the popstate listener without a document reload.
    await page.evaluate("history.pushState(null,'','?category=g_simulation');dispatchEvent(new PopStateEvent('popstate'))")
    assert await sidebar.locator('[data-category="g_simulation"]').get_attribute('aria-pressed')=='true'
    await page.go_back()
    assert await sidebar.locator('[data-track="generation"]').get_attribute('aria-pressed')=='true'
    await page.locator('#clear').click()

    for width in [1440,1024,768,390]:
        await page.set_viewport_size({'width':width,'height':1000})
        if width<=800:
            assert not await sidebar.is_visible()
            await page.locator('#mobile-filters').click()
            assert await sidebar.is_visible()
            assert await page.locator('.library-options').get_attribute('open') is not None
        assert await page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        assert await sidebar.locator('.category-button').evaluate_all('(els) => els.every(el => el.getBoundingClientRect().height >= 44)')
        assert await sidebar.locator('.category-button').evaluate_all('''(els) => els.every(el => {
            const name=el.firstElementChild.getBoundingClientRect(), count=el.lastElementChild.getBoundingClientRect();
            return name.right<=count.left && count.right<=el.getBoundingClientRect().right;
        })''')
        await page.evaluate("document.querySelector('#library').scrollIntoView({behavior:'instant'})")
        await page.mouse.move(0,0)
        await page.screenshot(path=str(out/f'navigation-{width}.png'))
        if width==1440:
            await page.locator('#categories').screenshot(path=str(out/'navigation-directions.png'))
        if width<=800:
            await page.locator('#mobile-filters').click()
    await page.set_viewport_size({'width':1440,'height':1100})


async def main():
    results=[];errors=[]
    records=json.loads((ROOT/'data/papers.json').read_text())['papers']
    count=len(records)
    taxonomy=json.loads((ROOT/'data/taxonomy.json').read_text())
    news=json.loads((ROOT/'data/updates.json').read_text())['news']
    async with async_playwright() as pw:
        options={'headless':True,'args':['--no-sandbox','--disable-dev-shm-usage']}
        if os.environ.get('CWM_BROWSER_PATH'):options['executable_path']=os.environ['CWM_BROWSER_PATH']
        browser=await pw.chromium.launch(**options)
        page=await browser.new_page(viewport={'width':1440,'height':1100},device_scale_factor=1)
        await page.emulate_media(reduced_motion='reduce')
        page.on('pageerror',lambda e:errors.append(str(e)))
        out=ROOT/'test-results';out.mkdir(exist_ok=True)
        await check_main_navigation(browser,out)
        results.append('统一主导航、Repository guide → Contribute 往返、辅助文档面包屑及仓库配置不覆盖本地链接')
        await check_layout_polish(browser,out)
        results.append('1440×900 三张标题首屏、集合文字链接、首页两栏平衡、统一筛选计数与触屏视图状态')
        await check_themes(browser,out)
        await check_visual_enhancements(browser,out)
        results.append('字体预加载、图文不遮挡、吸顶 header、目录锚点、SVG 徽标、计数和动画降级')
        results.append('系统深浅主题、手动切换与持久化、跨页面与跨标签同步、自托管字体、键盘操作及五种屏宽')
        await check_file_document_themes(pw,out)
        results.append('file:// Chrome/Edge/Firefox 主题导航、文档当前页、绕过缓存刷新、390px 锚点与详情关闭（已安装浏览器）')
        await check_deep_links(page)
        results.append('390px 直接与旧版 benchmark 锚点展开、hashchange 定位及详情关闭清除 paper 参数')
        await check_home_navigation(page,records,taxonomy,news,out)
        results.append('首页与论文库独立、双向导航、方向/路径/详情跳转及旧链接兼容')
        await page.goto(LIBRARY,wait_until='networkidle')
        await page.wait_for_selector('.paper-card')
        assert await page.locator('.paper-card').count()==count
        await page.screenshot(path=str(out/'papers-1440.png'))
        results.append(f'首屏完整加载 {count} 条记录')
        await check_research_navigation(page,records,taxonomy,out)
        results.append('分类导航层级、方向与子类计数、组合筛选、URL 恢复、键盘操作及四种屏幕宽度')
        await page.screenshot(path=str(out/'desktop.png'))
        await page.locator('#library').scroll_into_view_if_needed()
        await page.evaluate("document.querySelector('#library').scrollIntoView({behavior:'instant'})")
        await page.screenshot(path=str(out/'desktop-library.png'))
        for tag in ['classic','available','not_found']:
            await page.locator(f'[data-tag="{tag}"]').click()
            expected=sum(p['classic'] if tag=='classic' else p['resource_status']['status']==tag for p in records)
            assert await page.locator('.paper-card').count()==expected
        await page.locator('#clear').click()
        results.append('新闻、近期论文和三种徽标筛选')
        await page.locator('[data-view="categories"]').click()
        assert await page.locator('.category-block').count()==len(taxonomy['categories'])
        assert await page.locator('.category-entry').first.get_attribute('data-category-paper')=='code-world-model'
        await page.screenshot(path=str(out/'categories.png'))
        await page.locator('#clear').click()
        results.append('分类逐篇排列、交叉列出和代表作置顶')
        await page.locator('#benchmark-entry a[href*="collection=benchmarks"]').click()
        assert await page.locator('[data-benchmark]').count()==sum(len(p['benchmarks']) for p in records)
        for ident in ['4dcodebench','bvb','blenderworld','video2world']:
            assert await page.locator(f'[data-benchmark="{ident}"]').count()==1
        await page.reload(wait_until='networkidle')
        assert await page.locator('[data-benchmark]').count()==sum(len(p['benchmarks']) for p in records)
        await page.locator('#paper-list [data-detail="code4scene"]').click()
        assert 'different releases' in await page.locator('.detail-benchmarks').inner_text()
        await page.keyboard.press('Escape')
        await page.screenshot(path=str(out/'benchmark-atlas.png'))
        await page.locator('[data-collection="b_reconstruction"]').click()
        assert await page.locator('[data-benchmark]').count()==sum(len(p['benchmarks']) for p in records if 'b_reconstruction' in p['collections'])
        await page.locator('#clear').click()
        await page.locator('#search').fill('SimCode4D')
        assert await page.locator('.paper-card').count()==1
        assert await page.locator('.paper-card').first.get_attribute('data-paper')=='code2worlds-2'
        await page.locator('#benchmark-entry a[href*="collection=d_corpora"]').click()
        assert await page.locator('[data-paper="3dcodeverse"]').count()==1
        await page.locator('#benchmark-entry a[href*="collection=d_streaming"]').click()
        for ident in ['worldstream','streamrender-h3','h3-streaming-vae']:
            assert await page.locator(f'[data-paper="{ident}"]').count()==1
        await page.locator('#clear').click()
        results.append('基准入口、具名协议检索、URL 恢复、版本差异及数据／流式组件索引')
        await page.locator('#search').fill('VideoCoCo: Code-as-CoT')
        assert await page.locator('.paper-card').count()==1
        await page.reload(wait_until='networkidle')
        assert await page.locator('.paper-card').count()==1
        results.append('搜索与 URL 刷新恢复')
        await page.locator('#clear').click()
        await page.locator('[data-category="u_verification"]').click()
        assert await page.locator('[data-paper="worldsolver"]').count()==1
        results.append('交叉类别索引')
        await page.locator('#clear').click()
        await page.locator('#scope').select_option('foundation')
        assert await page.locator('.paper-card').count()==sum(p['scope']=='foundation' for p in records)
        await page.locator('#clear').click()
        await page.locator('.facet-group:has(#dimension-filters) > summary').click()
        await page.locator('#code_role').select_option('target')
        assert await page.locator('.paper-card').count()==sum('target' in p['dimensions']['code_role'] for p in records)
        await page.locator('#clear').click()
        await page.locator('#delivery').select_option('streaming')
        await page.locator('#interaction').select_option('none')
        assert await page.locator('.paper-card').count()==1
        assert await page.locator('[data-paper="h3-streaming-vae"]').count()==1
        await page.reload(wait_until='networkidle')
        assert await page.locator('[data-paper="h3-streaming-vae"]').count()==1
        await page.locator('#clear').click()
        await page.locator('#code_role').select_option('target')
        await page.locator('#domain').select_option('physical')
        assert await page.locator('.empty-state').count()==1
        await page.locator('[data-reset]').click()
        results.append('组合机制筛选、范围与空状态恢复')
        await page.locator('[data-view="matrix"]').click()
        assert await page.locator('#paper-list tbody tr').count()==count
        await page.locator('[data-view="timeline"]').click()
        assert await page.locator('.timeline-heading').count()>5
        await page.locator('#month').select_option('unknown')
        assert await page.locator('.paper-card').count()==sum(p['published'] is None for p in records)
        results.append('矩阵、时间线和未知日期筛选')
        await page.locator('#clear').click()
        await page.locator('#search').fill('StreamRender-H3')
        await page.locator('[data-detail="streamrender-h3"]').click()
        assert await page.locator('#detail-dialog').is_visible()
        assert '8 GB200' in await page.locator('.detail-note').inner_text()
        assert 'Publication date is unconfirmed' in await page.locator('.provenance').inner_text()
        await page.keyboard.press('Escape')
        assert not await page.locator('#detail-dialog').is_visible()
        results.append('详情、性能语境、来源说明与 Escape 关闭')
        await page.locator('#clear').click()
        for ident in ['code-world-model','solarrenderer','streamrender-h3','matrix-game-4','videococo']:
            await page.locator(f'[data-compare="{ident}"]').click()
        assert '4 / 4' in await page.locator('#compare-count').inner_text()
        await page.locator('#compare-open').click()
        assert await page.locator('#compare-dialog thead th').count()==5
        assert '112 ms' in await page.locator('#compare-content').inner_text()
        await page.keyboard.press('Escape')
        await page.locator('#compare-clear').click()
        results.append('四篇对比上限与测量语境对照')
        await page.goto(LIBRARY+'?path=render',wait_until='networkidle')
        assert await page.locator('.paper-card').count()==len(next(p['papers'] for p in taxonomy['reading_paths'] if p['id']=='render'))
        assert await page.locator('.paper-card').first.get_attribute('data-paper')=='videococo'
        results.append('阅读路径顺序')
        await page.locator('#clear').click()
        await page.locator('#search').fill('zzzz-no-match')
        assert await page.locator('.empty-state').count()==1
        await page.locator('#clear').click()
        await page.set_viewport_size({'width':390,'height':844})
        await page.evaluate("document.querySelector('#toast').hidden=true;scrollTo({top:0,behavior:'instant'})")
        assert await page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        await page.screenshot(path=str(out/'mobile.png'))
        assert not await page.locator('#research-filters').is_visible()
        await page.locator('#mobile-filters').click()
        assert await page.locator('#research-filters').is_visible()
        await page.locator('#mobile-filters').click()
        await page.evaluate("document.querySelector('#library').scrollIntoView({behavior:'instant'})")
        await page.screenshot(path=str(out/'mobile-library.png'))
        await page.locator('.library-options > summary').click()
        await page.locator('#benchmark-entry a[href*="collection=benchmarks"]').click()
        assert await page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        await page.screenshot(path=str(out/'benchmark-mobile.png'))
        results.append('390 px 移动端无水平溢出')
        await page.goto((ROOT/'site/index.html').as_uri(),wait_until='load')
        assert await page.locator('.hero').is_visible()
        await page.locator('nav[aria-label="Main navigation"] a[href="papers.html"]').click()
        await expect(page.locator('.paper-card')).to_have_count(count)
        await page.locator('.library-options > summary').click()
        await page.locator('#benchmark-entry a[href*="collection=benchmarks"]').click()
        await expect(page.locator('[data-benchmark="bvb"]')).to_have_count(1)
        await page.goto((ROOT/'site/index.html').as_uri()+'?track=generation',wait_until='load')
        await page.wait_for_url('**/papers.html?track=generation')
        await expect(page.locator('.paper-card')).to_have_count(sum(p['track']=='generation' for p in records))
        await page.get_by_role('navigation',name='Main navigation').get_by_role('link',name='Home',exact=True).click()
        assert await page.locator('.hero').is_visible()
        results.append('file:// 离线直接打开')
        await page.goto(BASE+'/benchmarks.html',wait_until='networkidle')
        assert await page.get_by_role('link',name='← Research library').get_attribute('href')=='papers.html'
        assert await page.locator('td').filter(has_text='SimCode4D').count()==1
        assert await page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        await page.goto(BASE+'/readme.html',wait_until='networkidle')
        assert await page.locator('h2').filter(has_text='News & Updates').count()==1
        assert await page.locator('h2').filter(has_text='Recent Paper Updates').count()==1
        assert await page.locator('a[id="g-hybrid"]').count()==1
        assert await page.locator('.prose > p > strong > a[href="https://arxiv.org/abs/2608.25927"]').count()>=1
        assert await page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        assert await page.locator('.prose details').count()==3
        for details in await page.locator('.prose details').all():
            await details.locator('summary').click()
            assert await details.get_attribute('open') is not None
        assert await page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        for details in await page.locator('.prose details').all():
            await details.locator('summary').click()
        for link in await page.locator('.prose a[href^="#"]').all():
            target=await link.get_attribute('href')
            assert await page.locator(target).count()==1, target
        await page.evaluate('scrollTo(0,0)')
        await page.screenshot(path=str(out/'readme-mobile.png'))
        await page.set_viewport_size({'width':1440,'height':1100})
        await page.screenshot(path=str(out/'readme-desktop.png'))
        results.append('README 居中入口、图例、标题、锚点及加粗论文链接')
        assert not errors,errors
        results.append('无浏览器 JavaScript 异常')
        (out/'browser.json').write_text(json.dumps({'checks':results,'errors':errors},ensure_ascii=False,indent=2)+'\n')
        print(json.dumps(results,ensure_ascii=False,indent=2))
        await browser.close()


if __name__=='__main__':asyncio.run(main())
