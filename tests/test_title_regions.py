import unittest
from footagepilot.resolve import title_timing_band

class TitleRegionTests(unittest.TestCase):
    def job(self):return {'height':1920,'titles':[{'start':0,'frames':53,'y':.43,'size':40},{'start':27,'frames':26,'y':.58,'size':40}]}

    def test_simultaneous_titles_have_disjoint_stable_regions(self):
        job=self.job();first=title_timing_band(job,0,284);second=title_timing_band(job,1,284)
        self.assertIsNotNone(first);self.assertIsNotNone(second)
        self.assertEqual(first[1],second[0]);self.assertLess(first[0],.43*284);self.assertGreater(second[1],.58*284)

    def test_same_centre_cannot_be_presented_as_isolated(self):
        job=self.job();job['titles'][1]['y']=.43
        self.assertIsNone(title_timing_band(job,0,284));self.assertIsNone(title_timing_band(job,1,284))

    def test_nonoverlapping_events_do_not_steal_each_others_region(self):
        job=self.job();job['titles'][1].update(start=53,y=.43)
        self.assertIsNotNone(title_timing_band(job,0,284))
        self.assertEqual(title_timing_band(job,0,284),title_timing_band(job,1,284))
        # At the shared boundary the next legitimate title cannot be separated.
        self.assertIsNone(title_timing_band(job,0,284,number=53))
