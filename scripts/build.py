#!/usr/bin/env python3
"""校验统一数据源，确定性生成 README、网页数据和导出文件。"""
import argparse
import csv
import html
import io
import json
import re
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]


def validate(catalog, taxonomy):
    categories = {c['id']: c for c in taxonomy['categories']}
    dimensions = {d['id']: d for d in taxonomy['dimensions']}
    collections = {c['id']: c for c in taxonomy['collections']}
    sections = {s['id'] for s in taxonomy['collection_sections']}
    areas = {a['id']: a for a in taxonomy['research_areas']}
    tag_dimensions = {d['id']: d for d in taxonomy['tag_dimensions']}
    assert len(areas) == len(taxonomy['research_areas']), 'Duplicate research area'
    assert len(tag_dimensions) == len(taxonomy['tag_dimensions']), 'Duplicate tag dimension'
    direction_ids, tag_ids = set(), set()
    for area in areas.values():
        assert re.fullmatch(r'[a-z]+(?:-[a-z]+)*', area['id']) and area['name']
        for direction in area['directions']:
            assert re.fullmatch(r'[a-z]+(?:-[a-z]+)*', direction['id']) and direction['name']
            assert direction['id'] not in direction_ids, direction['id']
            direction_ids.add(direction['id'])
    for dimension in tag_dimensions.values():
        assert dimension['name'] and dimension['values']
        for tag, label in dimension['values'].items():
            assert re.fullmatch(r'[a-z]+(?:-[a-z]+)*', tag) and label
            assert tag not in tag_ids, tag
            tag_ids.add(tag)
    assert len(collections) == len(taxonomy['collections'])
    assert all(c['section'] in sections for c in collections.values())
    ids, arxiv_ids, titles = set(), set(), set()
    for p in catalog['papers']:
        assert re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', p['id']), p['id']
        assert p['id'] not in ids, f"重复 id: {p['id']}"
        ids.add(p['id'])
        normalized = re.sub(r'\W+', '', p['title'].casefold())
        assert normalized not in titles, f"重复标题: {p['title']}"
        titles.add(normalized)
        assert categories[p['category']]['track'] == p['track'], p['id']
        assert p['scope'] in taxonomy['scopes']
        classification = p.get('classification')
        assert isinstance(classification, dict) and {'area', 'direction', 'tags', 'basis'} <= set(classification), p['id']
        assert isinstance(classification['area'], str) and classification['area'] in areas, p['id']
        direction = classification['direction']
        assert direction is None or (isinstance(direction, str) and direction in {d['id'] for d in areas[classification['area']]['directions']}), p['id']
        assert isinstance(classification['tags'], dict) and set(classification['tags']) == set(tag_dimensions), p['id']
        total_tags = 0
        for key, values in classification['tags'].items():
            assert isinstance(values, list) and all(isinstance(v, str) for v in values), (p['id'], key)
            assert len(values) == len(set(values)) and set(values) <= set(tag_dimensions[key]['values']), (p['id'], key)
            total_tags += len(values)
        assert total_tags >= 1, f"At least one auxiliary tag is required: {p['id']}"
        assert isinstance(classification['basis'], str) and classification['basis'].strip(), p['id']
        assert p['type'] in {'preprint', 'report', 'project'}
        assert set(p['dimensions']) == set(dimensions), p['id']
        for key, values in p['dimensions'].items():
            assert values and len(values) == len(set(values)), (p['id'], key)
            assert set(values) <= set(dimensions[key]['values']), (p['id'], key)
        assert all(c in categories and c != p['category'] for c in p['cross_categories'])
        assert p['verification']['status'] == 'verified'
        assert p['verification']['basis'] in {'primary_abstract', 'official_project', 'full_text'}
        checked = date.fromisoformat(p['verification']['checked'])
        if p['published']:
            assert date.fromisoformat(p['published']) <= checked
            assert p['date_basis'] != 'unknown'
        else:
            assert p['date_basis'] == 'unknown'
        if p['arxiv']:
            assert re.fullmatch(r'\d{4}\.\d{4,5}', p['arxiv'])
            assert p['arxiv'] not in arxiv_ids, f"重复 arXiv: {p['arxiv']}"
            arxiv_ids.add(p['arxiv'])
            assert p['date_basis'] == 'arxiv_first_submission'
        assert p['summary'].strip() and p['resources']
        assert len(p['collections']) == len(set(p['collections'])), p['id']
        assert set(p['collections']) <= set(collections), p['id']
        indexed = any(collections[c]['section'] == 'benchmarks' for c in p['collections'])
        assert indexed == bool(p['benchmarks']), f"基准协议与索引不匹配: {p['id']}"
        for b in p['benchmarks']:
            assert all(isinstance(b.get(k), str) and b[k].strip() for k in ['name','input','artifact','checks','caveat','source']), p['id']
            assert urlparse(b['source']).scheme == 'https', p['id']
        assert isinstance(p['classic'], bool)
        assert not p['classic'] or p['classic_note'].strip()
        available = {r['url'] for r in p['resources'] if r['kind'] != 'paper'}
        status = p['resource_status']
        assert status['status'] == ('available' if available else 'not_found'), p['id']
        assert set(status['evidence']) == available, p['id']
        date.fromisoformat(status['checked'])
        for r in p['resources']:
            assert r['kind'] in {'paper', 'project', 'code', 'data', 'weights'}
            for url in [r['url'], r['provenance'], p['verification']['source']]:
                parsed = urlparse(url)
                assert parsed.scheme == 'https' and parsed.hostname and not parsed.username, url
    for path in taxonomy['reading_paths']:
        assert set(path['papers']) <= ids, path['id']
    return True


def tex(value):
    mapping = {'\\': r'\textbackslash{}', '{': r'\{', '}': r'\}', '%': r'\%', '&': r'\&', '#': r'\#', '_': r'\_', '$': r'\$'}
    return ''.join(mapping.get(c, c) for c in value)


def bibtex(p):
    fields = [('title', tex(p['title']))]
    if p['authors']:
        fields.append(('author', ' and '.join(tex(a) for a in p['authors'])))
    if p['published']:
        fields.append(('year', p['published'][:4]))
    if p['arxiv']:
        fields.extend([('eprint', p['arxiv']), ('archivePrefix', 'arXiv')])
    resource = next((r for r in p['resources'] if r['kind'] == 'paper'), p['resources'][0])
    fields.append(('url', tex(resource['url'])))
    return '@misc{' + p['id'].replace('-', '') + ',\n' + ',\n'.join('  '+k+' = {'+v+'}' for k, v in fields) + '\n}'


def md(value):
    return value.replace('|', '\\|').replace('\n', ' ')


def category_entries(papers, category_id):
    """参考清单式顺序：代表作置顶，其余按首次提交日期倒序；包含交叉分类。"""
    selected = [p for p in papers if p['category'] == category_id or category_id in p['cross_categories']]
    return sorted(selected, key=lambda p:(p['classic'], p['published'] or '', p['id']), reverse=True)


def collection_entries(papers, collection_id):
    return sorted([p for p in papers if collection_id in p['collections']],
                  key=lambda p:(p['classic'], p['published'] or '', p['id']), reverse=True)


def research_entries(papers, area_id):
    """Each paper appears in exactly one primary research-area section."""
    return sorted([p for p in papers if p['classification']['area'] == area_id],
                  key=lambda p:(p['classic'], p['published'] or '', p['id']), reverse=True)


def render_benchmarks(catalog, taxonomy):
    parts = ['# Benchmark Atlas / 基准索引\n',
             '基准按任务、提交产物、评分证据与适用边界比较。任务设定与评测对象不同，分数不能跨基准直接排名。同一论文的配套 benchmark 作为具名协议索引，不重复计为新论文。\n']
    for group in taxonomy['collections']:
        if group['section'] != 'benchmarks': continue
        parts += [f"## {group['name']}\n", group['question']+'\n',
                  '| Benchmark / Paper | Input | Submitted artifact | Evaluation evidence | Boundary / version |',
                  '| --- | --- | --- | --- | --- |']
        for p in collection_entries(catalog['papers'],group['id']):
            for b in p['benchmarks']:
                parts.append('| '+ ' | '.join([f"[{md(b['name'])}]({b['source']})"]+[md(b[k]) for k in ['input','artifact','checks','caveat']])+' |')
        parts.append('')
    parts += ['## 阅读建议\n',
        'BVB → 4DCodeBench → PhysCodeGym → Video2World：依次关注时空事实、动态几何、物理机制与干预、具身任务。这个顺序是阅读路线，不是作者之间的继承关系。\n',
        'BlenderGym → 3DCodeBench → BlenderWorld / Code4Scene：从受约束的目标匹配，走向程序化资产、开放创作和原生场景状态检查。3DCodeVerse 在这条线上提供数据与 harness；使用 3DCodeBench 评测不等于二者是同一 benchmark。\n',
        'WorldSolver 与 GPUPhysBench 关注求解器实现；PhySimCode 还要求从视频识别规律和参数；ExeWorldBench 关注机制组合能否实际运行。\n',
        'Code4Scene 的 arXiv 论文与仓库 README 当前描述不同版本，表内分别保留。PhySimCode 的完整生成语料规模和公开评测子集规模也分别记录。每项来源链接与核验日期保存在统一文献数据中。\n']
    return '\n'.join(parts)


def readme_entry(p, recent=False):
    stamp = (p['published'] if recent else p['published'][:7]) if p['published'] else 'Date TBC'
    availability = '✅' if p['resource_status']['status'] == 'available' else '❌️'
    primary = next((r['url'] for r in p['resources'] if r['kind'] == 'paper'), p['verification']['source'])
    title = p['title'].replace('[', r'\[').replace(']', r'\]')
    if recent:
        return f'[{stamp}] {availability}[{title}]({primary})'
    star = f"🌟({p['classic_note']}) " if p['classic'] else ''
    line = f'[{stamp}] {availability}{star}[{title}]({primary})'
    extras = [f"[{r['kind'].title()}]({r['url']})" for r in p['resources'] if r['kind'] != 'paper' and r['url'] != primary]
    if extras:
        line += ' · ' + ' · '.join(extras)
    return f'**{line}**' if p['classic'] else line


def render_readme(catalog, taxonomy, repository):
    papers = catalog['papers']
    news = json.loads((ROOT / 'data/updates.json').read_text())['news']
    if repository:
        owner, repo = repository.split('/')
        site_url = f'https://{owner}.github.io/{repo}/'
    else:
        settings_path = ROOT / 'data/site.json'
        settings = json.loads(settings_path.read_text()) if settings_path.exists() else {}
        site_url = settings.get('preview_url') or 'site/index.html'
        assert site_url == 'site/index.html' or (urlparse(site_url).scheme == 'https' and urlparse(site_url).hostname and not urlparse(site_url).username)
    intro = (ROOT / 'docs/README.template.md').read_text().replace('{{SITE_URL}}', site_url)
    benchmarks = sum(len(p['benchmarks']) for p in papers)
    intro = intro.replace('{{STATS}}', f"**{len(papers)} unique papers / projects · {benchmarks} named benchmark suites · {len(taxonomy['research_areas'])} research areas · {len(taxonomy['tag_dimensions'])} auxiliary tag dimensions** · Sources checked **{catalog['curated_at']}**.")
    intro = intro.replace('{{NEWS}}', '\n\n'.join(f"{n['icon']} **[{n['date']}] {n['title']}** — {n['body']}" for n in news))
    parts = [intro, '\n---\n\n<a id="recent-paper-updates"></a>\n## 🔥 Recent Paper Updates\n']
    recent = sorted([p for p in papers if p['published']], key=lambda p:(p['published'],p['id']), reverse=True)[:20]
    parts.extend(readme_entry(p, recent=True)+'\n' for p in recent)
    parts.append('**Also tracked — official projects with unconfirmed first-release dates:**\n')
    parts.extend(readme_entry(p, recent=True)+'\n' for p in papers if not p['published'])
    parts.append('\n---\n\n## Overview\n')
    parts.extend(['- 🚩 [News & Updates](#news-updates)', '- 🔥 [Recent Paper Updates](#recent-paper-updates)'])
    parts.extend(f"- [{area['name']}](#{area['id']})" for area in taxonomy['research_areas'])
    parts.extend(['- 📊 [Benchmark Atlas](#benchmarks)', '- 🛠️ [Reusable resources](#infrastructure)', '- 🧭 [Taxonomy & reading guide](#reading-guide)', '- 📝 [Citation](#citation)'])
    parts.append('\n**World Models Taxonomy V2:** each paper has exactly one primary research area and one or more auxiliary tags. A direction refines the primary area when applicable. The six area sections below do not cross-list papers. Recent updates and reading paths are separate navigation aids.\n')
    for area in taxonomy['research_areas']:
        parts.append(f"\n---\n\n<a id=\"{area['id']}\"></a>\n## {area['name']}\n")
        parts.append('**Directions:** '+' · '.join(d['name'] for d in area['directions'])+'\n')
        direction_names = {d['id']:d['name'] for d in area['directions']}
        for p in research_entries(papers, area['id']):
            direction = p['classification']['direction']
            suffix = ' · **'+direction_names[direction]+'**' if direction else ''
            parts.append(readme_entry(p)+suffix+'\n')
    parts.append('\n---\n\n<a id="benchmarks"></a>\n## 📊 Benchmarks & Evaluation\n')
    parts.append('[Benchmark Atlas: inputs → artifacts → evaluation evidence](docs/BENCHMARKS.md). Named suites within method papers remain associated with their original paper; they do not create additional primary classifications.\n')
    parts.append('**Named suites:** '+' · '.join(b['name'] for p in papers for b in p['benchmarks'])+'\n')
    parts.append('\n<a id="infrastructure"></a>\n## 🛠️ Datasets, Harnesses & Streaming Systems\n')
    for group in taxonomy['collections']:
        if group['section'] == 'infrastructure':
            parts.append(f"- **{group['name']}**: {group['question']}")
    parts.append('''
---

<a id="reading-guide"></a>
## 🧭 Taxonomy & Reading Guide

Select **one research area** and optionally a direction, then combine **one or more auxiliary tags** across Research Challenges, Memory & State, Control & Interaction, Representation & Output, Methods & Training, Runtime & Efficiency, World Setting & Domain, and Evaluation Focus. Tag filters use an intersection and can be combined with publication month, title/author search, and resource badges.

The initial V2 assignments migrate the existing curated metadata and editorial summaries; they are not a new full-text review or a certification of reported capabilities. [Taxonomy / 中文分类说明](docs/TAXONOMY.md).
''')
    by_id = {p['id']:p for p in papers}
    for path in taxonomy['reading_paths']:
        links = [f"[{by_id[i]['short_title']}]({by_id[i]['verification']['source']})" for i in path['papers']]
        parts.append(f"- **{path['title']}**: "+' → '.join(links))
    parts.append('''
<a id="citation"></a>
## 📝 Citation

Please cite the original papers. Download [all BibTeX entries](site/papers.bib) and use the entries for the papers you reference.

## Contributing & Maintenance

See [CONTRIBUTING.md](CONTRIBUTING.md) to suggest a paper or correction. [Research notes](docs/RESEARCH.md) document source checks and title disambiguation.

`data/papers.json` is the single source of truth; `data/taxonomy.json` defines V2 research areas, directions, and auxiliary tags; `data/updates.json` records collection news. The README, website data, and exports are generated together.

```bash
python3 scripts/build.py
python3 -m unittest discover -s tests -v
python3 -m http.server 8000 --directory site
```

Open `http://localhost:8000`, or open `site/index.html` directly. [GitHub Pages deployment](docs/DEPLOYMENT.md) · [Daily discovery prototype / developer handoff](docs/CRAWLER_HANDOFF.md) · [JSON](data/papers.json) · [CSV](site/papers.csv).

The daily discovery prototype proposes candidates for review. It does not silently promote papers into the curated list.

## Acknowledgments & License

The simple paper-list layout is inspired by [EasonTuT/Awesome-Interactive-World-Model](https://github.com/EasonTuT/Awesome-Interactive-World-Model); compound paper indexing also draws inspiration from [Awesome 3D Gaussian Splatting](https://mrnerf.github.io/awesome-3D-gaussian-splatting/). The World Models Taxonomy V2 follows the maintainer-provided research-area and tag-dimension specification. Our metadata, editorial notes, and implementation are maintained independently.

Repository code and original editorial content: [MIT](LICENSE). Paper titles, abstracts, and external resources remain attributable to their respective authors and providers.
''')
    readme = '\n'.join(parts).strip()+'\n'
    return re.sub(r'(<a id="[a-z0-9-]+"></a>)\n(?=#)', r'\1\n\n', readme)



def web_link(url):
    links={'docs/TAXONOMY.md':'taxonomy.html','docs/RESEARCH.md':'research.html','CONTRIBUTING.md':'contributing.html',
           'docs/DEPLOYMENT.md':'deployment.html','docs/CRAWLER_HANDOFF.md':'crawler.html','docs/AGENT_REVIEW_PROMPT.md':'agent-review.html',
           'docs/BENCHMARKS.md':'benchmarks.html','BENCHMARKS.md':'benchmarks.html','site/index.html':'./','data/papers.json':'papers.json','site/papers.bib':'papers.bib','site/papers.csv':'papers.csv','LICENSE':'LICENSE'}
    return links.get(url, url[5:] if url.startswith('site/') else url)


class SafeReadmeHTML(HTMLParser):
    """允许 GitHub README 的排版标签，丢弃事件属性和不安全 URL。"""
    allowed={'div','h1','h2','h3','p','b','strong','a','img','br','table','tbody','tr','td'}
    attributes={'align','width','height','border','cellspacing','cellpadding','alt','id'}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts=[]

    def handle_starttag(self,tag,attrs):
        if tag not in self.allowed:return
        safe=[]
        for key,value in attrs:
            if value is None:continue
            if key in {'href','src'} and urllib_scheme_safe(value):safe.append((key,web_link(value)))
            elif key in self.attributes:safe.append((key,value))
        self.parts.append('<'+tag+''.join(f' {k}="{html.escape(v,quote=True)}"' for k,v in safe)+'>')

    def handle_endtag(self,tag):
        if tag in self.allowed and tag not in {'img','br'}:self.parts.append('</'+tag+'>')

    def handle_data(self,data):
        self.parts.append(html.escape(data))


def safe_readme_html(text):
    parser=SafeReadmeHTML();parser.feed(text)
    return ''.join(parser.parts)


def inline_markdown(text):
    """只处理项目文档使用的 Markdown 子集；原始 HTML 默认转义。"""
    pattern=re.compile(r'(`[^`]+`|\[[^\]]+\]\([^)]+\)|\*\*[^*]+\*\*|<br>)')
    output=[];pos=0
    for match in pattern.finditer(text):
        output.append(html.escape(text[pos:match.start()].replace('\\|','|')))
        token=match.group()
        if token.startswith('`'):output.append('<code>'+html.escape(token[1:-1])+'</code>')
        elif token.startswith('**'):output.append('<strong>'+inline_markdown(token[2:-2])+'</strong>')
        elif token=='<br>':output.append('<br>')
        else:
            link=re.match(r'\[([^\]]+)\]\(([^)]+)\)',token)
            label,url=link.groups();url=web_link(url)
            if urllib_scheme_safe(url):output.append(f'<a href="{html.escape(url,quote=True)}">{inline_markdown(label)}</a>')
            else:output.append(html.escape(label))
        pos=match.end()
    output.append(html.escape(text[pos:].replace('\\|','|')))
    return ''.join(output)


def urllib_scheme_safe(url):
    return urlparse(url).scheme in {'','https','http'} and not url.startswith('//')


def markdown_body(content):
    lines=content.splitlines();out=[];i=0
    while i<len(lines):
        line=lines[i]
        if not line.strip():i+=1;continue
        if line.strip()=='---':out.append('<hr>');i+=1;continue
        block=re.match(r'^<(div|table)\b',line)
        if block:
            raw=[line];i+=1
            while i<len(lines) and f'</{block[1]}>' not in raw[-1]:raw.append(lines[i]);i+=1
            out.append(safe_readme_html('\n'.join(raw)));continue
        if re.fullmatch(r'<a id="[a-z0-9-]+"></a>',line.strip()):
            out.append(safe_readme_html(line));i+=1;continue
        if line.startswith('```'):
            code=[];i+=1
            while i<len(lines) and not lines[i].startswith('```'):code.append(lines[i]);i+=1
            out.append('<pre><code>'+html.escape('\n'.join(code))+'</code></pre>');i+=1;continue
        heading=re.match(r'^(#{1,6}) (.+)',line)
        if heading:
            level=len(heading[1]);out.append(f'<h{level}>'+inline_markdown(heading[2])+f'</h{level}>');i+=1;continue
        if line.startswith('|') and i+1<len(lines) and re.match(r'^\|[\s:|\-]+\|$',lines[i+1]):
            cells=lambda s:re.split(r'(?<!\\)\|',s.strip().strip('|'))
            out.append('<div class="table-scroll" tabindex="0"><table><thead><tr>'+''.join('<th>'+inline_markdown(c.strip())+'</th>' for c in cells(line))+'</tr></thead><tbody>');i+=2
            while i<len(lines) and lines[i].startswith('|'):
                out.append('<tr>'+''.join('<td>'+inline_markdown(c.strip())+'</td>' for c in cells(lines[i]))+'</tr>');i+=1
            out.append('</tbody></table></div>');continue
        if re.match(r'^(?:- |\d+\. )',line):
            ordered=bool(re.match(r'^\d+\.',line));tag='ol' if ordered else 'ul';pattern=r'^\d+\. ' if ordered else r'^- '
            out.append('<'+tag+'>')
            while i<len(lines) and re.match(pattern,lines[i]):out.append('<li>'+inline_markdown(re.sub(pattern,'',lines[i]))+'</li>');i+=1
            out.append('</'+tag+'>');continue
        paragraph=[line];i+=1
        while i<len(lines) and lines[i].strip() and not re.match(r'^(#|\||```|- |\d+\. )',lines[i]):paragraph.append(lines[i]);i+=1
        out.append('<p>'+inline_markdown(' '.join(paragraph))+'</p>')
    return '\n'.join(out)


def document_page(title, content):
    return f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)} — Awesome Code World Model</title><link rel="stylesheet" href="style.css"><link rel="icon" href="icon.svg"><main class="document"><a href="./">← Research library</a><nav><a href="taxonomy.html">Taxonomy</a><a href="research.html">Research notes</a><a href="contributing.html">Contribute</a></nav><article class="prose">{markdown_body(content)}</article></main></html>\n'''


def outputs(catalog, taxonomy, repository):
    validate(catalog, taxonomy)
    if repository:
        assert re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repository), 'repository 格式应为 owner/name'
    updates = json.loads((ROOT/'data/updates.json').read_text())
    payload = {**catalog, 'taxonomy': taxonomy, 'repository': repository, 'news': updates['news']}
    readme = render_readme(catalog, taxonomy, repository)
    benchmark_guide = render_benchmarks(catalog, taxonomy)
    out = {
        ROOT/'README.md': readme,
        ROOT/'docs/BENCHMARKS.md': benchmark_guide,
        ROOT/'site/benchmarks.html': document_page('Benchmark Atlas / 基准索引', benchmark_guide),
        ROOT/'site/catalog.js': 'window.CWM_CATALOG = '+json.dumps(payload, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c')+';\n',
        ROOT/'site/papers.json': json.dumps(catalog, ensure_ascii=False, indent=2)+'\n',
        ROOT/'site/papers.bib': '\n\n'.join(bibtex(p) for p in catalog['papers'])+'\n',
        ROOT/'site/.nojekyll': '',
        ROOT/'site/LICENSE': (ROOT/'LICENSE').read_text(),
    }
    buf=io.StringIO(newline='')
    fields=['id','title','published','date_basis','type','research_area','research_direction','auxiliary_tags','classification_basis','track','category','scope','collections','benchmark_names','benchmark_protocols']+[d['id'] for d in taxonomy['dimensions']]+['source','summary']
    writer=csv.DictWriter(buf, fieldnames=fields)
    writer.writeheader()
    for p in catalog['papers']:
        row={k:p[k] or '' for k in fields if k in p}
        row['research_area']=p['classification']['area']
        row['research_direction']=p['classification']['direction'] or ''
        row['auxiliary_tags']=json.dumps(p['classification']['tags'],ensure_ascii=False)
        row['classification_basis']=p['classification']['basis']
        row.update({d['id']:'; '.join(p['dimensions'][d['id']]) for d in taxonomy['dimensions']})
        row['collections']='; '.join(p['collections'])
        row['benchmark_names']='; '.join(b['name'] for b in p['benchmarks'])
        row['benchmark_protocols']=json.dumps(p['benchmarks'],ensure_ascii=False) if p['benchmarks'] else ''
        row['source']=p['verification']['source']
        # CSV 内容是外部文本，避免表格软件把公式前缀当作公式执行。
        writer.writerow({k:("'"+v if isinstance(v,str) and v.startswith(('=','+','-','@')) else v) for k,v in row.items()})
    out[ROOT/'site/papers.csv']=buf.getvalue()
    for filename,title,source in [('taxonomy','Taxonomy / 分类说明',ROOT/'docs/TAXONOMY.md'),('research','Research scope / 核验记录',ROOT/'docs/RESEARCH.md'),('contributing','Contributing / 参与维护',ROOT/'CONTRIBUTING.md'),('deployment','Deployment / 部署',ROOT/'docs/DEPLOYMENT.md'),('crawler','Crawler / 爬虫交接',ROOT/'docs/CRAWLER_HANDOFF.md'),('agent-review','Agent review prompt',ROOT/'docs/AGENT_REVIEW_PROMPT.md')]:
        out[ROOT/f'site/{filename}.html']=document_page(title, source.read_text())
    out[ROOT/'site/readme.html']=document_page('Repository guide',readme)
    return out


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='只检查生成结果是否同步')
    parser.add_argument('--repository', default=None, help='GitHub owner/repository；默认读取 data/site.json')
    args=parser.parse_args()
    settings_path = ROOT / 'data/site.json'
    settings = json.loads(settings_path.read_text()) if settings_path.exists() else {}
    repository = args.repository if args.repository is not None else settings.get('repository', '')
    catalog=json.loads((ROOT/'data/papers.json').read_text())
    taxonomy=json.loads((ROOT/'data/taxonomy.json').read_text())
    stale=[]
    for path, content in outputs(catalog,taxonomy,repository).items():
        if args.check:
            # newline='' 保留 CSV 的标准 CRLF 行尾。
            if not path.exists() or path.open(newline='').read()!=content: stale.append(str(path.relative_to(ROOT)))
        else:
            path.write_bytes(content.encode('utf-8'))
    if stale:
        raise SystemExit('生成文件未同步：'+', '.join(stale)+'；请运行 python3 scripts/build.py')
    print(f"{'已检查' if args.check else '已生成'} {len(catalog['papers'])} 条记录；分类与导出校验通过。")


if __name__=='__main__':
    main()
