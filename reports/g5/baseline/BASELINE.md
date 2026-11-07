# G5 baseline (T-001, 2026-11-07)

Taban: `main` @ `219a2c1` (W0 birleşmesi) + T-001 (bom.py LF). Fiziksel ölçüm yok; SİM davranışsal modeldir.

| Kontrol | Komut | Çıkış | Sonuç | Karşılaştırma |
|---|---|---|---|---|
| pytest | `python -m pytest -q` | 0 | **110 passed** | W0 109 + LF testi 1 |
| run_all | `python analysis/run_all.py` | 0 | 12/12 adım exit 0, 7 dk 24 s; SPICE F1 7/7 tamam (6 PASS + korumasız referans FAIL), F2 4/4, F3 13/13 (11 PASS + 2 trimsiz yığılmış FAIL), F4 3/3 (2 PASS + D_REV'siz FAIL), F5 49/49 | G4 ile aynı; beklenen FAIL'ler korunur |
| Tutarlılık | `python analysis/check_consistency.py` | 0 | 0 hata | aynı |
| İş akışı | `python scripts/check_workflow.py` | 0 | 0 hata (2 uyarı: izin matrisi dışı yollar, beklenen) | — |
| ERC | `kicad-cli sch erc --format json PDU.kicad_sch` (KiCad 10.0.7) | 0 | **0 ihlal** → [erc.json](erc.json) | G4 baseline 0 |
| DRC | `kicad-cli pcb drc --format json --schematic-parity PDU.kicad_pcb` | 0 | **228 uyarı / 197 bağlantısız / 73 parite** → [drc.json](drc.json) | G4 baseline 228 / 197 / 73 (fark yok) |
| CSV satır sonu | `python -m analysis.g2.bom` + bayt kontrolü (test) | 0 | `design/bom-v2.csv`, `design/footprint-map.csv` CR içermez; `git diff` içerik farkı yok | G4'te CRLF yazılıyordu |

kicad-cli yolu: `C:\Program Files\KiCad\10.0\bin\kicad-cli.exe`. run_all'un yeniden yazdığı `reports/g2/sim/**` log'larında yalnız süre/bellek satırları değiştiği için geri alındı (kart kuralı).
