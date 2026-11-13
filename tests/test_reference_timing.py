import json
from pathlib import Path
import tempfile
import unittest

from footagepilot.__main__ import binary
from footagepilot.reference import analyze_reference, execute
from footagepilot.reference_evidence import select_frames, timing_for_frames
from footagepilot.reference_timing import decoded_frames, estimate_pulse


class ReferenceTimingTests(unittest.TestCase):
    def test_pulse_requires_repeated_support(self):
        def estimate(times):
            return estimate_pulse([{'time': t} for t in times])

        self.assertEqual(estimate([])['status'], 'inconclusive')
        self.assertEqual(estimate([.2,.41,.92,1.75,1.93,2.71,3.65])['status'], 'inconclusive')
        pulse = estimate([.2 + i*.5 for i in range(10)])
        self.assertEqual(pulse['bpm'], 120)
        self.assertEqual(pulse['times'], [.2,.7,1.2,1.7,2.2,2.7,3.2,3.7,4.2,4.7])

    def test_microseconds_survive_rounded_display_time(self):
        frames = decoded_frames(
            'frame:0 pts:10000001 pts_time:10\nlavfi.scd.mafd=0.000\nlavfi.scd.score=0.000\n'
            'frame:1 pts:10040002 pts_time:10.04\nlavfi.scd.mafd=5.000\nlavfi.scd.score=4.000\n'
        )
        self.assertEqual(frames[0]['time'], 10.000001)
        self.assertEqual(frames[1]['time'], 10.040002)
        self.assertEqual(frames[1]['change_score'], 4)
        with self.assertRaisesRegex(ValueError, 'Missing per-frame'):
            decoded_frames('frame:0 pts:0 pts_time:0\n')

    def test_variable_rate_video_with_delayed_audio(self):
        try:
            ff = binary('ffmpeg')
            binary('ffprobe')
        except ValueError as error:
            self.skipTest(str(error))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / 'known.mp4'
            output = root / 'report'
            execute([ff, '-v', 'error', '-f', 'lavfi', '-i',
                     "color=black:s=160x288:r=25:d=6,drawbox=color=white:t=fill:"
                     "enable='gte(t,1.2)*lt(t,2.76)+gte(t,4.2)',select='not(eq(mod(n,7),3))'",
                     '-itsoffset', '0.2', '-f', 'lavfi', '-i',
                     r'aevalsrc=if(lt(mod(t\,0.5)\,0.022)\,0.8*sin(2*PI*500*t)\,0):s=48000:d=5.8',
                     '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-fps_mode', 'vfr', '-c:a', 'alac', source])
            analyze_reference(str(source), output)
            data = json.loads((output/'analysis.json').read_text())
            self.assertEqual(data['scene_changes'], [1.2, 2.76, 4.2])
            self.assertEqual(len(data['frame_timeline']), 129)
            self.assertEqual([row['time'] for row in data['frame_timeline'][:5]], [0,.04,.08,.16,.2])
            self.assertEqual(data['audio']['pulse']['bpm'], 120)
            self.assertEqual(data['audio']['onsets'][0]['time'], .2)
            self.assertEqual([row['cut_minus_pulse_seconds'] for row in data['transitions']], [0,.06,0])
            evidence = select_frames(data, output)
            timing = timing_for_frames(data, evidence)
            self.assertEqual(len(timing['changes']), 3)
            for cut in data['transitions']:
                index = cut['frame_index']
                self.assertEqual(data['frame_timeline'][index]['time'], cut['time'])
                neighbors = [frame for frame in data['frames'] if abs(frame['frame_index']-index)<=1]
                self.assertEqual([frame['frame_index'] for frame in neighbors], [index-1,index,index+1])
                # The middle frame's pixels should depict the incoming shot.
                levels = [execute([ff, '-v', 'error', '-i', output/frame['file'],
                                   '-vf', 'scale=1:1,format=gray', '-f', 'rawvideo', '-']).stdout[0]
                          for frame in neighbors]
                self.assertGreater(abs(levels[0]-levels[1]), 150)
                self.assertAlmostEqual(levels[1], levels[2], delta=5)
