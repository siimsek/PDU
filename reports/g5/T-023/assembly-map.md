# T-023 montaj haritası: silk referansı gizli pasifler

**Bu harita yalnız şu kart içeriği için geçerlidir.** `PDU.kicad_pcb` SHA-256 (satır sonu LF): `d87bd7bfd03822d8bd34220172c75ac1819cf0bc79d101ac30ca7380df9b649e`. KiCad 10.0.7. BOM: `design/bom-v2.csv`. Kart değişirse `--assembly-map` ile yeniden üretin; SHA uyuşmuyorsa bu tabloyu kullanmayın. T-024 imalat kapısı bu eşleşmeyi ister.

Konum, yön, değer ve ağlar karttan betikle alındı; değerler BOM ile karşılaştırıldı. D-006: orijin sol alt, y yukarı. PCB: KiCad pafta koordinatı. Dönme KiCad açısıdır.

| Ref | Değer | MPN | Üretici | Footprint | D-006 x ; y (mm) | PCB x ; y (mm) | Dönme | Yüz | Pad ağları |
|---|---|---|---|---|---|---|---:|---|---|
| RFB1 | 130k | ERA3AEB134V | Panasonic | `R_0603_1608Metric` | 42,550 ; 83,800 | 72,550 ; 31,200 | 0° | F | 1: `/FB_INJ`, 2: `/FB` |
| RFB2 | 9.76k | TNPW06039K76BXEA | Vishay | `R_0603_1608Metric` | 45,950 ; 83,800 | 75,950 ; 31,200 | 0° | F | 1: `/FB`, 2: `/FB_TRIM` |
| R_TRIM | 442 | TNPW0603442RBXEA | Vishay | `R_0603_1608Metric` | 49,150 ; 83,800 | 79,150 ; 31,200 | 0° | F | 1: `/FB_TRIM`, 2: `/GND` |
| CHF | 22p | C1608C0G1H220J080AA | TDK | `C_0603_1608Metric` | 53,600 ; 83,800 | 83,600 ; 31,200 | 0° | F | 1: `/COMP`, 2: `/GND` |
| RCOMP | 33.2k | CRCW060333K2FKEA | Vishay | `R_0603_1608Metric` | 57,000 ; 83,800 | 87,000 ; 31,200 | 0° | F | 1: `/COMP`, 2: `/COMP_MID` |
| CCOMP | 10n | C1608C0G1H103J080AA | TDK | `C_0603_1608Metric` | 60,400 ; 83,800 | 90,400 ; 31,200 | 0° | F | 1: `/COMP_MID`, 2: `/GND` |
| CVCC1 | 4.7u | C2012X7R1E475K125AB | TDK | `C_0805_2012Metric` | 46,540 ; 81,775 | 76,540 ; 33,225 | 0° | F | 1: `/VCC1`, 2: `/GND` |
| CVDDA1 | 100n | C1608X7R1H104K080AA | TDK | `C_0603_1608Metric` | 51,038 ; 82,025 | 81,038 ; 32,975 | 0° | F | 1: `/VDDA1`, 2: `/GND` |
| RT1 | 49.9k | CRCW060349K9FKEA | Vishay | `R_0603_1608Metric` | 55,221 ; 82,025 | 85,221 ; 32,975 | 0° | F | 1: `/RT_PH1`, 2: `/GND` |

## Doğrulanamayanlar

Montaj hattı, yeniden işleme erişimi ve kart üzerinde yerinde tanıma doğrulanmadı. Bu dosya üretici montaj çizimi yerine geçmez.
