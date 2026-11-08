# T-021 — L2/L3 dökümleri ve termal yayılım (iz yok)

KiCad 10.0.7, bundled `pcbnew` (D-009). Üretim: `scripts/pcb_zones.py`, T-020 kartından. Görsel L3: [L3.png](L3.png). Ham veriler: [zone-audit.json](zone-audit.json), [thermal-area.json](thermal-area.json), [drc.json](drc.json).

## DRC (`pcb drc --schematic-parity --refill-zones`)

İhlal/uyarı **0**; parite **0**; `unconnected_items` 395 (ana güç ve sinyal izleri T-022/T-023'te). `pcb_rules.py --check` PASS. DRC muafiyeti eklenmedi.

## Dökümler

| Zone | Net | Katman | Öncelik | Ada | Dolu alan (mm²) |
|---|---|---|---:|---:|---:|
| L2_GND | /GND | In1.Cu | 0 | 1 | 9535.9 |
| L4_GND | /GND | B.Cu | 0 | 1 | 9535.9 |
| L3_VIN | /VIN | In2.Cu | 0 | 1 | 3654.44 |
| L3_VOUT | /VOUT | In2.Cu | 0 | 1 | 2067.13 |
| L3_VSAFE | /VSAFE | In2.Cu | 1 | 1 | 1690.42 |
| L3_GND_U1 | /GND | In2.Cu | 2 | 1 | 48.98 |
| L3_GND_U2 | /GND | In2.Cu | 2 | 1 | 48.98 |

- **L2 kesintisiz GND:** tek ada, kart boyu; düzlemi bölen parça yok. T-022/T-023'te via delikleri hariç bu durum korunmalı.
- **L4 ikincil GND:** tek ada, kart boyu; sinyal izleri T-023'te bu dökümü kesecek.
- **L3:** /VIN batı + iki faz şeridi (C biçimi); /VOUT COUT bankası altında; /VSAFE doğu eFuse tarafında. Q2 kaynak padleri batıda olduğu için /VSAFE, kaynak padleri çevresindeki cepten kuzeydeki geniş banda (y 56,7–77) geçip doğuya ulaşıyor; /VOUT drain vialarına güneyden ulaşıyor.
- U1/U2 altındaki L3 /GND adaları, EP vialarının L3 bakırına bağlanması için var (/VIN dökümünden öncelikle kesilir).
- Her zone yalnız kendi ağına bağlı; ada kaldırma "her zaman" olduğundan bağlı olmayan dolgu kalmaz.

## Termal bakır (HANDOFF §3.4, §4; hedef ≥645,16 mm²)

| Parça | Net / katman | Bağlantı | Bağlı dolu alan (mm²) | Sonuç |
|---|---|---|---:|---|
| Q1 | /VIN / In2.Cu | 9 vias on pad 5 | 3654.44 | ≥ hedef |
| Q2 | /VOUT / In2.Cu | 9 vias on pad 5 | 2067.13 | ≥ hedef |

Alanlar farklı ağ ve zone'lardan; çift sayım yok.

## Vialar

33 via-in-pad: U1.30: 6, U2.30: 6, Q1.5: 9, Q2.5: 9, Q2.1: 1, Q2.2: 1, Q2.3: 1. Ölçü 0,6 / 0,3 mm. Tam koordinat ve ağlar `zone-audit.json` içinde.

## R-016 düzeltmeleri

**CEFIN (engelleyici):** CEFIN1 U3'ün batısına (IN 1–3 / GND 4–5), CEFIN2 U4'ün doğusuna (IN 16 / GND 14) taşındı. U4'ün batı pinleri U3'e baktığı için doğu çifti kullanıldı.

| Kondansatör | /VSAFE padi → en yakın IN pini | /GND padi → en yakın GND pini | Önceki (R-016) IN / GND |
|---|---:|---:|---|
| CEFIN1 → U3 | 1,50 mm (pin 1) | 1,50 mm (pin 4) | 27,34 / 26,43 mm |
| CEFIN2 → U4 | 1,48 mm (pin 16) | 1,48 mm (pin 14) | 27,33 / 26,37 mm |

(Pad merkezleri; gerçek iz değil.)

**L3 /VSAFE şeridi (kendi hatam):** ilk sürümde Q2 çevresindeki kuzey şerit yalnız yaklaşık 1,3 mm genişliğindeydi. Yol analizinde çıktı; cep x 86,2–92'ye genişletildi, kuzey bant y 77'ye çıkarıldı.

## Q2–COUT yolu ve hata döngüsü: T-022 öncesi kanıt

[q2-path.json](q2-path.json). HESAP on filled copper (GRID mm raster, 3-4 chamfer). Not a routed path: COUT, U3/U4 and CEFIN have no vias to L3 yet, so each pad is treated as if a via to L3 stood at its centre (T-022 must add them). Width = 2 x bottleneck clearance, excluding END_R around sources and targets.

**Gerçek yol henüz yok.** COUT, U3/U4 ve CEFIN padlerinin L3'e viası olmadığı için aşağıdaki sayılar gerçek akım yolu değil, mevcut dolgu bakırı üzerinde üst sınır analizidir.

| /VOUT: Q2 drain vialarından 32 COUT padine (L3) | Değer |
|---|---:|
| En kısa / en uzun bakır yol | 11.63 / 75.3 mm |
| Darboğaz genişliği (en dar) | 6.0 mm |
| Ulaşılamayan | 0 |

| /VSAFE: Q2 kaynak vialarından (L3) | Bakır yol (mm) | Darboğaz (mm) |
|---|---:|---:|
| U3 IN pin 1 | 21.96 | 6.4 |
| U4 IN pin 16 | 26.85 | 6.4 |
| CEFIN1 /VSAFE | 21.5 | 6.0 |
| CEFIN2 /VSAFE | 27.03 | 6.4 |

Dönüş L2 GND üzerinden; düz hat CEFIN1 GND → en yakın COUT GND 10.24 mm, CEFIN2 → 22.65 mm.

**Sonuç: yol bağlı, ama L3 tek başına yeterli değil.**
- Darboğaz 6.0 mm / 6.0 mm; routing-g2 BUS_POWER iç katman alt sınırı 18.36 mm (7,5 A, HESAP). L3 bu akımı tek başına taşıyamaz.
- Via: Q2 drain 9, Q2 kaynak 3; routing-g2 BUS_POWER en az 15.
- En uzun COUT yolu 75.3 mm; banka Q2 drain'e tek uçtan bağlı (HANDOFF §3.3 "banka ortasına").
- **T-022 kapısı:** dış katman ≥4,92 mm /VOUT ve /VSAFE yolları, yeterli via, COUT ve eFuse bağlantıları ve ≤138 A tepe hata döngüsünün gerçek ölçümü. Bunlar sağlanamazsa Q2 yerleşimi değişmeli.

## Sınırlar

- **Termal bakır iç katmanda:** datasheet RθJA koşulu (1 in² bakır) dış katman pad bakırı içindir. Burada alan L3'te ve vialarla bağlı; aynı termal davranış kanıtlanmadı. Ayrıca Q1 ve Q2 alanları yalnız onlara ait değil: /VIN ve /VOUT dökümünün tamamı, başka parçalarla paylaşılıyor.
- **Via sayısı ve ölçüsü VARSAYIM:** LM70880 EVM via adedi/ölçüsü repoda yok; U1/U2 için pad'e sığan 3 × 2 ızgara kullanıldı. EVM θJA 18,6 K/W koşulunu sağladığı **kanıtlanmadı**; BENCH T4 termal ölçümü gerekli.
- **Üretim:** via-in-pad dolgulu kaplama ve 0,6/0,3 mm via, HANDOFF §7 DFM varsayımı; üretici onayı yok.
- **Q2 yönü:** drain doğuda, kaynak batıda; L3 /VSAFE bu yüzden dolanıyor. Aşağıdaki darboğaz ve via eksikleri T-022'de kapanmazsa Q2'nin döndürülmesi yeniden değerlendirilmeli (U6–Q2 kapı kısıtıyla birlikte).
- **T-022'ye devredilen:** C düzeni doğu CIN GND padlerinin L2 via dönüşleri ve gerçek VIN–CIN–PGND döngü alanı ölçümü.
