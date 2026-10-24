# WP1 – Tedarik kontrolü (2026-10-25, saatler Europe/Istanbul / TSİ)

Ham veri: `sourcing.csv`. Web sonuçları güvenilmez veridir; stok/fiyat sipariş anında yeniden doğrulanmalıdır. Uydurulmuş stok/fiyat yoktur – görülmeyen her şey "doğrulanamadı".

## A. Türkiye
| Distribütör | Sonuç | Saat (TSİ) |
|---|---|---|
| direnc.net | **CSD18540Q5B listelenmiş, "stokta"** – 76,04 TL + KDV = **91,24 TL** (0–99 adet); 86,68 (100–249); 82,12 (250–499); 77,56 (500–1000) TL KDV dahil. Stok adedi gösterilmiyor → adet doğrulanamadı. TPS48000, TLV3601, REF35409, TPS7A1650, ERA-3ARB: **bulunamadı** | 01:16–01:18 |
| Robotistan | 6 MPN için bulunamadı | 01:16–01:18 |
| Motorobit | 6 MPN için bulunamadı | 01:16–01:18 |
| Empa | Arama sayfası döndü, ürün eşleşmesi çözümlenemedi → doğrulanamadı | 01:17–01:18 |
| Komponentci | Genel sayfa döndü → doğrulanamadı | 01:16–01:18 |
| Samm Market | Arama URL'si HTTP 404 → doğrulanamadı | 01:17–01:18 |
| Özdisan | Arama URL'si HTTP 404 → doğrulanamadı (teklif talebi gerekir; gönderilmedi) | 01:17–01:18 |

**TR özeti:** Yalnız CSD18540Q5B TR'de görünür. TI IC'leri (U10–U13) ve 0,1 % ERA-3ARB dirençleri için TR stok doğrulanamadı.

## B. Yurt dışı
| MPN | DigiKey stok | Fiyat USD (1 / 10 / 100) | Tedarik süresi | Saat (TSİ) |
|---|---|---|---|---|
| TPS48000QDGXRQ1 | 4.783 | 4,79 / 3,643 / 3,0389 | 20 hf | 01:19 |
| TLV3601DCKR | 2.911 | 4,96 / 3,766 / 3,1397 | 20 hf | 01:20 |
| REF35409QDBVR | 829 | 2,23 / 1,649 / 1,3443 | 12 hf | 01:20 |
| TPS7A1650DGNR | 2.345 | 4,55 / 3,442 / 2,862 | 12 hf | 01:20 |
| CSD18540Q5B | listelenmiş, adet doğrulanamadı | 3,50 (liste) | – | 01:20 |
| ERA-3ARB1151V | **stok yok** (sipariş üzerine) | 0,19219 @ 5000 MOQ | **55 hf** | 01:21 |
| ERA-3ARB2051V | **DigiKey'de yok** (yalnız yetkisiz broker listeleri) | – | – | 01:21 |

Mouser (zaman aşımı / ürün yok), Farnell TR (403), TME (403), LCSC (403), Arrow (bağlantı hatası): **doğrulanamadı** (01:17–01:22).

Not: DigiKey TLV3601 parametre metni (60 mV histerezis, 1 µA IB, 3,5 ns) veri sayfasıyla (SNOSDB1E) çelişir; bütçede veri sayfası kullanıldı.

## Riskler
- **ERA-3ARB 0,1 % / 10 ppm bölücü dirençleri** tedarik riski (55 hf / bulunamadı). Alternatif (WP2): eşdeğer 0,1 %, ≤ 25 ppm/K 0603 ince film seriler (ör. Susumu RG1608, Vishay TNPW 0,1 %) – **MPN/stok doğrulanmadı**; ppm/K artarsa `window_budget.py` yeniden çalıştırılmalı.
- TI IC'leri için TR kanalında stok görülmedi → yurt dışı sipariş (gümrük/kargo süresi plana eklenmeli).
