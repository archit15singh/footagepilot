import unittest
from footagepilot.source_previews import preview_windows


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
