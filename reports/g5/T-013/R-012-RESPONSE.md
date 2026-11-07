# R-012 tur 1 yanıtı (BUILDER)

| R-012 bulgusu | Düzeltme | Kanıt |
|---|---|---|
| #1 CIN1–8 kontrolcülerden uzak (en yakın 29,60 / 43,28 mm) | CIN1–4 → U1, CIN5–8 → U2; IC'nin VIN–PGND kenarına tek sütun, aralık 0,3 mm (`pcb_setup.py` `HOT_LOOP`). Merkez uzaklıkları 5,64–16,41 mm. | `placement.json` (`hot_loop`, `positions_d006`), `placement.png`, `test_cin_at_buck_hot_loop` |
| #2 courtyard içi 0,25 mm istisnası çok geniş | DRU: genel `intersectsCourtyard('*')` kaldırıldı; sınıf başına yalnız o sınıfta ince adımlı (≤ 0,65 mm) padi olan ayak izleri. Uzunluk ve uç DRU'da ifade edilemediği için ayrı denetim: `pcb_drc.py neck_audit` (≥ 0,25 mm, ≤ 1,5 mm, aynı ağda listeli ince adımlı padde biter) → ihlal kapıyı düşürür. | `PDU.kicad_dru`, `drc-summary.json` `neck_down`, `neck-probe.json` (A/B/C/D deneme izleri, PASS), `test_neck_audit_limits_scope_and_length` |

Yeniden üretim: `pcb_setup.py` → `pcb_rules.py` → `pcb_drc.py` → `pcb_neck_probe.py`. Boş kart DRC 0, parite 0, yerleşimli kartta hata yalnız unconnected 402; pre_merge PASS.
