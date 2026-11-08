# T-023 Adım 3 — FB/COMP/OVP/OC (R-022 Tur 2 sonrası)

**Durum: T-023 InProgress. Adım 3 hedef ağları kapandı; adım 4'e geçilmedi, THINKER onayı bekleniyor.** KiCad 10.0.7 (`--refill-zones --schematic-parity`): DRC hatası **0**, parite **0**, açık çift **199 → 68**, adım 1'e göre yeni açık ağ **0**, adım 2'ye göre yeni açık ağ **0**, L2 **1** ada. Uyarı: `{'warning:via_dangling': 6}`. Bu sayılar ara aşamadır, final kabul değildir.

Kaynak: [`scripts/pcb_route_signals.py`](../../../scripts/pcb_route_signals.py) sırasıyla `--step2`, `--step3`, `--gnd`, `--audit3`. D-012 seçenek B: 0,15 mm ızgaralı deterministik A\*. Ham çıktı: [step3-audit.json](step3-audit.json), [step3-routes.json](step3-routes.json), [step3-gnd-applied.json](step3-gnd-applied.json), [drc-step3.json](drc-step3.json). Netclass ve DRC kuralları değişmedi.

## R-022 Tur 2 engelleri

| Madde | Sonuç | Kanıt |
|---|---|---|
| U14.2 GND dönüşü | Kapandı. U14.2, adım 2'de F.Cu ile U12.4'e bağlanıyor ve U12.2/3/4 ile aynı via'yı paylaşıyor | via [42.54, 24.63], `pads_not_on_L2`: yok |
| TP_GND_OC yerel GND | Taşındı: (50,5; 22,0), U14 grubunun yanı | kendi via'sı [49.65, 22.85], kol 1,2 mm |
| TP_OC_SENSE1 uzun kol | Taşındı: (33,0; 59,5) | TP kolu 2,96 mm, 0 via |
| TP_OC_SENSE2 uzun kol | Taşındı: (38,5; 27,0) | TP kolu 2,31 mm, 0 via |
| Kalan 8 sinyal bağlantısı | Tamamlandı. Tamamlanan bağlantı **44**, başarısız **0** | step3-routes.json |

U1 ölçüm kolları değiştirilmedi: `/COMP` önce, `/FB` ikinci, `/OC_TRIP2_N` üçüncü sırada yönlendirildi ve pad çıkışları sabit waypoint ile verildi (`STEP3_PREFIX`, `STEP3_FIRST`). `/ISNS1` ve `/ISNS2` izleri önceki adım 3 kartıyla aynıdır.

## T-022 bakırında yapılan iki küçük değişiklik

Betik karşılaştırması (önceki commit ile bu kart): `/VIN`, `/ANODE`, `/ISO_GATE`, `/ISNS1`, `/ISNS2` izleri ve tüm bölge sınırları aynı. Yalnız şu ikisi değişti:

1. U6.5 `/VOUT` via'sı (93,40; 45,75) → (93,75; 45,75); boyun izinin via ucu birlikte taşındı, pad ucu (93,40; 46,70) aynı. `/ISO_OV` U6'nın altından geçerken 0,6 mm HV açıklığı bu sayede sağlanıyor.
2. U6.8 `/VSAFE` saplaması pad merkezi yerine padin üst kısmında bitiyor: (93,733; 48,79) → (93,733; 49,00). U6.7 `/ISO_OV` çıkışıyla 0,6 mm bunun için gerekli.

İkisi de `--step2` içinde konum değişikliğidir; `scripts/pcb_route_power.py` değişmedi. Yeniden ölçüm: dört Kelvin kolu adım 2 ile aynı (8,205 / 8,798 / 7,917 / 10,468 mm), sense via'ları güç bakırı dışında, kol üstü güç bakırı örneği 0. THINKER bu iki değişikliği kabul etmelidir.

## Ağlar

| Ağ | Açık çift | İz (mm) | Katman | Via | SW pad / SW bakır (mm) |
|---|---:|---:|---|---:|---:|
| `/FB` | 0 | 64,53 | F | 0 | 1,3 / 2,95 |
| `/FB_TRIM` | 0 | 16,33 | B, F | 4 | 6,82 / 16,45 |
| `/FB_INJ` | 0 | 94,21 | B, F | 8 | 6,59 / 10,82 |
| `/COMP` | 0 | 151,94 | F | 0 | 1,9 / 2,65 |
| `/COMP_MID` | 0 | 9,14 | F | 0 | 9,7 / 19,15 |
| `/OVP_SENSE` | 0 | 87,09 | F | 0 | 31,88 / 40,3 |
| `/OVP_REF` | 0 | 321,92 | B, F | 19 | 4,86 / 7,55 |
| `/OVP_TRIP_N` | 0 | 84,99 | B, F | 4 | 30,46 / 35,47 |
| `/OVP_Q` | 0 | 135,46 | B, F | 2 | 4,56 / 7,55 |
| `/OVP_BUS_N` | 0 | 91,49 | B, F | 3 | 26,42 / 30,95 |
| `/OC_SENSE1` | 0 | 8,43 | F | 0 | 13,42 / 13,63 |
| `/OC_SENSE2` | 0 | 13,25 | B, F | 2 | 9,88 / 11,19 |
| `/OC_REF` | 0 | 176,13 | B, F | 11 | 6,68 / 8,45 |
| `/OC_TRIP1_N` | 0 | 68,79 | B, F | 2 | 6,9 / 6,9 |
| `/OC_TRIP2_N` | 0 | 86,92 | F | 0 | 13,35 / 13,35 |
| `/CLR_N` | 0 | 130,07 | B, F | 5 | 27,32 / 37,13 |
| `/ISO_EN` | 0 | 23,22 | F | 0 | 32,82 / 41,15 |
| `/ISO_OV` | 0 | 150,58 | B, F | 7 | 18,73 / 20,81 |

SW mesafeleri ölçülen en küçük plan mesafesidir; gürültü kuplajı **doğrulanamadı**. HV 0,6 mm ve sınıf açıklıkları DRC ile sınandı.

## İnceleme gerektiren noktalar

- Router uzun yollar üretti: `/OVP_REF` 321,92 mm, 19 via; `/OC_REF` 176,13 mm, 11 via; `/COMP` 151,94 mm, 0 via. DRC temiz olsa da `/OVP_REF` ve `/OC_REF` referans ağlarının uzunluğu ve via sayısı gürültü açısından **doğrulanamadı**.
- `/FB` ile en yakın SW padi arasındaki en küçük plan mesafesi 1,3 mm, `/COMP` için 1,9 mm. Bu değerler ölçümdür, başarı iddiası değildir.
- `TP_GND_OC` ve `TP_ISNS2N` için silk'te referans gizlendi: boş yer bulunamadı (TP_ISNS2N için beş konum denendi). `TP_ISO_GATE` ile aynı yöntemdir; prob tanımı silk'te yoktur.
- U6.2, U15.2 ve U11.2/3/4 GND vialari sinyallerden önce rezerve edildi (`STEP3_PREFIX`), yoksa sinyaller padleri kapatıyordu.

## GND

Yeni GND via **67**, 4 tanesi aranmış F.Cu yolla. L2'ye bağlı olmayan GND padi: **yok**. `/GND` açık çifti **0**.

## Kalanlar

BLOCKED-ON-USER kaydı açılmadı: iki tur sonunda R-022 Tur 2'den kalan engel yok. Toplam 68 açık çift adım 4 kapsamındadır; en çok: `/P5V_PROT` 22, `/EN_BUCK` 5, `/EN_EFUSE` 3, `/PG_O1` 3, `/PG_S2E` 3, `/IMON_O1` 2, `/IMON_S2E` 2, `/SYNC` 2, `/VDDA1` 2, `/VOUT` 2. `/VOUT` 2 açık çift önceki adım 3 kartında da vardı (adım 1'de 6).

## Doğrulanamayanlar

Startup/gürültü davranışı, gerçek akım ve ısı dağılımı, dönüş SI, fiziksel prob erişimi, üretici via onayı.
