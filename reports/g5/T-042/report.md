# T-042 — Türkiye tedarik ve alternatif planı (2026-11-09)

**Durum: Review. Sipariş, dış iletişim, BOM/şema/PCB değişikliği yok.** Bu defterde 20 kritik referans var: [sourcing-20.csv](sourcing-20.csv). Kalan BOM referansları sayılı devam gruplarına ayrıldı: [coverage.json](coverage.json). Global stok Türkiye stoğu veya garanti teslim değildir.

## Özet

- 20 referansın hiçbiri için Türkiye'de stok doğrulanamadı.
- 12 MPN için satıcı sayfası bu turda okunmadı; bunlar **AÇIK**.
- Ozdisan'da LM74700QDBVRQ1: stok 0, "On Order: No", üretici standart termini 1–2 hafta yazıyor, fiyat talep üzerine, MOQ 1. Termin bir teslim sözü değildir. T-028 `tr-sourcing.md` içindeki "On Order" ifadesi bu okuma ile düzeltilmelidir.
- Ozdisan arama URL'si 404 verdi; ürün sayfası olmayan MPN'ler için stok sorgulanamadı.

## Kanal

- TI distribütör sayfası [Arrow, DigiKey, Mouser](https://www.ti.com/distributors) gibi global kanalları yetkili sayar. Türkiye adı sayfada açık geçmiyor (arama özeti); **Türkiye yetkili distribütörü doğrulanamadı**.
- [Fidersan](https://www.fidersan.com/farnell) Farnell'den haftalık yükleme yapıyor, 5–8 iş günü ortalama, ilk sipariş peşin. Bu MPN'ler için teklif alınmadı.
- Doğrudan DigiKey/Mouser gümrük koşulu resmi kaynaktan **doğrulanamadı**.

## LM70880QRRXRQ1

DigiKey (ABD sayfası) 2026-11-09: stok 0, 28.12.2026'da 2990 adet beklenen, üretici standart termini 26 hafta, durum Active. Türkiye kanalı bulunamadı. Bu, tüm dağıtıcılar için yokluk kanıtı değildir.

Alternatif değerlendirmesi. Bire bir uyum kanıtlanmadan öneri değildir:

| Aday | Kaynak | Pin / paket | Gerilim | Akım | Durum |
|---|---|---|---|---|---|
| LM70860-Q1 | [TI SNVSBX7A](https://www.ti.com/lit/ds/symlink/lm70880-q1.pdf) ortak belge | Aynı belge ve RRX paketi | Aynı belge 80 V | 6 A | **AÇIK**: faz başına tepe akım, OC eşiği, Rds, ısı, N-1 hesabı yapılmadı |
| LM70840-Q1 | Aynı belge | Aynı | Aynı | 4 A | **AÇIK**: bara hedefi 7,5 A ile faz paylaşımı ve OC eşiği karşılaştırılmadı |
| LM70880-Q1 RRX başka ambalaj kodu | TI ürün sayfası | Aynı parça ailesi | Aynı | 8 A | **AÇIK**: orderable kodu ve stok okunmadı |

Farklı üreticiden pin uyumlu parça bulunamadı; yeni bir parça şema/PCB değişikliği ve ayrı karar gerektirir.

## S2 — 20 TDK kondansatör (R-026)

Kayıt: [sourcing-s2.csv](sourcing-s2.csv), [gen_s2.py](gen_s2.py). 8 MPN, 2026-11-09. Sipariş veya teklif isteği yok.

- 20 referansın hiçbiri için Türkiye stoğu doğrulanamadı; stok ve MOQ **AÇIK**.
- 8 MPN TDK sayfasında `Production`, AEC-Q200 `NO`.
- Ozdisan alan aramasında tam MPN sayfası çıkmadı. Bu, yokluk kanıtı değildir.
- Ozdisan `C1608X7R1H104KT-L` sayfası: 100 nF 50 V ±%10 X7R 0603, üretici standart termini 5–6 hafta, gelecek stok yok. Stok sayısı okunmadı. BOM'daki `C1608X7R1H104K080AA` ile aynı sipariş kodu olduğu **doğrulanamadı**.
- Aynı sayfanın "Benzer Ürünler" listesi onaylı alternatif değildir, deftere alternatif olarak yazılmadı.
- mouser.com.tr arama sayfası bot koruması gösterdi; aşılmadı, veri alınmadı.

## Devam

`coverage.json` grup listesi sırasıyla taranmalı; her satıra tarihli stok, MOQ ve kaynak yazılmalı. Satıcıdan yazılı teklif dış iletişim gerektirir ve bu kartta yapılmadı.
