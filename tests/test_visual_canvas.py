import tempfile,unittest
from pathlib import Path
from footagepilot.visual import compile_plan,canvas_options,shot_budget,schema

class VisualCanvasTests(unittest.TestCase):
    def test_landscape_can_compile_without_any_on_screen_title(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'a.jpg').touch();(root/'music.wav').touch()
            spec={'native_backend':'resolve','aspect':'16:9','show_titles':False,'assets':[{'id':'a','path':'a.jpg'}],'music':'music.wav','music_timing':{'bpm':120,'provenance':'authored'},'min_seconds':2,'max_seconds':2}
            plan={'title':'Project metadata','shots':[{'asset_id':'a','beats':2,'fit':'fill','zoom':0}]*2,'panels':[],'title_sequence':[],'title_start_beat':0,'title_beats':0}
            result=compile_plan(plan,spec,root);self.assertEqual(result['aspect'],'16:9');self.assertEqual(result['titles'],[]);self.assertEqual(result['overlays'],[])
            plan['title_sequence']=[{'text':'Unexpected','start_beat':0,'beats':1,'y':.4}]
            with self.assertRaisesRegex(ValueError,'empty title sequence'):compile_plan(plan,spec,root)

    def test_options_are_explicit_and_default_compatible(self):
        self.assertEqual(canvas_options({}),('9:16',True))
        for change in ({'aspect':'cinema'},{'show_titles':'false'}):
            with self.assertRaisesRegex(ValueError,'supported canvas'):canvas_options(change)

    def test_shot_budget_is_in_schema_and_compiler(self):
        self.assertEqual(shot_budget({}),(2,30))
        self.assertEqual(schema(['a'],counts=(10,14))['properties']['shots']['minItems'],10)
        for spec in ({'min_shots':1},{'min_shots':15,'max_shots':10},{'max_shots':True}):
            with self.assertRaisesRegex(ValueError,'Shot count budget'):shot_budget(spec)
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'a.jpg').touch();(root/'music.wav').touch()
            spec={'assets':[{'id':'a','path':'a.jpg'}],'music':'music.wav','music_timing':{'bpm':120,'provenance':'authored'},'min_shots':10}
            plan={'title':'Metadata','shots':[{'asset_id':'a','beats':2,'fit':'fill','zoom':0}]*2}
            with self.assertRaisesRegex(ValueError,'requested budget'):compile_plan(plan,spec,root)
