# R-012 yanıtı (BUILDER)

## Tur 1

| R-012 bulgusu | Düzeltme | Kanıt |
|---|---|---|
| #1 CIN1–8 kontrolcülerden uzak (en yakın 29,60 / 43,28 mm) | CIN1–4 → U1, CIN5–8 → U2; IC'nin VIN–PGND kenarına tek sütun, aralık 0,3 mm (`pcb_setup.py` `HOT_LOOP`). Merkez uzaklıkları 5,64–16,41 mm. | `placement.json` (`hot_loop`, `positions_d006`), `placement.png`, `test_cin_at_buck_hot_loop` |
| #2 courtyard içi 0,25 mm istisnası çok geniş | DRU: genel `intersectsCourtyard('*')` kaldırıldı; sınıf başına yalnız o sınıfta ince adımlı (≤ 0,65 mm) padi olan ayak izleri. Uzunluk ve uç DRU'da ifade edilemediği için ayrı denetim: `pcb_drc.py neck_audit` (≥ 0,25 mm, ≤ 1,5 mm, aynı ağda listeli ince adımlı padde biter) → ihlal kapıyı düşürür. | `PDU.kicad_dru`, `drc-summary.json` `neck_down`, `neck-probe.json` (A/B/C/D deneme izleri, PASS), `test_neck_audit_limits_scope_and_length` |

Yeniden üretim: `pcb_setup.py` → `pcb_rules.py` → `pcb_drc.py` → `pcb_neck_probe.py`. Boş kart DRC 0, parite 0, yerleşimli kartta hata yalnız unconnected 402; pre_merge PASS.

## Tur 2 (R-012 KOŞULLU, 1 engelleyici: yay uzunluğu)

R-012 iki turla sınırlı olduğundan bu düzeltme R-012'nin üçüncü turu değildir; bağımsız doğrulaması ayrı kartta: `tasks/R-013.md` (dal wp/R-013).

| Bulgu | Düzeltme | Kanıt |
|---|---|---|
| `neck_audit` yaylarda uçlar arası kirişi ölçüyordu | `scripts/pcb_drc.py`: `arc_length(start, mid, end)` çevrel merkez + `mid`'i içeren süpürme açısı → r·θ (eşdoğrusal noktalarda çoklu çizgi uzunluğu). `track_length()`: `segment` → doğrusal start–end (değişmedi), `arc` → gerçek yay uzunluğu. Denetim şartları aynı: ≥ 0,25 mm, ≤ 1,5 mm (gerçek uzunluk), aynı ağda listeli ince adımlı padde biter. İhlal kaydına `kind` ve `length` eklendi. | `test_arc_length_is_true_length_not_chord` (yarım çember π·0,6; ¾ çember uzak taraf 1,5π; eşdoğrusal 1,0) |
| Prob ve testlerde yay durumu yoktu | `pcb_neck_probe.py`: U1 pad 1'den (/VIN, 0,30 mm) iki `PCB_ARC`, KiCad kaydı üzerinden okunur (kaydedilen kartta yay sayısı 2). **E:** kiriş 1.2 mm, gerçek uzunluk 1.885 mm → denetim `length 1.88 > 1.5 mm` (**FAIL**, beklenen). **F:** kiriş 0.9 mm, gerçek uzunluk 0.9188 mm → denetim temiz (beklenen). Önceki A–D sonuçları değişmedi. Prob `pass: true`. | [neck-probe.json](neck-probe.json), `test_neck_audit_arcs` |

Yeniden koşum: `pcb_drc.py` → boş kart 0 hata, parite 0, neck ihlali 0, `pass: true`; `pcb_neck_probe.py` → `pass: true`; `pytest scripts/test_pcb_setup.py` 11 geçti; `pre_merge.py --schematic B1…B7` PASS (pytest 133, check_workflow 0 hata, check_consistency 0, B1–B7 fark 0).

