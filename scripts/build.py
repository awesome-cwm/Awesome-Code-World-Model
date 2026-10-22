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
    topics = {t['id']: t for t in taxonomy['topics']}
    assert len(topics) == len(taxonomy['topics']), 'Duplicate topic'
    assert not {'research_areas', 'tag_dimensions'} & set(taxonomy), 'Use a flat topic vocabulary'
    for topic in topics.values():
        assert re.fullmatch(r'[a-z]+(?:-[a-z]+)*', topic['id'])
        assert all(isinstance(topic.get(key), str) and topic[key].strip() for key in ['name','zh','description'])
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
        required = {'readme_topic','topics','checked','summary_reason','topic_reasons','sources','uncertainties'}
        assert isinstance(classification, dict) and required <= set(classification), p['id']
        selected = classification['topics']
        assert isinstance(selected, list) and selected and all(isinstance(t, str) for t in selected), p['id']
        assert len(selected) == len(set(selected)) and set(selected) <= set(topics), p['id']
        assert isinstance(classification['readme_topic'], str) and classification['readme_topic'] in selected, p['id']
        assert not {'area','direction','tags'} & set(classification), p['id']
        assert isinstance(classification['summary_reason'], str) and classification['summary_reason'].strip(), p['id']
        reasons = classification['topic_reasons']
        assert isinstance(reasons, dict) and set(reasons) == set(selected), p['id']
        assert all(isinstance(reason, str) and reason.strip() for reason in reasons.values()), p['id']
        date.fromisoformat(classification['checked'])
        assert classification['sources'] and isinstance(classification['sources'], list), p['id']
        for source in classification['sources']:
            assert source['basis'] in {'primary_abstract','official_project','full_text'}, p['id']
            parsed = urlparse(source['url'])
            assert parsed.scheme == 'https' and parsed.hostname and not parsed.username, p['id']
            assert isinstance(source['note'], str) and source['note'].strip(), p['id']
        assert isinstance(classification['uncertainties'], list) and all(isinstance(note, str) and note.strip() for note in classification['uncertainties']), p['id']
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


def topic_entries(papers, topic_id):
    """README placement is unique; website topic membership may overlap."""
    return sorted([p for p in papers if p['classification']['readme_topic'] == topic_id],
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
    reviewed = max(p['classification']['checked'] for p in papers)
    intro = (ROOT / 'docs/README.template.md').read_text().replace('{{SITE_URL}}', site_url)
    intro = intro.replace('{{STATS}}', f"**{len(papers)} unique papers / projects · {len(taxonomy['topics'])} flat topics** · Topic assignments reviewed **{reviewed}**.")
    intro = intro.replace('{{NEWS}}', '\n\n'.join(f"{n['icon']} **[{n['date']}] {n['title']}** — {n['body']}" for n in news))
    parts = [intro, '\n---\n\n## Browse by Topic\n',
             'Each paper is listed **exactly once** below, under the topic that best describes its main contribution. The website uses the same flat vocabulary and allows each paper to appear under **multiple topics**. Select several website topics to find their intersection. Only topics with a designated README entry become headings here; all 22 topics remain available on the website.\n']
    occupied = [(topic, topic_entries(papers, topic['id'])) for topic in taxonomy['topics']]
    for topic, entries in occupied:
        if entries:
            parts.append(f"- [{topic['name']}](#{topic['id']}) ({len(entries)})")
    parts.append('\n[All 22 topic filters]('+site_url+') · [Topic definitions](docs/TAXONOMY.md) · [Per-paper review and sources](docs/TOPIC_REVIEW.md)\n')
    for topic, entries in occupied:
        if not entries:
            continue
        parts.append(f"\n---\n\n<a id=\"{topic['id']}\"></a>\n## {topic['name']}\n\n{topic['description']}\n")
        parts.append(f"[Browse all papers tagged {topic['name']} →]({site_url}?topics={topic['id']})\n")
        parts.extend(readme_entry(p)+'\n' for p in entries)
    parts.append('''
---

<a id="benchmarks"></a>
## Benchmarks & Resources

[Benchmark Atlas](docs/BENCHMARKS.md) compares inputs, executable artifacts, evaluation evidence, and limitations. Named suites within method papers, such as CombatStateBench and SimCode4D, remain associated with their original paper; they are not duplicate paper records.

<a id="infrastructure"></a>
Datasets, execution harnesses, rendering components, and streaming systems are included in the topic list above. Supporting components remain distinguished in the source metadata and editorial descriptions.

## Reading & Review

The [topic guide](docs/TAXONOMY.md) explains the vocabulary. The [per-paper review](docs/TOPIC_REVIEW.md) records the single README placement, overlapping website topics, primary sources, and unresolved details for every record. The review uses author abstracts, official project documentation, and selected method or evaluation sections; it is not an independent reproduction.

For new work, use the website's publication-month navigation. Each paper has one bibliography entry in this README; recent-paper and reading-path lists are kept out of the README to preserve that rule.

<a id="citation"></a>
## Citation

Please cite the original papers. Download [all BibTeX entries](site/papers.bib) and use the entries for the papers you reference.

## Contributing & Maintenance

See [CONTRIBUTING.md](CONTRIBUTING.md) to suggest a paper or correction. [Research notes](docs/RESEARCH.md) document the original scope and identity checks.

`data/papers.json` is the single source of truth. `data/taxonomy.json` defines the flat topics; `classification.readme_topic` gives one README placement, while `classification.topics` gives all reviewed website topics. Source links and reasons are stored with each assignment. The README, website data, review report, and exports are generated together.

```bash
python3 scripts/build.py
python3 -m unittest discover -s tests -v
python3 -m http.server 8000 --directory site
```

Open `http://localhost:8000`, or open `site/index.html` directly. [GitHub Pages deployment](docs/DEPLOYMENT.md) · [Daily discovery prototype](docs/CRAWLER_HANDOFF.md) · [JSON](data/papers.json) · [CSV](site/papers.csv).

The daily discovery prototype proposes candidates for review. It does not silently promote papers into the curated list.

## Acknowledgments & License

The simple list and topic naming draw inspiration from [Awesome Interactive World Model](https://github.com/EasonTuT/Awesome-Interactive-World-Model); compound indexing also draws inspiration from [Awesome 3D Gaussian Splatting](https://mrnerf.github.io/awesome-3D-gaussian-splatting/). The flat topic scheme follows the maintainer's direction. Metadata, editorial decisions, and implementation are maintained independently.

Repository code and original editorial content: [MIT](LICENSE). Paper titles, abstracts, and external resources remain attributable to their respective authors and providers.
''')
    readme = '\n'.join(parts).strip()+'\n'
    return re.sub(r'(<a id="[a-z0-9-]+"></a>)\n(?=#)', r'\1\n\n', readme)


def render_topic_review(catalog, taxonomy):
    names = {t['id']:t['name'] for t in taxonomy['topics']}
    parts = ['# Per-paper Topic Review\n',
             'Every record was individually checked against the primary sources linked below. README placement is an editorial choice based on the main contribution; website topics overlap. Reading scope is stated per source. No independent reproduction is claimed.\n',
             'The topic vocabulary is defined in [the topic guide](TAXONOMY.md). Reasons and source links are also available in `data/papers.json`.\n']
    for p in catalog['papers']:
        c = p['classification']
        parts.extend([f"## {p['short_title']}\n", f"- **Record:** `{p['id']}`",
                      f"- **Reviewed:** {c['checked']}", f"- **README:** {names[c['readme_topic']]}",
                      '- **Website:** '+', '.join(names[t] for t in c['topics']),
                      '- **Placement reason:** '+c['summary_reason'], '\n**Topic evidence**\n'])
        parts.extend(f"- **{names[t]}:** {c['topic_reasons'][t]}" for t in c['topics'])
        parts.append('\n**Sources actually consulted**\n')
        for i, source in enumerate(c['sources'], 1):
            parts.append(f"- [Source {i}]({source['url']}) — `{source['basis']}`. {source['note']}")
        if c['uncertainties']:
            parts.append('\n**Limits / unresolved details**\n')
            parts.extend('- '+note for note in c['uncertainties'])
        parts.append('')
    return '\n'.join(parts).strip()+'\n'


def web_link(url):
    links={'docs/TAXONOMY.md':'taxonomy.html','docs/TOPIC_REVIEW.md':'topic-review.html','TAXONOMY.md':'taxonomy.html','docs/RESEARCH.md':'research.html','CONTRIBUTING.md':'contributing.html',
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
    topic_review = render_topic_review(catalog, taxonomy)
    out = {
        ROOT/'README.md': readme,
        ROOT/'docs/BENCHMARKS.md': benchmark_guide,
        ROOT/'docs/TOPIC_REVIEW.md': topic_review,
        ROOT/'site/topic-review.html': document_page('Per-paper topic review', topic_review),
        ROOT/'site/benchmarks.html': document_page('Benchmark Atlas / 基准索引', benchmark_guide),
        ROOT/'site/catalog.js': 'window.CWM_CATALOG = '+json.dumps(payload, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c')+';\n',
        ROOT/'site/papers.json': json.dumps(catalog, ensure_ascii=False, indent=2)+'\n',
        ROOT/'site/papers.bib': '\n\n'.join(bibtex(p) for p in catalog['papers'])+'\n',
        ROOT/'site/.nojekyll': '',
        ROOT/'site/LICENSE': (ROOT/'LICENSE').read_text(),
    }
    buf=io.StringIO(newline='')
    fields=['id','title','published','date_basis','type','readme_topic','topics','topic_checked','topic_reason','topic_evidence','topic_sources','track','category','scope','collections','benchmark_names','benchmark_protocols']+[d['id'] for d in taxonomy['dimensions']]+['source','summary']
    writer=csv.DictWriter(buf, fieldnames=fields)
    writer.writeheader()
    for p in catalog['papers']:
        row={k:p[k] or '' for k in fields if k in p}
        classification=p['classification']
        row['readme_topic']=classification['readme_topic']
        row['topics']='; '.join(classification['topics'])
        row['topic_checked']=classification['checked']
        row['topic_reason']=classification['summary_reason']
        row['topic_evidence']=json.dumps(classification['topic_reasons'],ensure_ascii=False)
        row['topic_sources']=json.dumps(classification['sources'],ensure_ascii=False)
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
