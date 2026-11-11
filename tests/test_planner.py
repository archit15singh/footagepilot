import unittest
from spliceforge.planner import validate_plan
from spliceforge.graphics import word_captions_for_cut

class WordPlans(unittest.TestCase):
    def test_rejects_invented_or_reordered_words(self):
        for first,last in [(0,3),(-1,0),(True,1),(2,1)]:
            with self.assertRaises(ValueError):validate_plan({'title':'Test','rationale':'Test','ranges':[{'first_word':first,'last_word':last,'reason':'Test'}]},[{},{}])
    def test_caption_times_follow_words_after_cut(self):
        words=[{'text':'Remove','start':0,'end':1},{'text':'Keep','start':2,'end':2.4},{'text':'this.','start':2.6,'end':3}]
        self.assertEqual(word_captions_for_cut(words,[[1.9,3.1]]),[{'text':'Keep this.','start':.10000000000000009,'end':1.1}])

    def test_multiple_ranges_cannot_overlap_or_reorder(self):
        with self.assertRaises(ValueError):
            validate_plan({'title':'Test','rationale':'Test','ranges':[{'first_word':0,'last_word':1,'reason':'A'},{'first_word':1,'last_word':2,'reason':'B'}]},[{},{},{}])
