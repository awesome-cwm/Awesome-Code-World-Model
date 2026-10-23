"""可选真实浏览器验收：需要 playwright 和 Chromium，不属于标准库单元测试。"""
import asyncio
import json
import os
from pathlib import Path
from playwright.async_api import async_playwright

ROOT=Path(__file__).resolve().parents[1]
BASE=os.environ.get('CWM_TEST_URL','http://127.0.0.1:8000')


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
