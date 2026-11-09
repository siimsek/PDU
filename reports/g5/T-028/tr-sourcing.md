# Türkiye tedarik taraması (2026-11-09)

**Sonuç: Bu taramada grup 1 parçalarından hiçbiri için Türkiye'de stokta olduğu doğrulanamadı.** Fiyat ve stok anlık değerlerdir, sipariş öncesi satıcıdan teyit edilmelidir. Yalnız aşağıda adı geçen parçalar sorgulandı, kalan BOM **AÇIK**.

## Kanal

| Kanal | Bulgu | Kaynak |
|---|---|---|
| Fidersan (aracı) | Farnell'den haftalık yükleme, cuma siparişi ortalama 5–8 iş günü, e-posta ile MPN+adet, ilk sipariş peşin | [fidersan.com/farnell](https://www.fidersan.com/farnell) |
| Ozdisan | TI kodlarını listeliyor | [ozdisan.com](https://www.ozdisan.com/en/p/or-controllers-and-ideal-diodes-280/texas-lm74700qdbvrq1-1588786) |
| e-komponent | LM74700EVM 12 adet, yurt dışından 7–10 iş günü (IC değil, arama özeti) | [e-komponent.com](https://www.e-komponent.com/lm74700-q1-oring-controller-ideal-diode-power-management-evaluation-board) |
| DigiKey/Mouser doğrudan | Forum kaynaklı gümrük ve maliyet riski; resmi 2026 eşiği **doğrulanamadı** | [mekatronik.org](https://mekatronik.org/forum/threads/yurt-disindan-tedarik-hakkinda.9654/) |

TI'nin Türkiye yetkili distribütörü **doğrulanamadı**.

## Parça

| MPN | Türkiye | Global | Durum |
|---|---|---|---|
| LM70880QRRXRQ1 (U1, U2) | Bulunamadı | DigiKey ABD sayfası: stok 0, 28.12.2026 için 2990 beklenen, standart termin 26 hafta, Active ([sayfa](https://www.digikey.com/en/products/detail/texas-instruments/LM70880QRRXRQ1/24420927)) | **Tedarik riski, AÇIK** |
| LM74700QDBVRQ1 (U5) | Ozdisan: On Order, stok 0, 1–2 hafta (arama özeti) | LCSC 3349 adet (arama özeti, [sayfa](https://www.lcsc.com/product-detail/C2941042.html)); Arrow stok yok (arama özeti) | AÇIK |
| TPS259824LNRGER, INA296A2QDGKRQ1, TLV3601DCKR, REF5025AQDRQ1, TPS7A1650QDGNRQ1, SN74LVC1G74DCUR | Bulunamadı | Sonuç yok | **AÇIK** |
| SN74LVC1G11DBVR, LM74502HDDFR, CSD19531Q5A, BSC160N10NS3G | Sorgulanmadı | Sorgulanmadı | **AÇIK** |

LM70880 termini grup 1'in en büyük tedarik riskidir; alternatif parça kararı THINKER'ındır, bu raporda önerilmedi.
