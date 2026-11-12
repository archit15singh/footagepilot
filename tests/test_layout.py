import unittest
from unittest.mock import patch
from footagepilot.layout import rectangle,validate_panels
from footagepilot.resolve import expected_frame


class LayoutTests(unittest.TestCase):
    def test_staggered_rectangles_allow_incomplete_rows_and_different_aspects(self):
        rows=[{'start':i*.5,'duration':3-i*.5,'x':(i+.5)/3,'y':.15,'width':1/3,'height':.3} for i in range(3)]
        self.assertEqual(len(validate_panels(rows)),3)
        self.assertEqual(rectangle({'x':.5,'y':.25,'width':1,'height':.5}),(0.,0.,1.,.5))
        with self.assertRaisesRegex(ValueError,'overlap'):validate_panels(rows+[rows[0]])
        with self.assertRaisesRegex(ValueError,'exceeds canvas'):rectangle({'x':.1,'y':.1,'width':.5,'height':.5})
        # Same space can be reused at a later, non-overlapping time.
        validate_panels([rows[0],{**rows[0],'start':3}])

    def test_expected_composite_leaves_empty_background_before_panel_arrival(self):
        job={'fps':30,'shots':[{'path':'main','start':0,'frames':90}],'backgrounds':[{'start':0,'frames':90}],'overlays':[{'path':'panel','start':30,'frames':60,'x':.25,'y':.25,'width':.5,'height':.5}]}
        def frame(path,n,fps,w,h):return ([1.] if path=='panel' else [.5])*(w*h*3)
        with patch('footagepilot.resolve.sample_frame',side_effect=frame):
            before=expected_frame(job,15,4,4);after=expected_frame(job,45,4,4)
        self.assertEqual(before,[0.]*48)
        self.assertEqual(after[:12],[1.]*6+[0.]*6)
        self.assertEqual(after[24:],[0.]*24)

    def test_resolve_plan_preserves_title_timing_and_partial_layout(self):
        import tempfile
        from pathlib import Path
        from footagepilot.visual import compile_plan
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'a.jpg').touch();(root/'score.wav').touch()
            spec={'native_backend':'resolve','assets':[{'id':'a','path':'a.jpg'}],'music':'score.wav','music_timing':{'bpm':120,'offset':0,'provenance':'authored'},'min_seconds':2,'max_seconds':8}
            panel={'asset_id':'a','start_beat':4,'beats':4,'x':.2,'y':.2,'width':.3,'height':.2}
            plan={'title':'Travel','title_start_beat':2,'title_beats':2,'title_y':.5,'title_color':'#FFE49C','shots':[{'asset_id':'a','beats':4,'fit':'fill','zoom':0}]*2,'panels':[panel],'backgrounds':[{'start_beat':2,'beats':2},{'start_beat':4,'beats':4}]}
            result=compile_plan(plan,spec,root)
            self.assertEqual((result['titles'][0]['start'],result['titles'][0]['duration']),(1,1))
            self.assertEqual(len(result['overlays']),1);self.assertEqual(result['overlays'][0]['width'],.3)
            self.assertEqual(result['layout_backgrounds'][1]['start'],2)
