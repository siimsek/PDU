# T-022 — İstisnalar

**DRC istisnası: 0.** `PDU.kicad_dru`, `PDU.kicad_pro`, netclass ve UUID hariç tutma değişmedi.

Güç ağı ölçüm ve küçük besleme uçları dar **zone tap** ile bağlandı (T-022 kabulü: öncelik zone tap). Bu 22 şerit mA seviyesi uçlar içindir, güç akımı taşımaları amaçlanmadı. `track_width` kuralı zone görmediği için bu genişlikler tasarımda sabitlendi: 0,8 mm (via'lı uçlar; 0,6 mm via'dan geniş olmalı), bir kolda 0,5 mm ve D_REV/CEFOUT kollarında 1,0 mm.

| Şerit | Net | Katman |
|---|---|---|
| TAP_TP_VOUT | `/VOUT` | B |
| TAP_R_OV | `/VOUT` | B |
| TAP_R_GS | `/VSAFE` | B |
| TAP_TP_VSAFE | `/VSAFE` | In2 |
| TAP_O1_DREV | `/O1_11V` | B |
| TAP_O1_CEFOUT | `/O1_11V` | B |
| TAP_O1_RPG | `/O1_11V` | B |
| TAP_O1_TP_A | `/O1_11V` | B |
| TAP_O1_TP_B | `/O1_11V` | In2 |
| TAP_S2E_DREV | `/S2E_11V` | F |
| TAP_S2E_CEFOUT | `/S2E_11V` | F |
| TAP_S2E_RPG | `/S2E_11V` | F |
| TAP_S2E_TP | `/S2E_11V` | B |
| TAP_TP_ANODE | `/ANODE` | B |
| TAP_U5 | `/ANODE` | B |
| TAP_U5B | `/ANODE` | B |
| TAP_U5A | `/ANODE` | B |
| TAP_ANODE_N | `/ANODE` | B |
| TAP_ANODE_NW | `/ANODE` | B |
| TAP_VIN_E | `/VIN` | B |
| TAP_VIN_E2 | `/VIN` | B |
| TAP_VIN_E3 | `/VIN` | B |
