"""可选真实浏览器验收：需要 playwright 和 Chromium，不属于标准库单元测试。"""
import asyncio
import json
import os
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
from playwright.async_api import async_playwright

ROOT=Path(__file__).resolve().parents[1]
BASE=os.environ.get('CWM_TEST_URL','http://127.0.0.1:8000')


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
    await page.goto(BASE+'/'+query.replace('&track=generation',''),wait_until='networkidle')
    expected_ids=await page.locator('.paper-card').evaluate_all('(els) => els.map(el => el.dataset.paper)')
    assert expected_ids
    await page.goto(BASE+'/'+query+'&path=render',wait_until='networkidle')
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

    await page.goto(BASE+'/',wait_until='networkidle')
    await page.goto(BASE+'/?track=generation',wait_until='networkidle')
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
            assert await page.locator('#mobile-filters').get_attribute('aria-expanded')=='true'
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
        await page.goto(BASE,wait_until='networkidle')
        await page.wait_for_selector('.paper-card')
        assert await page.locator('.paper-card').count()==count
        results.append(f'首屏完整加载 {count} 条记录')
        out=ROOT/'test-results';out.mkdir(exist_ok=True)
        await check_research_navigation(page,records,taxonomy,out)
        results.append('分类导航层级、方向与子类计数、组合筛选、URL 恢复、键盘操作及四种屏幕宽度')
        await page.screenshot(path=str(out/'desktop.png'))
        await page.locator('#library').scroll_into_view_if_needed()
        await page.evaluate("document.querySelector('#library').scrollIntoView({behavior:'instant'})")
        await page.screenshot(path=str(out/'desktop-library.png'))
        assert await page.locator('#news-list .news-item').count()==len(news)
        assert await page.locator('#recent-updates > p').count()==20
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
        await page.locator('#benchmark-entry [data-collection="benchmarks"]').click()
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
        await page.locator('#benchmark-entry [data-collection="d_corpora"]').click()
        assert await page.locator('[data-paper="3dcodeverse"]').count()==1
        await page.locator('#benchmark-entry [data-collection="d_streaming"]').click()
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
        await page.locator('[data-path="render"]').click()
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
        await page.locator('#benchmark-entry [data-collection="benchmarks"]').click()
        assert await page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        await page.screenshot(path=str(out/'benchmark-mobile.png'))
        results.append('390 px 移动端无水平溢出')
        await page.goto((ROOT/'site/index.html').as_uri(),wait_until='load')
        assert await page.locator('.paper-card').count()==count
        await page.locator('#benchmark-entry [data-collection="benchmarks"]').click()
        assert await page.locator('[data-benchmark="bvb"]').count()==1
        results.append('file:// 离线直接打开')
        await page.goto(BASE+'/benchmarks.html',wait_until='networkidle')
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
