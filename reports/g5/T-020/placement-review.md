# T-020 — ayrıntılı yerleşim (iz/via/döküm yok)

KiCad 10.0.7, bundled `pcbnew` (D-009). Üretim: `scripts/pcb_place.py`, T-013 kartından. Koordinatlar D-006 (sol-alt orijin, y yukarı). Karşılaştırma: `placement.json` `moved_vs_t013` (140 parça) ve [placement.png](placement.png), [placement.svg](placement.svg).

## DRC

| Kontrol | Sonuç |
|---|---|
| Yerleşimli kart + parite ([drc-placed.json](drc-placed.json)) | ihlal/uyarı **0**; parite **0**; `unconnected_items` 402 (iz yok, beklenen) |
| Boş kart ([drc-empty.json](drc-empty.json)) | 0 öğe |
| `pcb_rules.py --check` ([pcb-rules-check.txt](pcb-rules-check.txt)), darboğaz denetimi | PASS; ihlal 0 |

Değişmeyenler: 120 × 85 dış hat, H1–H4 {'H1': [6.0, 6.0], 'H2': [114.0, 6.0], 'H3': [6.0, 79.0], 'H4': [114.0, 79.0]}, J1/J2/J3/J_OVP_INJ_BUS konumları, ağlar, değerler, footprint'ler, stackup, netclass.

## Yerleşim ölçüleri (HESAP, pad/parça merkezleri; gerçek iz uzunluğu değil)

| Kısıt | Ölçü |
|---|---|
| CIN → LM70880 merkez (U1: CIN1–4, U2: CIN5–8) | [5.59, 9.13, 6.41, 9.65] / [5.59, 9.13, 6.41, 9.65] mm; 2 güney + 2 doğu (aşağıda) |
| RS → INA296 (hedef ≤15 mm bağlantı) | RS1–U11 8.79 mm, RS2–U12 9.42 mm |
| INA296 → TLV3601 | U11–U13 5.21 mm, U12–U14 5.21 mm |
| U6 GATE – Q2 G pad (≤10 mm iz için) | 5.42 mm; gerçek uzunluk T-023'te |
| Mantık parçaları → en yakın SW pad merkezi (≥10 mm) | en küçük 15.47 mm (U13) |
| L → LM70880 merkez | L1–U1 11.2 mm, L2–U2 11.05 mm |
| D1 → J1 merkez | 9.38 mm |

U1 180° (VIN/PGND güneyde, SW batıda L1'e); U2 0° (VIN/PGND kuzeyde, SW doğuda L2'ye). **R-015 turunda düzeltme:** L1 180° döndürüldü; önceki yerleşimde L1'in SW padi U1'den uzak taraftaydı (33,29 mm; U1 SW pinleri 46,1 mm), artık U1 tarafında. Kontrol pini parçaları (CVCC, CVDDA, RT) SW bakırının dışında.

## CIN yerleşim alternatifleri (R-015)

Tam veri: [cin-alternatives.json](cin-alternatives.json). Her satır aynı betikle (`PDU_CIN_VARIANT`) üretildi; U2 aynı yerleşimin 180° dönmüşü, sayılar aynı. HESAP, routed loop değil. Yol = kondansatör /VIN padi – en yakın IC /VIN padi + kondansatör /GND padi – en yakın IC PGND padi (23–26) kenar aralığı; kutu = bu dört pad merkezinin kapsayan dikdörtgeni.

| Seçenek (U1) | Yol toplamı (mm) | En uzun yol (mm) | Kutu toplamı (mm²) | DRC hatası (unconnected hariç) |
|---|---:|---:|---:|---:|
| A — tek sütun, güney (önceki) | 50.8 | 23.32 | 111.2 | 0 |
| B — 2 × 2, güney | 25.037 | 9.495 | 83.4 | 3 |
| C — 2 güney + 2 doğu, IC yanında (**seçilen**) | 29.626 | 12.724 | 77.17 | 0 |
| D — 2 güney + 2 doğu, IC altı hizasında | 29.249 | 11.613 | 99.36 | 0 |

- **A → C:** yol toplamı %42 azaldı (50,8 → 29,63 mm), en uzun yol 23,32 → 12,72 mm, kutu toplamı 111,2 → 77,17 mm².
- **B reddedildi:** DRC hatası yalnız CVCC2'nin CIN7 ile çakışmasından geliyor ve giderilebilir; asıl engel kutup sırası. U1 güney kenarında PGND 47,0–48,5 mm, VIN 50,0–51,0 mm. B'nin ilk sırasında batı kondansatörün VIN padi 48,02 mm (PGND altı), doğu kondansatörün GND padi 49,98 mm (VIN altı): akım yolları çaprazlanır. Yol ölçütü (kenar aralığı) bunu görmez, B'nin düşük sayıları bu yüzden yanıltıcıdır.
- **C ve D:** ikisi de kutup sırasını korur ve DRC temizdir. C seçildi çünkü kart ölçütü alan: kutu toplamı C'de 77,17, D'de 99,36 mm². D'nin yol toplamı ve en uzun yolu biraz daha kısa (29,25 ve 11,61 mm).
- **Denenmeyen yönler:** U1 batısında SW pinleri 20–22 ve L1, kuzeyinde kontrol pinleri 9–16 var; bu kenarlarda VIN/PGND padi yok. Kartın alt yüzü D-006 §2 gereği kapalı.

## Sınırlar

- **CIN (C seçildi):** doğu kondansatörlerin GND padi PGND pinlerine yüzeyden doğrudan bağlanamaz (yol CIN1 VIN padinin altından geçer), L2'ye via gerektirir. Asıl döngü alanı yönlendirilmeden ölçülemez; T-022'de ölçülmeli. Bu tabloda B dışında hiçbir seçenek kutup sırasını bozmuyor.
- **Etiket mesafesi:** bazı refdes etiketleri parçadan uzak: [(9.12, 'TP_OVP_REF'), (6.85, 'J2'), (5.0, 'TP_GND_POWER'), (5.0, 'H4')]. DRC temiz ve okunuyor, ama bu etiketlerin parça ile eşleşmesi zayıf; özellikle TP sıralarında.
- **Kelvin ve bakır:** RS/INA296 koridorları yalnız yer olarak ayrıldı; Kelvin iz ayrımı, sıcak döngü alanı ve 645 mm² bakır iz/döküm olmadan doğrulanamaz (T-021…T-023).
- **Dwgs.User bölge işaretleri** T-013'ten kaldı ve bazı grup sınırlarıyla artık örtüşmüyor (üretim katmanı değil).
- Üretim için silkscreen ve test noktası ayrıntıları üretici DFM'i ile yeniden gözden geçirilmeli.
