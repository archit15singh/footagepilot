import array
import math
import unittest
from footagepilot.reference import instagram_url,audio_events,cut_alignment

class ReferenceTests(unittest.TestCase):
    def test_single_instagram_url(self):
        self.assertEqual(instagram_url('https://www.instagram.com/name/reel/ABC_123/?x=y'),'https://www.instagram.com/name/reel/ABC_123/')
        for value in ['https://evil.test/p/abc/','http://instagram.com/p/abc/','https://instagram.com/saved/','https://instagram.com.evil.test/p/x/','https://x@instagram.com/p/x/','https://instagram.com:8080/p/x/']:
            with self.assertRaises(ValueError):instagram_url(value)
    def test_onsets_match_known_pulses_and_silence(self):
        data=array.array('f',[0.] * 24000)
        for start in (8000,16000):
            for i in range(start,start+160):data[i]=.7*math.sin((i-start)*.4)
        energy,events=audio_events(data)
        self.assertEqual(len(events),2)
        self.assertLess(abs(events[0]['time']-1),.03)
        self.assertLess(abs(events[1]['time']-2),.03)
        self.assertEqual(audio_events(array.array('f',[0.]*8000))[1],[])
        aligned=cut_alignment([1.02,2.05],events)
        self.assertAlmostEqual(aligned[0]['offset_seconds'],.02,places=2)
        self.assertIsNone(cut_alignment([1],[])[0]['offset_seconds'])
