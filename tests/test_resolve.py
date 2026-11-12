import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from footagepilot.resolve import lua,prepare,verify

class ResolveTests(unittest.TestCase):
    def setUp(self):
        gate=patch("footagepilot.learning.check_sources",return_value={"needs_research":False})
        gate.start();self.addCleanup(gate.stop)

    def test_lua_strings_cannot_escape_data(self):
        value='x\"; os.execute(\"bad\"); --\n\\ café'
        encoded=lua(value)
        self.assertNotIn('"bad"',encoded)
        self.assertIn('\\034',encoded)
        self.assertIn('\\010',encoded)
        self.assertIn('\\195\\169',encoded)
        with self.assertRaises(ValueError):lua(float('nan'))

    def test_unsupported_edit_fails_before_media_preparation(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'a.jpg').write_bytes(b'input')
            manifest=root/'edit.json'
            manifest.write_text(json.dumps({'shots':[{'path':'a.jpg','duration':1}], 'titles':[{'text':'keep me','start':0,'duration':1}]}))
            with self.assertRaisesRegex(ValueError,'not yet implemented'):prepare(manifest,root/'job')
            self.assertFalse((root/'job').exists())

    def test_cumulative_frame_rounding_and_hashed_preparation(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'a.jpg').write_bytes(b'input')
            manifest=root/'edit.json';manifest.write_text(json.dumps({'fps':30,'shots':[{'path':'a.jpg','duration':.15}]*3}))
            def fake_run(cmd):Path(cmd[-1]).write_bytes(b'prepared')
            with patch('footagepilot.resolve.probe',return_value={'streams':[{'codec_type':'video'}]}),patch('footagepilot.resolve.run',side_effect=fake_run),patch('footagepilot.resolve.binary',return_value='ffmpeg'):
                prepare(manifest,root/'job')
            job=json.loads((root/'job/job.json').read_text())
            self.assertEqual(sum(s['frames'] for s in job['shots']),round(.45*30))
            self.assertEqual(job['shots'][1]['start'],job['shots'][0]['frames'])
            self.assertEqual(job['status'],'prepared-not-executed')
            self.assertIn('FOOTAGEPILOT_FAILED',(root/'job/console.lua').read_text())
            (root/'a.jpg').write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError,'inputs changed'):verify(root/'job/job.json',root/'missing.mp4',root/'verification.json')

if __name__=='__main__':unittest.main()
