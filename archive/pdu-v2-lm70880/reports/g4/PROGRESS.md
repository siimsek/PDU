# G4 ilerleme kaydı (wp/g4-closure)

| Bölüm | Durum | Commit | Çıktı |
|---|---|---|---|
| A — G3 doğrulama (alt ajan A/B) | tamam | `5133f44`, `49e700c` | [AUDIT2.md](AUDIT2.md), [baseline/](baseline/), [datasheet-inputs.md](datasheet-inputs.md) |
| B1 — N1 bobin doyumu | tamam: faz OC tetiği, O1 HESAP ≤11.41 V | `e558e54` | [N1-DECISION.md](N1-DECISION.md), [n1-results.json](n1-results.json) |
| B2 — eFuse L varyantı | doğrulandı | `49e700c` | [B2-B6.md](B2-B6.md) §B2 |
| B3 — LM70880 BIAS | düzeltildi: AGND | `e558e54` | §B3 |
| B4 — yığılmış tolerans + trim | tamam: 32× COUT, RCOMP 33.2k, R_TRIM | `e558e54` | §B4, [b4-results.json](b4-results.json) |
| B5 — açık varsayımlar | gm / UVLO tarandı; tezgâh AÇIK | `49e700c` | §B5, [b5-results.json](b5-results.json) |
| B6 — tutarlılık | Family 2/4 ifadeleri yeniden yazıldı | `49e700c` | §B6 |
| C — BOM / footprint / tutarlılık | 146/147 MPN; footprint-map; check_consistency | `9672ab3` | `design/bom-v2.csv`, `design/footprint-map.csv`, [consistency.json](consistency.json) |
| D — belge zinciri, temizlik | tamam | bu dal | START-HERE, AGENTS, README, KICAD/PCB-HANDOFF/BENCH/DESIGN-RULES/PROTECTION/POWER/LOOP |
| E — PCB-READY v2 | tamam | bu dal | [PCB-READY-v2.md](PCB-READY-v2.md) |
| F — GitHub adımları | kapı sonucuna bağlı | — | PCB-READY-v2 §GitHub |

Notlar
- G4 sırasında düzeltilen hata: N1 INA gecikme duyarlılığı belgede eski sayılarla yazılmıştı (4 µs → 11.94 V); hesap VIN 20/26 V kötüsünü alacak şekilde genişletildi, JSON değeri 11.56 V belgelere işlendi.
- `loop.py` tezgâh ayar aralığı (10–33k) seçilen 33.2k'yı kapsamıyordu → 22–47k.
- `params.py` RFB2 kaynağı ERA3AEB1022V → "9.76k + R_TRIM 442 Ω = 10.202k" (değer 10.2k nominal, fark %0.02).
