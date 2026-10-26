"""Visual-affordance regression checks; run with a static server on port 8000.

CWM_BROWSER=msedge selects an installed Edge instead of Playwright Chromium.
Screenshots and machine-readable measurements go to ignored test-results/.
"""
import json
import os
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
BASE = os.environ.get('CWM_TEST_URL', 'http://127.0.0.1:8000').rstrip('/')
OUT = ROOT / 'test-results'
PAPERS = json.loads((ROOT / 'data/papers.json').read_text(encoding='utf-8'))['papers']
TAXONOMY = json.loads((ROOT / 'data/taxonomy.json').read_text(encoding='utf-8'))


def run():
    OUT.mkdir(exist_ok=True)
    measurements = []
    errors = []
    with sync_playwright() as p:
        options = {'channel': os.environ['CWM_BROWSER']} if os.environ.get('CWM_BROWSER') else {}
        browser = p.chromium.launch(**options)
        page = browser.new_page(reduced_motion='reduce')
        page.on('pageerror', lambda error: errors.append(str(error)))

        def check_text():
            small = page.locator('a, button, select, summary, [role="option"]').evaluate_all('''els => els
                .filter(el => el.checkVisibility() && parseFloat(getComputedStyle(el).fontSize) < 14)
                .map(el => ({tag:el.tagName, text:el.textContent, size:getComputedStyle(el).fontSize}))''')
            assert not small, small

        for theme in ['light', 'dark']:
            page.goto(BASE)
            page.evaluate('(theme) => localStorage.setItem("cwm-theme",theme)', theme)
            for width, height in [(1440, 1000), (768, 1024), (375, 812)]:
                page.set_viewport_size({'width': width, 'height': height})
                page.goto(BASE)
                expect(page.locator('.paper-card')).to_have_count(len(PAPERS))
                page.evaluate('document.fonts.ready')
                check_text()
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                expect(page.locator('#filter-count')).to_be_hidden()
                expect(page.locator('#result-count')).to_have_text(f'{len(PAPERS)} papers')
                expect(page.locator('#browse-tags')).to_be_visible()
                expect(page.locator('#browse-tags button')).to_have_count(6)
                expect(page.locator('.tag-group')).to_have_count(2)
                expect(page.locator('#direction-topics')).to_be_hidden()
                assert page.locator('.browse-tags').bounding_box()['height'] <= 120
                resources_box = page.locator('[data-tag-group="resources"]').bounding_box()
                tracks_box = page.locator('[data-tag-group="tracks"]').bounding_box()
                assert resources_box['y'] + resources_box['height'] <= tracks_box['y']
                expect(page.get_by_label('Search papers', exact=True)).to_be_visible()
                expect(page.locator('#command-help')).to_be_visible()
                assert ':' not in page.locator('#search').get_attribute('placeholder')
                expect(page.locator('.search-icon')).to_be_visible()
                expect(page.locator('.quick-row')).to_have_count(0)
                for key in ['classic', 'code']:
                    expect(page.locator(f'[data-command="{key}"]')).to_have_count(1)
                    emoji = page.locator(f'[data-command="{key}"] .filter-emoji')
                    expect(emoji).to_be_visible()
                    expect(emoji).to_have_attribute('aria-hidden', 'true')
                    expect(emoji).to_have_text('\u2b50' if key == 'classic' else '\U0001f4bb')
                commands = page.locator('[data-command]').evaluate_all(
                    'els => els.map(el=>el.dataset.command+":"+el.dataset.value)')
                assert len(commands) == len(set(commands)), commands
                tags_box = page.locator('.browse-tags').bounding_box()
                assert page.locator('.command-toolbar').bounding_box()['y'] < tags_box['y']
                assert tags_box['y'] + tags_box['height'] <= page.locator('.results-toolbar').bounding_box()['y']
                assert page.locator('#syntax-open').evaluate('el => !!el.closest(".command-box")')
                assert not page.get_by_text('THE EXECUTABLE WORLD INDEX', exact=True).count()
                assert not page.get_by_text('COMMIT LOG', exact=True).count()

                cards = page.locator('.paper-card').evaluate_all('''els => els.map(card => ({
                    id:card.dataset.paper,
                    codeStatus:card.querySelector('[data-code-status]').dataset.codeStatus,
                    codeStatusText:card.querySelector('[data-code-status]').textContent.trim(),
                    codeStatusVisible:card.querySelector('[data-code-status]').checkVisibility(),
                    links:[...card.querySelectorAll('.world-resources a')].map(link => ({
                        kind:link.dataset.resource, url:link.getAttribute('href'), text:link.textContent.trim(),
                        height:link.getBoundingClientRect().height, top:link.getBoundingClientRect().top,
                        font:parseFloat(getComputedStyle(link).fontSize),
                        weight:getComputedStyle(link).fontWeight, visible:link.checkVisibility(),
                        border:getComputedStyle(link).borderTopWidth,
                        icon:!!link.querySelector('svg'), bottom:!!link.closest('.world-card-bottom'),
                        background:getComputedStyle(link).backgroundColor,
                        color:getComputedStyle(link).color
                    })),
                    actions:[...card.querySelectorAll('.world-actions button')].map(button => ({
                        height:button.getBoundingClientRect().height, visible:button.checkVisibility(),
                        icon:!!button.querySelector('svg'), label:button.getAttribute('aria-label'),
                        title:button.title, opacity:getComputedStyle(button.parentElement).opacity
                    }))
                }))''')
                for card in cards:
                    paper = next(paper for paper in PAPERS if paper['id'] == card['id'])
                    has_code = any(resource['kind'] == 'code' for resource in paper['resources'])
                    assert card['codeStatus'] == ('available' if has_code else 'not_found')
                    assert card['codeStatusText'] == ('Public code' if has_code else 'No public code found')
                    assert card['codeStatusVisible']
                    resources = [r for kind in ['paper', 'project', 'code']
                                 for r in paper['resources'] if r['kind'] == kind]
                    assert [(link['kind'], link['url']) for link in card['links']] == [
                        (resource['kind'], resource['url']) for resource in resources], card['id']
                    assert len({round(link['top']) for link in card['links']}) <= 1, card
                    for link in card['links']:
                        assert link['text'] == link['kind'].title(), link
                        assert link['height'] == (40 if width <= 520 else 32), link
                        assert link['font'] == 14 and int(link['weight']) >= 600, link
                        assert link['border'] == '1px', link
                        assert link['icon'] and link['bottom'] and link['visible'], link
                        if link['kind'] == 'code':
                            assert link['background'] != 'rgba(0, 0, 0, 0)', link
                            assert link['color'] == 'rgb(255, 255, 255)', link
                    assert len(card['actions']) == 3
                    assert all(action['visible'] and action['icon'] and action['label'] and
                               action['title'] and action['opacity'] == '1' for action in card['actions'])

                switch = page.locator('.view-switch button').evaluate_all('''els => els.map(el => ({
                    top:el.getBoundingClientRect().top, height:el.getBoundingClientRect().height
                }))''')
                assert len({item['top'] for item in switch}) == 1, switch
                assert all(item['height'] == (40 if width <= 520 else 32) for item in switch)
                if width <= 520:
                    short = page.locator('button').evaluate_all('''els => els
                        .filter(el => el.checkVisibility() && el.getBoundingClientRect().height < 40)
                        .map(el => ({text:el.textContent, height:el.getBoundingClientRect().height}))''')
                    assert not short, short
                page.screenshot(path=str(OUT / f'affordances-{theme}-{width}.png'))
                page.locator('#search').fill('SolarRender')
                expect(page.locator('.paper-card')).to_have_count(1)
                expect(page.locator('.paper-card')).to_have_attribute('data-paper', 'solarrenderer')
                page.locator('#search-clear').click()
                expect(page.locator('.paper-card')).to_have_count(len(PAPERS))

                for selector in ['#filter-open', '.generate-chip', '.world-signature button',
                                 '.world-actions button', '.world-resources a']:
                    button = page.locator(selector).first
                    button.hover()
                    assert button.evaluate('''el => getComputedStyle(el).borderTopColor ===
                        getComputedStyle(document.documentElement).getPropertyValue('--green').trim()
                        || (() => {const sample=document.createElement('span');
                            sample.style.color='var(--green)';document.body.append(sample);
                            const match=getComputedStyle(sample).color===getComputedStyle(el).borderTopColor;
                            sample.remove();return match;})()'''), selector
                title = page.locator('.world-heading h3 a').first
                title.hover()
                assert 'underline' in title.evaluate('el => getComputedStyle(el).textDecorationLine')
                page.evaluate('scrollTo(0,0)')

                first_tag = page.locator('.world-signature button').first
                dimension, value = first_tag.get_attribute('data-signature'), first_tag.get_attribute('data-value')
                first_tag.click()
                expect(page.locator('.world-signature button').first).to_have_attribute('aria-pressed', 'true')
                assert f'dim:{dimension}={value}' in page.locator('#search').input_value()
                page.goto(BASE)

                # Selected filters, badge and sort reuse the existing query state.
                for selector in ['.understand-chip', '#browse-tags [data-command="classic"]', '#browse-tags [data-command="code"]']:
                    page.locator(selector).click()
                expect(page.locator('#filter-count')).to_have_text('3')
                expect(page.locator('#browse-tags [data-command="classic"]')).to_have_attribute('aria-pressed', 'true')
                expect(page.locator('#browse-tags [data-command="code"]')).to_have_attribute('aria-pressed', 'true')
                expect(page.locator('#filter-open')).to_have_class('filter-open has-filters')
                expect(page.locator('.understand-chip')).to_have_attribute('aria-pressed', 'true')
                assert page.locator('[data-tag-group="tracks"] button').evaluate_all(
                    'els => new Set(els.map(el=>el.getBoundingClientRect().top)).size === 1')
                assert '2713' in page.locator('.understand-chip').evaluate(
                    'el => getComputedStyle(el,"::after").content.codePointAt(1).toString(16)')
                page.select_option('#result-sort', 'oldest')
                expect(page.locator('#sort')).to_have_value('oldest')
                expect(page.locator('#filter-count')).to_have_text('3')
                page.keyboard.press('Tab')
                page.locator('#syntax-open').focus()
                expect(page.locator('.syntax-tooltip')).to_be_visible()
                assert page.locator('#syntax-open').evaluate('el => getComputedStyle(el).outlineWidth') == '2px'
                page.locator('#syntax-open').click()
                expect(page.locator('#syntax-dialog')).to_be_visible()
                check_text()
                page.keyboard.press('Escape')
                page.locator('#filter-open').click()
                check_text()
                page.locator('#filter-done').click()

                page.goto(BASE + '/?q=code%3Ayes')
                expect(page.locator('.paper-card').first.locator('[data-resource="code"]')).to_be_visible()
                page.screenshot(path=str(OUT / f'affordances-code-{theme}-{width}.png'))
                for view in ['categories', 'benchmarks', 'matrix', 'timeline', 'list']:
                    page.locator(f'[data-view="{view}"]').click()
                    check_text()
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), (width, view)
                page.locator('.world-actions [data-detail]').first.click()
                expect(page.locator('#detail-dialog')).to_be_visible()
                check_text()
                page.keyboard.press('Escape')
                measurements.append({'theme': theme, 'width': width, 'cards': len(cards),
                                     'resource_buttons': sum(len(card['links']) for card in cards)})
        page.set_viewport_size({'width': 1440, 'height': 1000})
        page.goto(BASE)
        tags = page.locator('[data-command]').evaluate_all('''els => els.map(el => ({
            key:el.dataset.command,value:el.dataset.value,label:el.textContent.trim()
        }))''')
        for tag in tags:
            page.goto(BASE)
            if tag['key'] == 'category':
                category = next(c for c in TAXONOMY['categories'] if c['id'] == tag['value'])
                track_value = {'generation': 'generate', 'understanding': 'understand', 'adjacent': 'related'}[category['track']]
                page.locator(f'[data-command="track"][data-value="{track_value}"]').click()
                expect(page.locator('#direction-topics')).to_be_visible()
                visible_categories = page.locator('[data-topic-track]:visible').evaluate_all('els=>els.map(el=>el.dataset.value)')
                assert set(visible_categories) == {c['id'] for c in TAXONOMY['categories'] if c['track'] == category['track']}
                assert page.locator('[data-topic-track]:visible').all_text_contents() == [
                    c['name'] for c in TAXONOMY['categories'] if c['track'] == category['track']]
            button = page.locator(f'[data-command="{tag["key"]}"][data-value="{tag["value"]}"]')
            button.click()
            expect(button).to_have_attribute('aria-pressed', 'true')
            if tag['key'] == 'category':
                expected = [paper for paper in PAPERS if paper['track'] == category['track'] and
                            (paper['category'] == tag['value'] or tag['value'] in paper['cross_categories'])]
            elif tag['key'] == 'track':
                track = {'generate': 'generation', 'understand': 'understanding', 'related': 'adjacent'}.get(tag['value'])
                expected = [paper for paper in PAPERS if not track or paper['track'] == track]
            elif tag['key'] == 'classic':
                expected = [paper for paper in PAPERS if paper['classic']]
            elif tag['key'] == 'code':
                expected = [paper for paper in PAPERS if any(r['kind'] == 'code' for r in paper['resources'])]
            else:
                expected = [paper for paper in PAPERS if tag['value'] in paper['dimensions'][tag['key']]]
            actual = page.locator('.paper-card').evaluate_all('els => els.map(el=>el.dataset.paper)')
            assert set(actual) == {paper['id'] for paper in expected}, tag
            button.click()
            expect(button).to_have_attribute('aria-pressed', str(tag['key'] == 'track' and tag['value'] == 'all').lower())
            if tag['key'] == 'category':
                page.locator('[data-command="track"][data-value="all"]').click()
            expect(page.locator('.paper-card')).to_have_count(len(PAPERS))
        page.locator('.generate-chip').click()
        page.locator('[data-command="category"][data-value="g_scene"]').click()
        page.locator('.understand-chip').click()
        assert 'cat:' not in page.locator('#search').input_value()
        expect(page.locator('[data-topic-track="understanding"]:visible')).to_have_count(4)
        assert not errors, errors
        browser.close()
    (OUT / 'affordance-checks.json').write_text(json.dumps(measurements, indent=2), encoding='utf-8')
    print(f'Affordance checks passed: {len(tags)} track/topic/resource controls, curated hierarchy, filtering and deselection, '
          '14px controls, resource rows, persistent icons, selected states, sort sync, focus ring, '
          'tooltips, five views, light/dark, 1440/768/375px.')


if __name__ == '__main__':
    run()
