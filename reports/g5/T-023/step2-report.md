# T-023 Adım 2 — GND dönüşleri, INA296 Kelvin, gate dönüşü (D-012, R-019, R-020 Tur 1 düzeltmeleri)

**Durum: T-023 InProgress; adım 3 ve 4 başlamadı (R-020 Tur 2 bekliyor).** KiCad 10.0.7 (`--refill-zones --schematic-parity`): DRC hatası **0**, parite **0**, açık çift **199 → 112**, adım 1'e göre yeni açık ağ **0**. Uyarı: `{'warning:via_dangling': 6}`.

Kaynak: [`scripts/pcb_route_signals.py`](../../../scripts/pcb_route_signals.py) `--step2`, `--audit2` (T-022 kartından üretilir). Ham çıktı: [step2-audit.json](step2-audit.json), [step2-gnd-applied.json](step2-gnd-applied.json), [drc-step2.json](drc-step2.json). Netclass ve DRC kuralları değişmedi.

## R-020 engelleyici 1 — Kelvin

**Kök neden (ölçüm):** RS padleri ve INA296 pinlerinin sırası. RS2 ve U12 için U12'yi 180° çevirmek sırayı eşitledi; IN+ ve IN− aynı katmanda, kesişmeden, paralel gidiyor. U11'de RS1 INA'nın kuzeyinde olduğu için aynı çevirme çözüm vermiyor (pin 1/8 güney ucuna düşer); burada IN+ ve IN− kısa ortak bölümde paralel gidiyor, IN− tek via ile B.Cu'ya geçip pin 1'e uzanıyor.

Her kol RS padinin iç kenarındaki **ayrı** via'dan alınıyor (RS1.1 (32,3; 66,4), RS1.2 (37,6; 68,3), RS2.1 (43,8; 15,6), RS2.2 (49,1; 15,6)); güç bağlantısı aynı padin başka noktasında.

| Kol | Uçlar | Gerçek uzunluk (mm, sınır 15) | Parçalar (mm) | Via | SW pad / SW bakır (mm) | Rota altında L2 dolu |
|---|---|---:|---|---:|---:|---:|
| RS1-U11 IN+ (/ISNS1) | U11.8 → RS1.1 | 4,016 | F.Cu 4,016 | 0 | 11,36 / 12,95 | %85,2 |
| RS1-U11 IN- (/VOUT) | U11.1 → RS1.2 | 14,006 | F.Cu 6,706 + B.Cu 6,4 + neck 0,9 | 2 | 6,52 / 7,64 | %78,6 |
| RS2-U12 IN+ (/ISNS2) | U12.8 → RS2.1 | 10,017 | F.Cu 10,017 | 0 | 4,78 / 5,86 | %93,6 |
| RS2-U12 IN- (/VOUT) | U12.1 → RS2.2 | 10,522 | F.Cu 10,522 | 0 | 7,99 / 10,1 | %93,9 |

| Çift | Ana bölüm açı farkı (°) | IN+→IN− medyan (mm) | IN+→IN− en büyük (mm) | IN−→IN+ en büyük (mm) | Boy farkı (mm) |
|---|---:|---:|---:|---:|---:|
| phase 1 | 0,27 | 1,015 | 1,731 | 5,63 | 9,99 |
| phase 2 | 0,0 | 2,927 | 5,268 | 5,287 | 0,505 |

- **Faz 2 paralel:** ana bölümde açı farkı 0,0°, boylar 0,505 mm farklı, aynı katman (F.Cu).
- **Faz 1 kısmen paralel:** IN+ kolunun tamamı IN− koluna yakın (ana bölüm açı farkı 0,27°, medyan 1,015 mm); ama IN− kolunun 9,99 mm fazlası eşsiz (B.Cu üzerinde pin 1'e). Tam eşleşme için RS1'in veya U11'in yerleşimi değişmeli; bu T-022 güç yolunu da değiştirir. **Karar THINKER'da.**
- Uzunluk: `route_mm` polyline merkez hatlarının toplamıdır (zone ribbon + neck), via boyu dahil değildir.
- Tüm uçlar KiCad bağlantı denetiminde bağlı; SW bakırı altından geçmiyor.

## R-020 engelleyici 2 — R_GS

R_GS Q2 gate'in yanına taşındı: (97,5; 49,3). Q2.4 gate → R_GS.1 merkez 2,288 mm; gate pad merkezinden R_GS'ye yol 2,927 mm. R_GS.2 VSAFE, B.Cu üzerinden Q2 source'a döner. U6.6 → Q2.4 gate izi **5,469 mm** (sınır 10,0 mm), değişmedi. Eski R_GS.2 viası ve B.Cu kolu parçayla birlikte taşındı.

## Test padleri

| Pad | Yeni konum | Kol (mm) | Net | Şönt padine bağlı |
|---|---|---:|---|---|
| TP_ISNS1P | (29,4; 65,6) | 1,746 | `/ISNS1` | evet |
| TP_ISNS1N | (24,7; 65,1) | 1,78 | `/VOUT` | evet |
| TP_ISNS2P | (38,8; 20,0) | 1,905 | `/ISNS2` | evet |
| TP_ISNS2N | (45,6; 19,6) | 1,26 | `/VOUT` | evet |

TP_ISO_GATE (97,4; 44,6), gate koluna 4,815 mm (tepeden erişim var, fiziksel prob erişimi **doğrulanamadı**). Bu padin silkscreen etiketi yer olmadığı için gizlendi (D-008 ve montaj çiziminde tanımlı).

## GND ve L2

- Yeni GND via **72**, L2'ye bağlı olmayan GND padi **0**. U12 çevrildiği için U12.7–U14.2 ortak via'sı kalktı; her GND grubu kendi yerel via'sına bağlı.
- L2: **1** ada, dolu alan 9284,83 mm². Dönüş akımı dağılımı ve SI **doğrulanamadı**.

## Açık kalanlar (adım 3 ve 4)

Toplam 112 açık çift; en çok: `/P5V_PROT` 22, `/CLR_N` 5, `/EN_BUCK` 5, `/COMP` 4, `/ISO_OV` 4, `/OC_REF` 4, `/OVP_REF` 4, `/EN_EFUSE` 3. Adım 3'e R-020 Tur 2 sonucundan önce geçilmedi.

## Doğrulanamayanlar

Gerçek Kelvin ölçüm doğruluğu; dönüş akımı/SI; fiziksel prob erişimi; üretici via onayı (0,6/0,3 mm, PCB-HANDOFF §7 VARSAYIM).
