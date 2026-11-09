# T-023 Adım 4 — kalan sinyaller (başladı, tamamlanmadı)

**Durum: T-023 InProgress; T-023 Done değil.** R-022 Tur 7 ile U-011 kapatıldı, adım 4 başladı. KiCad 10.0.7 (`--refill-zones --schematic-parity`): DRC hatası **0**, parite **0**, açık çift **68 → 14**, `/GND` açık çifti **0**, L2 **1** ada, adım 1 ve 2'ye göre yeni açık ağ **0**. Uyarı: `{'warning:via_dangling': 6}`. Bu ara aşamadır, final kabul değildir.

Ham çıktı: [step4-audit.json](step4-audit.json), [step3-routes.json](step3-routes.json), [step3-audit.json](step3-audit.json), [step3-ref-audit.json](step3-ref-audit.json), [drc-step3.json](drc-step3.json). Netclass ve DRC kuralları değişmedi. "Önce" `a1c6076` kartıdır.

## Kalan açık çiftler (14)

Router 90 bağlantı kurdu, 11 bağlantı kurulamadı; `/GATE`, `/DVDT_O1`, `/DVDT_S2E` HV nedeniyle bilerek yönlendirilmedi.

### Karar gerektirenler: 0,6 mm HV ile çelişen pin çıkışları

- **`/GATE` (U5.5):** pad 0,95 mm aralıkla /ANODE ve /VIN T-022 via'ları arasında. 0,25 mm iz için kenar boşluğu 0,525 mm (HESAP: 0,95 − 0,3 − 0,125), DRC 0,6 mm ister.
- **`/DVDT_S2E` (U4.15):** yan pin U4.16 /VSAFE T-022 saplamasının ucuna merkez mesafesi 0,527 mm, kenar 0,277 mm (HESAP). 0,5 mm pin aralığında çıkış izi 0,6 mm'yi sağlayamıyor. Denemede DRC bu çifti hata verdi.
- **`/DVDT_O1` (U3.15):** aynı yapı varsayıldı, U3'te ayrıca **ölçülmedi** (VARSAYIM).

Kural gevşetilmedi. Seçenekler THINKER'ındır: T-022 via/saplamalarını taşımak veya HV kuralının pad istisnasına ilişkin karar.

### Yönlendirilemeyenler

| Ağ | Pin | Router nedeni |
|---|---|---|
| `/VCC1` | CVCC1.1 | no route (555834 expansions) |
| `/RT_PH1` | RT1.1 | no route (7 expansions) |
| `/CBOOT1` | RBOOT1.2 | no route (2 expansions) |
| `/LDO_DELAY` | U10.7 | no route (591213 expansions) |
| `/CFG_PRI` | RCFG1.1 | no free grid cell at the pad |
| `/CFG_SEC` | RCFG2.1 | no free grid cell at the pad |
| `/IMON_S2E` | RIMON2.1 | no route (63 expansions) |
| `/IMON_S2E` | TP_IMON_S2E.1 | no route (63 expansions) |
| `/IMON_O1` | U3.9 | no route (554849 expansions) |
| `/P5V_PROT` | U10.1 | no route (535525 expansions) |
| `/PG_O1` | U3.13 | no route (506987 expansions) |

- U1.13 `/CFG_PRI` ve U1.14 `/RT_PH1`: kuzey cebi kapalı. Batıda /COMP ve /FB, doğuda /VOUT via (49,0; 80,4) ve B.Cu şeridi var (ızgara haritası). Çıkış için T-022 U1 sense via/şeridinin taşınması gerekebilir; **denenmedi**.
- Diğerlerinin kök nedeni tek tek **doğrulanamadı**.

## Probe GND rolleri

Merkezden merkeze düz mesafe (mm); fiziksel erişim kanıtı değildir.

| Rol | GND pad | Üyeler |
|---|---|---|
| FB | TP_GND_FB | U1.16 19,036; RCOMP 9,431; R_TRIM.2 15,629; TP_FB_INJ_A 12,081; TP_FB_INJ_B 11,982; TP_OVP_REF 2,804 |
| OC | TP_GND_OC | TP_OC_SENSE1 41,382; TP_OC_SENSE2 13,0; TP_OC_REF 2,9; TP_COMP 3,864; U14.2 6,245; U13.2 44,438 |
| OVP/J_OVP | TP_GND_OVP | J_OVP_INJ_BUS.2 12,697; TP_OVP_SENSE 4,53; TP_OVP_BUS_N 4,846; TP_OVP_TRIP_N 5,883; TP_OVP_Q 86,897; TP_VSAFE 11,917; TP_VOUT 15,94 |
| POWER | TP_GND_POWER | J1.2 11,312; TP_ANODE 7,81; TP_VIN 13,412 |

Taşınanlar: TP_GND_OVP (76,5; 14,0), TP_OC_REF (47,6; 22,0), TP_OVP_REF (68,4; 83,6), TP_FB_INJ_A (62,4; 71,8), TP_FB_INJ_B (68,4; 71,8). `ASSIGNED_PROBE_GND` eşlemeleri [probe-map.md](probe-map.md) içindedir. TP_COMP–TP_GND_OC paylaşımı korundu; D-008 değiştirilmedi.

Kapsanamayan üyeler: TP_OC_SENSE1 (TP_GND_OC'ye 41,382 mm) ve TP_OVP_Q (TP_GND_OVP'ye 86,897 mm). Mevcut dört GND padiyle bu iki üye yakınlaştırılmadı. TP'yi taşımak mı yeni pad mi gerektiği THINKER kararıdır; bu yüzden yeni pad kartı **açılmadı**.

En yakın prob GND'si değişen test noktaları (en çok iyileşen önce):

| TP | Önce | Sonra |
|---|---|---|
| TP_FB_INJ_A | TP_GND_OC 40,07 | TP_GND_FB 12,08 |
| TP_PG_S2E | TP_GND_OC 44,84 | TP_GND_OVP 17,65 |
| TP_CLR_N | TP_GND_OC 45,88 | TP_GND_OVP 19,02 |
| TP_OVP_SENSE | TP_GND_OC 31,35 | TP_GND_OVP 4,53 |
| TP_VOUT | TP_GND_OC 38,43 | TP_GND_OVP 15,94 |
| TP_VSAFE | TP_GND_OC 32,47 | TP_GND_OVP 11,92 |
| TP_OVP_TRIP_N | TP_GND_OC 24,34 | TP_GND_OVP 5,88 |
| TP_S2E | TP_GND_OVP 38,01 | TP_GND_OVP 20,27 |
| TP_OVP_BUS_N | TP_GND_OC 22,43 | TP_GND_OVP 4,85 |
| TP_ISO_OV | TP_GND_OC 17,65 | TP_GND_OVP 16,31 |
| TP_OVP_REF | TP_GND_OVP 2,79 | TP_GND_FB 2,8 |
| TP_OC_REF | TP_GND_OVP 2,79 | TP_GND_OC 2,9 |
| TP_FB_INJ_B | TP_GND_POWER 8,51 | TP_GND_FB 11,98 |
| TP_ISO_GATE | TP_GND_OVP 17,44 | TP_GND_OVP 37,06 |

## R_INJ ve FRA padleri

TP_FB_INJ_A R_INJ.1'e 2,115 mm, TP_FB_INJ_B R_INJ.2'ye 2,235 mm, A–B arası 6,0 mm. Fixture bağlantısı ve fiziksel erişim **doğrulanamadı**.

R_INJ.1 ve TP_FB_INJ_A için `/VOUT`, U1.12'nin B.Cu şeridinden bölge bakırıyla alındı (`T023_TAP_R_INJ_F/B`, via 64,5; 74,0): BUS_POWER genişlik kuralı 0,25 mm izi kabul etmez. **Güç bakırına iki bölge ve bir via eklendi.** Mevcut güç izleri ve bölgeleri `a1c6076` ile aynı; Kelvin 8,205 / 8,798 / 7,917 / 10,468 mm, U6–Q2 gate 5,469 mm (`--audit2`).

## FB/COMP ve referanslar

| Ağ | Önce mm / via | Sonra mm / via | Önce SW kenar (mm) | Sonra SW kenar (mm) |
|---|---:|---:|---:|---:|
| `/FB` | 8,9 / 0 | 8,9 / 0 | 1,197 | 1,197 |
| `/COMP` | 130,581 / 0 | 130,581 / 0 | 1,798 | 1,798 |
| `/FB_INJ` | 108,919 / 2 | 57,97 / 4 | 3,848 | 2,057 |
| `/OVP_REF` | 40,437 / 0 | 52,98 / 0 | 25,558 | 12,66 |
| `/OC_REF` | 117,42 / 2 | 114,817 / 2 | 9,775 | 9,925 |

`/OVP_REF` TP_OVP_REF dalıyla uzadı ve SW kenarı azaldı. SI ve kararlılık **doğrulanamadı**.

## İnceleme gerektiren uzun ağlar

AUX_LOCAL netclass genişliği 0,5 mm; pad uçlarında 0,25 mm kullanıldı.

| Ağ | Toplam mm | 0,5 mm kısım | Via |
|---|---:|---:|---:|
| `/VDDA1` | 71,562 | 67,372 | 6 |
| `/VDDA2` | 62,077 | 51,535 | 0 |
| `/VCAP` | 31,511 | 30,267 | 0 |
| `/SW4_PH2` | 34,01 | 30,81 | 2 |
| `/CBOOT2` | 26,697 | 24,411 | 2 |

TI SNVSCD3 s.44 VCC ve BOOT kondansatörlerini pinlere yakın ister; `/VDDA1` ve `/VDDA2`, `/CBOOT2`, `/SW4_PH2` uzunlukları bu amaçla çelişebilir. Bu sayılar kabul edilmiş değildir, yeniden yerleşim kararı gerekebilir. Uzun diğer ağlar: `/P5V_PROT` 252,834 mm, 30 via; `/EN_BUCK` 199,418 mm, 19 via; `/OVP_Q` 138,166 mm, 13 via; `/COMP` 130,581 mm, 0 via; `/CLR_N` 130,024 mm, 12 via; `/SYNC` 129,851 mm, 10 via.

## Doğrulanamayanlar

SI/kararlılık, kuplaj/gürültü, startup, dönüş akımı, ısı, fiziksel prob ve montaj erişimi, üretici via onayı.
