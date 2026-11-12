import tempfile,unittest
from pathlib import Path
from footagepilot.visual import compile_plan,schema,title_sizes

class PlannedTypeTests(unittest.TestCase):
    def fixture(self,root):
        (root/'a.jpg').touch();(root/'b.jpg').touch();(root/'music.wav').touch()
        spec={'native_backend':'resolve','assets':[{'id':'a','path':'a.jpg'},{'id':'b','path':'b.jpg'}],'music':'music.wav','music_timing':{'bpm':120,'provenance':'authored'},'min_seconds':2,'max_seconds':2,'title_sizes':[28,40]}
        plan={'title':'A day','title_size':40,'title_bold':True,'shots':[{'asset_id':a,'beats':2,'fit':'fill','zoom':0} for a in ('a','b')],'panels':[],'title_sequence':[{'text':'A day','start_beat':0,'beats':2,'y':.4},{'text':'outside','start_beat':1,'beats':1,'y':.6}]}
        return spec,plan

    def test_style_reaches_every_native_sequence_line(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);spec,plan=self.fixture(root);edit=compile_plan(plan,spec,root)
            self.assertEqual([(t['size'],t['bold']) for t in edit['titles']],[(40,True),(40,True)])
            contract=schema(['a','b'],video_ranges=True,sizes=[28,40]);self.assertEqual(contract['properties']['title_size']['enum'],[28,40]);self.assertIn('title_bold',contract['required'])

    def test_unsupported_size_and_nonboolean_weight_reject(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);spec,plan=self.fixture(root)
            for change in ({'title_size':41},{'title_size':True},{'title_bold':'Bold'}):
                with self.assertRaisesRegex(ValueError,'size/weight'):compile_plan({**plan,**change},spec,root)
            for sizes in ([0],[True],[28,28],[73]):
                with self.assertRaises(ValueError):title_sizes({**spec,'title_sizes':sizes})

    def test_old_recorded_plans_keep_their_original_type(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);spec,plan=self.fixture(root);plan.pop('title_size');plan.pop('title_bold')
            self.assertEqual([(t['size'],t['bold']) for t in compile_plan(plan,spec,root)['titles']],[(28,False),(28,False)])
