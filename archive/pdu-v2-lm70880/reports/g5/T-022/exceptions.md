# T-022 — İstisnalar

**DRC istisnası: 0.** `PDU.kicad_dru`, `PDU.kicad_pro`, netclass değişmedi; `drc_exclusions` eklenmedi.

Dar uçlar **zone tap** ile bağlandı (T-022 kabulü). `track_width` kuralı zone görmediği için genişlikler tasarımda sabit: 0,8 mm (via'lı uçlar, 0,6 mm viadan geniş olmalı), bir kolda 0,5 mm, D_REV/CEFOUT kollarında 1,5 mm. Kesit ölçümü ve IPC taraması: route-review.md.

| Şerit | Net | Katman | Akım sınıfı |
|---|---|---|---|
| TAP_TP_VOUT | `/VOUT` | B | mA seviyesi uç (VARSAYIM): TP, bölücü, LDO, pull-up veya Kelvin |
| TAP_R_OV | `/VOUT` | B | mA seviyesi uç (VARSAYIM): TP, bölücü, LDO, pull-up veya Kelvin |
| TAP_R_GS | `/VSAFE` | B | mA seviyesi uç (VARSAYIM): TP, bölücü, LDO, pull-up veya Kelvin |
| TAP_TP_VSAFE | `/VSAFE` | In2 | mA seviyesi uç (VARSAYIM): TP, bölücü, LDO, pull-up veya Kelvin |
| TAP_O1_DREV | `/O1_11V` | B | D_REV1 diyot akımı, 3 A değer |
| TAP_O1_CEFOUT | `/O1_11V` | B | CEFOUT1 kapasitif, geçici akım doğrulanamadı |
| TAP_O1_RPG | `/O1_11V` | B | mA seviyesi uç (VARSAYIM): TP, bölücü, LDO, pull-up veya Kelvin |
| TAP_O1_TP_A | `/O1_11V` | B | mA seviyesi uç (VARSAYIM): TP, bölücü, LDO, pull-up veya Kelvin |
| TAP_O1_TP_B | `/O1_11V` | In2 | mA seviyesi uç (VARSAYIM): TP, bölücü, LDO, pull-up veya Kelvin |
| TAP_S2E_DREV | `/S2E_11V` | F | D_REV2 diyot akımı, 3 A değer |
| TAP_S2E_CEFOUT | `/S2E_11V` | F | CEFOUT2 kapasitif, geçici akım doğrulanamadı |
| TAP_S2E_RPG | `/S2E_11V` | F | mA seviyesi uç (VARSAYIM): TP, bölücü, LDO, pull-up veya Kelvin |
| TAP_S2E_TP | `/S2E_11V` | B | mA seviyesi uç (VARSAYIM): TP, bölücü, LDO, pull-up veya Kelvin |
| TAP_TP_ANODE | `/ANODE` | B | mA seviyesi uç (VARSAYIM): TP, bölücü, LDO, pull-up veya Kelvin |
| TAP_U5 | `/ANODE` | B | mA seviyesi uç (VARSAYIM): TP, bölücü, LDO, pull-up veya Kelvin |
| TAP_U5B | `/ANODE` | B | mA seviyesi uç (VARSAYIM): TP, bölücü, LDO, pull-up veya Kelvin |
| TAP_U5A | `/ANODE` | B | mA seviyesi uç (VARSAYIM): TP, bölücü, LDO, pull-up veya Kelvin |
| TAP_ANODE_N | `/ANODE` | B | mA seviyesi uç (VARSAYIM): TP, bölücü, LDO, pull-up veya Kelvin |
| TAP_ANODE_NW | `/ANODE` | B | mA seviyesi uç (VARSAYIM): TP, bölücü, LDO, pull-up veya Kelvin |
| TAP_VIN_E | `/VIN` | B | mA seviyesi uç (VARSAYIM): TP, bölücü, LDO, pull-up veya Kelvin |
| TAP_VIN_E2 | `/VIN` | B | mA seviyesi uç (VARSAYIM): TP, bölücü, LDO, pull-up veya Kelvin |
| TAP_VIN_E3 | `/VIN` | B | mA seviyesi uç (VARSAYIM): TP, bölücü, LDO, pull-up veya Kelvin |
| TAP_ISNS1 | `/ISNS1` | B | mA seviyesi uç (VARSAYIM): TP, bölücü, LDO, pull-up veya Kelvin |
| TAP_U1_VOUT | `/VOUT` | B | mA seviyesi uç (VARSAYIM): TP, bölücü, LDO, pull-up veya Kelvin |
| TAP_ISNS2 | `/ISNS2` | B | mA seviyesi uç (VARSAYIM): TP, bölücü, LDO, pull-up veya Kelvin |
| TAP_U2_VOUT | `/VOUT` | B | mA seviyesi uç (VARSAYIM): TP, bölücü, LDO, pull-up veya Kelvin |
