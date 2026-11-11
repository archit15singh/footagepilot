import unittest
from unittest.mock import patch
from pathlib import Path
from tempfile import TemporaryDirectory
from spliceforge.__main__ import validate

class ProjectContract(unittest.TestCase):
    def test_rejects_invalid_ranges(self):
        with TemporaryDirectory() as directory:
            source = Path(directory)/'source.mp4'
            source.touch()
            with patch('spliceforge.__main__.probe', return_value={'format': {'duration': '10'}}):
                for ranges in ([], 'bad', [1], [[0]], [[0,1,2]], [[2, 1]], [[0, 11]], [[0, 4], [3, 5]], [[float('nan'), 2]], [[True, 2]]):
                    with self.subTest(ranges=ranges), self.assertRaises(ValueError):
                        validate({'source': str(source), 'keep': ranges})
                self.assertEqual(validate({'source': str(source), 'keep': [[0, 2], [5, 9]]}), 10)

    def test_missing_source(self):
        with self.assertRaises(ValueError):
            validate({'source': '/nonexistent/spliceforge-source', 'keep': [[0, 1]]})
