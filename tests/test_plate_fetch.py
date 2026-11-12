import copy,hashlib,io,json,tempfile,unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch
from footagepilot.plate_fetch import PLATES,fetch_plate,download,license_evidence

HTML=b'<h3>Breaking Glass Overlay</h3><p>Public Domain, Creative Commons CC0</p><a href="breaking_glass_overlay_h264.mp4">Video</a><h3>Long Exposure Photography</h3>'


class PlateFetchTests(unittest.TestCase):
    def setUp(self):
        self.directory=tempfile.TemporaryDirectory();self.addCleanup(self.directory.cleanup)
        self.root=Path(self.directory.name);self.source=b'reviewed source'
        entry=copy.deepcopy(PLATES['marburg-glass']);entry.update(bytes=len(self.source),sha256=hashlib.sha256(self.source).hexdigest())
        catalog=patch.dict(PLATES,{'marburg-glass':entry});catalog.start();self.addCleanup(catalog.stop)
        clock=patch('footagepilot.plate_fetch.date');self.clock=clock.start();self.addCleanup(clock.stop)
        self.clock.today.return_value=date(2026,11,12);self.clock.fromisoformat.side_effect=date.fromisoformat

    def network(self,url,**kwargs):return io.BytesIO(HTML if 'studio' in url else self.source)

    def test_verified_fetch_keeps_original_and_exports_separate_derived_catalog(self):
        def render(command):
            if str(command[-1]).endswith('glass-impact.mp4'):Path(command[-1]).write_bytes(b'derived')
        with patch('footagepilot.plate_fetch.urlopen',side_effect=self.network),patch('footagepilot.plate_fetch.probe',side_effect=[{'streams':[{'codec_type':'video','width':1280,'height':720}]},{'streams':[{'codec_type':'video','width':1920,'height':1080,'avg_frame_rate':'30/1','duration':'1.0'}]}]),patch('footagepilot.plate_fetch.binary',return_value='ffmpeg'),patch('footagepilot.plate_fetch.run',side_effect=render):
            result=fetch_plate('marburg-glass',self.root/'asset')
        self.assertEqual((self.root/'asset/original.mp4').read_bytes(),self.source)
        self.assertEqual(result['status'],'verified-local-asset')
        catalog=json.loads((self.root/'asset/plate-assets.json').read_text())
        self.assertEqual(catalog['plate_assets'][0]['id'],'marburg-glass')
        self.assertEqual(Path(catalog['plate_assets'][0]['path']).read_bytes(),b'derived')
        record=json.loads((self.root/'asset/provenance.json').read_text())
        self.assertEqual(record['license'],'CC0-1.0');self.assertEqual(record['source_decode'],'passed')
        with self.assertRaisesRegex(ValueError,'fresh effect'):fetch_plate('marburg-glass',self.root/'asset')

    def test_wrong_derived_rate_rejects_instead_of_publishing_catalog(self):
        def render(command):
            if str(command[-1]).endswith('glass-impact.mp4'):Path(command[-1]).write_bytes(b'derived')
        metadata=[{'streams':[{'codec_type':'video','width':1280,'height':720}]},
                  {'streams':[{'codec_type':'video','width':1920,'height':1080,'avg_frame_rate':'25/1','duration':'1.0'}]}]
        with patch('footagepilot.plate_fetch.urlopen',side_effect=self.network),patch('footagepilot.plate_fetch.probe',side_effect=metadata),patch('footagepilot.plate_fetch.binary',return_value='ffmpeg'),patch('footagepilot.plate_fetch.run',side_effect=render):
            with self.assertRaisesRegex(ValueError,'differs from recipe'):fetch_plate('marburg-glass',self.root/'asset')
        self.assertFalse((self.root/'asset/plate-assets.json').exists())

    def test_changed_hash_fails_before_media_tools_and_retains_failure(self):
        PLATES['marburg-glass']['sha256']='0'*64
        with patch('footagepilot.plate_fetch.urlopen',side_effect=self.network),patch('footagepilot.plate_fetch.probe') as media:
            with self.assertRaisesRegex(ValueError,'reviewed bytes/hash'):fetch_plate('marburg-glass',self.root/'asset')
            media.assert_not_called()
        self.assertEqual(json.loads((self.root/'asset/provenance.json').read_text())['status'],'failed')
        self.assertFalse((self.root/'asset/plate-assets.json').exists())

    def test_stale_review_and_unknown_name_do_not_download(self):
        self.clock.today.return_value=date(2027,1,1)
        with patch('footagepilot.plate_fetch.urlopen') as network:
            with self.assertRaisesRegex(ValueError,'stale'):fetch_plate('marburg-glass',self.root/'asset')
            with self.assertRaisesRegex(ValueError,'Unknown'):fetch_plate('arbitrary-url',self.root/'asset')
            network.assert_not_called()
        self.assertFalse((self.root/'asset').exists())

    def test_changed_license_evidence_rejects_before_source_download(self):
        with patch('footagepilot.plate_fetch.urlopen',return_value=io.BytesIO(HTML.replace(b'CC0',b'restricted'))) as network:
            with self.assertRaisesRegex(ValueError,'license evidence changed'):fetch_plate('marburg-glass',self.root/'asset')
        self.assertEqual(network.call_count,1)
        for body in (b'Public Domain, Creative Commons CC0',HTML.replace(b'Breaking Glass Overlay',b'Other footage')):
            with self.assertRaises(ValueError):license_evidence(body)

    def test_download_is_bounded_and_will_not_overwrite(self):
        with patch('footagepilot.plate_fetch.urlopen',side_effect=lambda *a,**k:io.BytesIO(b'abcd')):
            with self.assertRaisesRegex(ValueError,'size bound'):download('https://example.invalid',self.root/'partial',3)
            self.assertLessEqual((self.root/'partial').stat().st_size,3)
            with self.assertRaises(FileExistsError):download('https://example.invalid',self.root/'partial',10)


if __name__=='__main__':unittest.main()
