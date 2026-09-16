#!/usr/bin/env python3
"""Bundle the canonical skill for native Codex and Claude Code installers."""

import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "plugins/pull-android-apk/skills/pull-android-apk"
FILES = (
    "SKILL.md",
    "LICENSE",
    "agents/openai.yaml",
    "scripts/apk_pull.py",
    "scripts/android_tools.py",
    "references/export-format.md",
    "references/provenance.md",
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail if the committed bundle differs from source",
    )
    args = parser.parse_args()
    stale = []
    for relative in FILES:
        source, target = ROOT / relative, DEST / relative
        if args.check:
            if not target.is_file() or target.read_bytes() != source.read_bytes():
                stale.append(relative)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
    if stale:
        parser.exit(
            1,
            "Stale plugin files: "
            + ", ".join(stale)
            + ". Run python3 scripts/build_plugin.py\n",
        )
    print(
        "Plugin skill bundle matches source"
        if args.check
        else "Plugin skill bundle generated"
    )


if __name__ == "__main__":
    main()
