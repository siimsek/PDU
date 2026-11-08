# T-023 Adım 1 — Temel durum, envanter, GND via adayları (D-012)

**Durum: T-023 InProgress; yalnız adım 1 yapıldı.** `PDU.kicad_pcb` bu adımda değişmedi. Sinyal yolu çizilmedi.

Kaynak: [`scripts/pcb_route_signals.py`](../../../scripts/pcb_route_signals.py) `--step1`, KiCad 10.0.7, `--refill-zones --schematic-parity`. Ham çıktı: [step1-baseline.json](step1-baseline.json), [drc-step1-baseline.json](drc-step1-baseline.json), [step1-inventory.json](step1-inventory.json), [gnd-via-candidates.json](gnd-via-candidates.json).

## Taban (kartın kendisi)

DRC hatası **0**, parite **0**, açık çift **199**, uyarı: `{'warning:via_dangling': 6}`.

- via_dangling: Geçit [/VOUT] F.Cu - B.Cu üzerinde
- via_dangling: Geçit [/VOUT] F.Cu - B.Cu üzerinde
- via_dangling: Geçit [/O1_11V] F.Cu - B.Cu üzerinde
- via_dangling: Geçit [/O1_11V] F.Cu - B.Cu üzerinde
- via_dangling: Geçit [/O1_11V] F.Cu - B.Cu üzerinde
- via_dangling: Geçit [/VSAFE] F.Cu - B.Cu üzerinde

| Sınıf (D-012) | Açık çift |
|---|---:|
| GND dönüş | 77 |
| Diğer | 65 |
| OVP/OC mantık | 34 |
| FB/COMP | 12 |
| Kelvin | 8 |
| Gate | 3 |

| Ağ | Açık çift |
|---|---:|
| `/GND` | 77 |
| `/P5V_PROT` | 22 |
| `/VOUT` | 6 |
| `/CLR_N` | 5 |
| `/EN_BUCK` | 5 |
| `/COMP` | 4 |
| `/ISO_OV` | 4 |
| `/OC_REF` | 4 |
| `/OVP_REF` | 4 |
| `/EN_EFUSE` | 3 |
| `/OVP_SENSE` | 3 |
| `/PG_O1` | 3 |
| `/PG_S2E` | 3 |
| `/FB` | 2 |
| `/FB_INJ` | 2 |
| `/IMON_O1` | 2 |
| `/IMON_S2E` | 2 |
| `/ISNS1` | 2 |
| `/ISNS2` | 2 |
| `/ISO_EN` | 2 |
| `/ISO_GATE` | 2 |
| `/OC_SENSE1` | 2 |
| `/OC_SENSE2` | 2 |
| `/OVP_BUS_N` | 2 |
| `/OVP_Q` | 2 |
| `/OVP_TRIP_N` | 2 |
| `/SYNC` | 2 |
| `/VDDA1` | 2 |
| `/CBOOT1` | 1 |
| `/CBOOT2` | 1 |
| `/CBOOT_R1` | 1 |
| `/CBOOT_R2` | 1 |
| `/CFG_PRI` | 1 |
| `/CFG_SEC` | 1 |
| `/COMP_MID` | 1 |
| `/DVDT_O1` | 1 |
| `/DVDT_S2E` | 1 |
| `/FB_TRIM` | 1 |
| `/GATE` | 1 |
| `/ILIM_O1` | 1 |
| `/ILIM_S2E` | 1 |
| `/ISO_VCAP` | 1 |
| `/LDO_DELAY` | 1 |
| `/OC_TRIP1_N` | 1 |
| `/OC_TRIP2_N` | 1 |
| `/REF_NR` | 1 |
| `/RT_PH1` | 1 |
| `/RT_PH2` | 1 |
| `/SW4_PH1` | 1 |
| `/SW4_PH2` | 1 |
| `/VCAP` | 1 |
| `/VCC1` | 1 |
| `/VCC2` | 1 |
| `/VDDA2` | 1 |

Çiftlerin ref/pin/UUID listesi `step1-inventory.json` içinde (`open_pairs`).

## /GND envanteri

- /GND padi 152; L2'ye bağlı 75; L2'ye bağlı olmayan 77. Mevcut /GND via 90.
- Açık /GND çifti 77. Bu çiftlerin uçlarında 83 farklı açıklama var; 79 tanesi pad, 4 tanesi zone, via veya izdir. **D-012'deki "78 farklı pad" sayısıyla 1 fark var;** D-012 sayım yöntemini ayrıntılı vermediği için fark açıklanamadı, kart üzerinde ölçülen pad listesi esas alınmalı.

## L2 dönüşü ve gerçek yeni via sayısı (geçici kopyada deneme)

Her kopuk GND bakır grubu için kısa F.Cu kol (0,25 mm) + 0,6/0,3 mm through via adayı seçildi. Aynı ayak izinde düz çizgiyle bağlanabilen padler tek via paylaştı. Aday kümesi kartın geçici kopyasına uygulanıp KiCad ile sınandı; **repo kartına yazılmadı.**

| Ölçüm | Değer |
|---|---:|
| Kopuk GND grubu (paylaşım öncesi) | 77 |
| Paylaşım sonrası grup | 72 |
| **Gerçek yeni via** | **72** |
| Yer bulunamayan | 0 |
| En uzun kol (mm) | 2,66 |
| Deneme DRC hatası | 0 |
| Deneme parite | 0 |
| Deneme kalan /GND açık çift | 0 |
| Deneme kalan toplam açık çift | 122 |
| L2 ada sayısı (önce / sonra) | 1 / 1 |
| L2 dolu alan mm² (önce / sonra) | 9287,11 / 9287,11 |

Deneme kopyasındaki `lib_footprint_issues` uyarıları geçici dizinden kaynaklanır (kütüphane tablosu yok); repo kartının tabanında yoktur. L2 alanının değişmemesi beklenir: yeni vialar GND ağındadır, anti-pad açmaz.

Paylaşılan gruplar: U11.2, U11.3, U11.4; U12.2, U12.3, U12.4; U2.16, U2.17.

En uzun kollar:

| Padler | Kol (mm) | Via (D-006) |
|---|---:|---|
| U6.2 | 2,66 | (88,8; 48,14) |
| U7.2 | 2,41 | (105,81; 75,72) |
| TP_GND_OC.1 | 2,3 | (78,49; 24,05) |
| TP_GND_FB.1 | 1,5 | (70,62; 24,05) |
| TP_GND_OVP.1 | 1,5 | (63,18; 24,05) |
| TP_GND_POWER.1 | 1,5 | (6,41; 34,55) |
| U8.4 | 1,48 | (78,75; 79,55) |
| U10.9 | 1,45 | (87,12; 82,45) |

## Sınırlar

- Bu adımda Kelvin, gate ve diğer sinyal yolları çizilmedi; **gerçek Kelvin iz uzunlukları doğrulanamadı**. HV 0,6 mm ve netclass değişmedi.
- B.Cu gerçek serbest koridor genişliği **doğrulanamadı**. GND adaylarında B.Cu izlerine ve T-022 şeritlerine sabit engel olarak bakıldı.
- 0,6/0,3 mm via ve via boyutu **VARSAYIM**, üretici onayı AÇIK (PCB-HANDOFF §7).
- Aday via'lar akım veya SI analizi içermez; yalnız bağlantı ve DRC/L2 sürekliliği sınandı.

## Sonraki adım (D-012 adım 2)

GND adaylarını karta uygula; ardından RS1/RS2–INA296 Kelvin çiftleri ve Q2/U6 gate dönüşü, her Kelvin yolu ayrı ölçülerek.
