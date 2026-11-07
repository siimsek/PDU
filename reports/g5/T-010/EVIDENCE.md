# T-010 + T-009 — şema blokları B5 (koruma ayırıcı) ve B4 (faz OC zinciri) kanıtı

Düzenleme: `python scripts/sch_edit_b5.py` ardından `python scripts/sch_edit_b4.py` (B1–B3 uygulanmış main şeması üzerinde; ortak yardımcı `scripts/sch_place.py`: kütüphane sembolünü şema önbelleğine kopyalar, her pine spec ağının yerel etiketini, NC pinlere no-connect koyar — tel çizilmez). KiCad 10.0.7.

| Kontrol | Komut | Sonuç |
|---|---|---|
| ERC | `kicad-cli sch erc --format json` → [erc.json](erc.json) | **0 ihlal** (B5 tek başına 3 ihlal veriyordu: B4'e giden /OVP_BUS_N, /OVP_TRIP_N; iki blok birlikte 0) |
| Netlist | `kicad-cli sch export netlist --format kicadsexpr` → [netlist.net](netlist.net) | ham çıktı |
| Spec farkı | `python analysis/check_consistency.py --schematic B1 B2 B3 B4 B5` → [check-B1-B5.txt](check-B1-B5.txt) | B1–B5 **fark 0** (footprint, MPN, sayısal değer, pin→ağ) |
| Blok dışı | main netlistiyle karşılaştırma | pin→ağ değişikliği **0**; eklenen 42 ref (B5 30 + B4 12) |

## Eklenenler
- **B5 (30):** U6 LM74502HDDFR, Q2 CSD19531Q5A, U7 TLV3601DCKR, U8 REF5025AD (stok), U9 SN74LVC1G74DCUR, U10 TPS7A1650QDGNRQ1; RRAWBL, R_GS, C_ISO_VCAP/VS, R_OVT/R_OVB, C_CMP, C_REF_IN/OUT/NR, C_LAT, R_CLR, C_CLR, SW1, R_Q, R_OV2T/R_OV2B, R_EN1/R_EN2, C_LDO_IN/OUT/DELAY, R_BL5, R_BLS. Yer: iki faz bloğu arasındaki şerit (x 165–340, y 180–215 mm).
- **B4 (12):** U11/U12 INA296A2QDGKRQ1, U13/U14 TLV3601DCKR, U15 74LVC1G11 (stok sembol, SN74LVC1G11DBVR), R_OCT/R_OCB, C_INA1/2, C_OCC1/2, C_AND. Yer: sayfa alt ortası (x 150–270, y 368–390 mm).
- Semboller: T-017 (R-008 ONAY) + KiCad stok (REF5025AD, CSD19531Q5A, 74LVC1G11, SW_Push).

## Spec değişikliği
- **Q2 footprint `Package_SON:VSONP-8-1EP_5x6_P1.27mm` → `Package_TO_SOT_SMD:TDSON-8-1`**: stok VSONP pad numaraları 1 = S (×3), 2 = G, 3 = D (×5); stok CSD19531Q5A sembolü 1–3 S, 4 G, 5 D → eski eşleşmede kapı pini kaynak pad'ine düşerdi. TDSON-8-1 (KiCad'in bu sembol için varsayılanı) pad 1–5 ile tutarlı. Land'in TI CSD19531Q5A önerisine uyumu **R-009**'da doğrulanacak.
- U10 termal pad pin 9 → GND (T-017).

## Görsel
Entegrelerde Reference/Value gövde üstü/altında; pasiflerde etiket–yazı yakınlığı kalıyor → T-012 (antet ve görsel düzen) ve R-002 görsel kontrol listesi.
