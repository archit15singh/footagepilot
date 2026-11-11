import json,os,tomllib,unittest
from pathlib import Path
from unittest.mock import patch
from footagepilot.__main__ import binary

ROOT=Path(__file__).resolve().parents[1]


class ProductNaming(unittest.TestCase):
    def test_metadata_and_render_composition_agree(self):
        project=tomllib.loads((ROOT/'pyproject.toml').read_text())
        self.assertEqual(project['project']['name'],'footagepilot')
        self.assertEqual(project['project']['scripts'],{'footagepilot':'footagepilot.__main__:main'})
        for file in ['package.json','package-lock.json']:
            self.assertEqual(json.loads((ROOT/file).read_text())['name'],'footagepilot-renderer')
        for file in ['footagepilot/graphics.py','footagepilot/render/film.jsx']:
            self.assertIn("'FootagePilot'" if file.endswith('.py') else 'id="FootagePilot"',(ROOT/file).read_text())

    def test_only_current_environment_prefix_is_used(self):
        with patch.dict(os.environ,{'FOOTAGEPILOT_FFMPEG':'/selected/ffmpeg'},clear=True):
            self.assertEqual(binary('ffmpeg'),'/selected/ffmpeg')
        # Historical spelling is intentional negative-control input, not an alias.
        with patch.dict(os.environ,{'SPLICEFORGE_FFMPEG':'/legacy/ffmpeg'},clear=True),patch('footagepilot.__main__.shutil.which',return_value=None):
            with self.assertRaisesRegex(ValueError,'FOOTAGEPILOT_FFMPEG'):binary('ffmpeg')

    def test_live_sources_have_no_previous_brand(self):
        for path in (ROOT/'footagepilot').rglob('*'):
            if path.is_file() and path.suffix in ('.py','.jsx','.html'):
                with self.subTest(path=path.name):self.assertNotIn('spliceforge',path.read_text().lower())
        page=(ROOT/'footagepilot/web/index.html').read_text()
        self.assertIn('X-FootagePilot-Token',page);self.assertIn('class="mark">F/',page)
