"""W0 workflow checker (standard library only).

    python scripts/check_workflow.py            # exit 0 = OK, 1 = errors (warnings never fail)

Checks: card required fields; tasks/queue.md <-> card status; HANDOFF.md freshness and size; AGENTS.md / CLAUDE.md
<= 60 lines; docs/START-HERE.md <= 60 lines; changed paths outside the THINKER write matrix (warning only, role is not
known); broken relative links in the workflow documents.
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wf_common import (ROOT, SCALAR_FIELDS, SECTION_FIELDS, STATES, git, iter_cards,  # noqa: E402
                       parse_card)

LINE_LIMITS = {"AGENTS.md": 60, "CLAUDE.md": 60, "docs/START-HERE.md": 60, "HANDOFF.md": 40}
THINKER_PATHS = ("reviews/", "decisions/", "tasks/", "reports/R-", "reports/D-", "packs/")
PROTECTED = (re.compile(r"\.kicad_(sch|pcb|pro|sym|mod|dru)$"), re.compile(r"^(design|simulation)/"),
             re.compile(r"^analysis/.*\.py$"))
LINK_DOCS = ("README.md", "AGENTS.md", "CLAUDE.md", "HANDOFF.md", "docs/START-HERE.md", "docs/WORKFLOW.md")


def check_cards(root: Path) -> tuple[list[str], dict[str, str]]:
    errs, status = [], {}
    for p in iter_cards(root):
        c = parse_card(p.read_text(encoding="utf-8"))
        rel = p.relative_to(root).as_posix()
        for f in SCALAR_FIELDS:
            if not c["scalars"].get(f):
                errs.append(f"{rel}: zorunlu alan eksik/boş: {f}")
        for f in SECTION_FIELDS:
            if not c["sections"].get(f):
                errs.append(f"{rel}: zorunlu bölüm eksik/boş: ## {f}")
        cid = c["scalars"].get("ID", "")
        if cid and cid != p.stem:
            errs.append(f"{rel}: ID '{cid}' dosya adıyla aynı değil")
        d = c["scalars"].get("Durum", "")
        if d and d not in STATES:
            errs.append(f"{rel}: geçersiz Durum '{d}' (izinli: {', '.join(STATES)})")
        b = c["scalars"].get("Boyut", "")
        if b and b.split()[0] not in ("S", "M"):
            errs.append(f"{rel}: Boyut '{b}' (yalnız S/M; L yasak → böl)")
        r = c["scalars"].get("Rol", "")
        if r and r.split()[0] not in ("BUILDER", "THINKER"):
            errs.append(f"{rel}: Rol '{r}' (BUILDER/THINKER)")
        status[p.stem] = d
    return errs, status


def check_queue(root: Path, status: dict[str, str]) -> list[str]:
    q = root / "tasks" / "queue.md"
    if not q.exists():
        return ["tasks/queue.md yok"]
    errs, seen = [], {}
    for line in q.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\|\s*\[?([TRD]-\d{3}[a-z]?)\]?(?:\([^)]*\))?\s*\|(.*)\|\s*$", line)
        if m:
            seen[m.group(1)] = [x.strip() for x in m.group(2).split("|")][-1]
    for cid, st in status.items():
        if cid not in seen:
            errs.append(f"queue.md: {cid} kuyrukta yok")
        elif seen[cid] != st:
            errs.append(f"queue.md: {cid} durumu '{seen[cid]}' ≠ kart '{st}'")
    for cid in seen:
        if cid not in status:
            errs.append(f"queue.md: {cid} için kart dosyası yok")
    return errs


def check_handoff(root: Path) -> list[str]:
    h = root / "HANDOFF.md"
    if not h.exists():
        return ["HANDOFF.md yok"]
    m = re.search(r"\*\*Tarih:\*\*\s*(\d{4}-\d{2}-\d{2})", h.read_text(encoding="utf-8"))
    if not m:
        return ["HANDOFF.md: '**Tarih:** YYYY-MM-DD' satırı yok"]
    last = git("log", "-1", "--format=%cs", root=root)
    if last and m.group(1) < last:
        return [f"HANDOFF.md bayat: tarih {m.group(1)} < son commit {last}"]
    return []


def check_lines(root: Path) -> list[str]:
    errs = []
    for rel, lim in LINE_LIMITS.items():
        p = root / rel
        if p.exists():
            n = len(p.read_text(encoding="utf-8").splitlines())
            if n > lim:
                errs.append(f"{rel}: {n} satır > {lim}")
    return errs


def link_docs(root: Path) -> list[Path]:
    out = [root / d for d in LINK_DOCS if (root / d).exists()]
    for sub in ("tasks", "tasks/done", "reviews", "decisions"):
        if (root / sub).is_dir():
            out += sorted((root / sub).glob("*.md"))
    return out


def check_links(root: Path) -> list[str]:
    errs = []
    for doc in link_docs(root):
        for target in re.findall(r"\[[^\]]*\]\(([^)\s]+)\)", doc.read_text(encoding="utf-8")):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            t = target.split("#", 1)[0]
            if t and not (doc.parent / t).exists():
                errs.append(f"{doc.relative_to(root).as_posix()}: bozuk bağlantı → {target}")
    return errs


def changed_paths(root: Path) -> list[str]:
    base = "main" if git("rev-parse", "--verify", "--quiet", "main", root=root) else ""
    names = set(git("diff", "--name-only", f"{base}...HEAD", root=root).splitlines()) if base else set()
    for line in git("status", "--porcelain", root=root).splitlines():
        if len(line) > 3:
            names.add(line[3:].split(" -> ")[-1].strip('"'))
    return sorted(n for n in names if n)


def permission_warnings(root: Path) -> list[str]:
    ch = changed_paths(root)
    builder_only = [p for p in ch if not p.startswith(THINKER_PATHS)]
    prot = [p for p in ch if any(r.search(p) for r in PROTECTED)]
    out = []
    if builder_only:
        out.append(f"{len(builder_only)} değişen yol THINKER izin matrisi dışında (yalnız BUILDER yazabilir): "
                   + ", ".join(builder_only[:8]) + (" …" if len(builder_only) > 8 else ""))
    if prot:
        out.append(f"{len(prot)} korumalı yol değişti (KiCad/design/simulation/analysis .py) — kart izni gerekir: " + ", ".join(prot[:8]))
    return out


# T-025: text encoding gate. Markers are built from code points so this file does not flag itself.
BOM = b"\xef\xbb\xbf"
MOJIBAKE = (chr(0xC3), chr(0xC4) + chr(0xB1), chr(0xC5) + chr(0x178), chr(0xE2) + chr(0x20AC))
LOST_LETTER = re.compile(r"(?<=[^\W_])\?(?=[^\W_])")     # ASCII "?" between letters/digits = a Turkish letter was lost
URL = re.compile(r"https?://\S+")                         # known false alarm: query separators (reports/R-003/land-data.md, decisions/D-001-F1.md)
ENCODING_SKIP = re.compile(r"^(archive|design)/|\.kicad_|\.net$")   # historic evidence, design and KiCad output are out of scope


def tracked_files(root: Path) -> list[str]:
    out = git("ls-files", "-z", root=root)
    return [f for f in out.split("\0") if f]


def check_encoding(root: Path) -> list[str]:
    errs = []
    for rel in tracked_files(root):
        p = root / rel
        if ENCODING_SKIP.search(rel) or not p.is_file():
            continue
        data = p.read_bytes()
        if b"\0" in data:                                  # binary
            continue
        if data.startswith(BOM):
            errs.append(f"{rel}: UTF-8 BOM var")
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError as e:
            errs.append(f"{rel}: geçersiz UTF-8 (bayt {e.start})")
            continue
        for n, line in enumerate(text.splitlines(), 1):
            if any(m in line for m in MOJIBAKE):
                errs.append(f"{rel}:{n}: bozuk Türkçe karakter (mojibake)")
            bare = URL.sub("", line)
            if LOST_LETTER.search(bare):
                errs.append(f"{rel}:{n}: kelime içinde '?' (kaybolmuş Türkçe harf)")
    return errs


def check(root: Path = ROOT) -> tuple[list[str], list[str]]:
    errs, status = check_cards(root)
    errs += check_queue(root, status) + check_handoff(root) + check_lines(root) + check_links(root) + check_encoding(root) + check_standard(root)
    return errs, permission_warnings(root)


def _utf8():
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass


STANDARD_DOC = "docs/POWER-PCB-ENGINEERING-STANDARD.md"
STANDARD_SRC = "decisions/R-020-engineering-standard-source.md"
STANDARD_SHA = "5c03f55e43b985e87191ea46efc52dc3321ad9b196f42ecd7bb8056901c9fcfe"
STANDARD_LINKS = ("AGENTS.md", "CLAUDE.md", "docs/WORKFLOW.md")


def check_standard(root: Path, required: bool | None = None) -> list[str]:
    """T-026: the permanent standard stays byte-complete against its source and stays linked from the agent rules.

    required defaults to True for the real repository: there, both files missing is a FAIL (R-020). Only minimal test fixtures skip it.
    """
    required = (root.resolve() == ROOT.resolve()) if required is None else required
    errs = []
    src, doc = root / STANDARD_SRC, root / STANDARD_DOC
    if not src.exists() and not doc.exists():
        return [f"mühendislik standardı eksik: {STANDARD_SRC} ve {STANDARD_DOC}"] if required else []
    if not src.exists() or not doc.exists():
        return [f"mühendislik standardı eksik: {STANDARD_SRC} veya {STANDARD_DOC}"]
    data = src.read_bytes()
    if hashlib.sha256(data).hexdigest() != STANDARD_SHA:
        errs.append(f"{STANDARD_SRC}: SHA-256 beklenen değil")
    if not doc.read_bytes().endswith(data):
        errs.append(f"{STANDARD_DOC}: kaynak metin eksiksiz değil")
    for f in STANDARD_LINKS:
        text = (root / f).read_text(encoding="utf-8") if (root / f).exists() else ""
        targets = re.findall(r"\]\(([^)#]*POWER-PCB-ENGINEERING-STANDARD\.md)\)", text)
        if not targets:
            errs.append(f"{f}: mühendislik standardı bağlantısı yok")
        elif not all((root / f).parent.joinpath(t).resolve() == doc.resolve() for t in targets):
            errs.append(f"{f}: mühendislik standardı bağlantı hedefi yanlış")
    return errs


def main() -> int:
    _utf8()
    errs, warns = check()
    for w in warns:
        print("UYARI:", w)
    for e in errs:
        print("HATA:", e)
    print(f"check_workflow: {len(errs)} hata, {len(warns)} uyarı")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
