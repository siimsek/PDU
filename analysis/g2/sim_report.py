"""Render reports/g2/SIM-RESULTS.md from reports/g2/sim-results.json (no re-simulation)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
J = ROOT / "reports" / "g2" / "sim-results.json"
MD = ROOT / "reports" / "g2" / "SIM-RESULTS.md"

TITLES = {
    "F1": "Aile 1 — üst anahtar kısa devresi + ortak bara ayırıcı",
    "F2": "Aile 2 — 20–26 V açılış, UVLO kalkışı, hot-plug, dip",
    "F3": "Aile 3 — yük adımı 0.75→7→0.75 A, COMP/Ceff köşeleri",
    "F4": "Aile 4 — eFuse kısa devresi, O1/S2E izolasyonu, giriş kaybı / OUT>IN",
    "F5": "Aile 5 — koruma köşe taraması (eşik, gecikme, Ceff, hata akımı, L) + hassas yol açık artık riski",
}
EXPECTED_FAIL = {"f1_noprot_baseline": "korumasız referans: G1 FAIL'inin yeni netlistte yeniden üretimi (silinmez)",
                 "f4_input_loss_without_drev": "D_REV'siz karşılaştırma (D_REV gerekçesi)",
                 "f5_precision_path_open_residual": "R_OVT açık devre: G4'te faz OC tetiği bağımsız yol olarak kapatıyor",
                 "f3_stacked_low_setpoint_cmin_gmmin": "trimsiz statik alt köşe + transient (görünür FAIL; trim ile kapanır)",
                 "f3_stacked_high_setpoint_cmin_gmmin": "trimsiz statik üst köşe + bırakma (görünür FAIL; trim ile kapanır)",
                 "f1_voltage_trip_only_g3_design": "G3 tasarımı (OC tetiksiz) karşılaştırma; HESAP L-tabanı ≤0.15'te FAIL",
                 "f3_trimmed_low_setpoint_cmin_gmmin": "kart başı trim sonrası statik alt köşe (b4-results.json)",
                 "f3_trimmed_high_setpoint_cmin_gmmin": "kart başı trim sonrası statik üst köşe"}


def fmt(x):
    return f"{x:.4g}" if isinstance(x, (int, float)) else str(x)


def main():
    d = json.loads(J.read_text(encoding="utf-8"))
    L = ["# G2 tam sistem SPICE sonuçları", "",
         f"Netlist: [`design/pdu_v2.cir`](../../design/pdu_v2.cir) (SHA256 `{d['netlist_sha256'][:16]}…`), parametre kaynağı "
         "`analysis/g2/params.py` + `design.py` → her deck'te `.param` bloğu; koşucu [`analysis/g2/sim_runner.py`](../../analysis/g2/sim_runner.py). "
         f"Araç: {d['tool']}. **{d['classification']}.**", "",
         "Bir koşu yalnız ngspice çıkış kodu 0 ve istenen bütün `.meas` değerleri varsa *tamamlandı* sayılır; tamamlanmayan koşu PASS sayılmaz. "
         "Deck/log/girdi SHA256 `sim-results.json` içindedir; deck değiştiğinde önceki deck/log `-attemptN` olarak korunur.", "",
         "| Aile | Koşu | Tamamlanan | Kriter PASS |", "|---|---:|---:|---:|"]
    for fam, s in d["summary"].items():
        L.append(f"| {fam} | {s['runs']} | {s['completed']} | {s['pass']} |")
    for fam in ("F1", "F2", "F3", "F4"):
        L += ["", f"## {TITLES[fam]}", "", "| Koşu | Tamam | Ölçümler (kriterli) | Kriterler | Sonuç | Not |", "|---|---|---|---|---|---|"]
        for name, r in d["runs"].items():
            if r["family"] != fam:
                continue
            meas = ", ".join(f"{k}={fmt(r['measures'].get(k, '—'))}" for k in r["criteria"])
            crit = ", ".join(f"{k} {c['op']} {fmt(c['limit'])}" for k, c in r["criteria"].items())
            res = "PASS" if r["pass"] else ("FAIL" if r["completed"] else "TAMAMLANMADI (kanıt yok)")
            L.append(f"| [{name}]({r['log'].replace('reports/g2/', '', 1)}) | {r['completed']} | {meas} | {crit} | **{res}** | {EXPECTED_FAIL.get(name, '')} |")
    f5 = {n: r for n, r in d["runs"].items() if r["family"] == "F5"}
    sweep = {n: r for n, r in f5.items() if n != "f5_precision_path_open_residual"}
    if sweep:
        comp = [r for r in sweep.values() if r["completed"]]
        o1 = [r["measures"]["o1_max_fault"] for r in comp if "o1_max_fault" in r["measures"]]
        vs = [r["measures"]["vsafe_max_fault"] for r in comp if "vsafe_max_fault" in r["measures"]]
        worst = max(comp, key=lambda r: r["measures"].get("o1_max_fault", 0)) if comp else None
        L += ["", f"## {TITLES['F5']}", "",
              f"Tarama: VTRIP_EFF {{trip_min, trip_max}} + 50 mV×k overdrive × gecikme {{0.3 µs, max}} × Ceff {{min, typ, max}} × "
              f"Rsrc {{20, 200 mΩ}} × L {{0.8, 1.2}} = {len(sweep)} koşu; ön-hata barası statik alt köşe (10.8333 V), VIN 26 V, yüksüz.", "",
              f"- Tamamlanan: {len(comp)}/{len(sweep)}; kriter PASS: {sum(r['pass'] for r in sweep.values())}.",
              f"- O1 tepe aralığı: {min(o1):.4f} – {max(o1):.4f} V (sınır 12.0 V)." if o1 else "- O1 ölçümü yok.",
              f"- VSAFE (U3/U4 IN) tepe maks: {max(vs):.4f} V (sınır 30 V abs, 24 V önerilen)." if vs else "",
              f"- En kötü köşe: [{Path(worst['deck']).stem}]({worst['log'].replace('reports/g2/', '', 1)})." if worst else ""]
        incomplete = [n for n, r in sweep.items() if not r["completed"]]
        if incomplete:
            L.append(f"- Tamamlanmayan: {', '.join(incomplete)} → kanıt yok.")
    if "f5_precision_path_open_residual" in f5:
        r = f5["f5_precision_path_open_residual"]
        L += ["", f"Hassas yol açık (R_OVT açık devre, yalnız kaba OV): O1 tepe {fmt(r['measures'].get('o1_max_fault', '—'))} V, "
                  f"VSAFE tepe {fmt(r['measures'].get('vsafe_max_fault', '—'))} V → {'PASS' if r['pass'] else 'FAIL'} "
                  "(artık risk; PROTECTION-DECISION §4)."]
    L += ["", "## Model sınırları", "",
          "- Ortalama (anahtarlamasız) model: tepe akım komutu + sınırlı ortalama anahtar, akım döngüsü ~100 kHz eşdeğer; örnekleme etkisi ve "
          "LM70880 iç devresi yok. G4: bobin L(i) Vishay doc 34207 p.3 tipik eğrisi (16 A'ya kadar) + 16 A üstü taban LFLOOR (VARSAYIM); "
          "faz aşırı akım tetiği (INA296+TLV3601) TOC_DLY gecikmesiyle. eFuse: tek yönlü, aktif akım sınırı, UVLO histerezisi, 16.9 V OVLO; ITIMER/termal kapanma yok.",
          "- Koruma zinciri: karşılaştırıcı+mandal+LM74502H tek toplu gecikme (`TDLY`) ile; eşik garantili-gecikme seviyesinde "
          "(trip + 50 mV overdrive×k). FET ideal anahtar + gövde diyotu; SOA/termal yok.",
          "- Kapasitörler toplu Ceff + ESR/ESL; CIN/CEFOUT Ceff VARSAYIM (datasheet yok).",
          "- Bu sonuçlar tezgâh ölçümünün yerini tutmaz (BENCH-ACCEPTANCE)."]
    MD.write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
