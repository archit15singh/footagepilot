import json
import array
import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from footagepilot.resolve import lua,prepare,verify,similarity,audio_match

class ResolveTests(unittest.TestCase):
    def setUp(self):
        gate=patch("footagepilot.learning.check_sources",return_value={"needs_research":False})
        gate.start();self.addCleanup(gate.stop)

    def test_correspondence_rejects_constant_slate_and_reversed_structure(self):
        source=[.05,.2,.4,.8,.6]
        self.assertAlmostEqual(similarity(source,source)[1],1)
        self.assertLess(similarity(source,[.5]*5)[1],.9)
        self.assertLess(similarity(source,list(reversed(source)))[1],.9)
        with self.assertRaises(ValueError):similarity([],[])

    def test_audio_correspondence_rejects_wrong_gain_despite_same_waveform(self):
        a=array.array('f',[.2*math.sin(i*.1) for i in range(1000)])
        b=array.array('f',[x*.01 for x in a])
        with patch('footagepilot.resolve.raw',side_effect=[a.tobytes(),b.tobytes()]),patch('footagepilot.resolve.binary',return_value='ffmpeg'):
            with self.assertRaisesRegex(ValueError,'waveform does not match'):audio_match(Path('a'),Path('b'))

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
