# T-020 — ayrıntılı yerleşim (iz/via/döküm yok)

KiCad 10.0.7, bundled `pcbnew` (D-009). Üretim: `scripts/pcb_place.py`, T-013 kartından. Koordinatlar D-006 (sol-alt orijin, y yukarı). Karşılaştırma: `placement.json` `moved_vs_t013` (140 parça) ve [placement.png](placement.png), [placement.svg](placement.svg).

## DRC

| Kontrol | Sonuç |
|---|---|
| Yerleşimli kart + parite ([drc-placed.json](drc-placed.json)) | ihlal/uyarı **0** (413 silk uyarısı temizlendi); parite **0**; `unconnected_items` 402 (iz yok, beklenen) |
| Boş kart ([drc-empty.json](drc-empty.json)) | 0 öğe |
| `pcb_rules.py --check`, darboğaz denetimi | PASS; ihlal 0 |

Değişmeyenler: 120 × 85 dış hat, H1–H4 {'H1': [6.0, 6.0], 'H2': [114.0, 6.0], 'H3': [6.0, 79.0], 'H4': [114.0, 79.0]}, J1/J2/J3/J_OVP_INJ_BUS konumları, ağlar, değerler, footprint'ler, stackup, netclass.

## Yerleşim ölçüleri (HESAP, pad/parça merkezleri; gerçek iz uzunluğu değil)

| Kısıt | Ölçü |
|---|---|
| CIN → LM70880 merkez (U1: CIN1–4, U2: CIN5–8) | [5.59, 9.13, 12.67, 16.21] / [5.59, 9.13, 12.67, 16.21] mm; sütun IC'nin VIN–PGND kenarında |
| RS → INA296 (hedef ≤15 mm bağlantı) | RS1–U11 8.79 mm, RS2–U12 9.42 mm |
| INA296 → TLV3601 | U11–U13 5.21 mm, U12–U14 5.21 mm |
| U6 GATE – Q2 G pad (≤10 mm iz için) | 5.42 mm; gerçek uzunluk T-023'te |
| Mantık parçaları → en yakın SW pad merkezi (≥10 mm) | en küçük 13.22 mm (U13) |
| L → LM70880 merkez | L1–U1 11.2 mm, L2–U2 11.05 mm |
| D1 → J1 merkez | 9.38 mm |

U1 180° (VIN/PGND kuzeyden güneye, SW batıda L1'e); U2 0° (VIN/PGND kuzeyde, SW doğuda L2'ye). Kontrol pini parçaları (CVCC, CVDDA, RT) SW bakırının dışında, IC'nin kuzey/güney şeridinde.

## Sınırlar

- **Tek sütun:** dört 1210 CIN üst üste; yalnız ilki IC kenarına bitişik (courtyard aralığı 0,25 mm), son sütun elemanı 16,21 mm merkezde. Daha küçük döngü için kondansatörleri iki tarafa bölmek gerekirdi; IC çevresindeki pin parçaları nedeniyle denenmedi. Asıl döngü alanı T-022'de ölçülmeli.
- **Etiket mesafesi:** bazı refdes etiketleri parçadan uzak: [(9.12, 'TP_OVP_REF'), (6.85, 'J2'), (5.0, 'TP_GND_POWER'), (5.0, 'H4')]. DRC temiz ve okunuyor, ama bu etiketlerin parça ile eşleşmesi zayıf; özellikle TP sıralarında.
- **Kelvin ve bakır:** RS/INA296 koridorları yalnız yer olarak ayrıldı; Kelvin iz ayrımı, sıcak döngü alanı ve 645 mm² bakır iz/döküm olmadan doğrulanamaz (T-021…T-023).
- **Dwgs.User bölge işaretleri** T-013'ten kaldı ve bazı grup sınırlarıyla artık örtüşmüyor (üretim katmanı değil).
- Üretim için silkscreen ve test noktası ayrıntıları üretici DFM'i ile yeniden gözden geçirilmeli.
