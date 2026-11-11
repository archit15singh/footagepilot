import json,subprocess,sys,unittest
from pathlib import Path
from evals.audio_quality import BASELINE_SHA256

ROOT=Path(__file__).resolve().parents[1]


class AudioReference(unittest.TestCase):
    def test_reference_pin_matches_recorded_baseline_input(self):
        self.assertEqual(BASELINE_SHA256,json.loads((ROOT/'evals/results/audio-quality.json').read_text())['source_sha256'])

    def test_cli_requires_exactly_one_input_mode(self):
        for arguments in [[],['source.mp4','--baseline']]:
            result=subprocess.run([sys.executable,str(ROOT/'evals/audio_quality.py'),*arguments,'--work','unused'],capture_output=True,text=True)
            self.assertEqual(result.returncode,2);self.assertIn('Choose one source or --baseline',result.stderr)
