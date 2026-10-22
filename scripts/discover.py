#!/usr/bin/env python3
"""每日发现原型：公开元数据 → 去重 → 规则建议 → 人工审核队列。"""
import argparse
import hashlib
import json
import os
import re
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
NS={'a':'http://www.w3.org/2005/Atom','o':'http://a9.com/-/spec/opensearch/1.1/'}
USER_AGENT='AwesomeCodeWorldModel/0.1 (research metadata discovery)'


def normalized_title(title):
    return re.sub(r'[^\w]+','',unicodedata.normalize('NFKC',title).casefold())


def canonical_arxiv(url):
    match=re.search(r'(\d{4}\.\d{4,5})(?:v\d+)?(?:$|[/?#])',url.strip())
    return match.group(1) if match else None


def parse_atom(data):
    root=ET.fromstring(data)
    result=[]
    for e in root.findall('a:entry',NS):
        link=e.findtext('a:id',default='',namespaces=NS)
        arxiv=canonical_arxiv(link)
        if not arxiv:
            raise ValueError('arXiv 返回错误条目或不支持的 ID: '+link[:150])
        title=' '.join(e.findtext('a:title',default='',namespaces=NS).split())
        published=e.findtext('a:published',default='',namespaces=NS)
        if not title or not published:
            raise ValueError('arXiv 条目缺少标题或首次提交日期')
        result.append({'id':'arxiv-'+arxiv,'arxiv':arxiv,'title':title,
            'authors':[a.findtext('a:name',default='',namespaces=NS) for a in e.findall('a:author',NS)],
            'published':published[:10], 'updated':e.findtext('a:updated',default='',namespaces=NS)[:10],
            'abstract':' '.join(e.findtext('a:summary',default='',namespaces=NS).split()),
            'url':'https://arxiv.org/abs/'+arxiv,'source_type':'arxiv'})
    return result,int(root.findtext('o:totalResults',default=str(len(result)),namespaces=NS))


def suggest(item):
    text=(item['title']+' '+item.get('abstract','')).casefold()
    rules=[
        ('a_software',['software engineering','python execution','docker-free','execution trace']),
        ('u_inverse',['video-to-simulation','reconstruct','system identification','real2sim','inverse']),
        ('u_verification',['verification','benchmark','evaluation','obligation']),
        ('u_reasoning',['physical reasoning','solver generation','abductive']),
        ('u_planning',['planning','monte carlo','model-predictive','transition function']),
        ('g_learning',['curriculum','agent learning','evolving agents','train agents']),
        ('g_rendering',['renderer','rendering','proxy video','diffusion']),
        ('g_hybrid',['persistent','gameplay','programmable','playable']),
        ('g_simulation',['simulation','physics engine','physical world']),
        ('g_scene',['3d scene','scene program','3d code','asset'])]
    matches=[(category,[term for term in terms if term in text]) for category,terms in rules]
    hits=[(category,terms) for category,terms in matches if terms]
    relevant=[term for term in ['code world','executable world','world program','coding agent','program synthesis','code generation','generative render'] if term in text]
    return {'category':hits[0][0] if hits else None,'confidence':'low',
        'matched_terms':sorted(set(relevant+[term for _,terms in hits for term in terms])),
        'relevance_score':len(relevant)*3+sum(len(terms) for _,terms in hits),
        'note':'规则只用于排序；主分类必须阅读来源后确认。生成代码不一定属于生成主线。'}


def merge_candidates(existing, incoming, curated, today):
    known_arxiv={p['arxiv'] for p in curated if p.get('arxiv')}
    known_titles={normalized_title(p['title']) for p in curated}
    known_urls={r['url'].rstrip('/').casefold() for p in curated for r in p.get('resources',[])}
    result=[dict(p) for p in existing]
    by_arxiv={p['arxiv']:p for p in result if p.get('arxiv')}
    by_title={normalized_title(p['title']):p for p in result}
    by_url={p['url'].rstrip('/').casefold():p for p in result}
    counts={'new':0,'updated':0,'already_curated':0,'duplicates':0}
    for item in incoming:
        aid=item.get('arxiv');title=normalized_title(item['title']);url=item['url'].rstrip('/').casefold()
        if aid and aid in known_arxiv or title in known_titles or url in known_urls:
            counts['already_curated']+=1
            continue
        old=by_arxiv.get(aid) if aid else None
        old=old or by_title.get(title) or by_url.get(url)
        if old:
            if old.get('source_type')=='arxiv' and item.get('source_type')=='github':
                # 同名项目只能补充关联资源，不能覆盖论文身份、日期或摘要。
                old['related_urls']=sorted(set(old.get('related_urls',[])+[item['url']]))
                by_url[url]=old
                counts['duplicates']+=1
                continue
            # 保留人工决定与首次发现时间；只有新元数据才更新。
            changed=any(old.get(k)!=item.get(k) for k in ['title','abstract','updated'])
            if changed and item.get('updated','')>=old.get('updated',''):
                preserved={k:v for k,v in old.items() if k in {'id','status','decision_reason','discovered_at','reviewed_at'}}
                old.update(item);old.update(preserved);old['suggestion']=suggest(item)
                counts['updated']+=1
            else:counts['duplicates']+=1
            if aid:by_arxiv[aid]=old
            by_title[title]=old;by_url[url]=old
            continue
        candidate={**item,'status':'pending','discovered_at':today,'suggestion':suggest(item)}
        result.append(candidate)
        if aid:by_arxiv[aid]=candidate
        by_title[title]=candidate;by_url[url]=candidate;counts['new']+=1
    result.sort(key=lambda p:(p['discovered_at'],p['id']),reverse=True)
    return result,counts


def fetch(url, retries=3, opener=urllib.request.urlopen, sleep=time.sleep):
    headers={'User-Agent':USER_AGENT,'Accept':'application/atom+xml, application/json'}
    if urllib.parse.urlparse(url).hostname=='api.github.com' and os.environ.get('GITHUB_TOKEN'):
        headers['Authorization']='Bearer '+os.environ['GITHUB_TOKEN']
    for attempt in range(retries):
        try:
            with opener(urllib.request.Request(url,headers=headers),timeout=40) as response:
                return response.read()
        except (urllib.error.URLError,TimeoutError,OSError) as error:
            if attempt==retries-1:raise
            if isinstance(error,urllib.error.HTTPError) and error.code not in {403,429,500,502,503,504}:raise
            sleep(min(30,3*2**attempt))


def atomic_json(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+'.tmp')
    tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    tmp.replace(path)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--days',type=int)
    parser.add_argument('--fixture',type=Path,help='离线 Atom 文件；不访问网络')
    parser.add_argument('--output',type=Path,default=ROOT/'data/inbox.json')
    parser.add_argument('--report',type=Path,default=ROOT/'data/discovery-report.json')
    parser.add_argument('--skip-github',action='store_true')
    args=parser.parse_args()
    config=json.loads((ROOT/'data/discovery.json').read_text())
    now=datetime.now(timezone.utc);today=now.date().isoformat()
    days=args.days if args.days is not None else config['lookback_days']
    if days<1:parser.error('--days 必须大于 0')
    since=now-timedelta(days=days)
    incoming=[];sources=[]
    if args.fixture:
        rows,total=parse_atom(args.fixture.read_bytes());incoming.extend(rows)
        sources.append({'source':'fixture','ok':True,'returned':len(rows),'total':total,'truncated':total>len(rows)})
    else:
        for i,query in enumerate(config['arxiv_queries']):
            if i:time.sleep(3.1)
            full=f'({query}) AND submittedDate:[{since:%Y%m%d}0000 TO {now:%Y%m%d}2359]'
            url='https://export.arxiv.org/api/query?'+urllib.parse.urlencode({'search_query':full,'start':0,'max_results':config['max_results_per_query'],'sortBy':'submittedDate','sortOrder':'descending'})
            try:
                rows,total=parse_atom(fetch(url));incoming.extend(rows)
                sources.append({'source':'arxiv','query':full,'ok':True,'returned':len(rows),'total':total,'truncated':total>len(rows)})
            except Exception as error:
                sources.append({'source':'arxiv','query':full,'ok':False,'error':type(error).__name__+': '+str(error)[:250]})
        if not args.skip_github:
            for query in config['github_queries']:
                full=query+f' created:>={since:%Y-%m-%d}'
                url='https://api.github.com/search/repositories?'+urllib.parse.urlencode({'q':full,'per_page':50,'sort':'updated'})
                try:
                    result=json.loads(fetch(url));rows=[]
                    for r in result['items']:
                        rows.append({'id':'github-'+hashlib.sha256(r['full_name'].casefold().encode()).hexdigest()[:16],
                            'arxiv':None,'title':r['name'].replace('-',' '),'authors':[],'published':None,
                            'updated':r['pushed_at'][:10], 'abstract':r.get('description') or '',
                            'url':r['html_url'],'source_type':'github','repository_created':r['created_at'][:10]})
                    incoming.extend(rows)
                    sources.append({'source':'github','query':full,'ok':True,'returned':len(rows),'total':result['total_count'],'truncated':result['total_count']>len(rows) or result.get('incomplete_results',False)})
                except Exception as error:
                    sources.append({'source':'github','query':full,'ok':False,'error':type(error).__name__+': '+str(error)[:250]})
    succeeded=sum(s['ok'] for s in sources)
    report={'run_at':now.isoformat(),'mode':'fixture' if args.fixture else 'live','status':'ok' if succeeded==len(sources) else 'partial' if succeeded else 'failed','sources':sources}
    if not succeeded:
        atomic_json(args.report,report)
        raise SystemExit('全部来源失败；原审核队列已保留，详见运行报告。')
    existing=json.loads(args.output.read_text())['candidates'] if args.output.exists() else []
    curated=json.loads((ROOT/'data/papers.json').read_text())['papers']
    merged,counts=merge_candidates(existing,incoming,curated,today)
    atomic_json(args.output,{'schema_version':1,'candidates':merged})
    report.update(counts=counts,candidate_count=len(merged))
    atomic_json(args.report,report)
    print(json.dumps({'status':report['status'],**counts,'sources_ok':succeeded,'sources_total':len(sources)},ensure_ascii=False))
    if any(s.get('truncated') for s in sources):print('提示：有查询结果被截断，需缩小窗口或实现分页。')


if __name__=='__main__':main()
