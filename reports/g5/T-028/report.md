# T-028 Grup 1 — üretici pin ve footprint denetimi

**Durum: Review. Tasarım dosyası değiştirilmedi.** Kapsam 17 referans (U1–U15, Q1, Q2) ve 198 pin. Girdi: `reports/g5/T-027/ledger-*.csv`, `design/bom-v2.csv`. Pin eşleşmesi ve şema–PCB pad durumu T-027 defterinden gelir; ayrı PCB DRC'si bu kartta koşulmadı.

| Sonuç | Sayı |
|---|---:|
| Pin PASS (datasheet adı ve şema pin numarası uyumlu, T-027 PCB pad EŞLEŞTİ) | 194 / 198 |
| Pin AÇIK (U15 şema sembol adı boş: 1, 3, 4, 6) | 4 |
| Pin FAIL | 0 |
| Referans PASS | 1 (Q2) |
| Referans AÇIK | 16 |

Referansların AÇIK kalma nedeni pin değil, land pattern kabulüdür. [group1-refs.csv](group1-refs.csv) her referansın belgesini, revizyonunu, URL'sini ve land karşılaştırmasını; [group1-pins.csv](group1-pins.csv) her pinin satırını içerir. [gen_group1.py](gen_group1.py) dosyaları üretir; datasheet tabloları betikte elle yazılıdır, kaynak PDF URL'si ve sayfası kayıtlıdır.

## Pin bulguları

- **U1/U2 BIAS (pin 6) `/GND`:** SNVSBX7A s.13 "Tie the BIAS pin to AGND if unused" diyor. Aynı belgenin s.3 tablosu 12 V/ayarlı çıkışta BIAS'ı VOUT'a veya 10–30 V kaynağa bağlamayı önerir. Şema s.13'e uyar; VCC VIN'den beslenir ve ek LDO kaybı `power.py`'de VARSAYIM.
- **U15:** Şema sembolünde pin 1, 3, 4, 6 adları boş; R-023 sonrası bu dört pin AÇIK. Numara ve ağ rolü SN74LVC1G11 A/B/Y/C ile uyumlu görünüyor. T-035 ile kapatılacak.
- **U3/U4:** ITIMER boş (s.5 en hızlı tepki), RETRY_DLY, NRETRY, LDSTRT `/GND` (s.5). Pin PASS; davranış ayrıca simüle edilmedi.
- **U11/U12 pin 4:** s.2 "Reserved. Connect to ground"; şemada `/GND`.
- **U8 pin 1, 3, 7, 8; U9 Q̄; U10 FB/NC ve NC:** kasıtlı NC, veri sayfasıyla uyumlu.
- **Q1:** Resmi Infineon BSC160N10NS3 G Rev. 2.4 (2009-10-30, s.8 dipnotu) s.1 sembol görseli S 1–3, G 4, D 5–8; şema pin 1–3 S, 4 G, 5 D, kart pad 5 = pin 5–8. Pin eşleşmesi görselden okundu.
- **Q2:** s.1 Top View görseli aynı düzeni gösteriyor; PDF metin sırası yanıltıcıdır.

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

Şemada 180 referans. Grup 1: 17. Kalan 163, ≤20'lik 9 grup: [coverage-plan.json](coverage-plan.json). G2 aşağıda; G3–G10 (143 referans) AÇIK.

## Grup 2 — 20 kondansatör (R-026)

Kapsam: CBIN1–2, CBOOT1–2, CCOMP, CDVDT1–2, CEFIN1–2, CEFOUT1–2, CHF, CIN1–8; 40 pin; 8 TDK MPN. Kaynak: TDK Product Center ürün sayfaları, 2026-11-09'da tarayıcıyla okundu; sayfada belge sürüm numarası yok. Kayıtlar: [group2-refs.csv](group2-refs.csv), [group2-pins.csv](group2-pins.csv), [group2-board-pads.json](group2-board-pads.json). Üretici: [gen_group2.py](gen_group2.py), [dump_group2_pads.py](dump_group2_pads.py). Kart bu daldaki `PDU.kicad_pcb` dosyasıdır; SHA-256 JSON içindedir.

| Sonuç | Sayı |
|---|---:|
| Pin PASS (kutupsuz terminal, T-027 PCB pad EŞLEŞTİ, ağ dolu) | 40 / 40 |
| Pin FAIL veya AÇIK | 0 |
| Referans PASS | 0 |
| Referans AÇIK (nedeni yalnız land pattern) | 20 |
| Referans FAIL | 0 |

Değer, gerilim sınıfı, dielektrik, paket ve BOM/defter eşleşmesi 20 referansta uyumlu. Sekiz MPN sayfada `Production`.

**Land (OLGU):** TDK sayfa şekli PA = pad boşluğu, PB = pad uzunluğu, PC = pad genişliği tanımlar. Reflow aralıklarıyla kart padleri:

| Paket | Footprint | Kart PA/PB/PC mm | TDK reflow PA/PB/PC mm | Fark |
|---|---|---|---|---|
| 0603 | `C_0603_1608Metric` | 0,65 / 0,90 / 0,95 | 0,6–0,8 / 0,6–0,8 / 0,6–0,8 | PB +0,10; PC +0,15 |
| 1206 | `C_1206_3216Metric` | 1,80 / 1,15 / 1,80 | 2,0–2,4 / 1,0–1,2 / 1,1–1,6 | PA −0,20; PC +0,20 |
| 1210 | `C_1210_3225Metric` | 1,80 / 1,15 / 2,70 | 2,0–2,4 / 1,0–1,2 / 1,9–2,5 | PA −0,20; PC +0,20 |

KiCad IPC-7351 footprintleri TDK reflow aralığının dışında kalıyor. Bu farkın kabulü montajcı veya üretici onayı gerektirir; **AÇIK**. Footprint bu kartta değiştirilmedi.

**Diğer bulgular:**

- **AEC-Q200:** Sekiz MPN için sayfa `NO`, `Commercial Grade`. Sayfadaki otomotiv MPN'leri yalnız `group2-refs.csv` içinde işaret olarak kayıtlıdır; form-uyum veya tedarik doğrulaması yapılmadı. Ortam gereği T-043/T-044 kapsamında AÇIK.
- **CEFOUT1–2 BOM notu eski:** Not "25 V 0805: 46 % of rating" der. BOM paketi 1206 ve MPN C3216 (1206); oran 11,94/25 = %47,76. Elektriksel değer değişmiyor. Düzeltme `design/bom.py` yetkili bir kart gerektirir.
- **Etkin kapasite:** CEFOUT için %40 ve CIN için ≥%50 kabulleri VARSAYIM kalır. Bu turda TDK DC-bias eğrisi okunmadı, **AÇIK**.
- **BOM tolerans sütunu boş:** Toleranslar sayfalardan alındı (K ±%10, J ±%5) ve CSV'ye yazıldı.
- **C3225X7S2A475K200AB:** Sayfa yalnız reflow lehim belirtir; dalga lehim uygulanmaz.

## Tedarik

[tr-sourcing.md](tr-sourcing.md). LM70880QRRXRQ1 grup 1'in en büyük riski.

## Kaynaklar

Belge bağlantıları [group1-refs.csv](group1-refs.csv) içinde. PDF'ler 2026-11-09'da ti.com ve infineon.com'dan okundu.
