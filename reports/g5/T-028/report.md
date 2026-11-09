# T-028 Grup 1 — üretici pin ve footprint denetimi

**Durum: Review. Tasarım dosyası değiştirilmedi.** Kapsam 17 referans (U1–U15, Q1, Q2) ve 198 pin. Girdi: `reports/g5/T-027/ledger-*.csv`, `design/bom-v2.csv`. Pin eşleşmesi ve şema–PCB pad durumu T-027 defterinden gelir; ayrı PCB DRC'si bu kartta koşulmadı.

| Sonuç | Sayı |
|---|---:|
| Pin PASS (datasheet adı ve şema pin numarası uyumlu, T-027 PCB pad EŞLEŞTİ) | 198 / 198 |
| Pin FAIL | 0 |
| Referans PASS | 1 (Q2) |
| Referans AÇIK | 16 |

Referansların AÇIK kalma nedeni pin değil, land pattern kabulüdür. [group1-refs.csv](group1-refs.csv) her referansın belgesini, revizyonunu, URL'sini ve land karşılaştırmasını; [group1-pins.csv](group1-pins.csv) her pinin satırını içerir. [gen_group1.py](gen_group1.py) dosyaları üretir; datasheet tabloları betikte elle yazılıdır, kaynak PDF URL'si ve sayfası kayıtlıdır.

## Pin bulguları

- **U1/U2 BIAS (pin 6) `/GND`:** SNVSBX7A s.13 "Tie the BIAS pin to AGND if unused" diyor. Aynı belgenin s.3 tablosu 12 V/ayarlı çıkışta BIAS'ı VOUT'a veya 10–30 V kaynağa bağlamayı önerir. Şema s.13'e uyar; VCC VIN'den beslenir ve ek LDO kaybı `power.py`'de VARSAYIM.
- **U15:** Şema sembolünde pin 1, 3, 4, 6 adları boş. Numara ve ağ rolü SN74LVC1G11 A/B/Y/C ile uyumlu, ancak okunabilirlik eksik; kart taslağı T-035.
- **U3/U4:** ITIMER boş (s.5 en hızlı tepki), RETRY_DLY, NRETRY, LDSTRT `/GND` (s.5). Pin PASS; davranış ayrıca simüle edilmedi.
- **U11/U12 pin 4:** s.2 "Reserved. Connect to ground"; şemada `/GND`.
- **U8 pin 1, 3, 7, 8; U9 Q̄; U10 FB/NC ve NC:** kasıtlı NC, veri sayfasıyla uyumlu.
- **Q1/Q2:** pin 1–3 S, 4 G, pad 5 = pin 5–8 D. Q2 için s.1 Top View görseli okundu; PDF metin sırası yanıltıcıdır.

## Land pattern

Ölçüler TI örnek kart düzeni ile kartın footprint pad koordinatlarıdır. TI metnindeki `(2.6)` gibi span değerlerinin pad merkezi anlamı VARSAYIM.

| Grup | Sonuç |
|---|---|
| U5, U15 (DBV), U6 (DDF), U7/13/14 (DCK), U8 (D), U9 (DCU), U10 (DGN), U11/12 (DGK) | Pitch eşit. Pad boyu/span KiCad IPC-7351 ile TI örneği arasında farklı. **AÇIK**: üretici/montaj kabulü yok |
| U1/U2 (RRX), U3/U4 (RGE) | `check_footprints` PASS; bakır yaklaşımı ve pasta kabulü bom.py notunda açık. **AÇIK** |
| Q1 | Veri sayfasında önerilen land sayfası bulunamadı. **AÇIK** |
| Q2 | TI SLPS406B s.10 F-bantları `check_footprints` PASS. **PASS** |

U10 için belgede DGN0008B ve DGN0008C iki land var; kartın EP'si 1,57×1,89 mm, DGN0008C (1,6×1,92) ile yakın. Hangi çizimin bu MPN'ye ait olduğu **doğrulanamadı**.

## Kapsam

Şemada 180 referans. Grup 1: 17. Kalan 163, ≤20'lik 9 grup: [coverage-plan.json](coverage-plan.json). Devam grupları AÇIK.

## Tedarik

[tr-sourcing.md](tr-sourcing.md). LM70880QRRXRQ1 grup 1'in en büyük riski.

## Kaynaklar

Belge bağlantıları [group1-refs.csv](group1-refs.csv) içinde. PDF'ler 2026-11-09'da ti.com'dan okundu; Q1 repo kopyasıdır, revizyon tarihi metin kodlaması nedeniyle **doğrulanamadı**.
