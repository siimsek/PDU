"""Build a session pack for a task card (standard library only).

    python scripts/make_pack.py --task R-001 --for codex            # THINKER pack, BUILDER results excluded
    python scripts/make_pack.py --task R-001 --for codex --include-results
    python scripts/make_pack.py --task T-001 --for checker          # <= 3k-token control pack for the Claude chat

Output: packs/<task>-<for>.md (packs/ is git-ignored). Token estimate = characters / 4.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wf_common import ROOT, backtick_paths, card_path, git, is_result, parse_card, tokens  # noqa: E402

LIMIT = {"codex": 12000, "chatgpt": 12000, "checker": 3000}
MAX_FILE_CHARS = 16000
MAX_FILE_BYTES = 400_000
TEXT_EXT = {".md", ".txt", ".py", ".yaml", ".yml", ".json", ".csv", ".cir", ".inc", ".toml", ".cfg"}


def _file_block(root: Path, rel: str, max_chars: int) -> str:
    p = root / rel
    if p.is_dir():
        names = sorted(x.relative_to(root).as_posix() for x in p.rglob("*") if x.is_file())
        return f"### `{rel}/` (dizin; {len(names)} dosya)\n" + "\n".join(f"- {n}" for n in names[:40]) + "\n"
    if p.suffix.lower() not in TEXT_EXT or p.stat().st_size > MAX_FILE_BYTES:
        return f"### `{rel}`\n(ikili veya {p.stat().st_size} bayt — pakete gömülmedi; dosyayı ayrıca aç)\n"
    txt = p.read_text(encoding="utf-8", errors="replace")
    note = ""
    if len(txt) > max_chars:
        txt, note = txt[:max_chars], f"\n… (kısaltıldı: {len(txt)} karakterin ilk {max_chars}'i)\n"
    return f"### `{rel}`\n```\n{txt}\n```{note}\n"


def _git_block(root: Path) -> str:
    head = git("log", "-1", "--format=%h %cs %s", root=root)
    base = "main" if git("rev-parse", "--verify", "--quiet", "main", root=root) else ""
    stat = git("diff", "--stat", f"{base}...HEAD", root=root) if base else ""
    if not stat:
        stat = git("show", "--stat", "--format=", "HEAD", root=root)
    lines = stat.splitlines()
    if len(lines) > 25:
        lines = lines[:24] + [f"… ({len(lines) - 25} satır daha)", lines[-1]]
    return f"## Git\n- Dal: {git('branch', '--show-current', root=root)}\n- Son commit: {head}\n\n```\n" + "\n".join(lines) + "\n```\n"


def _latest_note(root: Path) -> str:
    cands = []
    for sub in ("reviews", "decisions"):
        d = root / sub
        if d.is_dir():
            cands += [p for p in d.glob("*.md") if p.stem not in ("README", "TEMPLATE")]
    if not cands:
        return "## Son karar/inceleme\n(henüz yok)\n"
    p = max(cands, key=lambda x: (git("log", "-1", "--format=%ct", "--", x.relative_to(root).as_posix(), root=root) or "0", x.stat().st_mtime))
    return "## Son karar/inceleme\n" + _file_block(root, p.relative_to(root).as_posix(), 2500)


def _failed_gates(root: Path, card: dict) -> str:
    import check_workflow
    errs, warns = check_workflow.check(root)
    lines = ["## Başarısız / açık kapılar"]
    lines += [f"- HATA (check_workflow): {e}" for e in errs] or ["- check_workflow: 0 hata"]
    lines += [f"- UYARI: {w}" for w in warns]
    import re
    want = re.findall(r"`([^`\s]+)`", card["sections"].get("Çıktı dosyaları", ""))
    missing = [w for w in want if "*" not in w and "<" not in w and not (root / w).exists()]
    if missing:
        lines.append("- Kartın çıktı dosyaları henüz yok: " + ", ".join(missing))
    q = root / "tasks" / "queue.md"
    if q.exists():
        blocked = [ln for ln in q.read_text(encoding="utf-8").splitlines() if ln.rstrip().endswith("| Blocked |")]
        lines += [f"- Blocked: {ln}" for ln in blocked]
    return "\n".join(lines) + "\n"


def build_pack(task: str, target: str, include_results: bool = False, root: Path = ROOT, card_text: str | None = None):
    if card_text is None:
        cp = card_path(task, root)
        if cp is None:
            raise SystemExit(f"kart bulunamadı: tasks/{task}.md")
        card_text = cp.read_text(encoding="utf-8")
    card = parse_card(card_text)
    rol = card["scalars"].get("Rol", "").split()[0] if card["scalars"].get("Rol") else ""
    parts = [f"# Paket {task} → {target}\n\nÜretici: `python scripts/make_pack.py --task {task} --for {target}"
             f"{' --include-results' if include_results else ''}`. Rolün: "
             f"{'CHECKER (Claude sohbet) — yalnız denetle, repoya yazma' if target == 'checker' else 'THINKER — AGENTS.md kuralları'}.\n"]
    excluded = []
    if target == "checker":
        parts.append(_file_block(root, "HANDOFF.md", 3000) if (root / "HANDOFF.md").exists() else "")
        sc = card["scalars"]
        parts.append("## Kart özeti\n" + "\n".join(f"- {k}: {v}" for k, v in sc.items()) + "\n\n### Kabul kriterleri\n"
                     + card["sections"].get("Kabul kriterleri", "") + "\n")
        parts.append(_latest_note(root))
        parts.append(_failed_gates(root, card))
    else:
        parts.append("## Kart\n" + card_text + "\n")
        for rel in ("docs/START-HERE.md", "HANDOFF.md"):
            if (root / rel).exists():
                parts.append(_file_block(root, rel, MAX_FILE_CHARS))
        parts.append("## Girdiler (kartın listesi)\n")
        for rel in backtick_paths(card["sections"].get("Girdiler", ""), root):
            if rel in ("docs/START-HERE.md", "HANDOFF.md"):
                continue
            if is_result(rel) and not include_results:
                excluded.append(rel)
                continue
            parts.append(_file_block(root, rel, MAX_FILE_CHARS))
        if include_results:
            outs = backtick_paths(card["sections"].get("Çıktı dosyaları", ""), root)
            if outs:
                parts.append("## Sonuçlar (karşılaştırma turu)\n" + "".join(_file_block(root, r, 4000) for r in outs))
        if excluded:
            parts.append("## Bağımsızlık\nAşağıdaki BUILDER sonuç dosyaları pakete **konmadı** (`--include-results` ile eklenir):\n"
                         + "\n".join(f"- `{e}`" for e in excluded) + "\n")
        elif rol == "THINKER" and not include_results:
            parts.append("## Bağımsızlık\nKartın girdilerinde BUILDER sonuç dosyası yok; sonuçlar pakete konmadı.\n")
        parts.append(_git_block(root))
    text = "\n".join(p for p in parts if p)
    n = tokens(text)
    text += f"\n---\nYaklaşık token: {n} (karakter/4; sınır {LIMIT[target]}).\n"
    return text, n, excluded, [(p.split("\n", 1)[0][:80], tokens(p)) for p in parts if p]


def _utf8():
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass


def main(argv=None) -> int:
    _utf8()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--task", required=True)
    ap.add_argument("--for", dest="target", required=True, choices=sorted(LIMIT))
    ap.add_argument("--include-results", action="store_true")
    ap.add_argument("--out", default=str(ROOT / "packs"))
    a = ap.parse_args(argv)
    text, n, excluded, sizes = build_pack(a.task, a.target, a.include_results)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    f = out / f"{a.task}-{a.target}.md"
    f.write_text(text, encoding="utf-8", newline="\n")
    print(f"{f.relative_to(ROOT) if f.is_relative_to(ROOT) else f}: ~{n} token, {len(text)} karakter; sonuç dışı bırakılan: {len(excluded)}")
    if n > LIMIT[a.target]:
        print(f"UYARI: {n} > {LIMIT[a.target]} token. En büyük bölümler (kısaltma adayı):")
        for title, t in sorted(sizes, key=lambda x: -x[1])[:5]:
            print(f"  ~{t:6d}  {title}")
        print("Öneri: kartın Girdiler'ini bölüm/satır aralığına daralt veya büyük dosyayı özetle.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
