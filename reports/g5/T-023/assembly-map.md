# T-023 montaj haritası: silk referansı gizli pasifler

**Bu harita yalnız şu kart içeriği için geçerlidir.** `PDU.kicad_pcb` SHA-256 (satır sonu LF): `23e8ac027f76626ca5e5ceba96c44ac603c1a3eeeb46d881a2d80e0d15f5966c`. KiCad 10.0.7. BOM: `design/bom-v2.csv`. Kart değişirse `--assembly-map` ile yeniden üretin; SHA uyuşmuyorsa bu tabloyu kullanmayın. T-024 imalat kapısı bu eşleşmeyi ister.

Konum, yön, değer ve ağlar karttan betikle alındı; değerler BOM ile karşılaştırıldı. D-006: orijin sol alt, y yukarı. PCB: KiCad pafta koordinatı. Dönme KiCad açısıdır.

| Ref | Değer | MPN | Üretici | Footprint | D-006 x ; y (mm) | PCB x ; y (mm) | Dönme | Yüz | Pad ağları |
|---|---|---|---|---|---|---|---:|---|---|
| RFB1 | 130k | ERA3AEB134V | Panasonic | `R_0603_1608Metric` | 42,550 ; 83,800 | 72,550 ; 31,200 | 0° | F | 1: `/FB_INJ`, 2: `/FB` |
| RFB2 | 9.76k | TNPW06039K76BXEA | Vishay | `R_0603_1608Metric` | 45,950 ; 83,800 | 75,950 ; 31,200 | 0° | F | 1: `/FB`, 2: `/FB_TRIM` |
| R_TRIM | 442 | TNPW0603442RBXEA | Vishay | `R_0603_1608Metric` | 49,150 ; 83,800 | 79,150 ; 31,200 | 0° | F | 1: `/FB_TRIM`, 2: `/GND` |
| CHF | 22p | C1608C0G1H220J080AA | TDK | `C_0603_1608Metric` | 53,600 ; 83,800 | 83,600 ; 31,200 | 0° | F | 1: `/COMP`, 2: `/GND` |
| RCOMP | 33.2k | CRCW060333K2FKEA | Vishay | `R_0603_1608Metric` | 57,000 ; 83,800 | 87,000 ; 31,200 | 0° | F | 1: `/COMP`, 2: `/COMP_MID` |
| CCOMP | 10n | C1608C0G1H103J080AA | TDK | `C_0603_1608Metric` | 60,400 ; 83,800 | 90,400 ; 31,200 | 0° | F | 1: `/COMP_MID`, 2: `/GND` |
| CVCC1 | 4.7u | C2012X7R1E475K125AB | TDK | `C_0805_2012Metric` | 44,550 ; 69,500 | 74,550 ; 45,500 | 0° | F | 1: `/VCC1`, 2: `/GND` |
| CVDDA1 | 100n | C1608X7R1H104K080AA | TDK | `C_0603_1608Metric` | 46,300 ; 81,550 | 76,300 ; 33,450 | 0° | F | 1: `/VDDA1`, 2: `/GND` |
| RT1 | 49.9k | CRCW060349K9FKEA | Vishay | `R_0603_1608Metric` | 55,221 ; 82,025 | 85,221 ; 32,975 | 0° | F | 1: `/RT_PH1`, 2: `/GND` |
| RBOOT1 | 1 | CRCW06031R00FKEA | Vishay | `R_0603_1608Metric` | 54,930 ; 76,550 | 84,930 ; 38,450 | 180° | F | 1: `/CBOOT_R1`, 2: `/CBOOT1` |
| RBOOT2 | 1 | CRCW06031R00FKEA | Vishay | `R_0603_1608Metric` | 29,200 ; 7,550 | 59,200 ; 107,450 | 0° | F | 1: `/CBOOT_R2`, 2: `/CBOOT2` |
| CBOOT1 | 47n | C1608X7R1H473K080AA | TDK | `C_0603_1608Metric` | 54,625 ; 78,125 | 84,625 ; 36,875 | 180° | F | 1: `/CBOOT_R1`, 2: `/SW4_PH1` |
| CBOOT2 | 47n | C1608X7R1H473K080AA | TDK | `C_0603_1608Metric` | 29,200 ; 6,000 | 59,200 ; 109,000 | 0° | F | 1: `/CBOOT_R2`, 2: `/SW4_PH2` |
| CVDDA2 | 100n | C1608X7R1H104K080AA | TDK | `C_0603_1608Metric` | 40,000 ; 2,200 | 70,000 ; 112,800 | 0° | F | 1: `/VDDA2`, 2: `/GND` |
| RCFG1 | 54.9k | CRCW060354K9FKEA | Vishay | `R_0603_1608Metric` | 51,125 ; 81,700 | 81,125 ; 33,300 | 0° | F | 1: `/CFG_PRI`, 2: `/GND` |
| RCFG2 | 90.9k | CRCW060390K9FKEA | Vishay | `R_0603_1608Metric` | 32,400 ; 1,500 | 62,400 ; 113,500 | 180° | F | 1: `/CFG_SEC`, 2: `/GND` |
| RIMON2 | 806 | ERA3AEB8060V | Panasonic | `R_0603_1608Metric` | 101,208 ; 31,425 | 131,208 ; 83,575 | 0° | F | 1: `/IMON_S2E`, 2: `/GND` |
| RILIM2 | 300 | TNPW0603300RBXEA | Vishay | `R_0603_1608Metric` | 104,950 ; 32,150 | 134,950 ; 82,850 | -90° | F | 1: `/ILIM_S2E`, 2: `/GND` |
| CIN3 | 4.7u | C3225X7S2A475K200AB | TDK | `C_1210_3225Metric` | 54,550 ; 73,300 | 84,550 ; 41,700 | -90° | F | 1: `/VIN`, 2: `/GND` |

## Doğrulanamayanlar

Montaj hattı, yeniden işleme erişimi ve kart üzerinde yerinde tanıma doğrulanmadı. Bu dosya üretici montaj çizimi yerine geçmez.
