"""Write manifest.json (every source and output file) and a sha256sum-checkable manifest.sha256."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INCLUDE = ("source", "tests", "rendered", "check")
SKIP_SUFFIXES = (".pyc",)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def covered_files() -> list[Path]:
    files = [ROOT / "README.md", ROOT / "repair-log.md"]
    for folder in INCLUDE:
        for path in sorted((ROOT / folder).rglob("*")):
            if path.is_file() and not path.name.endswith(SKIP_SUFFIXES) and "__pycache__" not in path.parts:
                files.append(path)
    return sorted(files)


def main() -> None:
    entries = []
    for path in covered_files():
        entries.append({"path": str(path.relative_to(ROOT)), "sha256": digest(path),
                        "bytes": path.stat().st_size})
    manifest = {
        "revision": "B-hand-v2",
        "scope": "README, repair-log, source, tests, rendered panels/sheet and the reference-free draw-check bundle",
        "covered_folders": list(INCLUDE),
        "generated_by": "source/make_manifest.py",
        "reference_free": True,
        "files": entries,
    }
    (ROOT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    lines = [f"{entry['sha256']}  {entry['path']}" for entry in entries]
    lines.append(f"{digest(ROOT / 'manifest.json')}  manifest.json")
    (ROOT / "manifest.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{len(entries)} files hashed; manifest.json + manifest.sha256 written")


if __name__ == "__main__":
    main()
