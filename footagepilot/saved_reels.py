"""Track membership and completed reviews for two private saved collections."""
import json
import os
import re
from pathlib import Path
from tempfile import NamedTemporaryFile

COLLECTIONS = ("video-ideas", "tutorials")
SHORTCODE = re.compile(r"[A-Za-z0-9_-]+")


def reel_ids(values):
    if not isinstance(values, list) or any(
        not isinstance(value, str) or not SHORTCODE.fullmatch(value) for value in values
    ):
        raise ValueError("Expected a list of Instagram shortcodes")
    return set(values)


def check_collections(collections):
    if not isinstance(collections, dict) or set(collections) != set(COLLECTIONS):
        raise ValueError("Expected video-ideas and tutorials collections")


def load_state(path):
    try:
        state = json.loads(path.read_text())
    except FileNotFoundError:
        return {"revision": 0, "collections": {name: [] for name in COLLECTIONS}, "reviewed": []}
    if not isinstance(state, dict) or set(state) != {"revision", "collections", "reviewed"}:
        raise ValueError("Invalid saved reel baseline")
    if type(state["revision"]) is not int or state["revision"] < 1:
        raise ValueError("Invalid saved reel baseline revision")
    check_collections(state["collections"])
    for values in state["collections"].values():
        reel_ids(values)
    reel_ids(state["reviewed"])
    return state


def build_plan(state, snapshot):
    if not isinstance(snapshot, dict) or set(snapshot) != {"collections"}:
        raise ValueError("Expected a snapshot with a collections object")
    check_collections(snapshot["collections"])
    changes = {}
    current = {}
    for name in COLLECTIONS:
        capture = snapshot["collections"][name]
        if (not isinstance(capture, dict) or set(capture) != {"complete", "reels"}
                or type(capture["complete"]) is not bool):
            raise ValueError(f"{name}: expected complete (boolean) and reels (list)")
        observed = reel_ids(capture["reels"])
        previous = reel_ids(state["collections"][name])
        complete = capture["complete"]
        current[name] = observed if complete else observed | previous
        changes[name] = {
            "complete": complete,
            "observed": sorted(observed),
            "added": sorted(observed - previous),
            "removed": sorted(previous - observed) if complete else None,
        }
    pending = set.union(*current.values()) - reel_ids(state["reviewed"])
    return {
        "baseline_revision": state["revision"],
        "collections": changes,
        "review_queue": sorted(pending),
    }


def plan_saved_reels(baseline, snapshot):
    return build_plan(load_state(baseline), json.loads(snapshot.read_text()))


def advance_saved_reels(baseline, plan, reviewed, notes_dir):
    # The persistent lock inode also serializes the first writer to a new baseline.
    try:
        import fcntl
    except ImportError as error:
        raise ValueError("Advancing a saved reel baseline requires a POSIX file lock") from error

    if not isinstance(plan, dict):
        raise ValueError("Expected a saved reel plan object")
    requested = reel_ids(reviewed)
    baseline = baseline.resolve()
    baseline.parent.mkdir(parents=True, exist_ok=True)
    with baseline.with_name(baseline.name + ".lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        state = load_state(baseline)
        if plan.get("baseline_revision") != state["revision"]:
            raise ValueError("Saved reel baseline changed. Capture a fresh snapshot and plan again.")
        snapshot = {"collections": {
            name: {"complete": capture["complete"], "reels": capture["observed"]}
            for name, capture in plan["collections"].items()
        }}
        if build_plan(state, snapshot) != plan:
            raise ValueError("Saved reel plan disagrees with the baseline")
        if requested - reel_ids(plan["review_queue"]):
            raise ValueError("Only queued reels can be marked reviewed")
        for reel in sorted(requested):
            note = Path(notes_dir) / f"{reel}.md"
            if not note.is_file() or not note.read_text().strip():
                raise ValueError(f"Missing completed review note for {reel}")

        current = {}
        for name, capture in plan["collections"].items():
            observed = reel_ids(capture["observed"])
            if not capture["complete"]:
                observed |= reel_ids(state["collections"][name])
            current[name] = sorted(observed)
        completed = sorted(reel_ids(state["reviewed"]) | requested)
        if current == state["collections"] and completed == state["reviewed"]:
            return state
        updated = {"revision": state["revision"] + 1, "collections": current, "reviewed": completed}
        with NamedTemporaryFile(mode="w", dir=baseline.parent, delete=False) as temporary:
            target = Path(temporary.name)
            try:
                json.dump(updated, temporary, indent=2)
                temporary.write("\n")
                temporary.flush()
                os.fsync(temporary.fileno())
                target.replace(baseline)
            finally:
                target.unlink(missing_ok=True)
        return updated
