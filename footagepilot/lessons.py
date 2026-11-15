"""Store and retrieve editing lessons with their comparison evidence."""
import hashlib
import json
import math
import os
import re
from tempfile import NamedTemporaryFile
from pathlib import Path
from urllib.parse import urlsplit

TOPIC = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
SHA256 = re.compile(r"[0-9a-f]{64}")
FIELDS = ("topic", "source", "technique", "conditions", "changed", "check", "finding")


def validate_lesson(lesson):
    if not isinstance(lesson, dict) or set(lesson) != set(FIELDS):
        raise ValueError("Expected lesson fields: " + ", ".join(FIELDS))
    for field in FIELDS:
        if not isinstance(lesson[field], str) or not lesson[field].strip():
            raise ValueError(f"Lesson {field} must be nonempty text")
    if not TOPIC.fullmatch(lesson["topic"]):
        raise ValueError("Lesson topic must use lowercase words separated by hyphens")
    source = urlsplit(lesson["source"])
    if source.scheme != "https" or not source.hostname or source.username or source.password:
        raise ValueError("Lesson source must be an HTTPS reference URL")


def comparison_status(comparison):
    if not isinstance(comparison, dict) or comparison.get("technical_pass") is not True:
        raise ValueError("Use a passing compare-edits record")
    media = comparison.get("media")
    if not isinstance(media, list) or len(media) != 2:
        raise ValueError("Comparison must contain baseline and candidate media")
    for kind, item in zip(("baseline", "candidate"), media):
        if (not isinstance(item, dict) or item.get("kind") != kind
                or item.get("decode") != "passed" or not isinstance(item.get("sha256"), str)
                or not SHA256.fullmatch(item["sha256"])
                or type(item.get("duration")) not in (int, float)
                or not 0 < item["duration"] < math.inf):
            raise ValueError(f"Comparison has invalid {kind} media evidence")
    verdict = comparison.get("human_verdict")
    notes = comparison.get("review_notes")
    if (verdict not in ("unreviewed", "better", "worse", "tie") or not isinstance(notes, str)
            or (verdict != "unreviewed" and not notes.strip())
            or comparison.get("promote") is not (verdict == "better")):
        raise ValueError("Comparison has an inconsistent human verdict")
    return verdict


def record_id(record):
    payload = json.dumps(record, sort_keys=True, ensure_ascii=False, allow_nan=False).encode()
    return hashlib.sha256(payload).hexdigest()


def record_lesson(lesson_path, comparison_path, library):
    lesson = json.loads(lesson_path.read_text(encoding="utf-8"))
    comparison = json.loads(comparison_path.read_text(encoding="utf-8"))
    validate_lesson(lesson)
    verdict = comparison_status(comparison)
    record = {"schema_version": 1, "lesson": lesson, "comparison": comparison}
    identifier = record_id(record)
    library.mkdir(parents=True, exist_ok=True)
    destination = library / f"{identifier}.json"
    with NamedTemporaryFile(mode="w", encoding="utf-8", dir=library, delete=False) as handle:
        temporary = Path(handle.name)
        try:
            json.dump(record, handle, ensure_ascii=False, indent=2, allow_nan=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
            try:
                os.link(temporary, destination)
            except FileExistsError:
                existing = json.loads(destination.read_text(encoding="utf-8"))
                if record_id(existing) != identifier:
                    raise ValueError(f"Existing lesson record is damaged: {destination.name}")
        finally:
            temporary.unlink(missing_ok=True)
    return {"id": identifier, "path": str(destination), "human_verdict": verdict}


def recall_lessons(library, topic=None, preferred_only=False):
    if topic is not None and not TOPIC.fullmatch(topic):
        raise ValueError("Lesson topic must use lowercase words separated by hyphens")
    if library.exists() and not library.is_dir():
        raise ValueError("Lesson library must be a directory")
    entries = []
    for path in sorted(library.glob("*.json")):
        if not SHA256.fullmatch(path.stem):
            continue
        record = json.loads(path.read_text(encoding="utf-8"))
        if (not isinstance(record, dict) or record.get("schema_version") != 1
                or record_id(record) != path.stem):
            raise ValueError(f"Invalid learning record: {path.name}")
        lesson = record["lesson"]
        validate_lesson(lesson)
        verdict = comparison_status(record["comparison"])
        if (topic is None or topic == lesson["topic"]) and (not preferred_only or verdict == "better"):
            entries.append({"id": path.stem, **record})
    return {"lessons": entries}
