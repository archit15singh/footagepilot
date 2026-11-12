import hashlib,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from footagepilot.recreate import framing_options,review_plan_framing,recreate,finish_resolve

class RecreationFramingTests(unittest.TestCase):
    def test_invalid_options_reject_before_run_creation(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);spec=root/'spec.json'
            for value in (None,False,{'shots':[]},{'shots':[True]},{'shots':[1,1]},{'axis':'z'},{'extra':1}):
                spec.write_text(json.dumps({'framing_review':value}))
                with self.assertRaises(ValueError):recreate(spec,root/'run',backend='resolve')
                self.assertFalse((root/'run').exists())
            with self.assertRaises(ValueError):framing_options({'framing_review':{}},'edits')
            self.assertIsNone(framing_options({},'resolve'))

    def test_bookends_skip_contain_and_keep_selected_fill(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'source.mp4').write_bytes(b'source');manifest=root/'edit.json'
            manifest.write_text(json.dumps({'shots':[{'path':'source.mp4','duration':1,'fit':'contain'},{'path':'source.mp4','duration':1}]}))
            with patch('footagepilot.recreate.refine_framing',return_value={'manifest':'reviewed.json'}) as refine:
                result=review_plan_framing(manifest,{'shots':'bookends','axis':'y'},root/'review')
                self.assertEqual(refine.call_args.args[1],[2]);self.assertEqual(result['skipped_shots'],[1])
            manifest.write_text(json.dumps({'shots':[{'path':'source.mp4','duration':1,'fit':'contain'}]}))
            with patch('footagepilot.recreate.refine_framing') as refine:
                result=review_plan_framing(manifest,{'shots':'bookends','axis':'y'},root/'contained')
                refine.assert_not_called();self.assertEqual(result['status'],'skipped-contained-bookends')
            manifest.write_text('{"shots":[]}')
            with self.assertRaises(ValueError):review_plan_framing(manifest,{'shots':'bookends','axis':'y'},root/'bad')

    def test_reviewed_manifest_prepared_and_failure_stops_preparation(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);spec=root/'spec.json';spec.write_text(json.dumps({'reference':'ref.json','assets':[],'music':'music.wav','framing_review':{}}))
            reviewed=root/'reviewed.json';reviewed.write_text('{}');job=root/'job.json';job.write_text('{}')
            with patch('footagepilot.recreate.check_sources',return_value={'needs_research':False}),patch('footagepilot.recreate.plan_visual',return_value={'manifest':'initial.json'}),patch('footagepilot.recreate.review_plan_framing',return_value={'manifest':str(reviewed)}),patch('footagepilot.resolve.prepare',return_value={'job':str(job),'console':'console.lua'}) as prepare:
                result=recreate(spec,root/'run',backend='resolve')
                self.assertEqual(prepare.call_args.args[0],reviewed)
                self.assertEqual(result['native_manifest_sha256'],hashlib.sha256(reviewed.read_bytes()).hexdigest())
                self.assertNotIn('framing_review',json.loads((root/'run/visual-spec.json').read_text()))
            with patch('footagepilot.recreate.check_sources',return_value={'needs_research':False}),patch('footagepilot.recreate.plan_visual',return_value={'manifest':'initial.json'}),patch('footagepilot.recreate.review_plan_framing',side_effect=ValueError('crop review failed')),patch('footagepilot.resolve.prepare') as prepare:
                with self.assertRaisesRegex(ValueError,'crop review failed'):recreate(spec,root/'failed',backend='resolve')
                prepare.assert_not_called()
            state=json.loads((root/'failed/run.json').read_text());self.assertEqual(state['stages'][-1]['status'],'failed')
            reviewed.write_text('changed')
            with self.assertRaisesRegex(ValueError,'Reviewed native manifest changed'):finish_resolve(root/'run',root/'movie.mp4',root/'project.drp')
