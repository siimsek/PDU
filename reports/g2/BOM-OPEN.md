# G2 BOM — MPN seçilemeyen satırlar

Kaynak: [`design/bom-v2.csv`](../../design/bom-v2.csv), üretici: [`analysis/g2/bom.py`](../../analysis/g2/bom.py). MPN yalnız bu G2 oturumunda okunan resmi üretici belgesi seri/değer/paket/sipariş kodunu doğruladığında yazıldı.

Toplam satır: **148**; MPN'li: **147**; MPN AÇIK: **1**.

| Ref | Değer / gereksinim | Neden seçilemedi | Gereken belge |
|---|---|---|---|
| F1 | 10 A DC, >=53.3 VDC, >=1040 A breaking — candidate Littelfuse 0456020.ER (20 A, 65 VDC, I2t 18 A2s, 2.3 mOhm per Littelfuse page); DC interrupting rating not readable (PDF only via download) -> AÇIK | G4: Littelfuse ürün sayfası okundu, datasheet PDF yalnız indirme olarak açıldı (DC kesme kapasitesi okunamadı); kaynak kısa devre akımı 127–1040 A | Sigorta + yuva datasheet'i (DC kesme, I²t) |

## Derating uyarıları

- R/C satırlarında %50 sınırını aşan uygulama yok (MPN'siz C satırları için gereken anma gerilimi `v_rating` sütununda).

## Mutlak maksimuma yakın (>%80) aktif parçalar (53.3 V SMCJ33A kelepçesine göre, DATASHEET Vishay doc 88394 p.2)

- U5 (LM74700QDBVRQ1): 82% — kısa süreli kelepçe gerilimi; abs-max altında, BENCH T1 hot-plug ile ölç
- U6 (LM74502HDDFR): 82% — kısa süreli kelepçe gerilimi; abs-max altında, BENCH T1 hot-plug ile ölç
- U10 (TPS7A1650QDGNRQ1): 89% — kısa süreli kelepçe gerilimi; abs-max altında, BENCH T1 hot-plug ile ölç

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
- COUT17 (C5750X7S2A226M280KB): PDU:TDK_C5750_2220_Recommended — repo custom land (TDK recommended; prototype-accepted per docs/design.md)
- COUT18 (C5750X7S2A226M280KB): PDU:TDK_C5750_2220_Recommended — repo custom land (TDK recommended; prototype-accepted per docs/design.md)
- COUT19 (C5750X7S2A226M280KB): PDU:TDK_C5750_2220_Recommended — repo custom land (TDK recommended; prototype-accepted per docs/design.md)
- COUT20 (C5750X7S2A226M280KB): PDU:TDK_C5750_2220_Recommended — repo custom land (TDK recommended; prototype-accepted per docs/design.md)
- COUT21 (C5750X7S2A226M280KB): PDU:TDK_C5750_2220_Recommended — repo custom land (TDK recommended; prototype-accepted per docs/design.md)
- COUT22 (C5750X7S2A226M280KB): PDU:TDK_C5750_2220_Recommended — repo custom land (TDK recommended; prototype-accepted per docs/design.md)
- COUT23 (C5750X7S2A226M280KB): PDU:TDK_C5750_2220_Recommended — repo custom land (TDK recommended; prototype-accepted per docs/design.md)
- COUT24 (C5750X7S2A226M280KB): PDU:TDK_C5750_2220_Recommended — repo custom land (TDK recommended; prototype-accepted per docs/design.md)
- COUT25 (C5750X7S2A226M280KB): PDU:TDK_C5750_2220_Recommended — repo custom land (TDK recommended; prototype-accepted per docs/design.md)
- COUT26 (C5750X7S2A226M280KB): PDU:TDK_C5750_2220_Recommended — repo custom land (TDK recommended; prototype-accepted per docs/design.md)
- COUT27 (C5750X7S2A226M280KB): PDU:TDK_C5750_2220_Recommended — repo custom land (TDK recommended; prototype-accepted per docs/design.md)
- COUT28 (C5750X7S2A226M280KB): PDU:TDK_C5750_2220_Recommended — repo custom land (TDK recommended; prototype-accepted per docs/design.md)
- COUT29 (C5750X7S2A226M280KB): PDU:TDK_C5750_2220_Recommended — repo custom land (TDK recommended; prototype-accepted per docs/design.md)
- COUT30 (C5750X7S2A226M280KB): PDU:TDK_C5750_2220_Recommended — repo custom land (TDK recommended; prototype-accepted per docs/design.md)
- COUT31 (C5750X7S2A226M280KB): PDU:TDK_C5750_2220_Recommended — repo custom land (TDK recommended; prototype-accepted per docs/design.md)
- COUT32 (C5750X7S2A226M280KB): PDU:TDK_C5750_2220_Recommended — repo custom land (TDK recommended; prototype-accepted per docs/design.md)
- U3 (TPS259824LNRGER): PDU:TPS25982_RGE0024M — repo custom land
- U4 (TPS259824LNRGER): PDU:TPS25982_RGE0024M — repo custom land
