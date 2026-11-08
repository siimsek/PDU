# T-021 — L2/L3 dökümleri ve termal yayılım (iz yok)

KiCad 10.0.7, bundled `pcbnew` (D-009). Üretim: `scripts/pcb_zones.py`, T-020 kartından. Görsel L3: [L3.png](L3.png). Ham veriler: [zone-audit.json](zone-audit.json), [thermal-area.json](thermal-area.json), [drc.json](drc.json).

## DRC (`pcb drc --schematic-parity --refill-zones`)

İhlal/uyarı **0**; parite **0**; `unconnected_items` 395 (ana güç ve sinyal izleri T-022/T-023'te). `pcb_rules.py --check` PASS. DRC muafiyeti eklenmedi.

## Dökümler

| Zone | Net | Katman | Öncelik | Ada | Dolu alan (mm²) |
|---|---|---|---:|---:|---:|
| L2_GND | /GND | In1.Cu | 0 | 1 | 9535.9 |
| L4_GND | /GND | B.Cu | 0 | 1 | 9535.9 |
| L3_VIN | /VIN | In2.Cu | 0 | 1 | 3654.79 |
| L3_VOUT | /VOUT | In2.Cu | 0 | 1 | 2107.6 |
| L3_VSAFE | /VSAFE | In2.Cu | 1 | 1 | 1012.2 |
| L3_GND_U1 | /GND | In2.Cu | 2 | 1 | 48.98 |
| L3_GND_U2 | /GND | In2.Cu | 2 | 1 | 48.98 |

- **L2 kesintisiz GND:** tek ada, kart boyu; düzlemi bölen parça yok. T-022/T-023'te via delikleri hariç bu durum korunmalı.
- **L4 ikincil GND:** tek ada, kart boyu; sinyal izleri T-023'te bu dökümü kesecek.
- **L3:** /VIN batı + iki faz şeridi (C biçimi); /VOUT COUT bankası altında; /VSAFE doğu eFuse tarafında. Q2 kaynak padleri batıda olduğu için /VSAFE, kaynak padleri çevresinden kuzey şeridiyle doğuya taşınıyor; /VOUT drain vialarına güneyden ulaşıyor.
- U1/U2 altındaki L3 /GND adaları, EP vialarının L3 bakırına bağlanması için var (/VIN dökümünden öncelikle kesilir).
- Her zone yalnız kendi ağına bağlı; ada kaldırma "her zaman" olduğundan bağlı olmayan dolgu kalmaz.

## Termal bakır (HANDOFF §3.4, §4; hedef ≥645,16 mm²)

| Parça | Net / katman | Bağlantı | Bağlı dolu alan (mm²) | Sonuç |
|---|---|---|---:|---|
| Q1 | /VIN / In2.Cu | 9 vias on pad 5 | 3654.79 | ≥ hedef |
| Q2 | /VOUT / In2.Cu | 9 vias on pad 5 | 2107.6 | ≥ hedef |

Alanlar farklı ağ ve zone'lardan; çift sayım yok.

## Vialar

33 via-in-pad: U1.30: 6, U2.30: 6, Q1.5: 9, Q2.5: 9, Q2.1: 1, Q2.2: 1, Q2.3: 1. Ölçü 0,6 / 0,3 mm. Tam koordinat ve ağlar `zone-audit.json` içinde.

## Sınırlar

- **Termal bakır iç katmanda:** datasheet RθJA koşulu (1 in² bakır) dış katman pad bakırı içindir. Burada alan L3'te ve vialarla bağlı; aynı termal davranış kanıtlanmadı. Ayrıca Q1 ve Q2 alanları yalnız onlara ait değil: /VIN ve /VOUT dökümünün tamamı, başka parçalarla paylaşılıyor.
- **Via sayısı ve ölçüsü VARSAYIM:** LM70880 EVM via adedi/ölçüsü repoda yok; U1/U2 için pad'e sığan 3 × 2 ızgara kullanıldı. EVM θJA 18,6 K/W koşulunu sağladığı **kanıtlanmadı**; BENCH T4 termal ölçümü gerekli.
- **Üretim:** via-in-pad dolgulu kaplama ve 0,6/0,3 mm via, HANDOFF §7 DFM varsayımı; üretici onayı yok.
- **Q2 yönü:** drain doğuda, kaynak batıda; L3 /VSAFE bu yüzden dolanıyor. HANDOFF §3.3 drain'in banka ortasına bağlanmasını ister; gerçek akım yolu T-022'de değerlendirilmeli.
- **T-022'ye devredilen:** C düzeni doğu CIN GND padlerinin L2 via dönüşleri ve gerçek VIN–CIN–PGND döngü alanı ölçümü.
