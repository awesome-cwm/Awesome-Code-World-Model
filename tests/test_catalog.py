"""防止分类漂移、误去重、候选覆盖和生成内容丢失。"""
import copy
import importlib.util
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
        p=next(p for p in self.catalog['papers'] if p['id']=='streaming-cwm')
        self.assertIsNone(p['published'])
        self.assertNotIn('year =',build.bibtex(p))

    def test_public_repository_links_are_used_for_readme_and_catalog(self):
        repository='awesome-cwm/Awesome-Code-World-Model'
        generated=build.outputs(self.catalog,self.taxonomy,repository)
        self.assertIn('https://awesome-cwm.github.io/Awesome-Code-World-Model/',generated[ROOT/'README.md'])
        self.assertIn('https://awesome-cwm.github.io/Awesome-Code-World-Model/?area=world-construction&direction=reconstruction&tags=physical-consistency',generated[ROOT/'README.md'])
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

    def test_classic_entry_keeps_clickable_links(self):
        p=next(p for p in self.catalog['papers'] if p['id']=='code-world-model')
        rendered=build.inline_markdown(build.readme_entry(p))
        self.assertTrue(rendered.startswith('<strong>'))
        self.assertIn('<a href="https://arxiv.org/abs/2608.25927">',rendered)

    def test_readme_html_only_allows_safe_layout(self):
        rendered=build.safe_readme_html('<div onclick="bad()"><img src="site/banner.svg" onerror="bad()"><a href="javascript:bad()">bad</a></div>')
        self.assertNotIn('onclick',rendered)
        self.assertNotIn('onerror',rendered)
        self.assertNotIn('javascript:',rendered)
        self.assertIn('src="banner.svg"',rendered)

    def test_taxonomy_v2_matches_maintainer_design(self):
        self.assertEqual([a['name'] for a in self.taxonomy['research_areas']], [
            'World Construction', 'World Dynamics & Simulation',
            'World Interaction & Control', 'World Reasoning & Learning',
            'Modeling & Systems', 'Resources & Analysis'])
        self.assertEqual(sum(len(a['directions']) for a in self.taxonomy['research_areas']),22)
        self.assertEqual([d['name'] for d in self.taxonomy['tag_dimensions']], [
            'Research Challenges', 'Memory & State', 'Control & Interaction',
            'Representation & Output', 'Methods & Training', 'Runtime & Efficiency',
            'World Setting & Domain', 'Evaluation Focus'])

    def test_primary_area_is_required_and_single(self):
        for invalid in [None, [], ['world-construction','resources-analysis'], 'unknown']:
            with self.subTest(area=invalid):
                c=copy.deepcopy(self.catalog)
                c['papers'][0]['classification']['area']=invalid
                with self.assertRaises(AssertionError):build.validate(c,self.taxonomy)
        c=copy.deepcopy(self.catalog)
        del c['papers'][0]['classification']
        with self.assertRaises(AssertionError):build.validate(c,self.taxonomy)

    def test_direction_must_belong_to_primary_area_but_can_be_unspecified(self):
        c=copy.deepcopy(self.catalog)
        c['papers'][0]['classification'].update(area='world-construction',direction='benchmark')
        with self.assertRaises(AssertionError):build.validate(c,self.taxonomy)
        c['papers'][0]['classification']['direction']=None
        self.assertTrue(build.validate(c,self.taxonomy))

    def test_auxiliary_tags_require_valid_unique_values_in_their_own_dimension(self):
        for invalid in [[], ['unknown'], ['explicit-state'], ['physical-consistency','physical-consistency']]:
            with self.subTest(tags=invalid):
                c=copy.deepcopy(self.catalog)
                classification=c['papers'][0]['classification']
                classification['tags']={d['id']:[] for d in self.taxonomy['tag_dimensions']}
                classification['tags']['research_challenges']=invalid
                with self.assertRaises(AssertionError):build.validate(c,self.taxonomy)

    def test_primary_readme_sections_partition_all_records_once(self):
        grouped=[p['id'] for area in self.taxonomy['research_areas']
                 for p in build.research_entries(self.catalog['papers'],area['id'])]
        self.assertEqual(len(grouped),len(set(grouped)))
        self.assertEqual(set(grouped),{p['id'] for p in self.catalog['papers']})

    def test_csv_preserves_single_primary_area_and_grouped_auxiliary_tags(self):
        import csv,io
        generated=build.outputs(self.catalog,self.taxonomy,'')
        rows=list(csv.DictReader(io.StringIO(generated[ROOT/'site/papers.csv'])))
        by_id={p['id']:p for p in self.catalog['papers']}
        for row in rows:
            c=by_id[row['id']]['classification']
            self.assertEqual(row['research_area'],c['area'])
            self.assertEqual(row['research_direction'],c['direction'] or '')
            self.assertEqual(json.loads(row['auxiliary_tags']),c['tags'])


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
