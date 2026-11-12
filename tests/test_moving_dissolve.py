import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from footagepilot.resolve import prepare
from footagepilot.edits import render_edit
from footagepilot.visual import transitions_for

class MovingDissolveTests(unittest.TestCase):
    def test_prepared_handle_ends_where_main_excerpt_begins(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'clip.mp4').write_bytes(b'video');manifest=root/'edit.json';manifest.write_text(json.dumps({'shots':[{'path':'clip.mp4','source_start':1,'duration':2},{'path':'clip.mp4','source_start':4,'duration':2}],'transitions':[{'after_shot':0,'filter':'transition_moving_dissolve','duration':.4}]}))
            def fake_run(cmd):Path(cmd[-1]).write_bytes(b'prepared')
            with patch('footagepilot.learning.check_sources',return_value={'needs_research':False}),patch('footagepilot.resolve.probe',return_value={'streams':[{'codec_type':'video','duration':'10'}]}),patch('footagepilot.resolve.run',side_effect=fake_run),patch('footagepilot.resolve.binary',return_value='ffmpeg'):
                prepare(manifest,root/'job')
            j=json.loads((root/'job/job.json').read_text());t=j['transitions'][0]
            self.assertEqual((t['start'],t['frames'],t['source_start']),(48,12,3.6));self.assertEqual(t['source_start']+t['frames']/j['fps'],j['shots'][1]['source_start'])

    def test_no_handle_or_artificial_zoom_rejected_before_encoding(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'clip.mp4').write_bytes(b'video');manifest=root/'edit.json'
            (root/'still.jpg').write_bytes(b'image')
            for name,start,zoom in [('clip.mp4',0,0),('clip.mp4',.1,0),('clip.mp4',2,.025),('still.jpg',0,0)]:
                manifest.write_text(json.dumps({'shots':[{'path':'clip.mp4','duration':2},{'path':name,'source_start':start,'zoom':zoom,'duration':2}],'transitions':[{'after_shot':0,'filter':'transition_moving_dissolve','duration':.4}]}))
                with patch('footagepilot.learning.check_sources',return_value={'needs_research':False}),patch('footagepilot.resolve.probe',return_value={'streams':[{'codec_type':'video','duration':'10'}]}),patch('footagepilot.resolve.binary',return_value='ffmpeg'),patch('footagepilot.resolve.run') as render:
                    with self.assertRaisesRegex(ValueError,'pre-cut source handles'):prepare(manifest,root/'job')
                    render.assert_not_called()
                self.assertFalse((root/'job').exists())

    def test_opt_in_and_edits_backend_boundary(self):
        self.assertNotIn('moving_dissolve',transitions_for({'native_backend':'resolve'}))
        self.assertIn('moving_dissolve',transitions_for({'native_backend':'resolve','moving_transitions':True}))
        with self.assertRaises(ValueError):transitions_for({'native_backend':'edits','moving_transitions':True})
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'a.mp4').touch();p=root/'edit.json';p.write_text(json.dumps({'shots':[{'path':'a.mp4','duration':2}]*2,'transitions':[{'after_shot':0,'filter':'transition_moving_dissolve','duration':.4}]}))
            with patch('footagepilot.edits.EditsClient') as client:
                with self.assertRaisesRegex(ValueError,'require Resolve'):render_edit(p,root/'output.mp4')
                client.assert_not_called()
