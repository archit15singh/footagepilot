import unittest
from evals.caption_quality import evaluate
from footagepilot.graphics import word_captions_for_cut


class CaptionQuality(unittest.TestCase):
    def test_real_recording_improves_without_content_or_timing_regression(self):
        self.assertEqual(evaluate()['gate'],'passed')

    def test_long_pause_and_removed_speech_are_not_bridged(self):
        words=[{'text':'First.','start':0,'end':1},{'text':'Next','start':2,'end':2.5},{'text':'phrase.','start':2.5,'end':3},{'text':'Rejected','start':4,'end':5},{'text':'Last.','start':6,'end':7}]
        cues=word_captions_for_cut(words,[[0,3],[6,7]])
        self.assertEqual([c['text'] for c in cues],['First.','Next phrase.','Last.'])
        self.assertEqual(cues[-1],{'text':'Last.','start':3,'end':4})

    def test_dense_speech_and_long_tokens_are_preserved(self):
        words=[{'text':'x'*80,'start':0,'end':.1},{'text':'done.','start':.1,'end':.2}]
        cues=word_captions_for_cut(words,[[0,.2]])
        self.assertEqual(' '.join(c['text'] for c in cues),'x'*80+' done.')
