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
    site_url = 'site/index.html'
    if repository:
        owner, repo = repository.split('/')
        site_url = f'https://{owner}.github.io/{repo}/'
    benchmarks = sum(len(p['benchmarks']) for p in papers)
    intro = (ROOT / 'docs/README.template.md').read_text()
    intro = intro.replace('{{SITE_URL}}', site_url)
    intro = intro.replace('{{STATS}}', f"<b>{len(papers)} papers &amp; projects</b> · <b>{benchmarks} benchmark suites</b> · <b>{len(taxonomy['dimensions'])} comparison dimensions</b><br>Sources checked {catalog['curated_at']}")
    news_line = lambda n: f"{n['icon']} **[{n['date']}] {n['title']}** — {n['body']}"
    news_text = '\n\n'.join(news_line(n) for n in news[:2])
    news_text += '\n\n<details>\n<summary>Earlier collection updates</summary>\n\n' + '\n\n'.join(news_line(n) for n in news[2:]) + '\n\n</details>'
    parts = [intro.replace('{{NEWS}}', news_text), '\n<a id="recent-paper-updates"></a>\n## 🔥 Recent Paper Updates\n']
    recent = sorted([p for p in papers if p['published']], key=lambda p:(p['published'],p['id']), reverse=True)[:20]
    parts.extend(readme_entry(p, recent=True)+'\n' for p in recent[:6])
    parts.append('<details>\n<summary>More recent papers & projects with unconfirmed dates</summary>\n')
    parts.extend(readme_entry(p, recent=True)+'\n' for p in recent[6:])
    parts.append('**Official projects with unconfirmed first-release dates**\n')
    parts.extend(readme_entry(p, recent=True)+'\n' for p in papers if not p['published'])
    parts.append('</details>\n\n---\n\n<a id="overview"></a>\n## 🧭 Overview\n')
    parts.append('Two reading directions share one executable representation. Choose a research question below; use the benchmark and infrastructure indexes for reusable resources.\n')
    track_meta = {'generation':('💻','Code World Model · Generation','code-world-model'), 'understanding':('🧠','Code as Model · Understanding','code-as-model'), 'adjacent':('🔎','Related Perspectives','related-perspectives')}
    icons = {'g_hybrid':'🎮','g_rendering':'🎬','g_simulation':'⚙️','g_scene':'🏗️','g_learning':'🌱','u_inverse':'🔄','u_reasoning':'🧪','u_planning':'🧩','u_verification':'📏','a_software':'💻','a_representation':'💬','a_streaming':'⚡'}
    parts.append('<table width="100%">\n<tr>')
    for track in taxonomy['tracks'][:2]:
        icon, name, anchor = track_meta[track['id']]
        flow = 'Intent → program → world' if track['id']=='generation' else 'Observation → program → explanation'
        links = [f'<a href="#{c["id"].replace("_","-")}">{icons[c["id"]]} {html.escape(c["name"])}</a>' for c in taxonomy['categories'] if c['track']==track['id']]
        parts.append(f'<td width="50%" valign="top"><b><a href="#{anchor}">{icon} {name}</a></b><br>{flow}<br><br>'+ '<br>'.join(links) + '</td>')
    parts.append('</tr>\n<tr><td colspan="2" align="center"><a href="#benchmarks">📊 Benchmarks &amp; Evaluation</a> · <a href="#infrastructure">🛠️ Datasets &amp; Systems</a> · <a href="#related-perspectives">🔎 Related Perspectives</a><br><a href="#reading-guide">Reading paths &amp; dimensions</a> · <a href="#citation">Citation</a></td></tr>\n</table>\n')
    parts.append('Each work appears once in the main research list, under its primary contribution. Cross-category associations remain searchable in the website. [Classification rationale](docs/TAXONOMY.md).\n')
    for track in taxonomy['tracks'][:2]:
        icon, name, anchor = track_meta[track['id']]
        parts.append(f'\n---\n\n<a id="{anchor}"></a>\n## {icon} {name}\n\n{track["description"]}\n')
        for c in taxonomy['categories']:
            if c['track'] != track['id']: continue
            parts.append(f'\n<a id="{c["id"].replace("_","-")}"></a>\n### {icons[c["id"]]} {c["name"]}\n\n{c["question"]}\n')
            parts.extend(readme_entry(p)+'\n' for p in category_entries(papers,c['id']) if p['category']==c['id'])
    for section in taxonomy['collection_sections']:
        parts.append(f'\n---\n\n<a id="{section["id"]}"></a>\n## {section["icon"]} {section["name"]}\n\n{section["description"]}\n')
        if section['id']=='benchmarks':
            parts.append('**[Open the Benchmark Atlas →](docs/BENCHMARKS.md)** for inputs, submitted artifacts, evaluation evidence and version caveats. Suite names below link to their sources; method papers are counted only once.\n')
        parts.extend(['| Research task | Suites / resources |','| --- | --- |'])
        for group in taxonomy['collections']:
            if group['section']!=section['id']: continue
            links=[]
            for p in collection_entries(papers,group['id']):
                if section['id']=='benchmarks':links.extend(f"[{md(b['name'])}]({b['source']})" for b in p['benchmarks'])
                else:links.append(f"[{md(p['short_title'])}]({p['verification']['source']})")
            parts.append(f'| {group["name"]} | '+ ' · '.join(links)+' |')
        parts.append('')
    parts.append('\n---\n\n<a id="related-perspectives"></a>\n## 🔎 Related Perspectives\n\nNeighboring work clarifies the scope: software execution, non-program representations and decoder components.\n')
    for c in taxonomy['categories']:
        if c['track']!='adjacent':continue
        parts.append(f'\n<a id="{c["id"].replace("_","-")}"></a>\n### {icons[c["id"]]} {c["name"]}\n\n{c["question"]}\n')
        parts.extend(readme_entry(p)+'\n' for p in category_entries(papers,c['id']) if p['category']==c['id'])
    parts.append('\n---\n\n<a id="reading-guide"></a>\n## 🧭 Reading Guide & Taxonomy\n\nResearch categories describe the main question. Benchmarks and infrastructure describe reusable contributions. Comparison dimensions describe mechanisms; they are multi-label facets, not a ranking.\n')
    parts += ['| Dimension | What to compare |','| --- | --- |']
    parts.extend(f'| {d["name"]} | {d["question"]} |' for d in taxonomy['dimensions'])
    parts.append('\nStreaming delivery does not establish real-time control. Public resources do not establish an open-source license. [Full taxonomy and scope boundaries →](docs/TAXONOMY.md)\n')
    by_id = {p['id']:p for p in papers}
    for path in taxonomy['reading_paths']:
        links = [f"[{by_id[i]['short_title']}]({by_id[i]['verification']['source']})" for i in path['papers']]
        parts.append(f"- **{path['title']}**: "+' → '.join(links))
    parts.append('''

<a id="citation"></a>
## 📝 Citation

Please cite the original papers. Download [all BibTeX entries](site/papers.bib), or copy individual citations from the website.

## Contributing & Maintenance

Missing a paper or a resource? See [CONTRIBUTING.md](CONTRIBUTING.md). Source checks and naming boundaries are documented in [Research notes](docs/RESEARCH.md).

<details>
<summary>Local preview & maintenance</summary>

`data/papers.json` stores the literature; `data/taxonomy.json` defines categories and dimensions. Edit `docs/README.template.md` and `scripts/build.py` to change this generated README.

```bash
python3 scripts/build.py
python3 -m unittest discover -s tests -v
python3 -m http.server 8000 --directory site
```

Open `http://localhost:8000`, or open `site/index.html` directly. [GitHub Pages setup](docs/DEPLOYMENT.md) · [Daily discovery workflow](docs/CRAWLER_HANDOFF.md) · [JSON](data/papers.json) · [CSV](site/papers.csv).

</details>

## Acknowledgments & License

Visual hierarchy and paper-list conventions take inspiration from [Awesome Interactive World Model](https://github.com/EasonTuT/Awesome-Interactive-World-Model). The research taxonomy, editorial notes, vector artwork and implementation are maintained independently.

Repository code and original editorial content: [MIT](LICENSE). Papers and external resources belong to their respective authors and providers.
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
    allowed={'div','h1','h2','h3','p','b','strong','a','img','br','table','tbody','tr','td','details','summary'}
    attributes={'align','width','height','border','cellspacing','cellpadding','alt','id','valign','colspan'}

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
        if re.fullmatch(r'</?details>|<summary>.*</summary>',line.strip()):
            out.append(safe_readme_html(line));i+=1;continue
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
    fields=['id','title','published','date_basis','type','track','category','scope','collections','benchmark_names','benchmark_protocols']+[d['id'] for d in taxonomy['dimensions']]+['source','summary']
    writer=csv.DictWriter(buf, fieldnames=fields)
    writer.writeheader()
    for p in catalog['papers']:
        row={k:p[k] or '' for k in fields if k in p}
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
    parser.add_argument('--repository', default='', help='GitHub owner/repository，用于生成公开链接')
    args=parser.parse_args()
    catalog=json.loads((ROOT/'data/papers.json').read_text())
    taxonomy=json.loads((ROOT/'data/taxonomy.json').read_text())
    stale=[]
    for path, content in outputs(catalog,taxonomy,args.repository).items():
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
