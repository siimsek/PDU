# archive/ — taşınmış kanıt dizini (G3, G4 eki 2026-11-07)

Hiçbir dosya silinmedi; hepsi `git mv` ile taşındı (geçmiş: `git log --follow <yeni yol>`). Bayt bütünlüğü: [`MANIFEST-SHA256.txt`](MANIFEST-SHA256.txt) (`sha256sum -c archive/MANIFEST-SHA256.txt`), `.gitattributes` `/archive/** -text` ile satır sonu dönüşümü kapalı. **Gerekmedikçe okuma**; güncel durum için [`docs/START-HERE.md`](../docs/START-HERE.md).

| Klasör | Ne | Nereden | Neden taşındı | Bağlı olduğu sonuç belgesi |
|---|---|---|---|---|
| `sim-legacy/simulation/` (222) | G0/WP dönemi davranışsal deck/log, aday OVP (LTC4365, global) koşuları, `legacy_models`, `history`, LTspice parite dosyaları, eski koşucu betikleri | `simulation/` | G2 netlisti (`design/pdu_v2.cir`) yerini aldı; yalnız baseline O1 regresyon deck'i ve `pdu_calc` girdileri `simulation/`'da kaldı | `docs/verification.md` (SUPERSEDED), `reports/g1/SIMULATION-RESULTS.md` |
| `g1-evidence/reports/g1/sim/` | G1 ngspice deck/log'ları (Family 1–4, ortak bara, R6/R7 fikstürleri, deneme kopyaları) | `reports/g1/sim/` | G1 testlerinin okuduğu 8 dosya hariç | `reports/g1/REVIEW-LOG.md`, `reports/g1/*.json` |
| `g1-evidence/reports/g1/` | PR #2 tur raporları `PR2-REVIEW-*.md`, `*-attempt*.json` | `reports/g1/` | Tek tabloya indirildi | `reports/g1/REVIEW-LOG.md` |
| `g1-evidence/hardware/validation/` | Bileşen/footprint doğrulama çizimleri, LTC4365/TPS3701 kanıtları, C5750 vendor koşuları (KiCad `Pinmap.kicad_*` dosyaları yerinde bırakıldı) | `hardware/validation/` | Ham kanıt; `c5750/vendor-ac-summary.json` aktif kaldı | `hardware/COUT-qualification.md` |
| `g1-tooling/` | `generate_g1_reports.py`, `run_g1_simulations.py`, `run_ovp_component_checks.py` | `analysis/` | Test bağımlılığı yok; ilki G1 raporlarını eski içerikle ezer (**çalıştırma**) | `reports/g1/SIMULATION-RESULTS.md` |
| `konnect-diagnostics/.konnect/` | Konnect ara DRC/netlist/plan JSON'ları | `.konnect/diagnostics/` | Ara çıktı; `netclass-plan.json` aktif kaldı (`calculate_routing_rules.py`, `pdu_calc`) | `hardware/routing-width-calculations.json` |
| `docs-legacy/AI-WORKFLOW.md` | G1 dönemi AI çalışma düzeni | `docs/AI-WORKFLOW.md` | W0 ile yerini `docs/WORKFLOW.md` aldı | `docs/WORKFLOW.md` |
| `docs-legacy/docs/archive/` | Eski doküman arşivi, netlist ve ekran görüntüleri | `docs/archive/` | Zaten arşivdi; tek kökte toplandı | `docs/START-HERE.md` |
| `renders/` | Şema/PCB PNG/SVG render'ları | `hardware/`, kök | Üretilmiş görsel | — |
| `g2-sim-attempts/` (188) | G2 SPICE `-attemptN` deck/log çiftleri (yakınsama düzeltmeleri öncesi) | `reports/g2/sim/f1..f5/` | İlk/son deneme kanıtı; nihai koşular `reports/g2/sim/` | `reports/g2/SIM-RESULTS.md`, `reports/g2/PROGRESS.md` K5 |
| `g2-sim-attempts/g4-rerun/` (164), `superseded-g3/` (96), `g3-rerun/` (40) | G3/G4 yeniden koşularında deck değiştiği için korunan önceki deck/log'lar (G4: 32× COUT, L(i), OC tetiği) | `reports/g2/sim/f1..f5/` | `sim_runner.py` deneme kuralı (FAIL/deneme silinmez) | `reports/g2/SIM-RESULTS.md` |
| `g2-debug/` | G2 hata ayıklama deck/log'ları (d.cir, e.cir) | `reports/g2/sim/f2`, `f4` | Rapor sayısına bağlı değil | — |

Repodan çıkarılan (git rm, geçmişte duruyor): `reports/g2/sim/f2/d.txt` (10.8 MB) ve `reports/g2/sim/f4/e.txt` (29.1 MB) — G2 hata ayıklama dalga biçimi dökümleri, hiçbir rapor sayısına kaynak değil; commit `a99ee4b` içinde geri alınabilir (`git show a99ee4b:reports/g2/sim/f4/e.txt`).
