# D-008 — Test noktaları ve tezgâh arayüzleri

- **Kart:** tasks/D-008.md
- **Yazan:** Codex, 2026-11-07
- **Fiziksel iş gerekli mi:** Hayır — seçim ve isim eşlemesi THINKER kararıdır.

## Soru

BENCH-ACCEPTANCE T3/T5 testleri ve PCB-HANDOFF'un gerektirdiği erişimi, ölçüm padlerini BOM'a parça eklemeden ve yüksek akım darbesini küçük sinyal TP'lerinden geçirmeden nasıl uygulamalıyız?

## Seçenekler

| Seçenek | Temel değerler (etiketli) | Kriteri sağlıyor mu | Risk | Kanıt (belge + sayfa) |
|---|---|---|---|---|
| Tüm TP'lerde satın alınan klipsli/testpoint bileşeni | Değişik SMD TP MPN'leri gerekir | Hayır | Gereksiz BOM kalemi ve MPN/akım derecesi seçimi; tasarım girdilerinde bu bilgi yok. | KiCad resmi TestPoint footprint'leri çıplak ölçüm padleridir; BENCH §T3/T5 erişim noktalarını ister. |
| J_OVP_INJ_BUS için genel 2.54 mm header | 2 pin, /VOUT–/GND | Hayır | Test fixture'ı 26 V'u 1–2 Ω ve 6.8 µH üzerinden enjekte eder; genel pin-header için bu darbe yoluna uygunluk/akım derecesi kanıtlanmamış. | BENCH §Ekipman, T5a/T5c; PCB-HANDOFF §3. |
| J_OVP_INJ_BUS için 2 lehimli kablo pad'i; JP_EN_BUCK için açık solder jumper | J_OVP pin 1=/VOUT, pin 2=/GND; JP pini 1=/EN_BUCK, pin 2=/GND; ikisi de BOM dışı | Evet | SolderWire footprint'i 6 mm² kablo geometrisini tarif eder, ancak amper derecesi değildir; T5 fixture akımının sınırlandırılması ve lehim bağlantısının tezgâh prosedüründe doğrulanması gerekir. | KiCad resmi `Connector_Wire` ve `Jumper` footprints; BENCH §Ekipman, T5a/T5c. |

## Öneri

Tüm ölçüm TP'lerini aşağıdaki listede verildiği gibi BOM dışı çıplak pad yap. Sinyaller için 1.0 mm; raylar ve prob GND dönüşleri için 2.0 mm stok pad seç. J_OVP_INJ_BUS'a iki lehimli kablo terminali ve ayrı yerel TP_GND_OVP ver; pin 1'i /VOUT, pin 2'yi /GND yap. KiCad'in stok 6 mm² çift kablo footprint'i yalnız mekanik pad geometrisini belirtir; akım/ısı derecesi iddiası değildir. JP_EN_BUCK'u normal çalışmada açık kalacak, gerektiğinde lehimle /EN_BUCK'u /GND'ye bağlayacak stok solder-jumper yap. Bütün test noktaları, fixture kablo padleri ve solder jumper BOM'a girmez.

RS1/RS2 0–20 A test darbeleri yalnız şöntün Kelvin padlerine uygulanır; TP_ISNS* padleri yalnız probla ölçüm içindir. T5 enjeksiyonu öncesi JP_EN_BUCK kapatılır; T3/T4 kullanımında açık kalır.

## Önerilen uygulama listesi

| Ref | Ağ / pin eşlemesi | KiCad stok footprint | BOM |
|---|---|---|---|
| TP_ANODE | /ANODE | `TestPoint:TestPoint_Pad_D2.0mm` | Hayır |
| TP_VIN | /VIN | `TestPoint:TestPoint_Pad_D2.0mm` | Hayır |
| TP_VOUT | /VOUT (ham buck barası/VRAW) | `TestPoint:TestPoint_Pad_D2.0mm` | Hayır |
| TP_VSAFE | /VSAFE | `TestPoint:TestPoint_Pad_D2.0mm` | Hayır |
| TP_O1 | /O1_11V | `TestPoint:TestPoint_Pad_D2.0mm` | Hayır |
| TP_S2E | /S2E_11V | `TestPoint:TestPoint_Pad_D2.0mm` | Hayır |
| TP_ISO_GATE | /ISO_GATE | `TestPoint:TestPoint_Pad_D1.0mm` | Hayır |
| TP_ISO_OV | /ISO_OV | `TestPoint:TestPoint_Pad_D1.0mm` | Hayır |
| TP_OVP_TRIP_N | /OVP_TRIP_N | `TestPoint:TestPoint_Pad_D1.0mm` | Hayır |
| TP_OVP_Q | /OVP_Q | `TestPoint:TestPoint_Pad_D1.0mm` | Hayır |
| TP_CLR_N | /CLR_N | `TestPoint:TestPoint_Pad_D1.0mm` | Hayır |
| TP_OVP_SENSE | /OVP_SENSE | `TestPoint:TestPoint_Pad_D1.0mm` | Hayır |
| TP_OVP_REF | /OVP_REF | `TestPoint:TestPoint_Pad_D1.0mm` | Hayır |
| TP_OVP_BUS_N | /OVP_BUS_N | `TestPoint:TestPoint_Pad_D1.0mm` | Hayır |
| TP_P5V | /P5V_PROT | `TestPoint:TestPoint_Pad_D1.0mm` | Hayır |
| TP_OC_SENSE1 | /OC_SENSE1 | `TestPoint:TestPoint_Pad_D1.0mm` | Hayır |
| TP_OC_SENSE2 | /OC_SENSE2 | `TestPoint:TestPoint_Pad_D1.0mm` | Hayır |
| TP_OC_REF | /OC_REF | `TestPoint:TestPoint_Pad_D1.0mm` | Hayır |
| TP_FB_INJ_A | /VOUT (R_INJ fixture erişimi; TP_VOUT'tan ayrı, R_INJ yanında) | `TestPoint:TestPoint_Pad_D1.0mm` | Hayır |
| TP_FB_INJ_B | /FB_INJ (R_INJ fixture erişimi) | `TestPoint:TestPoint_Pad_D1.0mm` | Hayır |
| TP_COMP | /COMP | `TestPoint:TestPoint_Pad_D1.0mm` | Hayır |
| TP_EN_BUCK | /EN_BUCK | `TestPoint:TestPoint_Pad_D1.0mm` | Hayır |
| TP_SW1 | /SW_PH1 | `TestPoint:TestPoint_Pad_D1.0mm` | Hayır |
| TP_SW2 | /SW_PH2 | `TestPoint:TestPoint_Pad_D1.0mm` | Hayır |
| TP_ISNS1P | /ISNS1 (RS1 Kelvin +) | `TestPoint:TestPoint_Pad_D1.0mm` | Hayır |
| TP_ISNS1N | /VOUT (RS1 Kelvin −) | `TestPoint:TestPoint_Pad_D1.0mm` | Hayır |
| TP_ISNS2P | /ISNS2 (RS2 Kelvin +) | `TestPoint:TestPoint_Pad_D1.0mm` | Hayır |
| TP_ISNS2N | /VOUT (RS2 Kelvin −) | `TestPoint:TestPoint_Pad_D1.0mm` | Hayır |
| TP_PG_O1 | /PG_O1 | `TestPoint:TestPoint_Pad_D1.0mm` | Hayır |
| TP_PG_S2E | /PG_S2E | `TestPoint:TestPoint_Pad_D1.0mm` | Hayır |
| TP_IMON_O1 | /IMON_O1 | `TestPoint:TestPoint_Pad_D1.0mm` | Hayır |
| TP_IMON_S2E | /IMON_S2E | `TestPoint:TestPoint_Pad_D1.0mm` | Hayır |
| TP_GND_FB | /GND, FB/loop grubu yanı | `TestPoint:TestPoint_Pad_D2.0mm` | Hayır |
| TP_GND_OC | /GND, OC grubu yanı | `TestPoint:TestPoint_Pad_D2.0mm` | Hayır |
| TP_GND_OVP | /GND, OVP/J_OVP_INJ_BUS grubu yanı | `TestPoint:TestPoint_Pad_D2.0mm` | Hayır |
| TP_GND_POWER | /GND, güç/çıkış grubu yanı | `TestPoint:TestPoint_Pad_D2.0mm` | Hayır |
| J_OVP_INJ_BUS | 1=/VOUT; 2=/GND (fixture kablosu lehimlenir) | `Connector_Wire:SolderWire-6sqmm_1x02_P14mm_D3.5mm_OD7mm_Relief2x` | Hayır |
| JP_EN_BUCK | 1=/EN_BUCK; 2=/GND (normalde açık; lehimle kapatınca buck kapanır) | `Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm` | Hayır |

## Kanıt

- `reports/g2/BENCH-ACCEPTANCE.md` §Ekipman: OC darbesi RS1/RS2 Kelvin padlerine, buck kapalı, 0–20 A ve ≤10 µs; OVP fixture harici MOSFET/sürücü + 1–2 Ω + 6.8 µH ile 26 V'u J_OVP_INJ_BUS'a bağlar; JP_EN_BUCK buck'ı kapatır.
- `reports/g2/BENCH-ACCEPTANCE.md` T3: FRA bağlantısı R_INJ=49.9 Ω ile TP_FB_INJ_A/B; T5a–T5c ve T5g: TP_OVP_Q, TP_OVP_SENSE, TP_ISO_GATE, TP_OC_SENSE1/2, TP_OVP_BUS_N ve Q ölçümleri.
- `reports/g2/PCB-HANDOFF.md` §3: TP_OC_SENSE1/2, TP_OC_REF, TP_OVP_BUS_N; test noktalarını kart kenarına yakın, her grubun prob GND'sini yanında konumlandır; INA296 RS1/RS2'ye Kelvin bağlanır.
- KiCad resmi footprint library (KiCad 10): [TestPoint_Pad_D1.0mm](https://gitlab.com/kicad/libraries/kicad-footprints/-/blob/master/TestPoint.pretty/TestPoint_Pad_D1.0mm.kicad_mod), [TestPoint_Pad_D2.0mm](https://gitlab.com/kicad/libraries/kicad-footprints/-/blob/master/TestPoint.pretty/TestPoint_Pad_D2.0mm.kicad_mod), [SolderWire-6sqmm 2-wire](https://gitlab.com/kicad/libraries/kicad-footprints/-/blob/master/Connector_Wire.pretty/SolderWire-6sqmm_1x02_P14mm_D3.5mm_OD7mm_Relief2x.kicad_mod), [open solder jumper](https://gitlab.com/kicad/libraries/kicad-footprints/-/blob/master/Jumper.pretty/SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm.kicad_mod).
- KiCad footprint library bu pad tanımlarını/ölçülerini sağlar; bu kaynaklar J_OVP fixture akım derecesini veya lehim bağlantısının termal sınırını belirtmez. Bu kapasite `doğrulanamadı`; T5 test protokolünde harici akım sınırlama ve pulse duration ile onaylanmalıdır.

## Açık varsayımlar

- VARSAYIM: TP footprint'leri çıplak bakır prob padidir; tüm test noktaları, J_OVP fixture padleri ve solder jumper `bom.py` üretiminde `BOM=Hayır` olarak işaretlenir.
- VARSAYIM: TP_ISNS* padleri yalnız düşük akımlı probla ölçüm içindir; T5g akım enjeksiyonu RS1/RS2 Kelvin padlerinden yapılır.
- VARSAYIM: J_OVP_INJ_BUS için 6 mm² kablo footprint'i yalnız geometrik seçimdir; gerçek fixture akım/ısı onayı tezgâh prosedüründe yapılır.

## Doğrulanamayanlar

- J_OVP_INJ_BUS lehim bağlantısı/kablo için sayısal akım veya sıcaklık derecesi — `doğrulanamadı`; KiCad footprint dokümanı akım derecesi vermiyor: https://gitlab.com/kicad/libraries/kicad-footprints/-/blob/master/Connector_Wire.pretty/SolderWire-6sqmm_1x02_P14mm_D3.5mm_OD7mm_Relief2x.kicad_mod.
