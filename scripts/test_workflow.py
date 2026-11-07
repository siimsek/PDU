"""Tests for the W0 workflow scripts (pytest, standard library only)."""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_workflow as cw  # noqa: E402
import make_pack as mp  # noqa: E402
from wf_common import ROOT, is_result, parse_card  # noqa: E402

GOOD_CARD = """# T-999 — test

- **ID:** T-999
- **Rol:** BUILDER
- **Boyut:** S
- **Model önerisi:** Sonnet
- **Durum:** Ready
- **Dal adı:** wp/T-999
- **Bağımlılık:** —

## Hedef
x
## Girdiler
- `docs/START-HERE.md`
## İzinli yazma yolları
- `x/`
## Yasak
- y
## Kabul kriterleri
- z
## Durdurma koşulu
- w
## Çıktı dosyaları
- `x/out.md`
"""


def _mini_repo(tmp_path: Path, card: str = GOOD_CARD, queue_state: str = "Ready") -> Path:
    (tmp_path / "tasks").mkdir()
    (tmp_path / "tasks" / "T-999.md").write_text(card, encoding="utf-8")
    (tmp_path / "tasks" / "queue.md").write_text(
        f"| ID | Rol | Boyut | Bağımlılık | Durum |\n|---|---|---|---|---|\n| [T-999](T-999.md) | BUILDER | S | — | {queue_state} |\n",
        encoding="utf-8")
    return tmp_path


def test_repository_workflow_is_consistent():
    errs, _ = cw.check(ROOT)
    assert errs == [], errs


def test_line_limits_hold():
    for rel, lim in cw.LINE_LIMITS.items():
        assert len((ROOT / rel).read_text(encoding="utf-8").splitlines()) <= lim, rel


def test_card_missing_section_is_error(tmp_path):
    root = _mini_repo(tmp_path, GOOD_CARD.replace("## Kabul kriterleri\n- z\n", ""))
    errs, _ = cw.check_cards(root)
    assert any("Kabul kriterleri" in e for e in errs)


def test_size_L_rejected(tmp_path):
    root = _mini_repo(tmp_path, GOOD_CARD.replace("**Boyut:** S", "**Boyut:** L"))
    errs, _ = cw.check_cards(root)
    assert any("L yasak" in e for e in errs)


def test_queue_state_mismatch(tmp_path):
    root = _mini_repo(tmp_path, queue_state="Done")
    _, status = cw.check_cards(root)
    assert status == {"T-999": "Ready"}
    assert any("≠ kart" in e for e in cw.check_queue(root, status))


def test_broken_link_detected(tmp_path):
    root = _mini_repo(tmp_path)
    (root / "tasks" / "T-999.md").write_text(GOOD_CARD + "\n[yok](nope.md)\n", encoding="utf-8")
    assert any("nope.md" in e for e in cw.check_links(root))


def test_result_classification():
    assert is_result("reports/g4/n1-results.json")
    assert is_result("reports/g2/SIM-RESULTS.md")
    assert not is_result("design/pdu_v2_spec.yaml")


def test_thinker_pack_excludes_results_by_default():
    card = GOOD_CARD.replace("**Rol:** BUILDER", "**Rol:** THINKER").replace(
        "- `docs/START-HERE.md`", "- `design/pdu_v2_spec.yaml`\n- `reports/g2/SIM-RESULTS.md`")
    text, _, excluded, _ = mp.build_pack("T-999", "codex", card_text=card)
    assert excluded == ["reports/g2/SIM-RESULTS.md"]
    assert "### `reports/g2/SIM-RESULTS.md`" not in text
    text2, _, excluded2, _ = mp.build_pack("T-999", "codex", include_results=True, card_text=card)
    assert excluded2 == [] and "### `reports/g2/SIM-RESULTS.md`" in text2


def test_real_packs_within_budget():
    _, n_codex, excluded, _ = mp.build_pack("R-001", "codex")
    assert n_codex <= mp.LIMIT["codex"]
    assert "reports/g4/n1-results.json" in excluded
    _, n_chk, _, _ = mp.build_pack("T-001", "checker")
    assert n_chk <= mp.LIMIT["checker"]


def test_entry_pack_under_6k_tokens():
    files = ["docs/START-HERE.md", "CLAUDE.md", "HANDOFF.md", "tasks/T-001.md"]
    chars = sum(len((ROOT / f).read_text(encoding="utf-8")) for f in files)
    assert chars // 4 <= 6000
    files_t = ["docs/START-HERE.md", "AGENTS.md", "HANDOFF.md", "tasks/R-001.md"]
    assert sum(len((ROOT / f).read_text(encoding="utf-8")) for f in files_t) // 4 <= 6000


def test_all_cards_parse_with_required_fields():
    for p in (ROOT / "tasks").glob("[TRD]-*.md"):
        c = parse_card(p.read_text(encoding="utf-8"))
        assert c["scalars"]["ID"] == p.stem
