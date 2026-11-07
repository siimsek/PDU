# G3 — repo temizliği ve token optimizasyonu

Kural: hiçbir kanıt silinmedi; taşıma `git mv` ile `archive/` altına yapıldı ([`archive/INDEX.md`](../../archive/INDEX.md), [`MANIFEST-SHA256.txt`](../../archive/MANIFEST-SHA256.txt) — 880 dosya, `sha256sum -c` geçti). Tek istisna: G2 commit'ine yanlışlıkla giren iki hata ayıklama dalga dökümü (`reports/g2/sim/f2/d.txt` 10.8 MB, `f4/e.txt` 29.1 MB) `git rm` ile çıkarıldı; hiçbir rapor sayısının kaynağı değiller ve `a99ee4b` commit'inde duruyorlar. Her taşıma adımından sonra tüm pytest koşuldu; son adımda `analysis/run_all.py` 7/7 exit 0.

## Önce / sonra

| Ölçüm | Önce (G2 ucu `6b2b16b`) | Sonra (`wp/g3-pcb-ready`) | Değişim |
|---|---:|---:|---:|
| İzlenen dosya (toplam) | 1056 | 1209 (881 arşivde) | +153 (G3 yeniden koşu, rapor, attempt kanıtları) |
| **Aktif (arşiv dışı) dosya** | 1056 | **328** | **−%69** (hedef ≥%60 ✓) |
| İzlenen boyut | 76.0 MB | 37.7 MB | −%50 |
| Aktif boyut | 76.0 MB | 3.81 MB | −%95 |
| Ajan giriş paketi | yok; yön bulmak için README + `docs/` (11 dosya, ~68 kB ≈ 21k token) okunuyordu | `docs/START-HERE.md` (37 satır) + `AGENTS.md` (36) + `CLAUDE.md` (9) + `PCB-HANDOFF.md` (63) = 12.5 k karakter ≈ **3.9k token** | hedef ≤15k ✓ |
| pytest | 91 passed, 2.5 s | 95 passed, 2.7 s | +4 regresyon testi |

Token tahmini: karakter / 3.2 (Türkçe metin için tutucu oran).

## Taşınanlar

| Hedef | Kaynak | Dosya |
|---|---|---:|
| `archive/sim-legacy/` | `simulation/` (G0/WP deck/log, aday OVP koşuları, legacy_models, history, eski koşucular) | 222 |
| `archive/g1-evidence/` | `reports/g1/sim/` (testlerin okuduğu 8 dosya hariç), `PR2-REVIEW-*.md`, `*-attempt*`, `hardware/validation/` (KiCad `Pinmap.kicad_*` yerinde bırakıldı) | 199 |
| `archive/g2-sim-attempts/` | G2 `-attemptN` deck/log + G3 yeniden koşusunun eski adlı/öncül deck'leri | 324 |
| `archive/konnect-diagnostics/` | `.konnect/diagnostics/` (`netclass-plan.json` hariç) | 88 |
| `archive/docs-legacy/`, `archive/renders/` | `docs/archive/`, PNG/SVG render'lar | 37 |
| `archive/g1-tooling/` | `generate_g1_reports.py` (rapor ezme riski), `run_g1_simulations.py`, `run_ovp_component_checks.py` (test bağımlılığı yok) | 3 |
| `archive/g2-debug/` | G2 hata ayıklama deck/log | 6 |

## Birleştirme ve giriş belgeleri

- `reports/g1/PR2-REVIEW-*.md` (7 tur) → tek [`reports/g1/REVIEW-LOG.md`](../g1/REVIEW-LOG.md) (bulgu | G1 sonucu | G2 karşılığı | kanıt).
- 20 eski özet/karar belgesine `SUPERSEDED (G3) → <yeni belge>` başlığı (G1-SUMMARY, OVP-UVLO-DECISION, OVP-ENGINEERING-RESULT, G1/G2 USER-DECISIONS, docs/PROJECT-STATE, design, SON-TESLIM …); içerikleri değiştirilmedi.
- Yeni: [`docs/START-HERE.md`](../../docs/START-HERE.md), [`AGENTS.md`](../../AGENTS.md), [`CLAUDE.md`](../../CLAUDE.md), [`.claude/settings.json`](../../.claude/settings.json) (`permissions.ask` ile `archive/**`, `reports/*/sim/**`, `reports/g1/*.json`, `hardware/_datasheets/**` okumadan önce onay; sözdizimi code.claude.com/docs/en/settings belgesinden doğrulandı).
- `.gitignore`: `.pytest_cache/`, ad-hoc ngspice `_t.*`, `reports/**/sim/**/dbg/`. `.gitattributes`: mevcut `* text=auto eol=lf` korunur; `/archive/** -text` (manifest baytları sabit). CRLF kalan aktif dosyalar yalnız bilinçli `-text` olanlar (KiCad, export netlist/BOM, vendor JSON — kanıt hash'leri bu baytlara bağlı).

## Kullanılmayan / korunan betikler

- Aktif kalan G1 araçları (`analysis/ovp_*.py`, `shared_bus_fault.py`, `pdu_calc.py`, `verify_pr2_review.py`) G1 testlerinin bağımlılığıdır.
- `calculate.py` ve `tools/check_repository.py` test dışı eski kontrol araçları; `simulation/` içinde gereken girdileri bırakıldı, arşive taşınmadı (kök komut referansları README'de).
- `calculate_routing_rules.py` G2 yönlendirme planını okuyacak şekilde güncellendi.
