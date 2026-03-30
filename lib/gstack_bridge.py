#!/usr/bin/env python3
"""
gstack_bridge.py -- Bridge between gstack outputs and Datacore.

Reads gstack state files (~/.gstack/projects/{slug}/) and converts
them into Datacore-compatible formats: engram candidates, journal entries,
and org-mode tasks.
"""

import json
import os
import glob
from datetime import datetime, timezone
from pathlib import Path

GSTACK_HOME = Path(os.environ.get("GSTACK_HOME", os.path.expanduser("~/.gstack")))


def get_project_slug(repo_path: str = ".") -> str:
    """Derive gstack project slug from repo path."""
    import subprocess
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=repo_path, capture_output=True, text=True
        )
        if result.returncode == 0:
            return os.path.basename(result.stdout.strip()).lower()
    except FileNotFoundError:
        pass
    return "unknown"


def read_learnings(slug: str = None, limit: int = 50) -> list[dict]:
    """Read gstack learnings JSONL for a project."""
    if slug is None:
        slug = get_project_slug()
    learnings_file = GSTACK_HOME / "projects" / slug / "learnings.jsonl"
    if not learnings_file.exists():
        return []
    entries = []
    with open(learnings_file) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return entries[-limit:]


def read_review_log(slug: str = None) -> list[dict]:
    """Read gstack review log for a project."""
    if slug is None:
        slug = get_project_slug()
    review_dir = GSTACK_HOME / "projects" / slug
    logs = []
    for f in sorted(review_dir.glob("*-review-*.json")):
        try:
            logs.append(json.loads(f.read_text()))
        except (json.JSONDecodeError, OSError):
            continue
    return logs


def read_retro_history(slug: str = None) -> list[dict]:
    """Read gstack retro history snapshots."""
    if slug is None:
        slug = get_project_slug()
    retro_dir = GSTACK_HOME / "projects" / slug / ".context" / "retros"
    if not retro_dir.exists():
        return []
    snapshots = []
    for f in sorted(retro_dir.glob("*.json")):
        try:
            snapshots.append(json.loads(f.read_text()))
        except (json.JSONDecodeError, OSError):
            continue
    return snapshots


def learning_to_engram(learning: dict) -> dict:
    """Convert a gstack learning entry to a Datacore engram candidate."""
    type_map = {
        "pattern": "behavioral",
        "pitfall": "procedural",
        "preference": "behavioral",
        "architecture": "architectural",
        "tool": "procedural",
    }
    source_confidence = {
        "observed": 8,
        "user-stated": 9,
        "inferred": 5,
        "cross-model": 7,
    }
    return {
        "statement": learning.get("insight", ""),
        "type": type_map.get(learning.get("type", "pattern"), "behavioral"),
        "scope": "module:gstack",
        "confidence": min(learning.get("confidence", 5), 10),
        "tags": ["gstack", learning.get("type", "pattern"), learning.get("skill", "unknown")],
        "source": f"gstack learning: {learning.get('key', 'unknown')}",
        "files": learning.get("files", []),
    }


def format_journal_entry(retro_data: dict, metrics: dict = None) -> str:
    """Format a retro into a Datacore journal entry."""
    now = datetime.now(timezone.utc).strftime("%H:%M")
    lines = [f"## {now}", ""]
    if retro_data.get("summary"):
        lines.append(retro_data["summary"])
        lines.append("")
    if metrics:
        lines.append("### Sprint Metrics")
        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")
        for k, v in metrics.items():
            lines.append(f"| {k} | {v} |")
        lines.append("")
    if retro_data.get("wins"):
        lines.append("### Wins")
        for win in retro_data["wins"]:
            lines.append(f"- {win}")
        lines.append("")
    if retro_data.get("improvements"):
        lines.append("### Improvements")
        for imp in retro_data["improvements"]:
            lines.append(f"- {imp}")
        lines.append("")
    return "\n".join(lines)


def check_gstack_installed() -> dict:
    """Check if gstack is installed and return version info."""
    gstack_path = Path(os.path.expanduser("~/.claude/skills/gstack"))
    version_file = gstack_path / "VERSION"
    return {
        "installed": gstack_path.exists(),
        "path": str(gstack_path),
        "version": version_file.read_text().strip() if version_file.exists() else None,
    }


if __name__ == "__main__":
    import sys
    status = check_gstack_installed()
    print(f"gstack: {'installed' if status['installed'] else 'NOT FOUND'}")
    if status["version"]:
        print(f"version: {status['version']}")
    slug = get_project_slug()
    learnings = read_learnings(slug)
    print(f"project: {slug}")
    print(f"learnings: {len(learnings)}")
