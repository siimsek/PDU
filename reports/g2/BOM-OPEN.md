# G2 BOM — MPN seçilemeyen satırlar

Kaynak: [`design/bom-v2.csv`](../../design/bom-v2.csv), üretici: [`analysis/g2/bom.py`](../../analysis/g2/bom.py). MPN yalnız bu G2 oturumunda okunan resmi üretici belgesi seri/değer/paket/sipariş kodunu doğruladığında yazıldı.

Toplam satır: **114**; MPN'li: **71**; MPN AÇIK: **43**.

| Ref | Değer / gereksinim | Neden seçilemedi | Gereken belge |
|---|---|---|---|
| F1 | 10 A DC, >=53.3 VDC, >=1040 A breaking — Fuse vendor datasheets not reachable (403/DNS) | Sigorta üretici datasheet'leri erişilemedi (Littelfuse 403/DNS); kaynak kısa devre akımı 127–1040 A | Sigorta + yuva datasheet'i (DC kesme, I²t) |
| D1 | TVS SMCJ33A family (VRWM 33 V) — Vishay/Littelfuse SMCJ datasheet not reachable; VRWM>VIN_max only | TVS datasheet'i erişilemedi | SMCJ33A resmi datasheet'i (Vishay/Littelfuse) |
| CIN_U5 | 22n — rating >=53.3 V required | MLCC üretici datasheet'ine erişilemedi (TDK/Murata 403; Vishay VJ serisi X7R ≥1 µF ve seçim tablosu kombinasyonu metinden doğrulanamadı); DC-bias eğrisi yok | Seçilecek MLCC serisinin datasheet'i + DC-bias eğrisi |
| CIN1 | 4.7u — 100 V X7R/X7S 1210; DC-bias Ceff >=50 % at 26 V required (power.py assumption) | MLCC üretici datasheet'ine erişilemedi (TDK/Murata 403; Vishay VJ serisi X7R ≥1 µF ve seçim tablosu kombinasyonu metinden doğrulanamadı); DC-bias eğrisi yok | Seçilecek MLCC serisinin datasheet'i + DC-bias eğrisi |
| CIN2 | 4.7u — 100 V X7R/X7S 1210; DC-bias Ceff >=50 % at 26 V required (power.py assumption) | MLCC üretici datasheet'ine erişilemedi (TDK/Murata 403; Vishay VJ serisi X7R ≥1 µF ve seçim tablosu kombinasyonu metinden doğrulanamadı); DC-bias eğrisi yok | Seçilecek MLCC serisinin datasheet'i + DC-bias eğrisi |
| CIN3 | 4.7u — 100 V X7R/X7S 1210; DC-bias Ceff >=50 % at 26 V required (power.py assumption) | MLCC üretici datasheet'ine erişilemedi (TDK/Murata 403; Vishay VJ serisi X7R ≥1 µF ve seçim tablosu kombinasyonu metinden doğrulanamadı); DC-bias eğrisi yok | Seçilecek MLCC serisinin datasheet'i + DC-bias eğrisi |
| CIN4 | 4.7u — 100 V X7R/X7S 1210; DC-bias Ceff >=50 % at 26 V required (power.py assumption) | MLCC üretici datasheet'ine erişilemedi (TDK/Murata 403; Vishay VJ serisi X7R ≥1 µF ve seçim tablosu kombinasyonu metinden doğrulanamadı); DC-bias eğrisi yok | Seçilecek MLCC serisinin datasheet'i + DC-bias eğrisi |
| CIN5 | 4.7u — 100 V X7R/X7S 1210; DC-bias Ceff >=50 % at 26 V required (power.py assumption) | MLCC üretici datasheet'ine erişilemedi (TDK/Murata 403; Vishay VJ serisi X7R ≥1 µF ve seçim tablosu kombinasyonu metinden doğrulanamadı); DC-bias eğrisi yok | Seçilecek MLCC serisinin datasheet'i + DC-bias eğrisi |
| CIN6 | 4.7u — 100 V X7R/X7S 1210; DC-bias Ceff >=50 % at 26 V required (power.py assumption) | MLCC üretici datasheet'ine erişilemedi (TDK/Murata 403; Vishay VJ serisi X7R ≥1 µF ve seçim tablosu kombinasyonu metinden doğrulanamadı); DC-bias eğrisi yok | Seçilecek MLCC serisinin datasheet'i + DC-bias eğrisi |
| CIN7 | 4.7u — 100 V X7R/X7S 1210; DC-bias Ceff >=50 % at 26 V required (power.py assumption) | MLCC üretici datasheet'ine erişilemedi (TDK/Murata 403; Vishay VJ serisi X7R ≥1 µF ve seçim tablosu kombinasyonu metinden doğrulanamadı); DC-bias eğrisi yok | Seçilecek MLCC serisinin datasheet'i + DC-bias eğrisi |
| CIN8 | 4.7u — 100 V X7R/X7S 1210; DC-bias Ceff >=50 % at 26 V required (power.py assumption) | MLCC üretici datasheet'ine erişilemedi (TDK/Murata 403; Vishay VJ serisi X7R ≥1 µF ve seçim tablosu kombinasyonu metinden doğrulanamadı); DC-bias eğrisi yok | Seçilecek MLCC serisinin datasheet'i + DC-bias eğrisi |
| CBIN1 | 10n  | MLCC üretici datasheet'ine erişilemedi (TDK/Murata 403; Vishay VJ serisi X7R ≥1 µF ve seçim tablosu kombinasyonu metinden doğrulanamadı); DC-bias eğrisi yok | Seçilecek MLCC serisinin datasheet'i + DC-bias eğrisi |
| CBIN2 | 10n  | MLCC üretici datasheet'ine erişilemedi (TDK/Murata 403; Vishay VJ serisi X7R ≥1 µF ve seçim tablosu kombinasyonu metinden doğrulanamadı); DC-bias eğrisi yok | Seçilecek MLCC serisinin datasheet'i + DC-bias eğrisi |
| CVCAP | 100n  | MLCC üretici datasheet'ine erişilemedi (TDK/Murata 403; Vishay VJ serisi X7R ≥1 µF ve seçim tablosu kombinasyonu metinden doğrulanamadı); DC-bias eğrisi yok | Seçilecek MLCC serisinin datasheet'i + DC-bias eğrisi |
| CBOOT1 | 47n — LM70880 p.4 recommends 47 nF | MLCC üretici datasheet'ine erişilemedi (TDK/Murata 403; Vishay VJ serisi X7R ≥1 µF ve seçim tablosu kombinasyonu metinden doğrulanamadı); DC-bias eğrisi yok | Seçilecek MLCC serisinin datasheet'i + DC-bias eğrisi |
| CVCC1 | 4.7u  | MLCC üretici datasheet'ine erişilemedi (TDK/Murata 403; Vishay VJ serisi X7R ≥1 µF ve seçim tablosu kombinasyonu metinden doğrulanamadı); DC-bias eğrisi yok | Seçilecek MLCC serisinin datasheet'i + DC-bias eğrisi |
| CVDDA1 | 100n  | MLCC üretici datasheet'ine erişilemedi (TDK/Murata 403; Vishay VJ serisi X7R ≥1 µF ve seçim tablosu kombinasyonu metinden doğrulanamadı); DC-bias eğrisi yok | Seçilecek MLCC serisinin datasheet'i + DC-bias eğrisi |
| CBOOT2 | 47n — LM70880 p.4 recommends 47 nF | MLCC üretici datasheet'ine erişilemedi (TDK/Murata 403; Vishay VJ serisi X7R ≥1 µF ve seçim tablosu kombinasyonu metinden doğrulanamadı); DC-bias eğrisi yok | Seçilecek MLCC serisinin datasheet'i + DC-bias eğrisi |
| CVCC2 | 4.7u  | MLCC üretici datasheet'ine erişilemedi (TDK/Murata 403; Vishay VJ serisi X7R ≥1 µF ve seçim tablosu kombinasyonu metinden doğrulanamadı); DC-bias eğrisi yok | Seçilecek MLCC serisinin datasheet'i + DC-bias eğrisi |
| CVDDA2 | 100n  | MLCC üretici datasheet'ine erişilemedi (TDK/Murata 403; Vishay VJ serisi X7R ≥1 µF ve seçim tablosu kombinasyonu metinden doğrulanamadı); DC-bias eğrisi yok | Seçilecek MLCC serisinin datasheet'i + DC-bias eğrisi |
| CCOMP | 10n — G2 Stage 4; C0G/X7R; bench 2.2-10 nF | MLCC üretici datasheet'ine erişilemedi (TDK/Murata 403; Vishay VJ serisi X7R ≥1 µF ve seçim tablosu kombinasyonu metinden doğrulanamadı); DC-bias eğrisi yok | Seçilecek MLCC serisinin datasheet'i + DC-bias eğrisi |
| CHF | 22p — G2 Stage 4; bench 22-100 pF | MLCC üretici datasheet'ine erişilemedi (TDK/Murata 403; Vishay VJ serisi X7R ≥1 µF ve seçim tablosu kombinasyonu metinden doğrulanamadı); DC-bias eğrisi yok | Seçilecek MLCC serisinin datasheet'i + DC-bias eğrisi |
| C_ISO_VCAP | 100n — LM74502H VCAP-VS >=0.1 uF (p.4) | MLCC üretici datasheet'ine erişilemedi (TDK/Murata 403; Vishay VJ serisi X7R ≥1 µF ve seçim tablosu kombinasyonu metinden doğrulanamadı); DC-bias eğrisi yok | Seçilecek MLCC serisinin datasheet'i + DC-bias eğrisi |
| C_ISO_VS | 100n — LM74502H VS 100 nF (p.3); derating vs continuous bus, fault peak (SIM) < 100 V rating | MLCC üretici datasheet'ine erişilemedi (TDK/Murata 403; Vishay VJ serisi X7R ≥1 µF ve seçim tablosu kombinasyonu metinden doğrulanamadı); DC-bias eğrisi yok | Seçilecek MLCC serisinin datasheet'i + DC-bias eğrisi |
| C_CMP | 100n  | MLCC üretici datasheet'ine erişilemedi (TDK/Murata 403; Vishay VJ serisi X7R ≥1 µF ve seçim tablosu kombinasyonu metinden doğrulanamadı); DC-bias eğrisi yok | Seçilecek MLCC serisinin datasheet'i + DC-bias eğrisi |
| C_REF_IN | 1u  | MLCC üretici datasheet'ine erişilemedi (TDK/Murata 403; Vishay VJ serisi X7R ≥1 µF ve seçim tablosu kombinasyonu metinden doğrulanamadı); DC-bias eğrisi yok | Seçilecek MLCC serisinin datasheet'i + DC-bias eğrisi |
| C_REF_OUT | 1u — datasheet test CL=1 uF (p.4) | MLCC üretici datasheet'ine erişilemedi (TDK/Murata 403; Vishay VJ serisi X7R ≥1 µF ve seçim tablosu kombinasyonu metinden doğrulanamadı); DC-bias eğrisi yok | Seçilecek MLCC serisinin datasheet'i + DC-bias eğrisi |
| C_REF_NR | 1u — TRIM/NR optional | MLCC üretici datasheet'ine erişilemedi (TDK/Murata 403; Vishay VJ serisi X7R ≥1 µF ve seçim tablosu kombinasyonu metinden doğrulanamadı); DC-bias eğrisi yok | Seçilecek MLCC serisinin datasheet'i + DC-bias eğrisi |
| C_LAT | 100n  | MLCC üretici datasheet'ine erişilemedi (TDK/Murata 403; Vishay VJ serisi X7R ≥1 µF ve seçim tablosu kombinasyonu metinden doğrulanamadı); DC-bias eğrisi yok | Seçilecek MLCC serisinin datasheet'i + DC-bias eğrisi |
| C_CLR | 1u — POR ~120 ms | MLCC üretici datasheet'ine erişilemedi (TDK/Murata 403; Vishay VJ serisi X7R ≥1 µF ve seçim tablosu kombinasyonu metinden doğrulanamadı); DC-bias eğrisi yok | Seçilecek MLCC serisinin datasheet'i + DC-bias eğrisi |
| SW1 | momentary reset, SPST-NO — G1 candidate Omron B3U-1000P not re-read in G2 | G1 adayı bu turda okunmadı | Buton datasheet'i |
| C_LDO_IN | 1u — TI recommends 10 uF at IN (p.3); 1 uF local + CIN bank | MLCC üretici datasheet'ine erişilemedi (TDK/Murata 403; Vishay VJ serisi X7R ≥1 µF ve seçim tablosu kombinasyonu metinden doğrulanamadı); DC-bias eğrisi yok | Seçilecek MLCC serisinin datasheet'i + DC-bias eğrisi |
| C_LDO_OUT | 2.2u — datasheet test COUT=2.2 uF | MLCC üretici datasheet'ine erişilemedi (TDK/Murata 403; Vishay VJ serisi X7R ≥1 µF ve seçim tablosu kombinasyonu metinden doğrulanamadı); DC-bias eğrisi yok | Seçilecek MLCC serisinin datasheet'i + DC-bias eğrisi |
| C_LDO_DELAY | 10n  | MLCC üretici datasheet'ine erişilemedi (TDK/Murata 403; Vishay VJ serisi X7R ≥1 µF ve seçim tablosu kombinasyonu metinden doğrulanamadı); DC-bias eğrisi yok | Seçilecek MLCC serisinin datasheet'i + DC-bias eğrisi |
| CDVDT1 | 1.0n — sees VIN+4 V (TPS25982 p.37 design example) | MLCC üretici datasheet'ine erişilemedi (TDK/Murata 403; Vishay VJ serisi X7R ≥1 µF ve seçim tablosu kombinasyonu metinden doğrulanamadı); DC-bias eğrisi yok | Seçilecek MLCC serisinin datasheet'i + DC-bias eğrisi |
| CEFIN1 | 100n  | MLCC üretici datasheet'ine erişilemedi (TDK/Murata 403; Vishay VJ serisi X7R ≥1 µF ve seçim tablosu kombinasyonu metinden doğrulanamadı); DC-bias eğrisi yok | Seçilecek MLCC serisinin datasheet'i + DC-bias eğrisi |
| CEFOUT1 | 10u — 25 V 0805: 46 % of rating; Ceff assumed 40 % (DC-bias datasheet not available) | MLCC üretici datasheet'ine erişilemedi (TDK/Murata 403; Vishay VJ serisi X7R ≥1 µF ve seçim tablosu kombinasyonu metinden doğrulanamadı); DC-bias eğrisi yok | Seçilecek MLCC serisinin datasheet'i + DC-bias eğrisi |
| CDVDT2 | 1.0n — sees VIN+4 V (TPS25982 p.37 design example) | MLCC üretici datasheet'ine erişilemedi (TDK/Murata 403; Vishay VJ serisi X7R ≥1 µF ve seçim tablosu kombinasyonu metinden doğrulanamadı); DC-bias eğrisi yok | Seçilecek MLCC serisinin datasheet'i + DC-bias eğrisi |
| CEFIN2 | 100n  | MLCC üretici datasheet'ine erişilemedi (TDK/Murata 403; Vishay VJ serisi X7R ≥1 µF ve seçim tablosu kombinasyonu metinden doğrulanamadı); DC-bias eğrisi yok | Seçilecek MLCC serisinin datasheet'i + DC-bias eğrisi |
| CEFOUT2 | 10u — 25 V 0805: 46 % of rating; Ceff assumed 40 % (DC-bias datasheet not available) | MLCC üretici datasheet'ine erişilemedi (TDK/Murata 403; Vishay VJ serisi X7R ≥1 µF ve seçim tablosu kombinasyonu metinden doğrulanamadı); DC-bias eğrisi yok | Seçilecek MLCC serisinin datasheet'i + DC-bias eğrisi |
| J1 | 2-pin power, >=4.48 A continuous — header + mating housing + crimp + wire gauge set must be selected together | Molex PS-43045 sunucusu bağlantıyı reddetti | Molex PS-43045-001 + mating housing/crimp |
| J2 | 2-pin power, >=7.0 A continuous — header + mating housing + crimp + wire gauge set must be selected together | Molex PS-43045 sunucusu bağlantıyı reddetti | Molex PS-43045-001 + mating housing/crimp |
| J3 | 2-pin power, >=1.5 A continuous — header + mating housing + crimp + wire gauge set must be selected together | Molex PS-43045 sunucusu bağlantıyı reddetti | Molex PS-43045-001 + mating housing/crimp |

## Derating uyarıları

- R/C satırlarında %50 sınırını aşan uygulama yok (MPN'siz C satırları için gereken anma gerilimi `v_rating` sütununda).

## Mutlak maksimuma yakın (>%80) aktif parçalar (53.3 V TVS clamp VARSAYIMINA göre)

- U5 (LM74700QDBVRQ1): 82% — TVS datasheet doğrulanınca yeniden kontrol
- U6 (LM74502HDDFR): 82% — TVS datasheet doğrulanınca yeniden kontrol
- U10 (TPS7A1650QDGNRQ1): 89% — TVS datasheet doğrulanınca yeniden kontrol

## Özel footprint gereken satırlar

- F1 (10 A DC, >=53.3 VDC, >=1040 A breaking): AÇIK — AÇIK
- Q1 (BSC160N10NS3G): PDU:TDSON-8-1_Konnect — repo custom land (G1: adapted, final land/paste acceptance open)
- U1 (LM70880QRRXRQ1): PDU:LM70880_RRX0029B_RectLands — repo custom land (G1: copper approach/paste acceptance open)
- U2 (LM70880QRRXRQ1): PDU:LM70880_RRX0029B_RectLands — repo custom land (G1: copper approach/paste acceptance open)
- COUT1 (C5750X7S2A226M280KB): PDU:TDK_C5750_2220_Recommended — repo custom land (TDK recommended; prototype-accepted per docs/design.md)
- COUT2 (C5750X7S2A226M280KB): PDU:TDK_C5750_2220_Recommended — repo custom land (TDK recommended; prototype-accepted per docs/design.md)
- COUT3 (C5750X7S2A226M280KB): PDU:TDK_C5750_2220_Recommended — repo custom land (TDK recommended; prototype-accepted per docs/design.md)
- COUT4 (C5750X7S2A226M280KB): PDU:TDK_C5750_2220_Recommended — repo custom land (TDK recommended; prototype-accepted per docs/design.md)
- COUT5 (C5750X7S2A226M280KB): PDU:TDK_C5750_2220_Recommended — repo custom land (TDK recommended; prototype-accepted per docs/design.md)
- COUT6 (C5750X7S2A226M280KB): PDU:TDK_C5750_2220_Recommended — repo custom land (TDK recommended; prototype-accepted per docs/design.md)
- COUT7 (C5750X7S2A226M280KB): PDU:TDK_C5750_2220_Recommended — repo custom land (TDK recommended; prototype-accepted per docs/design.md)
- COUT8 (C5750X7S2A226M280KB): PDU:TDK_C5750_2220_Recommended — repo custom land (TDK recommended; prototype-accepted per docs/design.md)
- COUT9 (C5750X7S2A226M280KB): PDU:TDK_C5750_2220_Recommended — repo custom land (TDK recommended; prototype-accepted per docs/design.md)
- COUT10 (C5750X7S2A226M280KB): PDU:TDK_C5750_2220_Recommended — repo custom land (TDK recommended; prototype-accepted per docs/design.md)
- COUT11 (C5750X7S2A226M280KB): PDU:TDK_C5750_2220_Recommended — repo custom land (TDK recommended; prototype-accepted per docs/design.md)
- COUT12 (C5750X7S2A226M280KB): PDU:TDK_C5750_2220_Recommended — repo custom land (TDK recommended; prototype-accepted per docs/design.md)
- COUT13 (C5750X7S2A226M280KB): PDU:TDK_C5750_2220_Recommended — repo custom land (TDK recommended; prototype-accepted per docs/design.md)
- COUT14 (C5750X7S2A226M280KB): PDU:TDK_C5750_2220_Recommended — repo custom land (TDK recommended; prototype-accepted per docs/design.md)
- COUT15 (C5750X7S2A226M280KB): PDU:TDK_C5750_2220_Recommended — repo custom land (TDK recommended; prototype-accepted per docs/design.md)
- COUT16 (C5750X7S2A226M280KB): PDU:TDK_C5750_2220_Recommended — repo custom land (TDK recommended; prototype-accepted per docs/design.md)
- U3 (TPS259824LNRGER): PDU:TPS25982_RGE0024M — repo custom land
- U4 (TPS259824LNRGER): PDU:TPS25982_RGE0024M — repo custom land
