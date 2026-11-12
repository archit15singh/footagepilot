import hashlib,json,tempfile,unittest,zipfile
from pathlib import Path
from unittest.mock import patch
from footagepilot.source_import import import_archive,media_info,video_members,MAX_BYTES


class SourceImportTests(unittest.TestCase):
    def probe(self):return {'streams':[{'codec_type':'video','width':1440,'height':1080,'duration':'4','side_data_list':[{'rotation':-90}]},{'codec_type':'audio'}]}

    def test_archive_paths_cannot_escape_and_duplicate_names_remain_distinct(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);archive=root/'download.zip'
            with zipfile.ZipFile(archive,'w') as z:
                z.writestr('../../escape.mp4',b'one');z.writestr('/absolute/escape.mp4',b'two');z.writestr('irrelevant.txt',b'ignored')
            with patch('footagepilot.source_import.probe',return_value=self.probe()):result=import_archive(archive,root/'pool')
            self.assertEqual(result['videos'],2);self.assertFalse((root/'escape.mp4').exists());self.assertEqual((root/'pool/clip-02.mp4').read_bytes(),b'two')
            report=json.loads((root/'pool/sources.json').read_text());self.assertEqual(report['sources'][0]['display_dimensions'],[1080,1440]);self.assertEqual(report['sources'][0]['sha256'],hashlib.sha256(b'one').hexdigest())

    def test_missing_video_and_invalid_metadata_cannot_be_reported_complete(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);archive=root/'download.zip'
            with zipfile.ZipFile(archive,'w') as z:z.writestr('photo.jpg',b'photo')
            with self.assertRaises(ValueError):import_archive(archive,root/'none')
            self.assertFalse((root/'none').exists())
            with zipfile.ZipFile(archive,'w') as z:z.writestr('clip.mp4',b'not media')
            with patch('footagepilot.source_import.probe',return_value={'streams':[]}):
                with self.assertRaises(ValueError):import_archive(archive,root/'failed')
            self.assertFalse((root/'failed/assets.json').exists());self.assertTrue((root/'failed/failure.json').exists())

    def test_source_rotation_is_not_inferred_from_coded_dimensions(self):
        meta=self.probe();meta['streams'][0]['side_data_list']=[{'rotation':12}]
        with patch('footagepilot.source_import.probe',return_value=meta):self.assertIsNone(media_info(Path('source'))['display_dimensions'])

    def test_archive_change_cannot_produce_complete_provenance(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);source=root/'download.zip'
            with zipfile.ZipFile(source,'w') as archive:archive.writestr('clip.mp4',b'video')
            def concurrent_writer(path):
                with source.open('ab') as stream:stream.write(b'changed after selection')
                return self.probe()
            with patch('footagepilot.source_import.probe',side_effect=concurrent_writer):
                with self.assertRaisesRegex(ValueError,'archive changed'):import_archive(source,root/'pool')
            self.assertFalse((root/'pool/sources.json').exists());self.assertTrue((root/'pool/failure.json').exists())

    def test_large_or_encrypted_members_reject_without_extraction(self):
        from types import SimpleNamespace
        for size,flag in ((MAX_BYTES+1,0),(1,1),(0,0)):
            member=SimpleNamespace(filename='clip.mp4',file_size=size,flag_bits=flag,is_dir=lambda:False)
            with self.assertRaises(ValueError):video_members(SimpleNamespace(infolist=lambda:[member]))

    def test_non_archive_fails_without_output(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);source=root/'wrong.zip';source.write_bytes(b'not a ZIP')
            with self.assertRaisesRegex(ValueError,'readable ZIP'):import_archive(source,root/'pool')
            self.assertFalse((root/'pool').exists())
