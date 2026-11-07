"""Shared helpers for the W0 workflow scripts (standard library only)."""
from __future__ import annotations

import fnmatch
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SCALAR_FIELDS = ("ID", "Rol", "Boyut", "Model önerisi", "Durum", "Dal adı", "Bağımlılık")
SECTION_FIELDS = ("Hedef", "Girdiler", "İzinli yazma yolları", "Yasak", "Kabul kriterleri", "Durdurma koşulu", "Çıktı dosyaları")
STATES = ("Draft", "Ready", "InProgress", "Review", "Done", "Blocked")
CARD_RE = re.compile(r"^[TRD]-\d{3}[a-z]?$")

# Files that carry BUILDER results; excluded from THINKER packs unless --include-results (independence rule).
RESULT_PATTERNS = ("*results*.json", "*-results.json", "*RESULTS*.md", "reports/*/VERIFY.md", "reports/*/sim/*",
                   "reports/g4/N1-DECISION.md", "reports/g4/B2-B6.md", "reports/g4/AUDIT2.md", "reports/g4/PCB-READY-v2.md",
                   "reports/g3/PCB-READY.md", "reports/g3/AUDIT.md")


def is_result(path: str) -> bool:
    p = path.replace("\\", "/")
    return any(fnmatch.fnmatch(p, pat) or fnmatch.fnmatch(Path(p).name, pat) for pat in RESULT_PATTERNS)


def card_path(card_id: str, root: Path = ROOT) -> Path | None:
    for base in (root / "tasks", root / "tasks" / "done"):
        p = base / f"{card_id}.md"
        if p.exists():
            return p
    return None


def iter_cards(root: Path = ROOT):
    for base in (root / "tasks", root / "tasks" / "done"):
        if base.is_dir():
            for p in sorted(base.glob("*.md")):
                if CARD_RE.match(p.stem):
                    yield p


def parse_card(text: str) -> dict:
    """Return {'scalars': {field: value}, 'sections': {heading: body}}."""
    scalars, sections, cur, buf = {}, {}, None, []
    for line in text.splitlines():
        m = re.match(r"^- \*\*(.+?):\*\*\s*(.*)$", line)
        if m and cur is None:
            scalars[m.group(1).strip()] = m.group(2).strip()
            continue
        h = re.match(r"^##\s+(.+?)\s*$", line)
        if h:
            if cur is not None:
                sections[cur] = "\n".join(buf).strip()
            cur, buf = h.group(1), []
            continue
        if cur is not None:
            buf.append(line)
    if cur is not None:
        sections[cur] = "\n".join(buf).strip()
    return {"scalars": scalars, "sections": sections}


def backtick_paths(body: str, root: Path = ROOT) -> list[str]:
    """Repo-relative paths written in backticks that exist (files or directories)."""
    out = []
    for tok in re.findall(r"`([^`\s]+)`", body):
        tok = tok.strip().rstrip(",;")
        if tok.startswith(("http", "-", "\"")) or "*" in tok:
            continue
        if (root / tok).exists() and tok not in out:
            out.append(tok)
    return out


def git(*args: str, root: Path = ROOT) -> str:
    try:
        p = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, encoding="utf-8")
        return p.stdout.rstrip() if p.returncode == 0 else ""
    except OSError:
        return ""


def tokens(text: str) -> int:
    return len(text) // 4
