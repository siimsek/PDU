# T-023 Adım 3 — FB/COMP/OVP/OC (başladı, tamamlanmadı)

**Durum: T-023 InProgress; adım 3 eksik.** KiCad 10.0.7 (`--refill-zones --schematic-parity`): DRC hatası **0**, parite **0**, açık çift **199 → 77**, adım 1'e göre yeni açık ağ **0**, L2 **1** ada. Uyarı: `{'warning:via_dangling': 6}`. Bu sayılar ara aşamadır, final kabul değildir.

Kaynak: [`scripts/pcb_route_signals.py`](../../../scripts/pcb_route_signals.py) sırasıyla `--step2`, `--step3`, `--gnd`, `--audit3`. D-012 seçenek B: KiCad 10.0.7 pcbnew üzerinde 0,15 mm ızgaralı deterministik A\*; sonuçlar DRC ile sınandı. Ham çıktı: [step3-audit.json](step3-audit.json), [step3-routes.json](step3-routes.json), [step3-gnd-applied.json](step3-gnd-applied.json), [drc-step3.json](drc-step3.json). Netclass ve DRC kuralları değişmedi.

## Ağlar

| Ağ | Açık çift | İz (mm) | Katman | Via | SW pad / SW bakır (mm) |
|---|---:|---:|---|---:|---:|
| `/FB` | 0 | 46,4 | F | 0 | 3,04 / 2,95 |
| `/FB_TRIM` | 0 | 16,21 | F | 0 | 6,97 / 16,6 |
| `/FB_INJ` | 0 | 94,07 | B, F | 6 | 5,95 / 10,7 |
| `/COMP` | 4 | 0 | — | 0 | — / — |
| `/COMP_MID` | 0 | 9,14 | F | 0 | 9,7 / 19,15 |
| `/OVP_SENSE` | 0 | 85,55 | F | 0 | 31,88 / 40,3 |
| `/OVP_REF` | 1 | 155,01 | B, F | 7 | 6,34 / 16,5 |
| `/OVP_TRIP_N` | 0 | 83,85 | F | 0 | 30,46 / 35,47 |
| `/OVP_Q` | 1 | 123,2 | B, F | 2 | 4,03 / 6,95 |
| `/OVP_BUS_N` | 0 | 92,99 | B, F | 5 | 25,89 / 30,39 |
| `/OC_SENSE1` | 0 | 82,46 | B, F | 2 | 13,42 / 13,61 |
| `/OC_SENSE2` | 0 | 32,76 | F | 0 | 9,88 / 11,72 |
| `/OC_REF` | 0 | 176,48 | B, F | 9 | 12,52 / 12,52 |
| `/OC_TRIP1_N` | 0 | 68,79 | B, F | 2 | 6,9 / 6,9 |
| `/OC_TRIP2_N` | 1 | 0 | — | 0 | — / — |
| `/CLR_N` | 0 | 130,9 | B, F | 5 | 27,32 / 36,4 |
| `/ISO_EN` | 0 | 23,22 | F | 0 | 32,82 / 41,15 |
| `/ISO_OV` | 1 | 126,08 | B, F | 5 | 18,73 / 20,81 |

Tamamlanan bağlantı **36**. SW mesafeleri ölçülen en küçük plan mesafesidir; gürültü kuplajı **doğrulanamadı**. HV 0,6 mm ve sınıf açıklıkları DRC ile sınandı.

## Tamamlanamayan bağlantılar

| Ağ | Pin | Neden |
|---|---|---|
| `/ISO_OV` | U6.7 | no route (599971 expansions) |
| `/OC_TRIP2_N` | U14.1 | no route (88 expansions) |
| `/OVP_Q` | U9.5 | no free grid cell at the pad |
| `/COMP` | RCOMP.1 | no route (19 expansions) |
| `/COMP` | CHF.1 | no route (19 expansions) |
| `/COMP` | TP_COMP.1 | no route (19 expansions) |
| `/COMP` | U2.15 | no route (19 expansions) |
| `/OVP_REF` | U7.3 | no free grid cell at the pad |

- `/COMP` için U1.15'in çıkışı `/FB` tarafından kapanıyor; dört bağlantı buna bağlı. U1.15/U1.16 çıkışları T-022 U1 ölçüm kollarıyla sınırlı bir cepte.
- `U6.7` kuzeyde `F_VSAFE_Q2`, altta B.Cu /VSAFE barası ile sıkışık.
- `U7.3`, `U9.5`, `U14.1` ızgaraya çıkış yeri bulamıyor veya komşu izlerle kapanıyor.

Bu bağlantılar için yeniden sıralama, elle waypoint veya yerel yerleşim düzeltmesi gerekiyor; başarı sayılmadı.

## GND

GND dönüş vialarının sırası değişti: artık sinyallerden sonra yerleştiriliyor (önce yerleştirildiğinde U1 çıkışlarını kapatıyordu). Yeni GND via **70**, 5 tanesi aranmış F.Cu yolla. L2'ye bağlı olmayan GND padi: **U14.2**. U14.2 için yer bulunamadı; adım 2'deki U12.7–U14.2 ortak via'sı U12 çevrilince kalkmıştı.

## Kalanlar

Toplam 77 açık çift; en çok: `/P5V_PROT` 22, `/EN_BUCK` 5, `/COMP` 4, `/EN_EFUSE` 3, `/PG_O1` 3, `/PG_S2E` 3, `/IMON_O1` 2, `/IMON_S2E` 2, `/SYNC` 2, `/VDDA1` 2. Adım 3'ün kalanı ve adım 4 açık.

## Doğrulanamayanlar

Startup/gürültü davranışı, gerçek akım ve ısı dağılımı, dönüş SI, fiziksel prob erişimi, üretici via onayı.
