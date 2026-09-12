#!/pxrpythonsubst
"""Keep the repository within the published core contract."""
from fnmatch import fnmatchcase
from pathlib import Path
import re
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
ALLOWLIST = {
    "CHANGELOG.md": None,
    "docs/adr/[0-9][0-9][0-9][0-9]-*.md": "Context",
    "README.md": "Family",
}
KINDS = ("Wall", "Pipe", "Cc" "tv", "Sync", "BuildUp", "Axis", "Plan",
         "Compliance", "Typical", "Clash", "Solid")
NAMESPACES = ("wall", "pipe", "cc" "tv", "sync", "buildUp", "axis", "plan", "host", "diag")
WORDS = ("ifc2" "usdaeco", "aeco-" "ifc", "datacen" "tre", "re" "vit",
         "bon" "sai", "blen" "der", "scenar" "ios", "cc" "tv",
         "usd" "Solid", "hd" "Oc" "ct", "OC" "CT", "co" "dex")
TERMS = re.compile(
    r"(?:usd)?Aeco(?:" + "|".join(KINDS) + r")[A-Za-z0-9_]*"
    + r"|aeco:(?:" + "|".join(NAMESPACES) + r"):"
    + r"|usdaeco-(?:" + "|".join(KINDS + ("ifc", "record", "coord", "datum", "space", "flowsegment")) + r")\b"
    + "|" + "|".join(map(re.escape, WORDS)) + r"|\bla" r"nes?\b",
    re.IGNORECASE,
)
EXPORT_EXCLUDES = {".git", "out", "build", "dist", "result", "artifacts",
                   "__pycache__", ".pytest_cache"}


def source_files(root):
    """Include tracked files even when ignored, and new files before staging."""
    if (root / ".git").exists():
        listing = subprocess.run(
            ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
            cwd=root, check=True, capture_output=True,
        )
        paths = {root / name.decode() for name in listing.stdout.split(b"\0") if name}
    else:
        # Release archives and build source snapshots have no Git metadata.
        paths = {p for p in root.rglob("*")
                 if not EXPORT_EXCLUDES.intersection(p.relative_to(root).parts)}
    return sorted(p for p in paths if p.is_file())


def sections(content):
    """Track H2 sections; headings inside fenced examples are inert."""
    section, fence = None, None
    for number, line in enumerate(content.splitlines(), 1):
        marker = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if marker:
            run = marker[1]
            if fence is None:
                fence = run
            elif run[0] == fence[0] and len(run) >= len(fence):
                fence = None
        elif fence is None:
            heading = re.match(r"^(#{1,2})\s+(.+?)\s*#*\s*$", line)
            if heading:
                section = heading[2] if len(heading[1]) == 2 else None
        yield number, section, line


PUBLICATION_NAME = WORDS[2]


def term_hits(relative, content):
    # Shared publication metadata is bookkeeping, never a core data source.
    # Permit only protocol spellings in their designated files; scan all else.
    publication = relative == "dependencies.json" or fnmatchcase(relative, "examples/*/manifest.json")
    if publication:
        content = re.sub(rf'"(?:{PUBLICATION_NAME}|usdaeco-{PUBLICATION_NAME}|demo-{PUBLICATION_NAME}-01)"', '"publication"', content)
    if relative == "flake.nix":
        content = content.replace(PUBLICATION_NAME + ' = { url = "github:criad-com/usdaeco-' + PUBLICATION_NAME + '?ref=v0.4.8";',
                                  'publication = { url = "public-release";')
    if fnmatchcase(relative, "examples/*/result/README.md"):
        content = content.replace('Source pin: `usdaeco-' + PUBLICATION_NAME + ' v0.4.8`, variant `base`; source mode `minimal`',
                                  'Source mode: minimal')
    if relative == "tools/usdaeco_core/example.py":
        content = content.replace('AECO_' + PUBLICATION_NAME.upper() + '_ROOT', 'EXTERNAL_ROOT').replace('AECO_' + PUBLICATION_NAME.upper() + '_STAGE', 'EXTERNAL_STAGE')
    permissions = [section for pattern, section in ALLOWLIST.items()
                   if fnmatchcase(relative, pattern)]
    return [f"{relative}:{number}" for number, section, line in sections(content)
            if TERMS.search(line) and None not in permissions and section not in permissions]


def sweep(root=ROOT):
    hits, count = [], 0
    for path in source_files(root):
        data = path.read_bytes()
        if b"\0" in data:
            continue
        try:
            content = data.decode("utf-8")
        except UnicodeDecodeError:
            continue
        count += 1
        hits.extend(term_hits(path.relative_to(root).as_posix(), content))
    return count, hits


def docs_hits(root=ROOT):
    docs = root / "docs"
    hits, numbers = [], []
    for path in sorted(docs.iterdir()):
        if path.is_dir() and path.name == "adr":
            continue
        if path.is_file() and path.name == "README.md":
            continue
        match = re.fullmatch(r"(0[1-8])-[a-z0-9-]+\.md", path.name)
        if not path.is_file() or not match:
            hits.append(f"{path.relative_to(root)}:1")
        else:
            numbers.append(match[1])
    if sorted(numbers) != [f"{n:02}" for n in range(1, 9)]:
        hits.append("docs/:1 (expected one chapter each, 01–08)")
    hits.extend(f"{p.relative_to(root)}:1" for p in docs.rglob("*")
                if p.suffix.lower() == ".json" or p.name == "moved")
    return sorted(set(hits))


def add_checks(report, root=ROOT):
    count, hits = sweep(root)
    report.check("core-only term sweep", not hits,
                 f"{count} text files, {len(hits)} hits" + ("; " + "; ".join(hits) if hits else ""))
    layout = docs_hits(root)
    report.check("core documentation boundary", not layout, "; ".join(layout) or "8 chapters and ADRs")


class TestCoreOnly(unittest.TestCase):
    def test_repository(self):
        self.assertEqual(sweep()[1], [])
        self.assertEqual(docs_hits(), [])

    def test_all_vocabulary_is_rejected(self):
        samples = list(WORDS) + ["UsdAeco" + name + "API" for name in KINDS]
        samples += ["Aeco" + name + "Thing" for name in KINDS]
        samples += ["aeco:" + name + ":value" for name in NAMESPACES]
        samples += ["demo-" + WORDS[2], "la" "ne", "la" "nes"]
        for sample in samples:
            with self.subTest(sample=sample):
                self.assertEqual(term_hits("tools/example.py", "safe\n" + sample.upper()),
                                 ["tools/example.py:2"])

    def test_publication_metadata_exception_is_narrow(self):
        source = '"repo": "usdaeco-' + PUBLICATION_NAME + '"'
        self.assertEqual(term_hits("dependencies.json", source), [])
        self.assertEqual(term_hits("tools/unrelated.py", source), ["tools/unrelated.py:1"])
        self.assertEqual(term_hits("dependencies.json", source + "\n" + WORDS[0]), ["dependencies.json:2"])

    def test_allowlist_is_section_scoped(self):
        word = WORDS[0]
        for relative, heading in [("README.md", "Family"), ("docs/adr/0008-example.md", "Context")]:
            content = f"{word}\n## {heading}\n{word}\n### Detail\n{word}\n## Decision\n{word}"
            self.assertEqual(term_hits(relative, content), [f"{relative}:1", f"{relative}:7"])
            self.assertEqual(term_hits(relative, f"```md\n## {heading}\n{word}\n```"), [f"{relative}:3"])
        self.assertEqual(term_hits("CHANGELOG.md", word), [])
        self.assertEqual(term_hits("docs/adr/README.md", "## Context\n" + word), ["docs/adr/README.md:2"])

    def test_readme_pointer_is_one_line(self):
        content = (ROOT / "README.md").read_text()
        lines = [line for _, section, line in sections(content)
                 if section == "Family" and line.strip() and not line.startswith("## ")]
        self.assertEqual(len(lines), 1)
        self.assertRegex(lines[0], r"\[[^]]+\]\(https://[^)]+\)")

    def test_seeded_tracked_files_fail_report(self):
        from usdaeco_check import Report
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            (root / "docs").mkdir()
            for number in range(1, 9):
                (root / "docs" / f"{number:02}-chapter.md").write_text("Core.\n")
            (root / "out").mkdir()
            (root / ".gitignore").write_text("out/\n")
            (root / "out" / "tracked.txt").write_text(WORDS[0])
            subprocess.run(["git", "add", "-f", "out/tracked.txt"], cwd=root, check=True)
            report = Report()
            add_checks(report, root)
            self.assertFalse(report.results[0].ok)
            self.assertIn("out/tracked.txt:1", report.results[0].detail)
            self.assertEqual(report.finish(), 1)
            (root / "out" / "tracked.txt").unlink()
            (root / "new.py").write_text(WORDS[1])
            self.assertEqual(sweep(root)[1], ["new.py:1"])

    def test_docs_boundary_rejects_returning_artifacts(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            docs = root / "docs"
            (docs / "adr").mkdir(parents=True)
            for number in range(1, 9):
                (docs / f"{number:02}-chapter.md").touch()
            self.assertEqual(docs_hits(root), [])
            for name in ("10-extra.md", "01-duplicate.md", "adr/evidence.JSON"):
                path = docs / name
                path.touch()
                self.assertTrue(docs_hits(root), name)
                path.unlink()
            (docs / "moved").mkdir()
            self.assertTrue(docs_hits(root))


if __name__ == "__main__":
    raise SystemExit(unittest.main())
