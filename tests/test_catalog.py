"""防止分类漂移、误去重、候选覆盖和生成内容丢失。"""
import copy
import csv
import importlib.util
import io
import json
import sys
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import build
import discover


class CatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog=json.loads((ROOT/'data/papers.json').read_text())
        cls.taxonomy=json.loads((ROOT/'data/taxonomy.json').read_text())

    def test_curated_schema_and_cross_references(self):
        self.assertTrue(build.validate(self.catalog,self.taxonomy))

    def test_duplicate_arxiv_rejected(self):
        c=copy.deepcopy(self.catalog)
        c['papers'][1]['arxiv']=c['papers'][0]['arxiv']
        with self.assertRaises(AssertionError):build.validate(c,self.taxonomy)

    def test_wrong_primary_track_rejected(self):
        c=copy.deepcopy(self.catalog)
        c['papers'][0]['track']='nonsense'
        with self.assertRaises(AssertionError):build.validate(c,self.taxonomy)

    def test_no_script_urls(self):
        c=copy.deepcopy(self.catalog)
        c['papers'][0]['resources'][0]['url']='javascript:alert(1)'
        with self.assertRaises(AssertionError):build.validate(c,self.taxonomy)

    def test_build_is_deterministic_and_exports_all_records(self):
        a=build.outputs(self.catalog,self.taxonomy,'')
        self.assertEqual(a,build.outputs(self.catalog,self.taxonomy,''))
        self.assertEqual(a[ROOT/'site/papers.bib'].count('@misc{'),len(self.catalog['papers']))
        self.assertEqual(len(json.loads(a[ROOT/'site/papers.json'])['papers']),len(self.catalog['papers']))

    def test_unknown_date_is_not_invented(self):
        p=copy.deepcopy(next(p for p in self.catalog['papers'] if p['id']=='streaming-cwm'))
        p['published']=None
        p['date_basis']='unknown'
        p.pop('date_evidence',None)
        self.assertNotIn('year =',build.bibtex(p))

    def test_online_dates_require_matching_primary_evidence(self):
        for change in ['missing', 'empty', 'earlier', 'unsafe']:
            with self.subTest(change=change):
                c=copy.deepcopy(self.catalog)
                p=next(p for p in c['papers'] if p['id']=='streaming-cwm')
                if change=='missing':p.pop('date_evidence')
                elif change=='empty':p['date_evidence']['sources']=[]
                elif change=='earlier':p['published']='2026-10-02'
                else:p['date_evidence']['sources'][0]['url']='javascript:alert(1)'
                with self.assertRaises(AssertionError):build.validate(c,self.taxonomy)

    def test_public_repository_links_are_used_for_readme_and_catalog(self):
        repository='awesome-cwm/Awesome-Code-World-Model'
        generated=build.outputs(self.catalog,self.taxonomy,repository)
        self.assertIn('https://awesome-cwm.github.io/Awesome-Code-World-Model/',generated[ROOT/'README.md'])
        self.assertIn('https://awesome-cwm.github.io/Awesome-Code-World-Model/?topics=memory',generated[ROOT/'README.md'])
        self.assertIn('"repository":"'+repository+'"',generated[ROOT/'site/catalog.js'])

    def test_resource_badge_requires_matching_evidence(self):
        c=copy.deepcopy(self.catalog)
        p=next(p for p in c['papers'] if p['resource_status']['status']=='not_found')
        p['resource_status']['status']='available'
        with self.assertRaises(AssertionError):build.validate(c,self.taxonomy)

    def test_benchmark_protocol_cannot_be_orphaned(self):
        c=copy.deepcopy(self.catalog)
        p=next(p for p in c['papers'] if p['id']=='video2world')
        p['collections']=[]
        with self.assertRaises(AssertionError):build.validate(c,self.taxonomy)
        p['collections']=['b_reconstruction']
        p['benchmarks'][0]['checks']=''
        with self.assertRaises(AssertionError):build.validate(c,self.taxonomy)

    def test_benchmark_aliases_export_without_duplicate_papers(self):
        outputs=build.outputs(self.catalog,self.taxonomy,'')
        self.assertIn('SimCode4D',outputs[ROOT/'docs/BENCHMARKS.md'])
        self.assertIn('CombatStateBench',outputs[ROOT/'README.md'])
        import csv,io
        rows=list(csv.DictReader(io.StringIO(outputs[ROOT/'site/papers.csv'])))
        row=next(p for p in rows if p['id']=='code2worlds-2')
        self.assertEqual(row['benchmark_names'],'SimCode4D')
        self.assertTrue(json.loads(row['benchmark_protocols'])[0]['checks'])
        self.assertEqual(len(rows),len(self.catalog['papers']))

    def test_paper_entry_keeps_clickable_links(self):
        p=next(p for p in self.catalog['papers'] if p['id']=='code-world-model')
        rendered=build.inline_markdown(build.readme_entry(p))
        self.assertNotIn('<strong>',rendered)
        self.assertNotIn('🌟',rendered)
        self.assertIn('<a href="https://arxiv.org/abs/2608.25927">',rendered)

    def test_readme_html_only_allows_safe_layout(self):
        rendered=build.safe_readme_html('<div onclick="bad()"><img src="site/banner.svg" onerror="bad()"><a href="javascript:bad()">bad</a></div>')
        self.assertNotIn('onclick',rendered)
        self.assertNotIn('onerror',rendered)
        self.assertNotIn('javascript:',rendered)
        self.assertIn('src="banner.svg"',rendered)

    def test_flat_topics_match_the_agreed_vocabulary(self):
        expected=[
            ('general-world-model','General World Model'), ('memory','Memory'),
            ('interactive','Interactive'), ('real-time','Real-Time'),
            ('acceleration','Acceleration'), ('long-video-generation','Long Video Generation'),
            ('streaming','Streaming'), ('multi-agent','Multi-Agent'),
            ('action-control','Action Control'), ('physics','Physics'),
            ('world-generation','World Generation'), ('world-reconstruction','World Reconstruction'),
            ('world-editing','World Editing'), ('neural-rendering','Neural Rendering'),
            ('planning','Planning'), ('agent-learning','Agent Learning'),
            ('code-execution','Code Execution'), ('post-training','Post-Training'),
            ('benchmark','Benchmark'), ('dataset','Dataset'),
            ('evaluation','Evaluation'), ('survey','Survey')]
        self.assertEqual([(t['id'],t['name']) for t in self.taxonomy['topics']],expected)
        self.assertFalse({'research_areas','tag_dimensions'} & set(self.taxonomy))

    def test_readme_topic_is_single_valid_and_in_website_topics(self):
        for invalid in [None, [], ['memory','physics'], 'unknown']:
            with self.subTest(readme_topic=invalid):
                c=copy.deepcopy(self.catalog)
                c['papers'][0]['classification']['readme_topic']=invalid
                with self.assertRaises(AssertionError):build.validate(c,self.taxonomy)
        c=copy.deepcopy(self.catalog)
        classification=c['papers'][0]['classification']
        classification['topics']=['memory']
        classification['topic_reasons']={'memory':'Reviewed memory mechanism.'}
        classification['readme_topic']='physics'
        with self.assertRaises(AssertionError):build.validate(c,self.taxonomy)

    def test_flat_website_topics_must_be_nonempty_unique_and_known(self):
        for invalid in [None, 'memory', [], ['unknown'], ['memory','memory'], ['memory',None], [['memory']]]:
            with self.subTest(topics=invalid):
                c=copy.deepcopy(self.catalog)
                c['papers'][0]['classification']['topics']=invalid
                with self.assertRaises(AssertionError):build.validate(c,self.taxonomy)

    def test_review_fields_are_required_and_old_hierarchy_is_forbidden(self):
        c=copy.deepcopy(self.catalog)
        del c['papers'][0]['classification']
        with self.assertRaises(AssertionError):build.validate(c,self.taxonomy)
        for field in ['readme_topic','topics','checked','summary_reason','topic_reasons','sources','uncertainties']:
            with self.subTest(missing=field):
                c=copy.deepcopy(self.catalog)
                del c['papers'][0]['classification'][field]
                with self.assertRaises(AssertionError):build.validate(c,self.taxonomy)
        for field in ['area','direction','tags']:
            with self.subTest(legacy_field=field):
                c=copy.deepcopy(self.catalog)
                c['papers'][0]['classification'][field]=None
                with self.assertRaises(AssertionError):build.validate(c,self.taxonomy)

    def test_every_website_topic_has_exactly_one_nonempty_evidence_reason(self):
        c=copy.deepcopy(self.catalog)
        classification=c['papers'][0]['classification']
        for invalid in [None, {}, {t:'' for t in classification['topics']},
                        {t:None for t in classification['topics']},
                        dict(classification['topic_reasons'],unknown='Unsupported topic.')]:
            with self.subTest(reasons=invalid):
                changed=copy.deepcopy(c)
                changed['papers'][0]['classification']['topic_reasons']=invalid
                with self.assertRaises(AssertionError):build.validate(changed,self.taxonomy)
        for invalid in [None,'','   ']:
            with self.subTest(summary_reason=invalid):
                changed=copy.deepcopy(c)
                changed['papers'][0]['classification']['summary_reason']=invalid
                with self.assertRaises(AssertionError):build.validate(changed,self.taxonomy)

    def test_review_requires_primary_source_records_with_safe_urls_and_reading_scope(self):
        for invalid in [None, [], 'https://arxiv.org/abs/2608.25927']:
            with self.subTest(sources=invalid):
                c=copy.deepcopy(self.catalog)
                c['papers'][0]['classification']['sources']=invalid
                with self.assertRaises(AssertionError):build.validate(c,self.taxonomy)
        source={'url':'https://arxiv.org/abs/2608.25927','basis':'primary_abstract','note':'Read the author abstract.'}
        for field,value in [('url','http://arxiv.org/abs/2608.25927'),('url','javascript:alert(1)'),
                            ('url','https:///missing-host'),('url','https://user@example.org/paper'),
                            ('basis','unread'),('note',''),('note',None)]:
            with self.subTest(field=field,value=value):
                c=copy.deepcopy(self.catalog)
                c['papers'][0]['classification']['sources']=[dict(source,**{field:value})]
                with self.assertRaises(AssertionError):build.validate(c,self.taxonomy)

    def test_review_date_and_uncertainties_keep_their_documented_types(self):
        for invalid in ['2026/10/22','2026-99-99',None]:
            with self.subTest(checked=invalid):
                c=copy.deepcopy(self.catalog)
                c['papers'][0]['classification']['checked']=invalid
                with self.assertRaises((TypeError,ValueError)):build.validate(c,self.taxonomy)
        for invalid in [None,'Unverified claim.',[''],[1]]:
            with self.subTest(uncertainties=invalid):
                c=copy.deepcopy(self.catalog)
                c['papers'][0]['classification']['uncertainties']=invalid
                with self.assertRaises(AssertionError):build.validate(c,self.taxonomy)

    def test_readme_topics_partition_all_records_and_entries_never_repeat(self):
        papers=self.catalog['papers']
        grouped=[p['id'] for topic in self.taxonomy['topics']
                 for p in build.topic_entries(papers,topic['id'])]
        self.assertEqual(len(grouped),len(set(grouped)))
        self.assertEqual(set(grouped),{p['id'] for p in papers})
        readme=build.outputs(self.catalog,self.taxonomy,'')[ROOT/'README.md']
        bibliography_lines=[line for line in readme.splitlines()
                            if any(line==build.readme_entry(p) for p in papers)]
        self.assertEqual(len(bibliography_lines),len(papers))
        for paper in papers:
            with self.subTest(paper=paper['id']):
                self.assertEqual(readme.count(build.readme_entry(paper)),1)

    def test_a_paper_has_one_readme_placement_and_multiple_website_memberships(self):
        paper=next(p for p in self.catalog['papers'] if len(p['classification']['topics'])>1)
        placed=[topic['id'] for topic in self.taxonomy['topics']
                if paper['id'] in {p['id'] for p in build.topic_entries([paper],topic['id'])}]
        self.assertEqual(placed,[paper['classification']['readme_topic']])
        website_memberships=[topic['id'] for topic in self.taxonomy['topics']
                             if topic['id'] in paper['classification']['topics']]
        self.assertGreater(len(website_memberships),1)
        self.assertEqual(set(website_memberships),set(paper['classification']['topics']))

    def test_csv_preserves_readme_website_topics_and_review_evidence(self):
        generated=build.outputs(self.catalog,self.taxonomy,'')
        rows=list(csv.DictReader(io.StringIO(generated[ROOT/'site/papers.csv'])))
        by_id={p['id']:p for p in self.catalog['papers']}
        self.assertEqual(len(rows),len(self.catalog['papers']))
        self.assertEqual({row['id'] for row in rows},set(by_id))
        for row in rows:
            paper=by_id[row['id']]
            c=paper['classification']
            self.assertEqual(json.loads(row['date_evidence']) if row['date_evidence'] else None,paper.get('date_evidence'))
            self.assertEqual(row['readme_topic'],c['readme_topic'])
            self.assertEqual(row['topics'].split('; '),c['topics'])
            self.assertEqual(row['topic_checked'],c['checked'])
            self.assertEqual(row['topic_reason'],c['summary_reason'])
            self.assertEqual(json.loads(row['topic_evidence']),c['topic_reasons'])
            self.assertEqual(json.loads(row['topic_sources']),c['sources'])

    def test_per_paper_review_is_exported_to_markdown_and_website(self):
        generated=build.outputs(self.catalog,self.taxonomy,'')
        review=generated[ROOT/'docs/TOPIC_REVIEW.md']
        self.assertIn(ROOT/'site/topic-review.html',generated)
        for paper in self.catalog['papers']:
            self.assertIn('**Record:** `'+paper['id']+'`',review)
            self.assertIn(paper['classification']['summary_reason'],review)
            self.assertIn(paper['classification']['sources'][0]['url'],review)


class DiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.rows,self.total=discover.parse_atom((ROOT/'tests/fixtures/arxiv.xml').read_bytes())
        self.curated=json.loads((ROOT/'data/papers.json').read_text())['papers']

    def test_atom_versions_and_entities(self):
        self.assertEqual(self.rows[0]['arxiv'],'2608.25927')
        self.assertIn('&',self.rows[1]['title'])
        self.assertEqual(self.total,2)

    def test_error_feed_not_a_paper(self):
        bad=b'<feed xmlns="http://www.w3.org/2005/Atom"><entry><id>http://arxiv.org/api/errors#bad_query</id></entry></feed>'
        with self.assertRaises(ValueError):discover.parse_atom(bad)

    def test_known_records_not_added_and_run_idempotent(self):
        a,counts=discover.merge_candidates([],self.rows,self.curated,'2026-10-21')
        self.assertEqual(counts['already_curated'],1)
        self.assertEqual(len(a),1)
        b,counts=discover.merge_candidates(a,self.rows,self.curated,'2026-10-22')
        self.assertEqual(a,b)
        self.assertEqual(counts['new'],0)

    def test_new_version_preserves_rejection(self):
        a,_=discover.merge_candidates([],self.rows,self.curated,'2026-10-21')
        a[0].update(status='rejected',decision_reason='仅供测试')
        new={**self.rows[1],'title':'Changed title','updated':'2026-10-23'}
        b,counts=discover.merge_candidates(a,[new],self.curated,'2026-10-23')
        self.assertEqual(len(b),1)
        self.assertEqual(b[0]['status'],'rejected')
        self.assertEqual(b[0]['decision_reason'],'仅供测试')
        self.assertEqual(b[0]['discovered_at'],'2026-10-21')
        self.assertEqual(counts['updated'],1)

    def test_title_alias_deduplication(self):
        row={**self.rows[1],'source_type':'github','arxiv':None,'id':'project-test','url':'https://example.org/project','title':'Fixture Only Executable Worlds & Physical Reasoning'}
        a,counts=discover.merge_candidates([],[self.rows[1],row],[],'2026-10-21')
        self.assertEqual(len(a),1)
        self.assertEqual(a[0]['arxiv'],'2610.99999')
        self.assertIn('https://example.org/project',a[0]['related_urls'])

    def test_transient_http_retry(self):
        error=urllib.error.HTTPError('https://example.org',429,'Rate limit',{},None)
        class Response:
            def __enter__(self):return self
            def __exit__(self,*args):pass
            def read(self):return b'ok'
        with patch('time.sleep') as sleep:
            from unittest.mock import Mock
            opener=Mock(side_effect=[error,Response()])
            self.assertEqual(discover.fetch('https://example.org',opener=opener,sleep=sleep),b'ok')
            self.assertEqual(opener.call_count,2)

    def test_all_sources_fail_preserves_inbox(self):
        with tempfile.TemporaryDirectory() as temp:
            output=Path(temp)/'inbox.json';report=Path(temp)/'report.json'
            content='{"schema_version":1,"candidates":[]}\n';output.write_text(content)
            with patch.object(sys,'argv',['discover.py','--skip-github','--output',str(output),'--report',str(report)]), patch.object(discover,'fetch',side_effect=OSError('offline')), patch.object(discover.time,'sleep'):
                with self.assertRaises(SystemExit):discover.main()
            self.assertEqual(output.read_text(),content)
            self.assertEqual(json.loads(report.read_text())['status'],'failed')


if __name__=='__main__':unittest.main()
