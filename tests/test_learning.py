import json,tempfile,unittest
from pathlib import Path
from datetime import datetime,timezone
from footagepilot.learning import text_hash,check_sources
from footagepilot.edits import validate_edit

class LearningTests(unittest.TestCase):
    def test_visible_text_fingerprint_ignores_scripts(self):
        self.assertEqual(text_hash('<p>Alpha</p><script>x</script>'),text_hash('<p>Alpha</p><script>y</script>'))
        self.assertNotEqual(text_hash('<p>Alpha</p>'),text_hash('<p>Beta</p>'))
    def test_stale_claims_need_research(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'sources.json';p.write_text(json.dumps({'sources':[{'url':'https://edits.instagram.com/','verified_at':'2026-11-01T00:00:00+00:00','max_age_days':7}]}))
            self.assertTrue(check_sources(p,now=datetime(2026,11,12,tzinfo=timezone.utc))['needs_research'])
    def test_bad_manifest_rejected_before_project_mutation(self):
        with tempfile.TemporaryDirectory() as d:
            base=Path(d);(base/'photo.jpg').write_bytes(b'placeholder')
            good={'shots':[{'path':'photo.jpg','duration':2}]}
            self.assertEqual(validate_edit(good,base),2)
            for duration in [float('nan'),float('inf'),True,-1,0,31]:
                with self.assertRaises(ValueError):validate_edit({'shots':[{'path':'photo.jpg','duration':duration}]},base)
            with self.assertRaises(ValueError):validate_edit({**good,'overlays':[{'path':'photo.jpg','duration':2,'start':1}]},base)
