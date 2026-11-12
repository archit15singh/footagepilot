import unittest
from unittest.mock import patch
from pathlib import Path
from tempfile import TemporaryDirectory
from footagepilot.source_previews import preview_windows,preview_filter,window_sheet


class SourcePreviewTests(unittest.TestCase):
    def test_long_video_has_three_bounded_temporal_strips(self):
        windows=preview_windows(30)
        self.assertEqual(len(windows),3)
        self.assertEqual(windows[0]['sample_times'],[0,1,2,3,4])
        self.assertAlmostEqual(windows[-1]['end'],29.9)
        self.assertTrue(all(w['end']-w['start']<=4.000001 for w in windows))
        self.assertTrue(all(len(w['sample_times'])==5 for w in windows))

    def test_short_source_and_explicit_window_validation(self):
        self.assertEqual(len(preview_windows(2)),1)
        self.assertEqual(preview_windows(.05)[0]['sample_times'],[0])
        self.assertEqual(preview_windows(20,[{'start':8,'end':10}])[0]['sample_times'],[8,8.5,9,9.5,10])
        for rows in ([],[{'start':1,'end':9}],[{'start':2,'end':1}],[{'start':0,'end':float('nan')}],[{'start':0,'end':20}]):
            with self.assertRaises(ValueError):preview_windows(20,rows)

    def test_crop_preview_preserves_original_and_labels_alternative(self):
        with TemporaryDirectory() as td:
            target=Path(td)/'strip.jpg'
            def render(command):Path(command[-1]).write_bytes(b'jpeg')
            with patch('footagepilot.source_previews.binary',return_value='ffmpeg'),patch('footagepilot.source_previews.run',side_effect=render) as calls:
                row=window_sheet(Path('source.mp4'),{'sample_times':[1,2]},target,'16:9')
            self.assertEqual(row['canvas_preview_aspect'],'16:9')
            self.assertEqual(len(row['frame_sha256']),2)
            self.assertEqual(len(row['rows']),2)
            self.assertIn('crop=224:126',calls.call_args_list[0].args[0][-2])
            self.assertIn('vstack=inputs=2',calls.call_args_list[0].args[0][-2])
        self.assertNotIn('split=',preview_filter())
        for aspect in ('9:16','16:9','1:1','4:5'):self.assertIn('vstack',preview_filter(aspect))
        with self.assertRaisesRegex(ValueError,'Unsupported crop'):preview_filter('bad')
