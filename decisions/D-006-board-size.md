# D-006 — Kart dış ölçüsü ve yüz kullanımı

- **Kart:** tasks/D-006.md
- **Yazan:** Codex, 2026-11-07
- **Fiziksel iş gerekli mi:** Hayır — T-013 için THINKER kararı

## Soru
T-013'ün dört katmanlı PCB kurulumu için hangi kart dış ölçüsü ve hangi montaj yüzü seçilmeli? Karar, courtyard doluluk alt sınırını, Q1/Q2 ve LM70880 termal gereksinimlerini, geniş akım yollarını, karşı kenardaki konnektörleri ve üretim/montaj etkisini korumalıdır.

## Seçenekler
| Seçenek | Temel değerler (etiketli) | Kriteri sağlıyor mu | Risk | Kanıt (belge + sayfa) |
|---|---|---|---|---|
| 101.6×76.2 mm, tek yüz | Alan 7741.9 mm²; courtyard 3434.2 mm² → doluluk alt sınırı %44.4 | Termal bakır ve 5.5/5.3 mm güç yolları korunursa yerleşim sıkışık | COUT bankası, Q1/Q2 ≥645 mm² bakır ve konektör/kenar boşluğu için düşük marj | FLOORPLAN.md §“Kart ölçüsü seçenekleri”; floorplan.json |
| 101.6×76.2 mm, iki yüz | Parça alanının iki yüze eşit bölündüğü ideal durumda %22.2/yüz; toplam kart alanı aynı | Courtyard alanı aritmetiği sağlasa da termal/iz gereksinimi kanıtlanmış değil | Alt yüzde parça yerleşimi termal via/bakır sürekliliğini ve montaj kolaylığını zorlaştırır; gerçek dağılım bilinmiyor | FLOORPLAN.md sınırlar; PCB-HANDOFF §§3–4 |
| **120×85 mm, tek yüz (öneri)** | Alan 10200 mm²; doluluk alt sınırı %33.7 (iki yüze ideal bölünürse %16.8/yüz) | **Evet:** T-003 hesabı ve HANDOFF yerleşim grupları bu ölçüyü öneriyor; tüm bileşenler L1'de tutulabilir | Montaj deliği ve son yerleşim çakışmaları T-013'te DRC/gerçek yerleşimle kontrol edilecek | FLOORPLAN.md; floorplan.json; PCB-HANDOFF §§1,3–7 |
| 130×90 mm, tek yüz | Alan 11700 mm²; doluluk alt sınırı %29.4 (iki yüze ideal bölünürse %14.7/yüz) | Evet; daha fazla alan/termal yayılım marjı | 120×85'e göre %14.7 daha fazla çıplak kart alanı; birim fiyat teklifi yok | FLOORPLAN.md; floorplan.json |
| 130×90 mm, iki yüz | Parça alanı eşit dağıtılırsa %14.7/yüz | Alan açısından evet; alt yüzde bileşen şart değil | İlave montaj/reflow adımı; 120×85 tek yüzün sağladığı alan yeterliyken gereksiz | FLOORPLAN.md; PCB-HANDOFF §§1,3–4 |

## Öneri
**120×85 mm dış ölçü, tek yüz bileşen montajı (bileşenler L1/üst yüzde; alt yüzde komponent yok).** Dört katmanlı 1.6 mm kart ve güç katmanı planı korunurken courtyard doluluk alt sınırını %33.7'ye indirir. 63×25 mm civarındaki COUT bankası şeridi ve karşı kenar J1 / J2-J3 düzeni için FLOORPLAN'ın önerisidir. Termal bakır veya HANDOFF güç izi genişlikleri küçültülerek alan kazanılmayacak.

## Kanıt
- `reports/g5/FLOORPLAN.md`: 142 parça, 3434.2 mm² toplam courtyard; iz/via/döküm, termal bakır, test noktası, montaj deliği ve kenar payı dahil değil. Bu nedenle tüm doluluk değerleri **alt sınırdır**. COUT bankası 1567.75 mm²; 120×85 için iki faz arasında yaklaşık 63×25 mm şerit; J1+J2+J3 karşı kenar yerleşimi yaklaşık 35 mm kenar boyu.
- `reports/g5/floorplan.json`: alan/doluluk HESAP: 101.6×76.2 için %44.36 tek yüz / %22.18 iki yüz; 120×85 için %33.67 / %16.83; 130×90 için %29.35 / %14.68.
- `reports/g2/PCB-HANDOFF.md` §§1–4,6–7: dört katman, 1.6 mm, tüm katmanlarda istenen 1 oz bakır; L1 bileşen+güç, L2 GND, L3 güç dökümleri, L4 sinyal/ikincil GND. Netclass seçilen genişlikler INPUT 3.3 mm, BUS 5.5 mm, PHASE 2.6 mm, O1 5.3 mm, S2E 3.3 mm. Q1/Q2 için her biri en az 645 mm² bakır; LM70880 için EVM benzeri via dizisi.
- 120×85 alanında 2×645=1290 mm² Q1/Q2 bakır alanı, kart alanının %12.65'ine denktir. Aynı oran 101.6×76.2'de %16.66; 130×90'da %11.03 olur. Bu oranlar yerleşim alanı hesabı değildir; termal gereksinimin küçük kartta kapladığı göreli alanı gösterir. LM70880 termal bakır/via sayısı için handoff'ta ölçülü alan verilmediğinden değer türetilmemiştir.
- Kesin kart birim maliyeti üretici, panel, adet, bitmiş bakır, yüzey kaplama ve sipariş bilgileri olmadan hesaplanamaz; 130×90'ın 120×85'e göre alan farkı 15.0% değil, **14.71%**'dir (1500/10200). Tek yüz montaj seçimi mühendislik önerisidir; maliyet garantisi değildir.

## Açık varsayımlar
- **VARSAYIM:** Muhafaza / sabitleme ortamı tanımlı değil. Başlangıç delik planı 4× M3 clearance NPTH, Ø3.2 mm; sol-alt orijin, koordinatlar (6,6), (114,6), (6,79), (114,79) mm. T-013 bakır ve courtyard keepout'ları ile mekanik çakışmayı kontrol etsin. Montaj donanımı değişirse delik sayısı/ölçüsü mekanik çizimle güncellensin.
- **VARSAYIM:** Üretici 4 katmanda 1 oz tüm katmanları henüz onaylamadı (PCB-HANDOFF §1); T-013 güç dökümlerini bu stackup'a göre kursun ve üretici DFM'siyle teyit etsin.
- **VARSAYIM:** Tüm komponentler üst yüzde; alt yüzde L2 GND ve L3 güç bakırı sürekliliği, L4 sinyal/yardımcı GND tutulacak. THT konnektör gövdeleri üst yüzde, lehim bağlantısı alttan yapılabilir.

## Doğrulanamayanlar
- LM70880 başına gereken termal bakırın kesin alanı ve via adedi — reports/g2/PCB-HANDOFF.md yalnız EVM benzeri via dizisi ister, ölçü/adet tanımlamaz: https://github.com/siimsek/PDU/blob/main/reports/g2/PCB-HANDOFF.md
- Kart birim fiyatı — üretici/lot/stackup teklifi yok; karşılaştırma yalnız kart alanı oranıdır: https://github.com/siimsek/PDU/blob/main/reports/g2/PCB-HANDOFF.md
