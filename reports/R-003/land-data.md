# R-003 — Üretici land verisi ve footprint karşılaştırması

Tarih: 2026-11-07  
İncelenen repo tabanı: `main` @ `269183f5cc17c29fab90de279cada65d98993d6b`  
Birim ve koordinat: mm; KiCad footprint başlangıç noktası, X yatay, Y düşey. Pad merkezleri footprint dosyasından okunmuştur; üretici çizimindeki desen için koordinatlar pad merkezine göre normalize edilmiştir.

## Q1 — Infineon BSC160N10NS3 G, PG-TDSON-8-1

Birincil kaynak: BSC160N10NS3 G datasheet Rev. 2.4, sayfa 10 (package / land-pattern çizimi; ölçüler mm). Paket tanımı sayfa 1'de PG-TDSON-8 olarak geçer. Paket veri çizimi PG-TDSON-8-1, Rev. 01.00, 2016-04-11, sayfa 2'de ayrıca footprint layout'ı yayımlar.

| Pad / özellik | Merkez (x,y) | Boyut (x×y) | Delik | Kaynak / not |
|---|---:|---:|---:|---|
| 1 (S) | (-2.900,-1.905) | 0.85×0.50 | — | Infineon datasheet Fig. 2, p.10 |
| 2 (S) | (-2.900,-0.635) | 0.85×0.50 | — | Infineon datasheet Fig. 2, p.10 |
| 3 (S) | (-2.900,+0.635) | 0.85×0.50 | — | Infineon datasheet Fig. 2, p.10 |
| 4 (G) | (-2.900,+1.905) | 0.85×0.50 | — | Infineon datasheet Fig. 2, p.10 |
| 5 (D, exposed pad; 5–8 ortak net) | (+1.050,0) | 4.55×4.41 | — | Infineon datasheet Fig. 2, p.10 |
| Pad 5 üzerindeki dört stencil açıklığı | (+2.905, y=−1.905,−0.635,+0.635,+1.905) | her biri 0.75×0.50 | — | Paste açıklıkları; ayrı bakır pad değildir, Fig. 2 stencil çizimi |

**Q1 kararı: `PDU:TDSON-8-1_Konnect` özel footprint'i kullanılsın.** BSC160N10NS3 G'nin kendi Rev. 2.4 çizimindeki 1–4 land'leri, ortak drain land'i ve segmentli stencil deseni bu footprint ile eşleşiyor. Karşılaştırılan `Package_SON:Infineon_PG-TDSON-8_6.15x5.15mm` footprint'inde pad 1–4 1.20×0.65 mm ve x=−2.825 mm; pad 5 4.50×4.70 mm, x=+0.675 mm; ayrıca pad 5 ağına bağlı dört ayrı 1.00×0.70 mm drain land'i bulunuyor. Bunlar BSC160 parça çizimindeki küçük 1–4 land'leri ve merkezî pad/stencil düzeniyle aynı geometri değil. Özel footprint seçimi parça-özel üretici çizimine dayanır; Q1 bulgusu açılmadı.

## C5750 — TDK C5750X7S2A226M280KB, 2220

Birincil kaynak: TDK Product Center, tam parça numarası sayfası; “Recommended Land Pattern” PA/PB/PC aralıkları.

| Pad / parametre | Merkez (x,y) | Boyut / boşluk | TDK önerisi | Fark ve sonuç |
|---|---:|---:|---:|---|
| 1 | (−2.875,0) | 1.30×4.50 | PB=1.20–1.40; PC=4.00–5.00 | PB +0.00 mm üst sınırın içinde; PC=4.50 aralık içinde |
| 2 | (+2.875,0) | 1.30×4.50 | PB=1.20–1.40; PC=4.00–5.00 | Pad 1 ile simetrik |
| Bakır padler arası açıklık PA | — | (5.75−1.30)=4.45 | PA=4.10–4.80 | +0.35 mm üst sınıra pay; aralık içinde |
| Delik | — | — | SMD | Uygulanmaz |

Footprint değerleri `hardware/lib/PDU.pretty/TDK_C5750_2220_Recommended.kicad_mod` dosyasından. Sonuç: **mevcut C5750 footprint'i kabul**; TDK'nın üç önerilen ölçüsünün de içindedir.

## J2 — Molex Mini-Fit Plus HCS 46015-0206

Birincil kaynaklar: Molex SD-46015-001 Rev. C, sayfa 1 (4-devre çizimi ve PCB layout; çizelgede 46015-0206 da listeleniyor) ve resmi 46015-0206 ürün sayfası. Repo footprint'i KiCad resmi `Connector_Molex:Molex_Mini-Fit_Jr_5566-02A_2x01_P4.20mm_Vertical` dosyasıdır.

| Parametre | Üretici çizimi / ürün verisi | Repo pad geometrisi | Fark / değerlendirme |
|---|---:|---:|---|
| İki terminalin sıra-merkezi arası | 5.50 ±0.10 mm (SD-46015-001 p.1, önerilen PCB layout; 2-devre gövdede her sırada bir pin) | Pad1 (0,0), Pad2 (0,5.50) mm | Nominal fark 0.00 mm; kabul |
| Sıra içi art arda kontakt aralığı | 4.20 ±0.10 mm non-accumulative; iki devreli parçada pinler farklı sıralarda olduğundan bu J2.1–J2.2 sıra aralığı değildir | Uygulanmıyor; 2×01 footprint'te aynı sırada ikinci terminal yok | Önceki Tur 1 karşılaştırması 4.20'yi iki pin arası çapraz sıra ölçüsü kabul ederek hata yaptı |
| Terminal PCB deliği | Ø1.40 ±0.05 mm (SD-46015-001 p.1; terminal hole) | Her iki pad Ø1.40 mm drill | Nominal fark 0.00 mm; kabul |
| Opsiyonel peg deliği | Ø3.00 ±0.05 mm, yalnız opsiyonel peg için; 46015-0206 ürün çizelgesinde PEGS=NO | Footprint'te peg deliği yok | Eşleşiyor; Ø3.00 terminal deliği değildir |
| Bakır pad ölçüsü | Molex çizimi önerilen delik layout'u verir; bu çizimde pad bakır eni/boyu belirtilmemiş | 2.70×3.30 mm; pad1 roundrect, pad2 oval | Üretici hedef ölçüsü yayımlanmadığı için bakır pad farkı hesaplanamaz; repo pad geometrisi ölçülüdür ve uydurma üretici değeri atanmamıştır |

**Karar: stok 5566-02A footprint geometrisi J2 için kabul.** 5.50 mm iki sıra aralığı, Ø1.40 mm terminal deliği ve peg bulunmaması resmi 46015 ailesi çizimi / 0206 parça bilgisiyle uyumlu. KiCad footprint açıklamasındaki 5566-02A eski Mini-Fit Jr parça adıdır; gerçek J2 MPN'si BOM'da 46015-0206 kalmalıdır. Molex bakır pad ölçüsü yayımlamadığından 2.70×3.30 mm pad ölçüsünü üretici land ölçüsü gibi göstermeyin; değişiklik gerektiren kanıt yoktur.

Repo footprint'inden hesap: kısa eksen annular ring = (2.70−1.40)/2 = 0.65 mm; uzun eksen = (3.30−1.40)/2 = 0.95 mm. Bunlar geometri hesabıdır, Molex tavsiyesi değildir.

### Kaynaklar

- Molex SD-46015-001 Rev. C, p.1 (resmi satış çizimi; family land pattern, 46015-0206 ürün çizelgesi): https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/salesdrawingpdf/460/46015/460150402_sd.pdf
- Molex 46015-0206 resmi ürün sayfası (2 circuits, 2 rows, vertical, no peg retention; 4.20 mm series pitch): https://www.molex.com/en-us/products/part-detail/460150206
- KiCad footprint kaynak dosyası (pad merkezleri, şekil, ölçü ve drill): https://github.com/KiCad/kicad-footprints/blob/master/Connector_Molex.pretty/Molex_Mini-Fit_Jr_5566-02A_2x01_P4.20mm_Vertical.kicad_mod
## Kaynaklar

- Infineon, BSC160N10NS3 G datasheet, Rev. 2.4, pp. 1, 10: https://www.infineon.com/dgdl/Infineon-BSC160N10NS3-DS-v02_04-en.pdf?fileId=db3a30432239cccd01226040189a7f47
- Infineon, PG-TDSON-8-1 package drawing, Rev. 01.00, 2016-04-11, p. 2: https://www.infineon.com/dgdl/Infineon-PG-TDSON-8-1_BSC030N03LSGATMA1-PD-v01_00-EN.pdf?fileId=5546d46254e133b40154f1dca50d5906
- TDK Product Center, C5750X7S2A226M280KB: https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=C5750X7S2A226M280KB
- Molex product detail, 46015-0206: https://www.molex.com/en-us/products/part-detail/460150206
- Molex sales drawing SD-46015-001 Rev. C (46015-0403 exemplar, product table includes 46015-0206): https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/salesdrawingpdf/460/46015/460150403_sd.pdf?inline=
- Molex requested 46015-0206 drawing (URL could not be retrieved): https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/salesdrawingpdf/460/46015/460150206_sd.pdf
- KiCad official footprint source, Mini-Fit Jr 5566-02A: https://github.com/KiCad/kicad-footprints/blob/master/Connector_Molex.pretty/Molex_Mini-Fit_Jr_5566-02A_2x01_P4.20mm_Vertical.kicad_mod
- Repo custom Q1/C5750 footprint files: https://github.com/siimsek/PDU/tree/main/hardware/lib/PDU.pretty
