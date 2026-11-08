# T-023 Adım 2 — GND dönüşleri, INA296 Kelvin, gate dönüşü (D-012, R-019, R-020 Tur 2, R-021 düzeltmesi)

**Durum: T-023 InProgress; adım 3 ve 4 başlamadı.** KiCad 10.0.7 (`--refill-zones --schematic-parity`): DRC hatası **0**, parite **0**, açık çift **199 → 112**, adım 1'e göre yeni açık ağ **0**. Uyarı: `{'warning:via_dangling': 6}`.

Kaynak: [`scripts/pcb_route_signals.py`](../../../scripts/pcb_route_signals.py) (`--step2`, `--audit2`, `--probe1`) ve [`scripts/pcb_route_power.py`](../../../scripts/pcb_route_power.py); kart T-021 tabanından üretilir. Ham çıktı: [step2-audit.json](step2-audit.json), [phase1-alternatives.json](phase1-alternatives.json), [step2-gnd-applied.json](step2-gnd-applied.json), [drc-step2.json](drc-step2.json). Netclass ve DRC kuralları değişmedi.

## R-020 Tur 2 — faz 1 Kelvin

**Önce RS1/U11 sabitken ölçüldü** (T-022 kartının geçici kopyaları, yalnız faz 1 kolları eklendi):

| Alternatif | DRC hatası | Parite | IN+ (mm) | IN− (mm) | IN−'in IN+'a 2 mm içinde kalan payı | ≤15 mm |
|---|---:|---:|---:|---:|---:|---|
| B_mevcut_F_ve_B | 0 | 0 | 4,016 | 14,006 | %49,0 | evet |
| A_ikisi_F_kuzeyden | 0 | 0 | 4,016 | 17,479 | %0,0 | **hayır** |
| C_F_uzerinde_gidis_donus | 0 | 0 | 9,562 | 14,006 | %68,1 | evet |

Hiçbiri iki kolu boyunca paralel yapmıyor: A sınırı aşıyor ve kuzeyden dolaşıyor, B mevcut hal, C IN+ üzerinde gidiş-dönüş üretiyor. Kök neden pin sırası: RS1 kuzeydeyken RS1.1 (IN+) batıda, U11.8 (IN+) doğuda.

**Yerleşim düzeltmesi:** RS1 180° çevrildi (RS1.2 VOUT batıda, RS1.1 ISNS1 doğuda). Etkilenen T-022 güç yolu birlikte yeniden üretildi: RS1.2 çıkışı kuzeye (`F_VOUT_RS1`, 16 via, B.Cu bara), L1.2 → RS1.1 izi, U1 ölçüm kolları. Kelvin alma noktaları aşağıdaki R-021 tablosundadır.

| Kol | Uçlar | Gerçek uzunluk (mm, sınır 15) | Parçalar (mm) | Via | SW pad / SW bakır (mm) | Rota altında L2 dolu |
|---|---|---:|---|---:|---:|---:|
| RS1-U11 IN+ (/ISNS1) | U11.8 → RS1.1 | 8,205 | F.Cu 8,205 | 0 | 8,2 / 8,6 | %91,6 |
| RS1-U11 IN- (/VOUT) | U11.1 → RS1.2 | 8,798 | F.Cu 8,798 | 0 | 10,8 / 12,55 | %83,1 |
| RS2-U12 IN+ (/ISNS2) | U12.8 → RS2.1 | 7,917 | F.Cu 7,917 | 0 | 6,85 / 7,15 | %92,5 |
| RS2-U12 IN- (/VOUT) | U12.1 → RS2.2 | 10,468 | F.Cu 10,468 | 0 | 7,75 / 9,78 | %93,9 |

| Çift | Ana bölüm açı farkı (°) | IN+→IN− medyan (mm) | IN+→IN− en büyük (mm) | IN−→IN+ en büyük (mm) | Boy farkı (mm) |
|---|---:|---:|---:|---:|---:|
| phase 1 | 0,0 | 2,101 | 5,265 | 4,192 | 0,593 |
| phase 2 | 0,0 | 2,627 | 4,105 | 5,608 | 2,551 |

Her iki faz da artık aynı katmanda (F.Cu), kesişmeden ve via'sız paralel. `route_mm` polyline merkez hattı toplamıdır; akım çözümü değildir. Pad yakınındaki yaklaşma bölümleri eşlenik değildir; bu sayı tablodaki "en büyük" sütununda görünür.

## R-021 — sense alma noktası

R-021 engelleyicisi: U1.11 sense viası RS1.1'de L1 güç izinin bakırı içindeydi. Via (37,7; 66,4) konumuna, güç girişinin karşı (güney) iç kenarına taşındı. Aynı kusur iki noktada daha bulunup birlikte düzeltildi: RS2.1 sense viası L2 güç izi ucunun içindeydi, RS2.2 sense viası `F_VOUT_RS2` bakırının içindeydi. Dört RS padinde **pad merkezi, gerçek sense via ve ribbon başlangıcı ayrı alanlardır** (`step2-audit.json`: `pad_centre`, `sense_via`, `ribbon_start`).

| Pad | Pad merkezi | Sense via | Via ağda var | Via merkezi güç izinde | Via merkezi güç dökümünde | Güç izine kenar aralığı (mm) | Güç dökümü konturuna (mm) |
|---|---|---|---|---|---|---:|---:|
| RS1.1 | (37,962; 67,6) | (37,7; 66,4) | evet | hayır | hayır | 1,013 | — |
| RS1.2 | (32,037; 67,6) | (32,3; 66,4) | evet | hayır | hayır | 1,551 | 2,2 |
| RS2.1 | (43,538; 16,6) | (43,9; 17,7) | evet | hayır | hayır | 0,709 | — |
| RS2.2 | (49,462; 16,6) | (49,1; 15,6) | evet | hayır | hayır | 0,976 | 0,7 |

Ölçüm karttan: `PCB_TRACK.HitTest` ve `ZONE.HitTestFilledArea`. Dört Kelvin kolunun merkez hattının (uçlardaki 0,4 mm uzatma dahil) kendi ağının güç bakırına değen örnek sayısı: **0**. Bu, geometrik ayrımı gösterir; pad içi akım dağılımı ve ölçüm hatası **doğrulanamadı**.

## Gate ve R_GS

U6.6 → Q2.4 **5,469 mm** (sınır 10,0 mm). Q2.4 → R_GS.1 merkez 2,288 mm; en yakın Q2 source padi → R_GS.2 merkez 4,276 mm. R_GS.2 B.Cu /VSAFE üzerinden Q2 source'a döner; ortak empedans ve gate discharge **doğrulanamadı**.

## Test padleri

| Pad | Konum | Kol (mm) | Net | Şönt padine bağlı |
|---|---|---:|---|---|
| TP_ISNS1P | (40,2; 67,6) | 2,773 | `/ISNS1` | evet |
| TP_ISNS1N | (29,6; 67,4) | 1,649 | `/VOUT` | evet |
| TP_ISNS2P | (38,8; 20,0) | 1,905 | `/ISNS2` | evet |
| TP_ISNS2N | (45,6; 19,6) | 0,877 | `/VOUT` | evet |

TP_ISO_GATE (97,4; 44,6), kol 4,815 mm; silk etiketi gizli (montaj/test belgesinde eşleme doğrulanmadı). Prob erişimi ve kapasitif yük **doğrulanamadı**.

## GND ve L2

Yeni GND via **71**; L2'ye bağlı olmayan GND padi **0**. U11.7 kendi viasına Kelvin kolu nedeniyle yer bulamadı, U13.2 ile 0,25 mm F.Cu bağla ortak via kullanıyor (U12.7–U14.2 ile aynı yöntem; R-019 koşullu kabul etmişti, ortak empedans doğrulanmadı). L2: **1** ada, dolu alan 9287,11 mm².

## Açık kalanlar

Toplam 112 açık çift; en çok: `/P5V_PROT` 22, `/CLR_N` 5, `/EN_BUCK` 5, `/COMP` 4, `/ISO_OV` 4, `/OC_REF` 4, `/OVP_REF` 4, `/EN_EFUSE` 3. Adım 3'e geçilmedi.

## Doğrulanamayanlar

Gerçek Kelvin ölçüm doğruluğu; dönüş akımı/SI; fiziksel prob erişimi; üretici via onayı (0,6/0,3 mm, PCB-HANDOFF §7 VARSAYIM). T-022 kapsamındaki RS1 yolunun akım/termal davranışı ölçülmedi.
