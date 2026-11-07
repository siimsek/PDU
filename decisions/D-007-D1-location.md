# D-007 — D1 TVS konumu

- **Kart:** tasks/D-007.md
- **Yazan:** Codex, 2026-11-07
- **Fiziksel iş gerekli mi:** Hayır — kararı THINKER verir

## Soru

SMCJ33A-E3/57T TVS katodu /ANODE'a (Q1 öncesi) mı, /VIN'e (Q1 sonrası) mı bağlanmalı? Seçim; 26 V azami kaynak, ters batarya, 1 µH kablo varsayımlı sıcak takma ve Q1 kapalıyken VIN tarafında kalan enerji için yapılmıştır.

## Seçenekler

| Seçenek | Temel değerler (etiketli) | Kriteri sağlıyor mu | Risk | Kanıt (belge + sayfa) |
|---|---|---|---|---|
| **/ANODE — Q1 öncesi** | Normal 26 V < VWM 33 V; SMCJ33A VBR 36.7–40.6 V; VC 53.3 V @ IPPM 28.1 A; IFSM 200 A yalnız 8.3 ms tek yarım sinüs (DATASHEET) | Kaynak tarafındaki pozitif darbeleri Q1 ve U5'ten önce sınırlar; fakat Q1 kapalıyken /VIN enerjisini sınırlandırmaz | Ters bataryada D1'in katodu /ANODE negatif, anodu GND'de kalır; D1 ileri yönde iletime geçer ve ters akım yolunu oluşturur. Harici 10 A sigortanın D1'in izin verilen darbe akımından önce açacağına ilişkin I²t/zaman-akım doğrulaması yok | Vishay 88394 Rev. 09-Jan-2024, s.1–2; TI LM74700-Q1 Rev. G, s.5, 18–19 |
| **/VIN — Q1 sonrası** | 26 V < 33 V VWM; 53.3 V @ 28.1 A, 65 V LM74700 ANODE abs max'inin 11.7 V altında; Q1 VDS 100 V (DATASHEET) | Doğrudan /VIN ve CIN tarafını sınırlar; pozitif giriş darbelerinde Q1 iletimdeyken kaynak da Q1 kanalı/body diyodu üzerinden aynı koruma düğümüne bağlanır | Q1 kapalıyken /ANODE ve U5 ANODE/EN'i VIN TVS doğrudan sınırlamaz. F2'nin 42.1 V sonucu mevcut /ANODE-SPICE yerleşimine ait; /VIN varyantı yeniden simüle edilmelidir | Vishay 88394 s.2; TI LM74700-Q1 s.5; Infineon BSC160N10NS3 G Rev.2.4 s.1 |
| Otomotiv 24 V load-dump zarfı | TI örneği TVS+ için 48 V üzeri breakdown ve 65 V bastırılmış load-dump dayanımı ister; SMCJ33A VBR 36.7–40.6 V | Bu MPN ile bu özel otomotiv zarfına uygunluk gösterilmemiştir; konum seçimi eksik dalga biçimi/enerji bilgisini telafi etmez | Bu proje girdisi 6S LiPo, 26 V azami olarak ele alındı; otomotiv 24 V transient standardı gereksinimi verilmedi | TI LM74700-Q1 Rev. G, §10.1.1.4, s.18; Vishay 88394, s.2 |

## Öneri

**D1 katodu /VIN'e bağlansın.** Bu, ters bataryada TVS'nin girişte kısa devre oluşturup harici sigortanın açmasına güvenmez ve Q1 ters-akım için kapalıyken /VIN tarafındaki enerjiyi doğrudan sınırlar. Girdi zarfındaki 42.1 V F2 sıcak-takma sonucu U5'in 65 V mutlak maksimumının altında; ancak bu sonuç /ANODE TVS'li mevcut SPICE ağı içindir, seçilen /VIN yerleşiminin kanıtı sayılmaz. Pozitif transientlerde Q1 iletimdeyken VIN kelepçesi giriş yoluna da etki eder; F2/F4 yerleşimi yeniden çalıştırılmalıdır.

## Kanıt

- Vishay, *SMCJ5.0A thru SMCJ188CA*, doc 88394, Rev. 09-Jan-2024, s.1–2. SMCJ33A tablosu: VWM=33 V, VBR=36.7–40.6 V, IPPM=28.1 A, VC=53.3 V; IFSM=200 A @ 8.3 ms tek yarım sinüs (yalnız tek yönlü). [Resmi PDF](https://www.vishay.com/docs/88394/smcj.pdf)
- TI, *LM74700-Q1*, Rev. G, s.5: ANODE–GND ±65 V abs max; CATHODE–ANODE −5…75 V; DBV pin 4 CATHODE, 5 GATE, 6 ANODE. §10.1.1.4, s.18: TI'nin 24 V otomotiv örneğinde TVS+ gereksinimleri. [Resmi PDF](https://www.ti.com/lit/ds/symlink/lm74700-q1.pdf)
- Infineon, *BSC160N10NS3 G*, Rev. 2.4, s.1: VDS=100 V. [Resmi PDF](https://www.infineon.com/dgdl/Infineon-BSC160N10NS3-DS-v02_04-en.pdf?fileId=db3a30432239cccd01226040189a7f47)
- Proje girdisi: `design/pdu_v2.cir` DTVS düğümü `0 anode`; `design/pdu_v2_params.inc` LCAB=0.5 µH nominal. D-007 kartındaki F2=42.1 V / 1 µH değeri senaryo girdisidir, yeni bir simülasyon sonucu değildir.

## Açık varsayımlar

- **VARSAYIM:** Projenin koruma zarfı 6S LiPo, VIN ≤26 V ve T-006 kartındaki 1 µH sıcak-takma senaryosudur; otomotiv 48 V jump-start / 65 V ISO 16750-2 suppressed load dump gereksinimi yoktur. Doğrulama yolu: sistem gereksiniminde kaynak transientinin tepe, süre ve empedansını sabitleyip F2/F4'ü yeniden koşmak.
- **HESAP:** 65.0−53.3=11.7 V; bu yalnız 28.1 A test noktasındaki katalog kelepçe değerine göredir, her darbe biçiminde garanti edilen tepe değildir.

## Doğrulanamayanlar

- Harici Eaton PV-10A10F sigortanın ters batarya akımında açma süresi ve SMCJ33A'nın açma öncesi I²t dayanımı birlikte doğrulanmadı; D1 /ANODE seçeneği için kritik koordinasyon verisi. Eaton sigorta zaman-akım/I²t URL'si: https://www.eaton.com/us/en-us/skuPage.PV-10A10F.html
- Proje transient jeneratörünün load-dump tepe/süre/çıkış empedansı belirtilmedi; bu yüzden 65 V otomotiv load-dump uygunluğu doğrulanamadı. TI uygulama referansı: https://www.ti.com/lit/ds/symlink/lm74700-q1.pdf
- /VIN'e taşınmış DTVS ile F2/F4 sonuçları henüz yok; mevcut SPICE modeli DTVS 0 anode'dur. Girdi model ve senaryo dosyaları haricinde sonuç uydurulmamıştır.

## BUILDER uygulama notu

- `design/pdu_v2_spec.yaml` ve üretici `analysis/g2/bom.py` içindeki D1.K ağını /VIN yap; CSV BOM'da ayrı pin/net sütunu yok, MPN/değer değişmez.
- `design/pdu_v2.cir` içinde `DTVS 0 anode DTVSM` satırını `DTVS 0 vin DTVSM` yap; F2/F4 sıcak takma / kaynak transient vakalarını yeni düğümle tekrar çalıştır.
- T-006 şeması D1.K=/VIN olduğundan bu kararla uyumlu kalır; netlist/spec/SPICE tutarlılık denetimini yenile.
- Eğer sistem gereksinimi otomotiv 24 V load dump ise bu MPN için yeterlilik varsayma; TVS seçimini ayrı teknik kararla yeniden aç.
