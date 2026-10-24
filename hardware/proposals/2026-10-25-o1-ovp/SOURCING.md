# WP1 rev2 – Tedarik kontrolü (2026-10-25, saatler Europe/Istanbul / TSİ)

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

**TR özeti:** Yalnız CSD18540Q5B TR'de görünür. TI IC'leri (U10–U13) ve 0,1 % ERA-xARB dirençleri için TR stok doğrulanamadı. **rev3 P0-01:** bölücü 1206 ERA-8ARB102V + ERA-8ARB1051V + ERA-8ARB1151V'ye geçti; bu MPN'ler için stok/fiyat **doğrulanamadı** (DigiKey arama sayfası JS ile yükleniyor, kutudan curl ile içerik alınamadı, 2026-10-25 ~02:50 TSİ).

## B. Yurt dışı
| MPN | DigiKey stok | Fiyat USD (1 / 10 / 100) | Tedarik süresi | Saat (TSİ) |
|---|---|---|---|---|
| TPS48000QDGXRQ1 | 4.783 | 4,79 / 3,643 / 3,0389 | 20 hf | 01:19 |
| TLV3601DCKR | 2.911 | 4,96 / 3,766 / 3,1397 | 20 hf | 01:20 |
| REF35409QDBVR | 829 | 2,23 / 1,649 / 1,3443 | 12 hf | 01:20 |
| TPS7A1650DGNR | 2.345 | 4,55 / 3,442 / 2,862 | 12 hf | 01:20 |
| CSD18540Q5B | listelenmiş, adet doğrulanamadı | 3,50 (liste) | – | 01:20 |
| ERA-3ARB1151V (rev2; rev3'te ERA-8ARB1151V ile değişti) | **stok yok** (sipariş üzerine) | 0,19219 @ 5000 MOQ | **55 hf** | 01:21 |
| ERA-3ARB2051V (rev2; rev3'te 2 × 1206 ile değişti) | **DigiKey'de yok** (yalnız yetkisiz broker listeleri) | – | – | 01:21 |

Mouser (zaman aşımı / ürün yok), Farnell TR (403), TME (403), LCSC (403), Arrow (bağlantı hatası): **doğrulanamadı** (01:17–01:22).

Not: DigiKey TLV3601 parametre metni (60 mV histerezis, 1 µA IB, 3,5 ns) veri sayfasıyla (SNOSDB1E) çelişir; bütçede veri sayfası kullanıldı.

## C. rev2 – RAW bankı genişletmesi: TDK C5750X7S2A226M280KB (+8 adet, kartta toplam 16)
**Türkiye** (2026-10-25 01:32 TSİ)
| Distribütör | Sonuç |
|---|---|
| direnc.net | bulunamadı (site araması) |
| Robotistan | bulunamadı |
| Motorobit | bulunamadı |

TR stoğu: **doğrulanamadı / görülmedi**. Empa/Özdisan gibi teklif bazlı kanallara talep gönderilmedi.

**Yurt dışı**
| Distribütör | Stok | Fiyat USD | Tedarik süresi | Saat (TSİ) |
|---|---|---|---|---|
| DigiKey (445-C5750X7S2A226M280KBTR-ND, T&R) | **0** – sayfa metni: "500 expected in stock on 28-Oct-2026" (doğrulanmamış beyan) | 2,85010 @ 500 / 2,70630 @ 1.500 (makara) | **24 hf** (standart) | 01:32 |
| Mouser | doğrulanamadı (Access Denied / captcha) | – | – | 01:33 |
| TME | doğrulanamadı (HTTP 403) | – | – | 01:33 |
| LCSC | doğrulanamadı (sonuç çözümlenemedi) | – | – | 01:33 |

DigiKey'in önerdiği muadil Cal-Chip GMC55X7S226M100NT (7.000 adet görünüyor) **nitelendirilmemiştir ve kullanılmaz**; muadil gerekirse aynı DC-bias/ESR/ayak izi doğrulaması (COUT-qualification.md yöntemi) ve `window_budget.py` yeniden koşusu gerekir.

**Tedarik riski (yeni):** RAW bankının iki katına çıkması, bu MPN'in stok/tedarik süresini kritik yola taşır. Küçük adet (8–16) için kesme şerit/teklif kanalı ayrıca doğrulanmalı.

## D. rev2 – P1-4: 12 TBD satırına seçilen pasif MPN'ler (2026-10-25, TSİ)
| Ref | MPN | TR (direnc.net, 02:01 TSİ) | Yurt dışı |
|---|---|---|---|
| RIN10 | Yageo RC0603FR-071KL | bulunamadı | DigiKey HTTP 403 (02:00) → doğrulanamadı |
| CSNS10 | Murata GRM1885C1H101JA01D | bulunamadı | doğrulanamadı |
| CREF12 | Murata GRM188R71C105KA12D (1 µF, rev2'de 0,1 µF'tan büyütüldü) | bulunamadı | doğrulanamadı |
| CIN11 | Murata GRM21BR71H105KA12L | bulunamadı | doğrulanamadı |
| COUT11 | Murata GRM31CR71E106KA12L (10 µF/25 V/X7R/1206, rev2'de 2,2 µF'tan büyütüldü) | bulunamadı | doğrulanamadı (parametreler Murata spesifikasyon PDF'i + TI TIDR596 BOM ile çapraz görüldü – arama özeti, güvenilmez veri) |
| RBLD11 | Yageo RC0603FR-07499RL | bulunamadı | doğrulanamadı |
| CBST10 | Murata GRM188R71E474KA12D | bulunamadı | doğrulanamadı |
| REN10 / REN11 / ROV11 | Yageo RC0603FR-07100KL / RC0603FR-0710KL | bulunamadı | doğrulanamadı |
| ROV10 | Yageo RC0603FR-0790K9L | bulunamadı | doğrulanamadı |
| RPU10 | Panasonic ERJ-PA3F10R0V (anti-surge, AEC-Q200) | bulunamadı | Newark 10.000 adet / 0,019 USD @5000 – **yalnız DigiPart arama özeti, doğrulanmamış** (02:00) |

Not: Bu satırlar jenerik 0603/0805/1206 pasiflerdir; TR stoğu direnc.net'te görülmedi, diğer TR kanalları bu turda yeniden sorgulanmadı. Hiçbir stok/fiyat uydurulmamıştır. Murata ürün sayfaları yalnız JavaScript ile yüklendiği için parametreler bu turda Murata sayfasından okunamadı (MPN kodlama kuralı + üçüncü taraf özet; P1-4 PCB blokörü listesine bakınız: `docs/proposals/2026-10-25-o1-ovp/CHATGPT_REVIEW_RESPONSE.md`).

## Riskler
- **ERA-8ARB (rev3) 0,1 % / 10 ppm 1206 bölücü dirençleri** tedarik riski: stok doğrulanamadı (rev2 ERA-3ARB: 55 hf / bulunamadı). Muadil ararken 1206 (≥ 0,25 W @85 °C) ve ≥ 107 mW @125 °C şartı korunmalı (`rsns_power.py`). Alternatif (WP2): eşdeğer 0,1 %, ≤ 25 ppm/K 1206 ince film seriler (ör. Susumu RG3216, Vishay TNPW1206 0,1 %) – **MPN/stok doğrulanmadı**; ppm/K artarsa `window_budget.py` yeniden çalıştırılmalı.
- TI IC'leri için TR kanalında stok görülmedi → yurt dışı sipariş (gümrük/kargo süresi plana eklenmeli).
- **C5750X7S2A226M280KB** (rev2, +8 adet): DigiKey stok 0 / 24 hf; TR'de görülmedi → en yüksek yeni tedarik riski.
