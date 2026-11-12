import tempfile,unittest
from pathlib import Path
from footagepilot.visual import compile_plan

class VisualTests(unittest.TestCase):
    def test_plan_uses_only_known_assets_and_complete_collages(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'a.jpg').touch();(p/'score.wav').touch();spec={'assets':[{'id':'a','path':'a.jpg'}],'music':'score.wav','music_timing':{'bpm':120,'offset':0,'provenance':'authored'},'min_seconds':2,'max_seconds':8}
            plan={'title':'TRAVEL','shots':[{'asset_id':'a','beats':4,'fit':'fill','zoom':0}]*2,'panels':[]}
            result=compile_plan(plan,spec,p);self.assertEqual(sum(s['duration'] for s in result['shots']),4)
            bad={**plan,'shots':[{'asset_id':'unknown','beats':4,'fit':'fill','zoom':0}]*2}
            with self.assertRaises(ValueError):compile_plan(bad,spec,p)
            panel={'asset_id':'a','start_beat':0,'beats':2,'x':.25,'y':.25}
            with self.assertRaises(ValueError):compile_plan({**plan,'panels':[panel]},spec,p)
            four=[{**panel,'x':x,'y':y} for x in [.25,.75] for y in [.25,.75]]
            self.assertEqual(len(compile_plan({**plan,'panels':four},spec,p)['overlays']),4)
            with self.assertRaises(ValueError):compile_plan({**plan,'panels':four+[panel]},spec,p)
    def test_zero_tempo_rejected_without_division_error(self):
        with self.assertRaises(ValueError):
            compile_plan({}, {'assets':[],'music_timing':{'bpm':0,'provenance':'invalid'}},Path('.'))
