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

Birincil ürün kaynağı: Molex resmi parça sayfası. Sayfa 46015-0206 için 2 devre, dikey, through-hole, mating/termination pitch 4.20 mm ve önerilen PCB kalınlığı 1.78 mm bilgilerini veriyor. Molex resmi seri çizimi SD-46015-001 Rev. C, 46015 serisi dual-row HCS başlık düzenini ve 4.20 mm pin aralığını gösteriyor; çizelgede 46015-0206 da listeleniyor.

| Pad / parametre | Üretici hedefi | Repo'daki KiCad pad'i | Fark / sonuç |
|---|---:|---:|---|
| 1–2 merkez aralığı | 4.20 mm pitch; merkez koordinatı bu değere göre normalize edilebilir | pad 1 (0,0), pad 2 (0,5.50) | +1.30 mm; kabul toleransı ±0.02 mm'nin çok dışında |
| Pad boyutu | **doğrulanamadı** | her pad 2.70×3.30 | Üretici 46015-0206 PCB layout çizimi erişilemedi; boyut kıyaslanamıyor |
| Delik çapı | **doğrulanamadı** | her pad için Ø1.40 | Üretici 46015-0206 PCB layout çizimi erişilemedi; delik kıyaslanamıyor |
| Opsiyonel peg delikleri | 3.00 mm; yalnız opsiyonel peg için | stok footprint'te yok | Sinyal terminali delik çapı olarak kullanılamaz |

Repo eşlemesi `Connector_Molex:Molex_Mini-Fit_Jr_5566-02A_2x01_P4.20mm_Vertical` olarak kayıtlı; KiCad kaynak dosyasının açıklaması bu footprint'in eski 5566-02A Mini-Fit Jr parçası olduğunu belirtir. Bu, istenen 46015-0206 Mini-Fit Plus HCS parçasının MPN'si değildir. KiCad dosyasında pin merkezleri 5.50 mm, 1.40 mm delik ve 2.70×3.30 mm pad yazılıdır. Molex ürün sayfasındaki 4.20 mm termination pitch ile 5.50 mm footprint aralığı uyuşmaz.

**J2 sonucu: stok footprint kabul edilemez; 46015-0206 için üretici çizimine dayalı yeni footprint gerekir.** 4.20 mm pitch resmi parça sayfasında doğrulanmıştır. Molex'in bu MPN'ye ait `460150206_sd.pdf` satış çizimi resmi sayfada bulunamadı; doğrudan dosya URL'si okunamadı. Bu nedenle pad eni/boyu ve terminal deliği için değer yazılmamıştır.

## Kaynaklar

- Infineon, BSC160N10NS3 G datasheet, Rev. 2.4, pp. 1, 10: https://www.infineon.com/dgdl/Infineon-BSC160N10NS3-DS-v02_04-en.pdf?fileId=db3a30432239cccd01226040189a7f47
- Infineon, PG-TDSON-8-1 package drawing, Rev. 01.00, 2016-04-11, p. 2: https://www.infineon.com/dgdl/Infineon-PG-TDSON-8-1_BSC030N03LSGATMA1-PD-v01_00-EN.pdf?fileId=5546d46254e133b40154f1dca50d5906
- TDK Product Center, C5750X7S2A226M280KB: https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=C5750X7S2A226M280KB
- Molex product detail, 46015-0206: https://www.molex.com/en-us/products/part-detail/460150206
- Molex sales drawing SD-46015-001 Rev. C (46015-0403 exemplar, product table includes 46015-0206): https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/salesdrawingpdf/460/46015/460150403_sd.pdf?inline=
- Molex requested 46015-0206 drawing (URL could not be retrieved): https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/salesdrawingpdf/460/46015/460150206_sd.pdf
- KiCad official footprint source, Mini-Fit Jr 5566-02A: https://github.com/KiCad/kicad-footprints/blob/master/Connector_Molex.pretty/Molex_Mini-Fit_Jr_5566-02A_2x01_P4.20mm_Vertical.kicad_mod
- Repo custom Q1/C5750 footprint files: https://github.com/siimsek/PDU/tree/main/hardware/lib/PDU.pretty
