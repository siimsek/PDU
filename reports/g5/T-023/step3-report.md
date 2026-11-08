# T-023 Adım 3 — FB/COMP/OVP/OC (R-022 Tur 3 sonrası)

**Durum: T-023 InProgress. Adım 3 hedef ağları kapandı; adım 4'e geçilmedi, THINKER onayı bekleniyor.** KiCad 10.0.7 (`--refill-zones --schematic-parity`): DRC hatası **0**, parite **0**, açık çift **199 → 68**, adım 1'e göre yeni açık ağ **0**, adım 2'ye göre yeni açık ağ **0**, L2 **1** ada. Uyarı: `{'warning:via_dangling': 6}`. Bu sayılar ara aşamadır, final kabul değildir.

Kaynak: [`scripts/pcb_route_signals.py`](../../../scripts/pcb_route_signals.py) sırasıyla `--step2`, `--step3`, `--gnd`, `--audit3`. D-012 seçenek B: 0,15 mm ızgaralı deterministik A\*. Ham çıktı: [step3-audit.json](step3-audit.json), [step3-routes.json](step3-routes.json), [step3-gnd-applied.json](step3-gnd-applied.json), [drc-step3.json](drc-step3.json). Netclass ve DRC kuralları değişmedi.

## R-022 Tur 2 engelleri

| Madde | Sonuç | Kanıt |
|---|---|---|
| U14.2 GND dönüşü | Kapandı. U14.2, adım 2'de F.Cu ile U12.4'e bağlanıyor ve U12.2/3/4 ile aynı via'yı paylaşıyor | via [43.3, 23.96], `pads_not_on_L2`: yok |
| TP_GND_OC yerel GND | Taşındı: (50,5; 22,0), U14 grubunun yanı | kendi via'sı [49.65, 22.85], kol 1,2 mm |
| TP_OC_SENSE1 uzun kol | Taşındı: (33,0; 59,5) | TP kolu 5,34 mm, 2 via |
| TP_OC_SENSE2 uzun kol | Taşındı: (38,5; 27,0) | TP kolu 2,31 mm, 0 via |
| Kalan 8 sinyal bağlantısı | Tamamlandı. Tamamlanan bağlantı **44**, başarısız **0** | step3-routes.json |

U1 ölçüm kolları değiştirilmedi: `/COMP`, `/FB`, `/OVP_REF`, `/OC_REF`, `/OC_TRIP2_N` sırasıyla yönlendirildi ve pad çıkışları sabit waypoint ile verildi (`STEP3_PREFIX`, `STEP3_FIRST`). `/ISNS1` ve `/ISNS2` izleri önceki adım 3 kartıyla aynıdır.

## T-022 bakırında yapılan iki küçük değişiklik

`51a311f` ile karşılaştırma: `/VIN`, `/ANODE`, `/ISO_GATE`, `/ISNS1`, `/ISNS2` izleri ve tüm bölge sınırları aynı. Yalnız şu ikisi değişti:

1. U6.5 `/VOUT` via'sı (93,40; 45,75) → (93,75; 45,75); boyun izinin via ucu birlikte taşındı, pad ucu (93,40; 46,70) aynı. `/ISO_OV` U6'nın altından geçerken 0,6 mm HV açıklığı bu sayede sağlanıyor.
2. U6.8 `/VSAFE` saplaması pad merkezi yerine padin üst kısmında bitiyor: (93,733; 48,79) → (93,733; 49,00). U6.7 `/ISO_OV` çıkışıyla 0,6 mm bunun için gerekli.

İkisi de `--step2` içinde konum değişikliğidir; `scripts/pcb_route_power.py` değişmedi. Yeniden ölçüm: dört Kelvin kolu adım 2 ile aynı (8,205 / 8,798 / 7,917 / 10,468 mm), sense via'ları güç bakırı dışında, kol üstü güç bakırı örneği 0. R-022 Tur 3 bu iki değişikliği koşullu kabul etti; fiziksel transient/ısı kanıtı değildir.

## Ağlar

| Ağ | Açık çift | İz (mm) | Katman | Via | SW pad / SW bakır (mm) |
|---|---:|---:|---|---:|---:|
| `/FB` | 0 | 64,53 | F | 0 | 1,3 / 2,95 |
| `/FB_TRIM` | 0 | 16,33 | B, F | 4 | 6,82 / 16,45 |
| `/FB_INJ` | 0 | 94,56 | B, F | 8 | 6,59 / 7,38 |
| `/COMP` | 0 | 151,94 | F | 0 | 1,9 / 2,65 |
| `/COMP_MID` | 0 | 9,14 | F | 0 | 9,7 / 19,15 |
| `/OVP_SENSE` | 0 | 87,98 | B, F | 4 | 31,88 / 40,3 |
| `/OVP_REF` | 0 | 39,04 | F | 0 | 25,68 / 35,49 |
| `/OVP_TRIP_N` | 0 | 84,99 | B, F | 6 | 30,46 / 35,47 |
| `/OVP_Q` | 0 | 135,96 | B, F | 4 | 4,56 / 7,7 |
| `/OVP_BUS_N` | 0 | 96,17 | B, F | 5 | 25,45 / 30,95 |
| `/OC_SENSE1` | 0 | 10,81 | B, F | 2 | 13,42 / 13,61 |
| `/OC_SENSE2` | 0 | 13,87 | B, F | 2 | 9,88 / 10,47 |
| `/OC_REF` | 0 | 113,21 | F | 0 | 9,9 / 9,9 |
| `/OC_TRIP1_N` | 0 | 68,87 | B, F | 4 | 6,9 / 6,9 |
| `/OC_TRIP2_N` | 0 | 86,92 | B, F | 6 | 13,35 / 13,35 |
| `/CLR_N` | 0 | 130,24 | B, F | 7 | 27,32 / 37,13 |
| `/ISO_EN` | 0 | 23,35 | B, F | 2 | 32,82 / 41,15 |
| `/ISO_OV` | 0 | 168,16 | B, F | 11 | 18,73 / 20,81 |

SW mesafeleri ölçülen en küçük plan mesafesidir; gürültü kuplajı **doğrulanamadı**. HV 0,6 mm ve sınıf açıklıkları DRC ile sınandı.

## R-022 Tur 3: referans yolları

Ölçümler [step3-ref-audit.json](step3-ref-audit.json) içindedir (`--audit-ref`). Yöntem geometriktir: refill sonrası iz merkez çizgisi, 0,2 mm örnekleme. Akım çözümü, kuplaj ya da gürültü değeri **içermez**. "Önce" sütunu `888dcd9` kartıdır.

Yapılan değişiklikler: `/OVP_REF` ve `/OC_REF` üçüncü ve dördüncü sırada yönlendi, ağaç kaynaktan (U8.6, R_OCB.1) büyüdü, bu ağlarda B.Cu ve via maliyeti artırıldı ve SW'den 10 mm içinde ek maliyet verildi. TP_OVP_REF (12,0; 18,2 → 92,0; 71,85) ve TP_OC_REF (61,3; 4,1 → 93,5; 62,7) ait oldukları gruba taşındı.

| Ağ | Önce mm / via | Sonra mm / via | Sonra F / B mm | Önce SW kenar (mm) | Sonra SW kenar (mm) |
|---|---:|---:|---:|---:|---:|
| `/OVP_REF` | 321,921 / 19 | 39,04 / 0 | 39,04 / 0,0 | 4,736 | 25,558 |
| `/OC_REF` | 176,125 / 11 | 113,208 / 0 | 113,208 / 0,0 | 6,554 | 9,775 |
| `/FB` | 64,529 / 0 | 64,529 / 0 | 64,529 / 0,0 | 1,175 | 1,175 |
| `/COMP` | 151,941 / 0 | 151,941 / 0 | 151,941 / 0,0 | 1,777 | 1,777 |

Toplamlar dallar toplamıdır. Kaynak → kritik giriş ve TP dalları ayrı ayrı:

| Ağ | Yol | Önce mm / katman geçişi | Sonra mm / katman geçişi | Düz mesafe (mm) |
|---|---|---:|---:|---:|
| `/OVP_REF` | U8.6 → U7.3 | 261,865 / 16 | 28,087 / 0 | 21,944 |
| `/OVP_REF` | U8.6 → R_OCT.1 | 246,774 / 14 | 24,305 / 0 | 22,437 |
| `/OVP_REF` | U8.6 → C_REF_OUT.1 | 256,703 / 16 | 15,988 / 0 | 14,935 |
| `/OVP_REF` | U8.6 → TP_OVP_REF.1 | 126,433 / 6 | 14,328 / 0 | 13,271 |
| `/OC_REF` | R_OCB.1 → U13.3 | 102,599 / 6 | 63,496 / 0 | 61,03 |
| `/OC_REF` | R_OCB.1 → U14.3 | 129,102 / 10 | 89,145 / 0 | 63,553 |
| `/OC_REF` | R_OCB.1 → R_OCT.2 | 6,652 / 0 | 7,247 / 0 | 5,78 |
| `/OC_REF` | R_OCB.1 → TP_OC_REF.1 | 156,215 / 10 | 2,074 / 0 | 1,845 |
| `/FB` | U1.16 → RFB2.1 | 51,867 / 0 | 51,867 / 0 | 20,403 |
| `/FB` | U1.16 → RFB1.2 | 62,608 / 0 | 62,608 / 0 | 27,542 |
| `/COMP` | U1.15 → RCOMP.1 | 29,442 / 0 | 29,442 / 0 | 17,52 |
| `/COMP` | U1.15 → CHF.1 | 34,57 / 0 | 34,57 / 0 | 22,212 |
| `/COMP` | U1.15 → U2.15 | 119,809 / 0 | 119,809 / 0 | 75,679 |
| `/COMP` | U1.15 → TP_COMP.1 | 45,55 / 0 | 45,55 / 0 | 36,667 |

### Referans yollarının kalan durumu

- `/OC_REF` uzunluğu yerleşimden gelir: bölücü R_OCT/R_OCB doğuda, U13 ve U14 batıda. U13 yolu 63,5 mm (düz 61,0 mm). U14 yolu 89,1 mm (düz 63,6 mm), bu yolun U13 gövdesini paylaşan kısmı dahil. Daha kısası bölücünün taşınmasını veya yerel filtreyi gerektirir; bu kart yerleşim/şema değişikliğini kapsamıyor, yapılmadı.
- PCB-HANDOFF §3 madde 5, OVP+OC grubu için "SW düğümlerinden ≥10 mm uzak" der. `/OC_REF` en küçük kenar mesafesi 9,775 mm (8,46 mm iz 10 mm içinde). Bu ifadenin grup izlerine uygulanıp uygulanmadığı THINKER kararıdır; **sınır karşılandı denmiyor**.
- D-008/PCB-HANDOFF test noktalarını "kart kenarına yakın" ister. TP_OVP_REF ve TP_OC_REF R-022 Tur 3'teki yerel dal isteği için içeri alındı; iki hüküm çelişiyor, THINKER kararı gerekir.
- Bölücü çıkış empedansı, karşılaştırıcı girişinde gürültü ve GND ofseti **doğrulanamadı**.

## R-022 Tur 3: /FB ve /COMP

İki ağ da önceki kartla aynı rotada kaldı. Tüm uzunluk F.Cu, via ve katman geçişi yok.

| Ağ | En küçük SW kenar (mm) @ D-006 | ≤2 mm iz | ≤3 mm iz | ≤5 mm iz | ≤10 mm iz | L2'siz F.Cu (mm) |
|---|---|---:|---:|---:|---:|---:|
| `/OVP_REF` | 25,558 @ (82,22; 80,82) | 0,0 | 0,0 | 0,0 | 0,0 | 0,0 |
| `/OC_REF` | 9,775 @ (45,79; 61,2) | 0,0 | 0,0 | 0,0 | 8,46 | 0,0 |
| `/FB` | 1,175 @ (44,55; 80,1) | 2,65 | 9,6 | 31,92 | 49,11 | 0,0 |
| `/COMP` | 1,777 @ (44,7; 80,7) | 0,98 | 4,25 | 43,6 | 94,5 | 0,0 |

- Değerlendirme (GEOMETRİ): en yakın nokta U1.15/U1.16 çıkış cebinde, L1.1 /SW_PH1 padi köşesinin yanındadır. `/FB` 2,65 mm, `/COMP` 0,98 mm uzunluk boyunca SW'ye 2 mm'den yakındır.
- Cepten ikinci çıkış CVCC1 padlerinin arasındadır (x≈46,5 mm) ve tek iz sığar. Pin sırası nedeniyle /FB oraya ulaşmak için /COMP'u kesmek zorundadır ve yakında via yeri yoktur (0,15 mm ızgara haritası).
- Denenip reddedildi: 10 mm SW maliyetini /FB ve /COMP'a da uygulamak /FB dalını 84,0 mm'ye çıkardı ve U11.5 `/OC_SENSE1` yönlenemedi.
- Dönüş referansı: F.Cu örneklerinde L2 dolgusu altında olmayan uzunluk 0 mm. Düz hat paylarında 1'in altındaki değerler via antipadlerini de içerir:

| GND pad çifti | Düz mesafe (mm) | Düz hattın L2 dolgulu payı |
|---|---:|---:|
| U1.17-R_TRIM.2 | 20,779 | 1,0 |
| U1.17-CHF.2 | 24,681 | 0,848 |
| U1.17-CCOMP.2 | 25,166 | 1,0 |
| R_OCB.2-U13.2 | 62,656 | 1,0 |
| R_OCB.2-U14.2 | 64,422 | 0,934 |
| C_REF_OUT.2-U7.2 | 8,608 | 0,857 |
| C_REF_OUT.2-R_OCB.2 | 7,319 | 0,867 |



- **Doğrulanamadı:** SW dv/dt kuplajı, FB/COMP döngü etkisi, gerçek dönüş akımı. `/COMP` U2.15 dalı 119,8 mm'dir; iki faz arasındaki ortak COMP uzunluğunun kararlılığa etkisi ölçülmedi.

## R-022 Tur 3: Kelvin, güç, HV

- `888dcd9` ile pcbnew karşılaştırması: `/VOUT`, `/VSAFE`, `/VIN`, `/ANODE`, `/ISO_GATE`, `/ISNS1`, `/ISNS2` izleri ve via'ları ile tüm bölge sınırları aynı.
- Kelvin kolları 8,205 / 8,798 / 7,917 / 10,468 mm (sınır 15 mm), sense via'ları güç bakırı dışında. U6–Q2 gate 5,469 mm (sınır 10 mm). Değerler `--audit2` ile bu kartta yeniden ölçüldü, adım 2 kanıt dosyaları değiştirilmedi.
- HV 0,6 mm ve sınıf açıklıkları: DRC hatası 0, parite 0. DRC fiziksel kanıt değildir.

## Gizli test noktaları

Silk etiketi gizli olanlar: TP_GND_OC, TP_ISNS2N, TP_ISO_GATE, TP_OVP_REF. Koordinatlar, SHA-256 bağlı [probe-map.md](probe-map.md) ve [probe-map.json](probe-map.json) içindedir. Fiziksel yerinde doğrulama yapılmadı.

## Diğer uzun ağlar

En uzun üç ağ: `/ISO_OV` 168,16 mm, 11 via; `/COMP` 151,94 mm, 0 via; `/OVP_Q` 135,96 mm, 4 via. Bunlar R-022 Tur 3 kapsamında kısaltılmadı.

## Silk etiketi ve GND rezervasyonu

- `TP_GND_OC`, `TP_ISNS2N` ve `TP_OVP_REF` için silk'te boş yer bulunamadı, referans gizlendi (`TP_ISO_GATE` ile aynı yöntem). `TP_ISNS2N` için beş, `TP_OVP_REF` için dört konum denendi.
- U6.2, U15.2 ve U11.2/3/4 GND via'ları sinyallerden önce rezerve edildi (`STEP3_PREFIX`).

## GND

Yeni GND via **67**, 7 tanesi aranmış F.Cu yolla. L2'ye bağlı olmayan GND padi: **yok**. `/GND` açık çifti **0**.

## Kalanlar

BLOCKED-ON-USER: R-022 Tur 3 için `U-011` eklendi; THINKER doğrulaması bekliyor. Toplam 68 açık çift adım 4 kapsamındadır; en çok: `/P5V_PROT` 22, `/EN_BUCK` 5, `/EN_EFUSE` 3, `/PG_O1` 3, `/PG_S2E` 3, `/IMON_O1` 2, `/IMON_S2E` 2, `/SYNC` 2, `/VDDA1` 2, `/VOUT` 2. `/VOUT` 2 açık çift önceki adım 3 kartında da vardı (adım 1'de 6).

## Doğrulanamayanlar

Startup/gürültü davranışı, gerçek akım ve ısı dağılımı, dönüş SI, fiziksel prob erişimi, üretici via onayı.
