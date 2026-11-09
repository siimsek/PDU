# T-023 prob haritası

**Bu harita yalnız şu kart içeriği için geçerlidir.** `PDU.kicad_pcb` SHA-256 (satır sonu LF): `23e8ac027f76626ca5e5ceba96c44ac603c1a3eeeb46d881a2d80e0d15f5966c`. KiCad 10.0.7. Kart değişirse `--probe-map` ile yeniden üretin; SHA uyuşmuyorsa bu tabloyu kullanmayın.

Koordinatlar pcbnew pad merkezinden betikle alındı. D-006: orijin sol alt, y yukarı. PCB: KiCad pafta koordinatı, D-006 x+30, 115−y. Mesafeler düz çizgidir.

## Silk etiketi gizli test noktaları (12)

| Ref | Ağ | D-006 x ; y (mm) | PCB x ; y (mm) | Yüz | Pad Ø (mm) | En yakın prob GND |
|---|---|---|---|---|---:|---|
| TP_COMP | `/COMP` | 54,300 ; 22,700 | 84,300 ; 92,300 | F | 1,0 | TP_GND_OC (3,86 mm) |
| TP_FB_INJ_A | `/VOUT` | 62,400 ; 71,800 | 92,400 ; 43,200 | F | 1,0 | TP_GND_FB (12,08 mm) |
| TP_FB_INJ_B | `/FB_INJ` | 68,400 ; 71,800 | 98,400 ; 43,200 | F | 1,0 | TP_GND_FB (11,98 mm) |
| TP_GND_OC | `/GND` | 50,500 ; 22,000 | 80,500 ; 93,000 | F | 2,0 | TP_GND_OVP (27,2 mm) |
| TP_GND_OVP | `/GND` | 76,500 ; 14,000 | 106,500 ; 101,000 | F | 2,0 | TP_GND_OC (27,2 mm) |
| TP_ISNS1P | `/ISNS1` | 40,200 ; 67,600 | 70,200 ; 47,400 | F | 1,0 | TP_GND_FB (29,94 mm) |
| TP_ISNS2N | `/VOUT` | 45,600 ; 19,600 | 75,600 ; 95,400 | F | 1,0 | TP_GND_OC (5,46 mm) |
| TP_ISO_GATE | `/ISO_GATE` | 97,400 ; 44,600 | 127,400 ; 70,400 | F | 1,0 | TP_GND_OVP (37,06 mm) |
| TP_OC_REF | `/OC_REF` | 47,600 ; 22,000 | 77,600 ; 93,000 | F | 1,0 | TP_GND_OC (2,9 mm) |
| TP_OVP_Q | `/OVP_Q` | 101,500 ; 62,600 | 131,500 ; 52,400 | F | 1,0 | TP_GND_FB (41,52 mm) |
| TP_OVP_REF | `/OVP_REF` | 68,400 ; 83,600 | 98,400 ; 31,400 | F | 1,0 | TP_GND_FB (2,8 mm) |
| TP_SW1 | `/SW_PH1` | 45,400 ; 71,600 | 75,400 ; 43,400 | F | 1,0 | TP_GND_FB (23,42 mm) |

## Tüm test noktaları (36)

| Ref | Ağ | D-006 x ; y (mm) | PCB x ; y (mm) | Yüz | Pad Ø (mm) | En yakın prob GND |
|---|---|---|---|---|---:|---|
| TP_ANODE | `/ANODE` | 12,725 ; 34,552 | 42,725 ; 80,448 | F | 2,0 | TP_GND_POWER (7,81 mm) |
| TP_CLR_N | `/CLR_N` | 92,745 ; 4,111 | 122,745 ; 110,889 | F | 1,0 | TP_GND_OVP (19,02 mm) |
| TP_COMP | `/COMP` | 54,300 ; 22,700 | 84,300 ; 92,300 | F | 1,0 | TP_GND_OC (3,86 mm) |
| TP_EN_BUCK | `/EN_BUCK` | 12,727 ; 22,111 | 42,727 ; 92,889 | F | 1,0 | TP_GND_POWER (14,69 mm) |
| TP_FB_INJ_A | `/VOUT` | 62,400 ; 71,800 | 92,400 ; 43,200 | F | 1,0 | TP_GND_FB (12,08 mm) |
| TP_FB_INJ_B | `/FB_INJ` | 68,400 ; 71,800 | 98,400 ; 43,200 | F | 1,0 | TP_GND_FB (11,98 mm) |
| TP_GND_FB | `/GND` | 65,600 ; 83,450 | 95,600 ; 31,550 | F | 2,0 | TP_GND_OC (63,28 mm) |
| TP_GND_OC | `/GND` | 50,500 ; 22,000 | 80,500 ; 93,000 | F | 2,0 | TP_GND_OVP (27,2 mm) |
| TP_GND_OVP | `/GND` | 76,500 ; 14,000 | 106,500 ; 101,000 | F | 2,0 | TP_GND_OC (27,2 mm) |
| TP_GND_POWER | `/GND` | 4,915 ; 34,552 | 34,915 ; 80,448 | F | 2,0 | TP_GND_OC (47,28 mm) |
| TP_IMON_O1 | `/IMON_O1` | 4,181 ; 18,169 | 34,181 ; 96,831 | F | 1,0 | TP_GND_POWER (16,4 mm) |
| TP_IMON_S2E | `/IMON_S2E` | 13,095 ; 26,054 | 43,095 ; 88,946 | F | 1,0 | TP_GND_POWER (11,8 mm) |
| TP_ISNS1N | `/VOUT` | 29,600 ; 67,400 | 59,600 ; 47,600 | F | 1,0 | TP_GND_FB (39,42 mm) |
| TP_ISNS1P | `/ISNS1` | 40,200 ; 67,600 | 70,200 ; 47,400 | F | 1,0 | TP_GND_FB (29,94 mm) |
| TP_ISNS2N | `/VOUT` | 45,600 ; 19,600 | 75,600 ; 95,400 | F | 1,0 | TP_GND_OC (5,46 mm) |
| TP_ISNS2P | `/ISNS2` | 38,800 ; 20,000 | 68,800 ; 95,000 | F | 1,0 | TP_GND_OC (11,87 mm) |
| TP_ISO_GATE | `/ISO_GATE` | 97,400 ; 44,600 | 127,400 ; 70,400 | F | 1,0 | TP_GND_OVP (37,06 mm) |
| TP_ISO_OV | `/ISO_OV` | 61,313 ; 8,054 | 91,313 ; 106,946 | F | 1,0 | TP_GND_OVP (16,31 mm) |
| TP_O1 | `/O1_11V` | 59,839 ; 19,107 | 89,839 ; 95,893 | F | 2,0 | TP_GND_OC (9,78 mm) |
| TP_OC_REF | `/OC_REF` | 47,600 ; 22,000 | 77,600 ; 93,000 | F | 1,0 | TP_GND_OC (2,9 mm) |
| TP_OC_SENSE1 | `/OC_SENSE1` | 33,000 ; 59,500 | 63,000 ; 55,500 | F | 1,0 | TP_GND_POWER (37,57 mm) |
| TP_OC_SENSE2 | `/OC_SENSE2` | 38,500 ; 27,000 | 68,500 ; 88,000 | F | 1,0 | TP_GND_OC (13,0 mm) |
| TP_OVP_BUS_N | `/OVP_BUS_N` | 71,699 ; 14,664 | 101,699 ; 100,336 | F | 1,0 | TP_GND_OVP (4,85 mm) |
| TP_OVP_Q | `/OVP_Q` | 101,500 ; 62,600 | 131,500 ; 52,400 | F | 1,0 | TP_GND_FB (41,52 mm) |
| TP_OVP_REF | `/OVP_REF` | 68,400 ; 83,600 | 98,400 ; 31,400 | F | 1,0 | TP_GND_FB (2,8 mm) |
| TP_OVP_SENSE | `/OVP_SENSE` | 80,981 ; 14,664 | 110,981 ; 100,336 | F | 1,0 | TP_GND_OVP (4,53 mm) |
| TP_OVP_TRIP_N | `/OVP_TRIP_N` | 74,725 ; 19,609 | 104,725 ; 95,391 | F | 1,0 | TP_GND_OVP (5,88 mm) |
| TP_P5V | `/P5V_PROT` | 20,987 ; 61,054 | 50,987 ; 53,946 | F | 1,0 | TP_GND_POWER (30,99 mm) |
| TP_PG_O1 | `/PG_O1` | 9,783 ; 61,054 | 39,783 ; 53,946 | F | 1,0 | TP_GND_POWER (26,95 mm) |
| TP_PG_S2E | `/PG_S2E` | 93,113 ; 8,054 | 123,113 ; 106,946 | F | 1,0 | TP_GND_OVP (17,65 mm) |
| TP_S2E | `/S2E_11V` | 94,105 ; 24,052 | 124,105 ; 90,948 | F | 2,0 | TP_GND_OVP (20,27 mm) |
| TP_SW1 | `/SW_PH1` | 45,400 ; 71,600 | 75,400 ; 43,400 | F | 1,0 | TP_GND_FB (23,42 mm) |
| TP_SW2 | `/SW_PH2` | 38,100 ; 12,400 | 68,100 ; 102,600 | F | 1,0 | TP_GND_OC (15,68 mm) |
| TP_VIN | `/VIN` | 18,327 ; 34,552 | 48,327 ; 80,448 | F | 2,0 | TP_GND_POWER (13,41 mm) |
| TP_VOUT | `/VOUT` | 88,871 ; 24,052 | 118,871 ; 90,948 | F | 2,0 | TP_GND_OVP (15,94 mm) |
| TP_VSAFE | `/VSAFE` | 82,901 ; 24,052 | 112,901 ; 90,948 | F | 2,0 | TP_GND_OVP (11,92 mm) |

## TP_GND_FB ile FB/loop grubu (pad merkezleri, mm)

- U1.16: 19,036
- U1.15: 18,548
- RFB2.1: 20,478
- RFB1.2: 22,228
- R_TRIM.2: 15,629
- CHF.2: 11,23
- RCOMP.1: 9,431
- CCOMP.2: 4,439

## Atanmış prob GND

- TP_COMP → TP_GND_OC: 3,86 mm
- TP_FB_INJ_A → TP_GND_FB: 12,08 mm
- TP_FB_INJ_B → TP_GND_FB: 11,98 mm
- TP_OC_REF → TP_GND_OC: 2,9 mm
- TP_OVP_BUS_N → TP_GND_OVP: 4,85 mm
- TP_OVP_REF → TP_GND_FB: 2,8 mm
- TP_OVP_SENSE → TP_GND_OVP: 4,53 mm
- TP_OVP_TRIP_N → TP_GND_OVP: 5,88 mm

## Doğrulanamayanlar

Fiziksel prob erişimi ve yerinde tanıma doğrulanmadı. Bu dosya montaj çizimi değildir. Fiziksel test veya üretimden önce basılı kopya kart üzerinde yerinde doğrulanmalıdır.
