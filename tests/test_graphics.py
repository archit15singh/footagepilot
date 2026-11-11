import unittest
from footagepilot.graphics import captions_for_cut

class CaptionMapping(unittest.TestCase):
    def test_rejected_segments_absent_and_times_rebased(self):
        rows=[{'start':0,'end':2,'text':'reject this','keep':False},{'start':3,'end':6,'text':'keep these words','keep':True}]
        self.assertEqual(captions_for_cut(rows,[[3,6]]),[{'text':'keep these words','start':0,'end':3}])
    def test_groups_bounded_in_each_retained_interval(self):
        rows=[{'start':2,'end':10,'text':'one two three four five six seven eight nine ten','keep':True}]
        groups=captions_for_cut(rows,[[2,5],[7,10]])
        self.assertTrue(all(0<=c['start']<c['end']<=6 for c in groups))
        self.assertEqual(groups[-1]['end'],6)

    def test_long_token_is_wrapped_and_reported_as_groups(self):
        rows=[{'start':0,'end':5,'text':'x'*300,'keep':True}]
        groups=captions_for_cut(rows,[[0,5]])
        self.assertEqual(''.join(c['text'] for c in groups),'x'*300)
        self.assertTrue(all(len(c['text'])<=64 for c in groups))
