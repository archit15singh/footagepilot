import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


def capture(ideas, tutorials=(), *, complete=True):
    return {"collections": {
        "video-ideas": {"complete": complete, "reels": list(ideas)},
        "tutorials": {"complete": True, "reels": list(tutorials)},
    }}


class SavedReelDeltaTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.baseline = self.root / "baseline.json"
        self.snapshot = self.root / "snapshot.json"
        self.plan_file = self.root / "plan.json"
        self.notes = self.root / "notes"
        self.notes.mkdir()

    def cli(self, command, path, *args):
        return subprocess.run(
            [sys.executable, "-m", "footagepilot", command, self.baseline, path, *args],
            capture_output=True, text=True,
        )

    def plan(self, snapshot):
        self.snapshot.write_text(json.dumps(snapshot))
        result = self.cli("saved-reel-delta", self.snapshot)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.plan_file.write_text(result.stdout)
        return json.loads(result.stdout)

    def advance(self, *reviewed):
        args = ("--notes-dir", self.notes, "--reviewed", *reviewed) if reviewed else ()
        return self.cli("saved-reel-advance", self.plan_file, *args)

    def test_partial_capture_and_pending_retry(self):
        first = self.plan(capture(["Shared", "Keep"], ["Shared"]))
        self.assertEqual(first["review_queue"], ["Keep", "Shared"])
        self.assertFalse(self.baseline.exists())
        (self.notes / "Shared.md").write_text("Completed picture and sound review.")
        result = self.advance("Shared")
        self.assertEqual(result.returncode, 0, result.stderr)

        second = self.plan(capture(["New", "New"], ["Shared"], complete=False))
        self.assertEqual(second["collections"]["video-ideas"]["added"], ["New"])
        self.assertIsNone(second["collections"]["video-ideas"]["removed"])
        self.assertEqual(second["review_queue"], ["Keep", "New"])
        self.assertEqual(self.advance().returncode, 0)

        third = self.plan(capture(["New"], ["Shared"]))
        self.assertEqual(third["collections"]["video-ideas"]["removed"], ["Keep", "Shared"])
        self.assertEqual(third["review_queue"], ["New"])

    def test_note_gate_stale_plan_and_readd(self):
        self.plan(capture(["ReelA"]))
        result = self.advance("ReelA")
        self.assertIn("Missing completed review note", result.stderr)
        self.assertFalse(self.baseline.exists())

        (self.notes / "ReelA.md").write_text("Prior review with evidence.")
        self.assertEqual(self.advance("ReelA").returncode, 0)
        self.assertIn("baseline changed", self.advance("ReelA").stderr)
        self.assertEqual(self.plan(capture([]))["review_queue"], [])
        self.assertEqual(self.advance().returncode, 0)
        readded = self.plan(capture([], ["ReelA"]))
        self.assertEqual(readded["collections"]["tutorials"]["added"], ["ReelA"])
        self.assertEqual(readded["review_queue"], [])
        self.assertEqual(self.advance().returncode, 0)
        stable = self.baseline.read_bytes()
        self.plan(capture([], ["ReelA"]))
        self.assertEqual(self.advance().returncode, 0)
        self.assertEqual(self.baseline.read_bytes(), stable)

    def test_rejects_path_and_malformed_capture(self):
        for snapshot in (capture(["../escape"]), {"collections": {"video-ideas": []}}):
            with self.subTest(snapshot=snapshot):
                self.snapshot.write_text(json.dumps(snapshot))
                self.assertNotEqual(self.cli("saved-reel-delta", self.snapshot).returncode, 0)
                self.assertFalse(self.baseline.exists())
