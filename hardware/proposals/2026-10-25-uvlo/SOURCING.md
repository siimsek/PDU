# WP2 UVLO — Tedarik durumu (2026-10-25)

Kontrol zamanı: 2026-10-25 yaklaşık 09:40–09:55 (Europe/Istanbul, UTC+3). Ham veri: `sourcing.csv`.
Bu tablo bir anlık görüntüdür. Stok ve fiyatlar değişebilir. Doğrulanamayan her değer "doğrulanamadı" ya da "kontrol edilmedi" olarak yazılmıştır. Hiçbir değer tahminle doldurulmadı.

## Özet

| Parça | Kart başı adet | Türkiye fiziksel stok | İthalatçı / uluslararası | Risk |
|---|---|---|---|---|
| TLV3202AIDGKR (U20) | 1 | **YOK**: Özdisan sayfası "Stok: 0" (talep üzerine, 1–2 hafta beyanı); direnc.net bulunamadı | TME 508 adet, 1.68 USD; LCSC 2267 adet, 1.92 USD; TI.com stok yok | Orta |
| TLV3202AQDGKRQ1 (farklı MPN, Q1) | — | Taşkın Teknik "Stokta var", ₺66.13 (adet gösterilmiyor) | — | İkame **doğrulanmadı** |
| TMUX1102DBVR (U21) | 1 | **YOK**: direnc.net ve Özdisan'da sonuç yok | TME 843 adet, 1.68 USD (500 adette 1.13 USD) | Orta |
| ERA-3ARB 0.1 % 10 ppm (RTU, RBU, RXU, RR1U, RR2U, RTT, RK1, RK2) | 8 | **YOK**: direnc.net ve Özdisan'da sonuç yok | TME 9092V ve 4022V: stok 0, MOQ 5000; diğer değerlerin sayfası 404; DigiKey sonuç yok; Mouser zaman aşımı | **YÜKSEK** (stok doğrulanamadı) |
| 1N4148WS (DTT) | 1 | direnc.net 405 adet (üretici doğrulanamadı) | — | Düşük |
| GRM31CR71E106KA12L (CTT) | 1 | kontrol edilmedi | kontrol edilmedi (üretici sayfası ürünü doğruluyor) | Düşük–orta |
| RC0603FR-071ML (RHB) | 1 | kontrol edilmedi | kontrol edilmedi | Düşük (her 1 % / ≤100 ppm/K 1 M muadil uyar) |
| 100 nF / 10 nF X7R 0603, 100 Ω ve 10 k 1 % | 6 | kontrol edilmedi (jenerik) | — | Düşük |

## Notlar

1. **ERA-3ARB riski.** Bütçe 0.1 % / ±10 ppm/K dirençlere dayanır (C3 marjları +0.019 V ile +0.157 V arası). Daha gevşek dirençlerle (ör. 0.5 % / 25 ppm) bütçe **yeniden hesaplanmadan** ikame YAPILMAMALIDIR. Uygun muadil sınıfı Susumu RG1608 veya Vishay TNPW e3 0.1 % / 10 ppm olabilir. Bu muadiller bu çalışmada **doğrulanmadı**, stokları da **kontrol edilmedi**.
2. **TLV3202AQDGKRQ1.** AEC-Q100 sürümü. Elektriksel tabloları ve pin dizilimi bu çalışmada karşılaştırılmadı, bu yüzden ikame kararı kullanıcıya aittir.
3. **TME.** TME, Türkiye'ye gönderim yapan bir AB distribütörüdür. Listelenen stok onların deposundadır, Türkiye'de fiziksel stok değildir. TME sayfaları curl ile 403 döndürdü, WebFetch ile okundu.
4. **DigiKey ve Mouser.** Otomatik erişim kısıtlı. "Sonuç yok" ya da zaman aşımı, ürünün olmadığını göstermez.
5. Kart başı toplam yeni parça: 1 × TLV3202, 1 × TMUX1102, 8 × ERA-3ARB (7 farklı değer; 10.0 k iki adet: RR1U, RK1), 1 × 1N4148WS, 1 × 10 µF, 1 × 1 M, 5 × küçük kondansatör (CFU, CRU, CK, C20, C21), 2 × jenerik direnç (RDIS, RDEN). RUV1 sökülür (DNP).
