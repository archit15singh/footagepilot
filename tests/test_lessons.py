import json
from pathlib import Path
import tempfile
import unittest

from footagepilot.lessons import recall_lessons, record_lesson


class LessonLibraryTests(unittest.TestCase):
    def test_retains_unreviewed_and_negative_evidence_without_promoting_it(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            library = root / "library"
            lesson = root / "lesson.json"
            comparison = root / "comparison.json"
            lesson.write_text(json.dumps({
                "topic": "audio-timing", "source": "https://example.com/tutorial",
                "technique": "Lead with incoming sound", "conditions": "Fixed picture",
                "changed": "200 ms earlier", "check": "Compare measured cue position",
                "finding": "The cue moved 200 ms",
            }))
            receipt = {
                "technical_pass": True,
                "media": [
                    {"kind": kind, "sha256": digit * 64, "decode": "passed", "duration": 3}
                    for kind, digit in (("baseline", "a"), ("candidate", "b"))
                ],
                "human_verdict": "unreviewed", "review_notes": "", "promote": False,
            }
            comparison.write_text(json.dumps(receipt))
            first = record_lesson(lesson, comparison, library)
            self.assertEqual(first, record_lesson(lesson, comparison, library))
            self.assertEqual(recall_lessons(library, preferred_only=True), {"lessons": []})
            self.assertEqual(recall_lessons(library, topic="color"), {"lessons": []})

            receipt.update(human_verdict="worse", review_notes="The lead masked dialogue.")
            comparison.write_text(json.dumps(receipt))
            record_lesson(lesson, comparison, library)
            receipt.update(promote=True)
            comparison.write_text(json.dumps(receipt))
            with self.assertRaisesRegex(ValueError, "inconsistent human verdict"):
                record_lesson(lesson, comparison, library)

            receipt.update(human_verdict="better", review_notes="The incoming sound clarified the reveal.")
            comparison.write_text(json.dumps(receipt))
            preferred = record_lesson(lesson, comparison, library)
            self.assertEqual(len(recall_lessons(library, topic="audio-timing")["lessons"]), 3)
            results = recall_lessons(library, preferred_only=True)["lessons"]
            self.assertEqual([entry["id"] for entry in results], [preferred["id"]])

            Path(first["path"]).write_text("{}")
            with self.assertRaisesRegex(ValueError, "Invalid learning record"):
                recall_lessons(library)
