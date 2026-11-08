# T-023 Adım 3 — FB/COMP/OVP/OC (R-022 Tur 5 sonrası)

**Durum: T-023 InProgress. Adım 3 hedef ağları kapandı; adım 4'e geçilmedi, THINKER onayı bekleniyor.** KiCad 10.0.7 (`--refill-zones --schematic-parity`): DRC hatası **0**, parite **0**, açık çift **199 → 68**, adım 1'e göre yeni açık ağ **0**, adım 2'ye göre yeni açık ağ **0**, L2 **1** ada. Uyarı: `{'warning:via_dangling': 6}`. Bu sayılar ara aşamadır, final kabul değildir.

Kaynak: [`scripts/pcb_route_signals.py`](../../../scripts/pcb_route_signals.py) sırasıyla `--step2`, `--step3`, `--gnd`, `--audit3`. D-012 seçenek B: 0,15 mm ızgaralı deterministik A\*. Ham çıktı: [step3-audit.json](step3-audit.json), [step3-routes.json](step3-routes.json), [step3-gnd-applied.json](step3-gnd-applied.json), [drc-step3.json](drc-step3.json). Netclass ve DRC kuralları değişmedi.

## R-022 Tur 2 engelleri

| Madde | Sonuç | Kanıt |
|---|---|---|
| U14.2 GND dönüşü | Kapandı. U14.2, adım 2'de F.Cu ile U12.4'e bağlanıyor ve U12.2/3/4 ile aynı via'yı paylaşıyor | via [43.3, 23.96], `pads_not_on_L2`: yok |
| TP_GND_OC yerel GND | Taşındı: (50,5; 22,0), U14 grubunun yanı | kendi via'sı [49.65, 22.85], kol 1,2 mm |
| TP_OC_SENSE1 uzun kol | Taşındı: (33,0; 59,5) | TP kolu 5,34 mm, 2 via |
| TP_OC_SENSE2 uzun kol | Taşındı: (38,5; 27,0) | TP kolu 2,31 mm, 0 via |
| Kalan 8 sinyal bağlantısı | Tamamlandı. Tamamlanan bağlantı **38**, başarısız **0** | step3-routes.json |

U1 ölçüm kolları değiştirilmedi: yönlendirme sırası `STEP3_FIRST` ile sabitlendi ve pad çıkışları sabit waypoint ile verildi (`STEP3_PREFIX`, `STEP3_FIRST`). `/ISNS1` ve `/ISNS2` izleri önceki adım 3 kartıyla aynıdır.

## T-022 bakırında yapılan iki küçük değişiklik

`51a311f` ile karşılaştırma: `/VIN`, `/ANODE`, `/ISO_GATE`, `/ISNS1`, `/ISNS2` izleri ve tüm bölge sınırları aynı. Yalnız şu ikisi değişti:

1. U6.5 `/VOUT` via'sı (93,40; 45,75) → (93,75; 45,75); boyun izinin via ucu birlikte taşındı, pad ucu (93,40; 46,70) aynı. `/ISO_OV` U6'nın altından geçerken 0,6 mm HV açıklığı bu sayede sağlanıyor.
2. U6.8 `/VSAFE` saplaması pad merkezi yerine padin üst kısmında bitiyor: (93,733; 48,79) → (93,733; 49,00). U6.7 `/ISO_OV` çıkışıyla 0,6 mm bunun için gerekli.

İkisi de `--step2` içinde konum değişikliğidir; `scripts/pcb_route_power.py` değişmedi. Yeniden ölçüm: dört Kelvin kolu adım 2 ile aynı (8,205 / 8,798 / 7,917 / 10,468 mm), sense via'ları güç bakırı dışında, kol üstü güç bakırı örneği 0. R-022 Tur 3 bu iki değişikliği koşullu kabul etti; fiziksel transient/ısı kanıtı değildir.

## Ağlar

| Ağ | Açık çift | İz (mm) | Katman | Via | SW pad / SW bakır (mm) |
|---|---:|---:|---|---:|---:|
| `/FB` | 0 | 8,9 | F | 0 | 1,32 / 2,95 |
| `/FB_TRIM` | 0 | 1,55 | F | 0 | 5,62 / 7,35 |
| `/FB_INJ` | 0 | 109,43 | B, F | 2 | 3,97 / 7,08 |
| `/COMP` | 0 | 131,15 | F | 0 | 1,92 / 2,65 |
| `/COMP_MID` | 0 | 1,8 | F | 0 | 5,33 / 13,08 |
| `/OVP_SENSE` | 0 | 91,97 | B, F | 8 | 30,22 / 36,05 |
| `/OVP_REF` | 0 | 41,51 | F | 0 | 25,68 / 35,49 |
| `/OVP_TRIP_N` | 0 | 85,32 | B, F | 6 | 26,86 / 34,16 |
| `/OVP_Q` | 0 | 137,64 | B, F | 10 | 8,4 / 8,4 |
| `/OVP_BUS_N` | 0 | 91,65 | B, F | 2 | 29,35 / 31,5 |
| `/OC_SENSE1` | 0 | 10,81 | B, F | 2 | 13,42 / 13,61 |
| `/OC_SENSE2` | 0 | 13,87 | B, F | 2 | 9,88 / 10,47 |
| `/OC_REF` | 0 | 118,47 | B, F | 2 | 9,9 / 9,9 |
| `/OC_TRIP1_N` | 0 | 67,64 | B, F | 6 | 6,9 / 6,9 |
| `/OC_TRIP2_N` | 0 | 86,84 | B, F | 6 | 13,35 / 13,35 |
| `/CLR_N` | 0 | 131,78 | B, F | 10 | 27,07 / 36,4 |
| `/ISO_EN` | 0 | 23,35 | B, F | 2 | 32,82 / 41,15 |
| `/ISO_OV` | 0 | 109,7 | B, F | 6 | 18,73 / 20,81 |

SW mesafeleri ölçülen en küçük plan mesafesidir; gürültü kuplajı **doğrulanamadı**. HV 0,6 mm ve sınıf açıklıkları DRC ile sınandı.

## R-022 Tur 4: U1 yakınında FB/COMP aday yerleşimi

Aday uygulandı. Bu bölümdeki sayılar `7a37b1f` kartınındır, "önce" `69f7b7c` kartıdır; TP_COMP sonrası değişiklikler R-022 Tur 5 bölümündedir. Ölçümler [step3-ref-audit.json](step3-ref-audit.json) içindedir; iz merkezi geometrisidir, kuplaj veya gürültü ölçümü **değildir**.

**Değişiklik:** RFB1, RFB2, R_TRIM, CHF, RCOMP, CCOMP ve TP_COMP U1'in kuzeyindeki y=83,8 mm sırasına taşındı (`TP_MOVES`). /FB, /FB_TRIM, /COMP_MID ve /COMP gövdesi elle sabit bakırdır (`STEP3_FIXED`, `STEP3_PREFIX`). Şema, ağ, değer ve güç betiği değişmedi.

| Ağ | Önce mm / via | Sonra mm / via | Önce SW kenar | Sonra SW kenar | Önce ≤3 mm iz | Sonra ≤3 mm iz | L2'siz F.Cu (mm) |
|---|---:|---:|---:|---:|---:|---:|---:|
| `/FB` | 64,529 / 0 | 8,9 / 0 | 1,175 | 1,197 | 9,6 | 4,3 | 0,0 |
| `/COMP` | 151,941 / 0 | 129,895 / 0 | 1,777 | 1,798 | 4,25 | 4,14 | 0,0 |
| `/FB_INJ` | 94,56 / 8 | 109,429 / 2 | 6,464 | 3,848 | 0,0 | 0,0 | 2,12 |
| `/OVP_REF` | 39,04 / 0 | 41,506 / 0 | 25,558 | 25,558 | 0,0 | 0,0 | 0,0 |
| `/OC_REF` | 113,208 / 0 | 118,47 / 2 | 9,775 | 9,775 | 0,0 | 0,0 | 1,18 |

| Yol | Önce mm / geçiş | Sonra mm / geçiş | Düz mesafe (mm) |
|---|---:|---:|---:|
| U1.16 → RFB2.1 | 51,867 / 0 | 8,025 / 0 | 4,783 |
| U1.16 → RFB1.2 | 62,608 / 0 | 8,025 / 0 | 5,701 |
| U1.15 → RCOMP.1 | 29,442 / 0 | 18,575 / 0 | 9,727 |
| U1.15 → CHF.1 | 34,57 / 0 | 15,225 / 0 | 6,908 |
| U1.15 → U2.15 | 119,809 / 0 | 125,945 / 0 | 75,679 |
| U1.15 → TP_COMP.1 | 45,55 / 0 | 25,7 / 0 | 16,471 |
| U8.6 → U7.3 | 28,087 / 0 | 28,279 / 0 | 21,944 |
| U8.6 → R_OCT.1 | 24,305 / 0 | 24,373 / 0 | 22,437 |
| U8.6 → C_REF_OUT.1 | 15,988 / 0 | 15,783 / 0 | 14,935 |
| U8.6 → TP_OVP_REF.1 | 14,328 / 0 | 27,183 / 0 | 24,628 |
| R_OCB.1 → U13.3 | 63,496 / 0 | 63,493 / 2 | 61,03 |
| R_OCB.1 → U14.3 | 89,145 / 0 | 89,143 / 2 | 63,553 |
| R_OCB.1 → R_OCT.2 | 7,247 / 0 | 12,068 / 0 | 5,78 |
| R_OCB.1 → TP_OC_REF.1 | 2,074 / 0 | 2,072 / 0 | 1,845 |

### TI SNVSCD3 ile karşılaştırma

| Öneri (DATASHEET) | Aday | Durum |
|---|---|---|
| s.44: bölücü FB pinine olabildiğince yakın | U1.16→RFB2.1 8,025 mm, →RFB1.2 8,025 mm, via yok | İyileşti; "olabildiğince yakın" hesapla kanıtlanamaz |
| s.44: VOUT tarafı daha uzun olabilir, gürültü kaynağı yanından geçmemeli | /FB_INJ 109,429 mm, en küçük SW kenarı 3,848 mm, B.Cu altında /VIN 17,97 mm | **Açık:** RFB1.1→R_INJ.2 30,702 mm oldu (önce 6,162 mm) |
| s.20 §6.3.15: kompanzasyon primary yanında | U1.15→CHF.1 15,225 mm, →RCOMP.1 18,575 mm | İyileşti |
| s.20 §6.3.15: EXTCOMP pinleri arasında asgari iz | U1.15→U2.15 125,945 mm, düz 75,679 mm | **Kötüleşti** (önce 119,809 mm) |
| s.44: FB yolu SW'den ayrı | /FB en küçük kenar 1,197 mm, ≤2 mm iz 2,16 mm | Az iyileşti; kuplaj doğrulanamadı |

Notlar:
- /FB'nin en yakın noktası U1 çıkış cebinden batıya dönüş köşesidir, L1.1 /SW_PH1 padi köşesinin yanında (44,25; 80,25). Cep çıkışı pin sırası nedeniyle sınırlıdır; CVCC1 padleri arasındaki boşluk CVCC1.2'nin GND via'sında kaldı (TI s.44, "GND via at the return terminal").
- EXTCOMP uzunluğu yerleşimden gelir (U1–U2 düz 75,679 mm). Batı rotası FB grubuyla çakıştığı için doğuya döndü. Daha kısası faz düzenini değiştirmeyi gerektirir; bu kartta yapılmadı.
- Üç hedeften /OC_REF, COMP'un doğu rotasını kesmek için 2 via aldı (2,1 mm B.Cu, altında L3 dolgusu yok). Tur 3'te 0 via idi. /OC_REF F.Cu'da kalıp COMP'un geçiş yapması denenmedi.

L2 dönüş düz hat payı (1'in altı via antipadlerini içerir):

| GND pad çifti | Düz mesafe (mm) | L2 dolgulu pay |
|---|---:|---:|
| U1.17-R_TRIM.2 | 6,769 | 1,0 |
| U1.17-CHF.2 | 9,964 | 0,75 |
| U1.17-CCOMP.2 | 16,064 | 1,0 |
| R_OCB.2-U13.2 | 62,656 | 1,0 |
| R_OCB.2-U14.2 | 64,422 | 0,903 |
| C_REF_OUT.2-U7.2 | 8,608 | 0,886 |
| C_REF_OUT.2-R_OCB.2 | 7,319 | 0,967 |

## R-022 Tur 4: referans grubu prob GND

TP_GND_OVP (61,679; 24,052) → (96,2; 62,0) ve TP_OVP_REF (92,0; 71,85) → (98,9; 62,7) taşındı; TP_OVP_REF, R_OCT.1'e 3,0 mm dal ile bağlı. İki sinyal padine merkezden merkeze düz mesafe **2,79 mm** (TP_OVP_REF) ve **2,79 mm** (TP_OC_REF); önce 52,99 ve 45,69 mm idi. TP_GND_OVP'nin kendi GND via'sı [step3-gnd-applied.json](step3-gnd-applied.json) içindedir.

En yakın prob GND'si değişen test noktaları:

| TP | Önce | Sonra |
|---|---|---|
| TP_COMP | TP_GND_POWER 28,63 | TP_GND_OVP 39,33 |
| TP_ISO_GATE | TP_GND_FB 34,96 | TP_GND_OVP 17,44 |
| TP_ISO_OV | TP_GND_OVP 16,0 | TP_GND_OC 17,65 |
| TP_O1 | TP_GND_OVP 5,28 | TP_GND_OC 9,78 |
| TP_OC_REF | TP_GND_FB 45,69 | TP_GND_OVP 2,79 |
| TP_OVP_REF | TP_GND_FB 52,99 | TP_GND_OVP 2,79 |

TP_O1 ve TP_ISO_OV'un en yakın prob GND mesafesi arttı. TP_COMP için Tur 5'te yerel prob GND sağlandı. Yeni test pedi eklenmedi.

## R-022 Tur 4: Kelvin, güç, HV

- `69f7b7c` ile pcbnew karşılaştırması: /VOUT, /VSAFE, /VIN, /ANODE, /ISO_GATE, /ISNS1, /ISNS2, /O1_11V, /S2E_11V izleri ve via'ları ile tüm bölge sınırları aynı.
- Kelvin kolları 8,205 / 8,798 / 7,917 / 10,468 mm (sınır 15 mm), sense via'ları güç bakırı dışında. U6–Q2 gate 5,469 mm (sınır 10 mm). `--audit2` ile bu kartta ölçüldü, adım 2 dosyaları değiştirilmedi.
- HV 0,6 mm ve sınıf açıklıkları: DRC hatası 0, parite 0, açık çift 68. DRC fiziksel kanıt değildir.
- /OC_REF izi 9,775 mm: R-022 Tur 4 gereği bileşen 10 mm kuralının otomatik ihlali sayılmadı.

## R-022 Tur 5: TP_COMP prob GND

**Karar (uygulandı):** TP_COMP, /COMP hattı üzerinde TP_GND_OC'nin yanına taşındı: (63,4; 83,7) → (54,3; 22,7). TP_COMP→TP_GND_OC merkezden merkeze **3,86 mm** (önce en yakın atanmış GND 39,33 mm). `ASSIGNED_PROBE_GND` ile atanmıştır ve [probe-map.md](probe-map.md) içindedir. CCOMP.2 kullanılmadı.

Karşılaştırılan seçenek: TP_GND_FB'yi kuzeye (66,2; 83,4) almak. Yönlendirilmedi, HESAP olarak değerlendirildi. TP_GND_FB'yi kullanan pad'lerin en yakın prob GND'si şöyle uzardı:

| TP | Şimdi (mm) | TP_GND_FB kuzeye taşınırsa (mm) |
|---|---:|---:|
| TP_VSAFE | 13,78 | 32,47 |
| TP_VOUT | 19,75 | 38,43 |
| TP_FB_INJ_A | 22,8 | 40,07 |
| TP_OVP_TRIP_N | 7,15 | 24,34 |
| TP_OVP_SENSE | 15,13 | 31,35 |
| TP_PG_S2E | 28,84 | 44,84 |
| TP_CLR_N | 30,91 | 45,88 |
| TP_S2E | 24,98 | 38,01 |
| TP_OVP_BUS_N | 9,74 | 22,43 |

Bu nedenle hiçbir atanmış GND padi taşınmadı. Diğer test noktalarının en yakın prob GND'si ve mesafesi `7a37b1f` ile **aynı** (betikle karşılaştırıldı, tek fark TP_COMP).

**Elektriksel etki (GEOMETRİ):**
- TP_COMP ayrı dal değil, COMP hattı pad üzerinden geçiyor: dal uzunluğu 0,0 mm (önce 0,75 mm).
- U1.15→U2.15: 125,945 → 127,005 mm. /COMP toplam 129,895 → 131,152 mm, via yok.
- TP pad'in EXTCOMP'a kapasitif yükü ölçülmedi. TP_COMP artık primary yanında değil, COMP hattının orta kısmındadır; ölçüm noktası olarak kullanılabilirliği **doğrulanamadı**.
- D-008 TP_GND_OC'yi "OC grubu yanı" olarak tanımlar; FB/loop için paylaşımı THINKER kararıdır. D-008 değiştirilmedi.

## R-022 Tur 5: dokuz gizli pasif

[assembly-map.md](assembly-map.md) ve [assembly-map.json](assembly-map.json): RFB1, RFB2, R_TRIM, CHF, RCOMP, CCOMP, CVCC1, CVDDA1, RT1 için konum, dönme, yüz, pad ağları, BOM değer ve MPN. Betik kart değeri BOM'dan farklıysa veya referans görünürse durur. Harita kart SHA-256'sına bağlıdır (`30ff7da04f06ce4a…`, [probe-map.md](probe-map.md) ile aynı). `tasks/T-024.md` kabul kriterlerine SHA eşleşmesi kapısı eklendi. Yerinde montaj doğrulaması **yapılmadı**.

## R-022 Tur 5: doğrulama

- KiCad 10.0.7: DRC hatası 0, parite 0, açık çift 68 (adım 4), L2 1 ada, uyarı `{'warning:via_dangling': 6}`.
- `7a37b1f` ile pcbnew karşılaştırması: /VOUT, /VSAFE, /VIN, /ANODE, /ISO_GATE, /ISNS1, /ISNS2, /O1_11V, /S2E_11V izleri ve via'ları ile tüm bölge sınırları aynı.
- Kelvin 8,205 / 8,798 / 7,917 / 10,468 mm, U6–Q2 gate 5,469 mm. `--audit2` ile bu kartta ölçüldü.
- FB/COMP ve /OC_REF R-022 Tur 5 gereği koşullu ara kabul; SI ve kararlılık **doğrulanamadı**.

## Kapsam dışı bırakılanlar

Şema değişikliği, filtre eklenmesi ve bölücü taşınması yapılmadı; ölçüm/model bunları gösterirse [T-034](../../../tasks/T-034.md) kullanılacak.

## Silk etiketi ve GND rezervasyonu

- Silk referansı gizli test noktaları: TP_COMP, TP_GND_OC, TP_GND_OVP, TP_ISNS2N, TP_ISO_GATE, TP_OVP_REF. Koordinatlar [probe-map.md](probe-map.md) içinde; kart SHA-256'sına bağlı.
- Sıraya alınan pasiflerde RFB1, RFB2, R_TRIM, CHF, RCOMP, CCOMP, CVCC1, CVDDA1, RT1 referansları gizli; yer yok.
- U6.2, U15.2, U11.2/3/4, R_TRIM.2, CHF.2, CCOMP.2, R_BLS.2, C_LDO_DELAY.2 ve U10.9 GND via'ları sinyallerden önce rezerve edildi (`STEP3_PREFIX`).

## GND

Yeni GND via **60**, 4 tanesi aranmış F.Cu yolla. L2'ye bağlı olmayan GND padi: **yok**. `/GND` açık çifti **0**.

## Kalanlar

BLOCKED-ON-USER: `U-011` açık; THINKER doğrulaması bekliyor. Toplam 68 açık çift adım 4 kapsamındadır; en çok: `/P5V_PROT` 22, `/EN_BUCK` 5, `/EN_EFUSE` 3, `/PG_O1` 3, `/PG_S2E` 3, `/IMON_O1` 2, `/IMON_S2E` 2, `/SYNC` 2, `/VDDA1` 2, `/VOUT` 2. `/VOUT` 2 açık çift önceki adım 3 kartında da vardı (adım 1'de 6).

## Doğrulanamayanlar

Startup/gürültü davranışı, gerçek akım ve ısı dağılımı, dönüş SI, fiziksel prob erişimi, üretici via onayı.
