import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from footagepilot.resolve import prepare
from footagepilot.edits import render_edit


class VideoRangeTests(unittest.TestCase):
    def test_resolve_range_overrun_rejected_before_preparation(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);(p/'clip.mp4').write_bytes(b'video');manifest=p/'edit.json';manifest.write_text(json.dumps({'shots':[{'path':'clip.mp4','source_start':4,'duration':2}]}))
            with patch('footagepilot.learning.check_sources',return_value={'needs_research':False}),patch('footagepilot.resolve.probe',return_value={'streams':[{'codec_type':'video','duration':'5'}]}),patch('footagepilot.resolve.run') as render:
                with self.assertRaisesRegex(ValueError,'range exceeds'):prepare(manifest,p/'output')
                render.assert_not_called()
            self.assertFalse((p/'output').exists())

    def test_edits_rejects_nonzero_range_before_native_mutation(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);(p/'clip.mp4').write_bytes(b'video');manifest=p/'edit.json';manifest.write_text(json.dumps({'shots':[{'path':'clip.mp4','source_start':1,'duration':2}]}))
            with patch('footagepilot.edits.EditsClient') as native:
                with self.assertRaisesRegex(ValueError,'use Resolve'):render_edit(manifest,p/'output.mp4')
                native.assert_not_called()

    def test_frame_rounding_cannot_create_overlapping_panels(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);(p/'a.jpg').write_bytes(b'image');manifest=p/'edit.json'
            manifest.write_text(json.dumps({'shots':[{'path':'a.jpg','duration':1}],'overlays':[{'path':'a.jpg','start':at,'duration':.12,'x':.25,'y':.25,'width':.5,'height':.5} for at in (.02,.14)]}))
            def fake_run(cmd):Path(cmd[-1]).write_bytes(b'prepared')
            with patch('footagepilot.learning.check_sources',return_value={'needs_research':False}),patch('footagepilot.resolve.probe',return_value={'streams':[{'codec_type':'video'}]}),patch('footagepilot.resolve.run',side_effect=fake_run),patch('footagepilot.resolve.binary',return_value='ffmpeg'):
                prepare(manifest,p/'output')
            job=json.loads((p/'output/job.json').read_text())
            first,second=job['overlays']
            self.assertEqual(first['start']+first['frames'],second['start'])
