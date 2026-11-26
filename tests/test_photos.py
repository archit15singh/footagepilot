import math,tempfile,unittest
from pathlib import Path
from footagepilot.photos import validate_photo_film


class PhotoFilms(unittest.TestCase):
    def test_duration_accounts_for_transition_overlap(self):
        with tempfile.TemporaryDirectory() as tmp:
            photo=Path(tmp)/'photo.jpg';photo.touch();data={'photos':[{'path':str(photo),'duration':3},{'path':str(photo),'duration':4}],'transition':.5}
            self.assertEqual(validate_photo_film(data),(720,1280,6.5))

    def test_rejects_invalid_geometry_duration_transition_and_media(self):
        with tempfile.TemporaryDirectory() as tmp:
            photo=Path(tmp)/'photo.jpg';photo.touch();base={'photos':[{'path':str(photo),'duration':3}]*2}
            for change in [{'width':721},{'height':True},{'transition':float('nan')},{'transition':2},{'photos':[]},{'photos':[{'path':str(photo),'duration':float('inf')}]*2},{'photos':[{'path':'missing.jpg','duration':3}]*2},{'photos':[{'path':str(photo),'motion':'unknown'}]*2}]:
                with self.subTest(change=change),self.assertRaises(ValueError):validate_photo_film({**base,**change})
