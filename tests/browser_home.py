"""Command-home acceptance tests. Start a static server before running.

python tests/browser_home.py (CWM_BROWSER=msedge uses an installed Edge)
"""
import json
import os
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
BASE = os.environ.get('CWM_TEST_URL', 'http://127.0.0.1:8000').rstrip('/')
OUT = ROOT / 'test-results'
PAPERS = json.loads((ROOT / 'data/papers.json').read_text(encoding='utf-8'))['papers']
TAXONOMY = json.loads((ROOT / 'data/taxonomy.json').read_text(encoding='utf-8'))


def contrast(a, b):
    def luminance(color):
        color = color.strip().removeprefix('#')
        rgb = [int(color[i:i + 2], 16) / 255 for i in (0, 2, 4)]
        linear = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in rgb]
        return sum(v * w for v, w in zip(linear, [.2126, .7152, .0722]))
    low, high = sorted([luminance(a), luminance(b)])
    return (high + .05) / (low + .05)


def run():
    errors = []
    OUT.mkdir(exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(**({'channel': os.environ['CWM_BROWSER']} if os.environ.get('CWM_BROWSER') else {}))
        context = browser.new_context(viewport={'width': 1440, 'height': 1000}, reduced_motion='reduce', color_scheme='light')
        context.grant_permissions(['clipboard-read', 'clipboard-write'])
        page = context.new_page()
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.goto(BASE)
        expect(page.locator('.paper-card')).to_have_count(len(PAPERS))

        def search(text):
            page.locator('#search').fill(text)
            page.keyboard.press('Enter') if ':' not in text else page.locator('#search').blur()
            expect(page.locator('#search')).to_have_value(text)
            page.wait_for_function('(text) => (new URLSearchParams(location.search).get("q") || "") === text', arg=text.strip())

        def reset():
            search('')
            page.locator('[data-view="list"]').click()
            expect(page.locator('.paper-card')).to_have_count(len(PAPERS))

        for command, expected in [
            ('code:yes', [x for x in PAPERS if any(r['kind'] == 'code' for r in x['resources'])]),
            ('code:no', [x for x in PAPERS if not any(r['kind'] == 'code' for r in x['resources'])]),
            ('classic:yes', [x for x in PAPERS if x['classic']]),
            ('resource:not_found', [x for x in PAPERS if x['resource_status']['status'] == 'not_found']),
            ('resource:available', [x for x in PAPERS if x['resource_status']['status'] == 'available']),
            ('track:understand code:yes classic:yes', [x for x in PAPERS if x['track'] == 'understanding' and x['classic'] and any(r['kind'] == 'code' for r in x['resources'])]),
            ('scope:foundation', [x for x in PAPERS if x['scope'] == 'foundation']),
            ('month:unknown', [x for x in PAPERS if not x['published']]),
            ('collection:benchmarks', [x for x in PAPERS if x['benchmarks']]),
        ]:
            search(command)
            actual = page.locator('.paper-card').evaluate_all('els => els.map(el => el.dataset.paper)')
            assert set(actual) == {x['id'] for x in expected}, command

        for d in TAXONOMY['dimensions']:
            value = next(iter(d['values']))
            search(f'dim:{d["id"]}={value}')
            actual = page.locator('.paper-card').evaluate_all('els => els.map(el => el.dataset.paper)')
            assert set(actual) == {x['id'] for x in PAPERS if value in x['dimensions'][d['id']]}
        for c in TAXONOMY['categories']:
            search(f'cat:{c["id"]}')
            actual = page.locator('.paper-card').evaluate_all('els => els.map(el => el.dataset.paper)')
            assert set(actual) == {x['id'] for x in PAPERS if x['category'] == c['id'] or c['id'] in x['cross_categories']}

        reset()
        page.keyboard.press('/')
        expect(page.locator('#search')).to_be_focused()
        page.locator('#search').fill('track:')
        expect(page.locator('#completions')).to_be_visible()
        page.keyboard.press('ArrowDown')
        page.keyboard.press('Enter')
        expect(page.locator('#search')).to_have_value('track:understand ')
        expect(page.locator('.understand-chip')).to_have_attribute('aria-pressed', 'true')
        page.keyboard.press('Escape')
        expect(page.locator('.paper-card')).to_have_count(len(PAPERS))
        page.locator('#search').fill('code:')
        page.keyboard.press('Tab')
        expect(page.locator('#search')).to_have_value('code:yes ')
        page.keyboard.press('Escape')
        page.locator('.generate-chip').click()
        expect(page.locator('#search')).to_have_value('track:generate')
        page.locator('.understand-chip').click()
        expect(page.locator('#search')).to_have_value('track:understand')
        page.go_back()
        expect(page.locator('#search')).to_have_value('track:generate')
        page.go_forward()
        expect(page.locator('#search')).to_have_value('track:understand')
        page.reload()
        expect(page.locator('.understand-chip')).to_have_attribute('aria-pressed', 'true')

        reset()
        page.locator('.world-signature [data-signature]').first.click()
        assert 'dim:representation=' in page.locator('#search').input_value()
        reset()
        for sort in ['oldest', 'newest', 'title']:
            search('sort:' + sort)
            actual = page.locator('.paper-card').evaluate_all('els => els.map(el => el.dataset.paper)')
            records = [next(x for x in PAPERS if x['id'] == identifier) for identifier in actual]
            if sort != 'title':
                dates = [x['published'] for x in records if x['published']]
                assert dates == sorted(dates, reverse=sort == 'newest')
                assert records[-1]['published'] is None
            else:
                assert page.evaluate('''() => {const titles=[...document.querySelectorAll('.world-heading h3 a')].map(x=>x.textContent); return titles.every((x,i)=>i===0||titles[i-1].localeCompare(x)<=0)}''')

        reset()
        for view in ['categories', 'benchmarks', 'matrix', 'timeline', 'list']:
            page.locator(f'[data-view="{view}"]').click()
            expect(page.locator(f'[data-view="{view}"]')).to_have_attribute('aria-pressed', 'true')
            if view == 'categories': assert page.locator('.category-block').count() == len(TAXONOMY['categories'])
            if view == 'benchmarks': assert page.locator('[data-benchmark]').count() == sum(len(x['benchmarks']) for x in PAPERS)
            if view == 'matrix': assert page.locator('tbody tr').count() == len(PAPERS)
            if view == 'timeline': assert page.locator('.timeline-heading').count() > 10
            if view in ['list', 'timeline']: expect(page.locator('.paper-card')).to_have_count(len(PAPERS))
            assert page.locator('#month-nav a').count() > 0
            page.locator('#month-nav a').nth(2).click()
            assert abs(page.locator('.command-toolbar').bounding_box()['y']) < 1
            assert page.locator('#month-nav [aria-current]').count() == 1
            page.evaluate('scrollTo(0,0)')

        first = page.locator('.paper-card').first
        first.hover()
        first.locator('[data-detail]').click()
        expect(page.locator('#detail-dialog')).to_be_visible()
        assert page.locator('#detail-content .dimensions-grid > div').count() == len(TAXONOMY['dimensions'])
        page.locator('#detail-content details summary').click()
        expect(page.locator('#detail-content .abstract')).to_be_visible()
        page.locator('#copy-citation').click()
        expect(page.locator('#toast')).to_have_text('BibTeX copied.')
        assert page.evaluate('navigator.clipboard.readText()').startswith('@misc{')
        page.keyboard.press('Escape')
        expect(page.locator('#detail-dialog')).not_to_be_visible()
        for card in page.locator('.paper-card').all()[:2]:
            card.hover()
            card.locator('[data-compare]').click()
        expect(page.locator('#compare-tray')).to_be_visible()
        page.locator('#compare-open').click()
        expect(page.locator('#compare-dialog')).to_be_visible()
        assert page.locator('#compare-content thead th').count() == 3
        page.keyboard.press('Escape')
        page.locator('#compare-clear').click()
        expect(page.locator('#compare-tray')).not_to_be_visible()

        # Arbitrary text is escaped even in highlights and validation messages.
        search('<img src=x onerror=alert(1)>')
        assert page.locator('#paper-list img').count() == 0
        expect(page.locator('.empty-state')).to_be_visible()
        reset()

        for theme in ['light', 'dark']:
            page.evaluate('theme => localStorage.setItem("cwm-theme",theme)', theme)
            page.reload()
            colors = page.evaluate('''() => Object.fromEntries(['ink','paper','muted','surface','green','blue',
                'on-green','light-green','surface-soft','warning','warning-soft'].map(key =>
                [key,getComputedStyle(document.documentElement).getPropertyValue('--'+key)]))''')
            for a, b in [('ink','paper'),('muted','paper'),('muted','surface'),('green','surface'),
                         ('blue','paper'),('on-green','green'),('green','light-green'),
                         ('muted','surface-soft'),('warning','warning-soft')]:
                assert contrast(colors[a], colors[b]) >= 4.5, (theme, a, b)
            for width, height in [(1440,1000), (768,1024), (375,812)]:
                page.set_viewport_size({'width':width,'height':height})
                page.evaluate('scrollTo(0,0)')
                page.evaluate('document.fonts.ready')
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'), (theme,width)
                assert page.locator('.paper-card').first.bounding_box()['y'] < height - 100
                assert page.locator('.commit-log').is_visible() == (width >= 1100)
                page.screenshot(path=str(OUT / f'command-home-{theme}-{width}.png'))
                page.locator('#filter-open').click()
                expect(page.locator('#filter-dialog')).to_be_visible()
                page.select_option('#scope', 'foundation')
                assert 'scope:foundation' in page.locator('#search').input_value()
                page.screenshot(path=str(OUT / f'command-filters-{theme}-{width}.png'))
                page.locator('#filter-done').click()
                reset()
                for view in ['matrix','benchmarks','categories','timeline','list']:
                    page.locator(f'[data-view="{view}"]').click()
                    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'), (width,view)
                    page.evaluate('scrollTo(0,0)')
            page.set_viewport_size({'width':1440,'height':1000})

        page.keyboard.press('Control+k')
        expect(page.locator('#search')).to_be_focused()
        search('harmony')
        expect(page.locator('[data-paper="harmony"]')).to_be_visible()
        assert page.locator('mark').count() > 0
        page.goto((ROOT / 'site/index.html').as_uri() + '?q=track%3Agenerate%20code%3Ayes')
        assert page.locator('.paper-card').count() > 0
        page.locator('.understand-chip').click()
        assert 'track:understand' in parse_qs(urlsplit(page.url).query)['q'][0]
        page.goto(BASE + '/index.html?paper=harmony')
        expect(page.locator('#detail-dialog')).to_be_visible()
        page.evaluate("Object.defineProperty(navigator, 'clipboard', {value:undefined, configurable:true})")
        page.locator('#copy-citation').click()
        expect(page.locator('#toast')).to_have_text('BibTeX copied.')
        assert page.locator('textarea').count() == 0
        page.keyboard.press('Escape')
        expect(page.locator('#detail-dialog')).not_to_be_visible()
        page.wait_for_function('!new URLSearchParams(location.search).has("paper")')
        page.reload()
        expect(page.locator('#detail-dialog')).not_to_be_visible()
        page.goto(BASE + '/papers.html')
        expect(page.locator('.paper-card')).to_have_count(len(PAPERS))
        page.locator('[data-view="matrix"]').click()
        assert page.locator('tbody tr').count() == len(PAPERS)
        assert not errors, errors
        browser.close()
    print('Command-home checks passed: query grammar, taxonomy filters, five views, history, autocomplete, dialogs, clipboard, compare, themes, file://, 1440/768/375px.')


if __name__ == '__main__':
    run()
