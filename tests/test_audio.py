from pathlib import Path
import unittest
from unittest.mock import patch
from footagepilot.audio import mix_audio


class AudioSettings(unittest.TestCase):
    def test_invalid_controls_fail_before_external_work(self):
        for settings in [{'music_ducking':'false'},{'music_ducking':0},{'music_fade_seconds':True},{'music_fade_seconds':-1},{'music_fade_seconds':float('nan')},{'music_fade_seconds':11}]:
            with self.subTest(settings=settings),patch('footagepilot.audio.run') as run:
                with self.assertRaises(ValueError):mix_audio(Path('missing.mp4'),Path('out.mp4'),settings,10)
                run.assert_not_called()
