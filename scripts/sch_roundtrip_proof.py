"""T-002 evidence: lossless S-expression round trip of the KiCad project, checked with kicad-cli.

    python scripts/sch_roundtrip_proof.py      # writes reports/g5/tooling/roundtrip.json, exit 0 if all checks pass

Works on a temporary copy only; the repository's KiCad files are never written.
Checks: (1) PDU.kicad_sch / PDU.kicad_pcb / custom .kicad_mod byte-identical after parse+dump;
(2) ERC JSON violations and exported KiCad netlist identical between original copy and round-tripped copy;
(3) an edit made with set_property (RFB2 Value) loads in kicad-cli (ERC count unchanged) and appears in the netlist.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kicad_sexpr as ks  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
KICAD_CLI = os.environ.get("KICAD_CLI", r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe")
OUT = ROOT / "reports" / "g5" / "tooling" / "roundtrip.json"
PROJECT_FILES = ("PDU.kicad_pro", "PDU.kicad_sch", "PDU.kicad_pcb", "sym-lib-table", "fp-lib-table")


def cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([KICAD_CLI, *args], capture_output=True, text=True, encoding="utf-8", errors="replace")


def copy_project(dst: Path):
    for f in PROJECT_FILES:
        if (ROOT / f).exists():
            shutil.copy2(ROOT / f, dst / f)
    if (ROOT / "hardware" / "lib").exists():
        shutil.copytree(ROOT / "hardware" / "lib", dst / "hardware" / "lib")


def erc(d: Path) -> list:
    out = d / "erc.json"
    p = cli("sch", "erc", "--format", "json", "-o", str(out), str(d / "PDU.kicad_sch"))
    data = json.loads(out.read_text(encoding="utf-8"))
    return p.returncode, sorted(json.dumps(v, sort_keys=True) for s in data["sheets"] for v in s["violations"])


def netlist(d: Path) -> str:
    out = d / "net.net"
    cli("sch", "export", "netlist", "--format", "kicadsexpr", "-o", str(out), str(d / "PDU.kicad_sch"))
    txt = out.read_text(encoding="utf-8")
    # drop volatile header lines (date, source path, tool version)
    return "\n".join(ln for ln in txt.splitlines() if not re.search(r"\((date|source|tool)\b", ln))


def main() -> int:
    res = {"kicad_cli": cli("version").stdout.strip(), "byte_identical": {}, "checks": {}}
    files = [ROOT / "PDU.kicad_sch", ROOT / "PDU.kicad_pcb"] + sorted((ROOT / "hardware" / "lib" / "PDU.pretty").glob("*.kicad_mod"))
    for f in files:
        src = f.read_bytes().decode("utf-8")
        res["byte_identical"][f.relative_to(ROOT).as_posix()] = ks.dumps(ks.parse(src)) == src
    with tempfile.TemporaryDirectory() as t:
        a, b, c = Path(t) / "orig", Path(t) / "rt", Path(t) / "edit"
        for d in (a, b, c):
            d.mkdir()
            copy_project(d)
        src = (a / "PDU.kicad_sch").read_bytes().decode("utf-8")
        (b / "PDU.kicad_sch").write_bytes(ks.dumps(ks.parse(src)).encode("utf-8"))
        root = ks.parse(src)
        edited = ks.set_property(root, "RFB2", "Value", "9.76k")
        (c / "PDU.kicad_sch").write_bytes(ks.dumps(root).encode("utf-8"))
        (ea_rc, ea), (eb_rc, eb), (ec_rc, ec) = erc(a), erc(b), erc(c)
        na, nb, nc = netlist(a), netlist(b), netlist(c)
        res["checks"] = {
            "erc_original_violations": len(ea), "erc_roundtrip_violations": len(eb),
            "erc_identical": ea == eb, "netlist_identical": na == nb and len(na) > 0,
            "edit_applied": edited, "erc_after_edit_violations": len(ec),
            "edit_visible_in_netlist": '(value "9.76k")' in nc and '(value "9.76k")' not in na,
            "netlist_lines": len(na.splitlines()),
        }
    ok = all(res["byte_identical"].values()) and all(res["checks"][k] for k in
                                                     ("erc_identical", "netlist_identical", "edit_applied", "edit_visible_in_netlist")) \
        and res["checks"]["erc_after_edit_violations"] == res["checks"]["erc_original_violations"]
    res["pass"] = ok
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(res, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"pass": ok, **res["checks"], "files_byte_identical": sum(res["byte_identical"].values()),
                      "files": len(res["byte_identical"])}))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
