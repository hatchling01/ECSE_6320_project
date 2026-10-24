"""Validate GitHub-facing local Markdown links and staged image provenance."""
from __future__ import annotations
import argparse, re, subprocess, sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
PROJECTS = [
    ROOT / "ecse6320-project1-simd",
    ROOT / "ecse6320-project2-memory",
    ROOT / "Project2_Mac",
    ROOT / "ecse6320-project3-ssd",
]

def documents() -> list[Path]:
    selected = [ROOT / "README.md", *(p / "README.md" for p in PROJECTS)]
    for p in PROJECTS:
        selected += list((p / "results" / "plots").glob("FINAL_FIGURES.md"))
        selected += list((p / "results" / "tables").glob("FINAL_TABLES.md"))
        selected += list((p / "docs").glob("reproduction.md"))
        selected += list((p / "docs").glob("final_requirement_audit.md"))
        selected += list((p / "docs").glob("MAC_VS_WINDOWS_COMPARISON.md"))
        selected += list((p / "docs").glob("dependency_comparison.md"))
        selected += list((p / "results" / "comparison").glob("COMPARISON_TABLES.md"))
    selected += list((ROOT / "Project2_Mac").rglob("*.md"))
    return sorted(set(selected))

def staged_files() -> set[str]:
    result = subprocess.run(
        ["git", "-c", f"safe.directory={ROOT.as_posix()}", "ls-files", "-z"],
        cwd=ROOT, capture_output=True, check=True
    )
    return {x.decode("utf-8").replace("\\", "/") for x in result.stdout.split(b"\0") if x}

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--require-tracked-images", action="store_true")
    ns = ap.parse_args()
    failures: list[str] = []
    images: list[Path] = []
    docs = documents()
    for doc in docs:
        if not doc.is_file():
            failures.append(f"missing required document: {doc.relative_to(ROOT)}")
            continue
        text = doc.read_text(encoding="utf-8")
        for image_mark, raw in re.findall(r"(!?)\[[^\]]*\]\(([^)]+)\)", text):
            target = raw.strip().split(maxsplit=1)[0].strip("<>")
            if re.match(r"^(https?://|mailto:|#)", target, re.I):
                continue
            if re.match(r"^[A-Za-z]:[/\\]", target) or target.lower().startswith("file://"):
                failures.append(f"absolute/local-machine link in {doc.relative_to(ROOT)}: {raw}")
                continue
            target = unquote(target.split("#", 1)[0])
            resolved = (doc.parent / target.replace("/", str(Path('/')))).resolve()
            try:
                resolved.relative_to(ROOT)
            except ValueError:
                failures.append(f"link escapes repository in {doc.relative_to(ROOT)}: {raw}")
                continue
            if not resolved.exists():
                failures.append(f"broken link in {doc.relative_to(ROOT)}: {raw}")
            if image_mark:
                images.append(resolved)
    if ns.require_tracked_images:
        tracked = staged_files()
        for image in images:
            rel = image.relative_to(ROOT).as_posix()
            if rel not in tracked:
                failures.append(f"embedded image is not Git-tracked: {rel}")
    if failures:
        print("\n".join(failures))
        return 2
    print(f"validated {len(docs)} required Markdown documents and {len(images)} embedded images")
    return 0

if __name__ == "__main__":
    sys.exit(main())
