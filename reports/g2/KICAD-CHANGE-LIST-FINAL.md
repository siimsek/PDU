# G2 — KiCad'e aktarılacak nihai değişiklik listesi

Bu G2 dalında `*.kicad_*` dosyası **değiştirilmedi**. Liste, mevcut şemaya (`simulation/pdu-current.net` export'u, 73 satırlık `hardware/pdu-current-bom.csv`) göre eklenen/değişen her referansı verir. Makine okunur özet: [`design/pdu_v2_spec.yaml`](../../design/pdu_v2_spec.yaml); BOM: [`design/bom-v2.csv`](../../design/bom-v2.csv). Ağ adları export'taki gibidir; `/VOUT` = ham buck barası (raporlarda VRAW). Yeni ağlar (G3 denetimiyle düzeltilmiş): `/VSAFE`, `/P5V_PROT`, `/OVP_SENSE`, `/OVP_REF`, `/REF_NR`, `/OVP_TRIP_N`, `/OVP_Q`, `/ISO_OV`, `/ISO_EN`, `/ISO_GATE`, `/ISO_VCAP`, `/CLR_N`, `/LDO_DELAY`, `/FB_INJ`, `/F1_OUT`.

G1 [`KICAD-CHANGE-LIST.md`](../g1/KICAD-CHANGE-LIST.md) satırlarının yerini bu liste alır (G1 satırları geçmiş kaydı olarak orada kalır).

## 1. Değişen referanslar

| Ref | Eski → yeni | Ağ değişikliği | Gerekçe / hesap |
|---|---|---|---|
| U3, U4 | TPS259824ONRGET → **TPS259824LNRGER** (O = circuit breaker → L = aktif akım sınırlayıcı, 16.9 V OVLO; TPS25982 p.4; G3 denetim E1) | **IN: `/VOUT` → `/VSAFE`** | R01; U3/U4 IN 40.709 V FAIL (G1) → SİM F1 VSAFE ≤11.91 V; ILIM tablosu (p.9) L varyantının 'current limit' eşiği |
| U1, U2 (LM70880) pin 6 BIAS | aynı parça | **BIAS: `/VOUT` → `/VSAFE`** | G3 denetim E2: BIAS abs-max 32 V (DATASHEET p.5); yüksek taraf kısasında `/VOUT` SİM 33.0 V'a çıkar, `/VSAFE` ≤11.94 V. BIAS 10–30 V harici besleme olarak izinli (pin tablosu p.4); ayırıcı açılınca IC iç VCC LDO'suna döner |
| CEFIN1, CEFIN2 | 100n aynı | `/VOUT` → `/VSAFE` | eFuse IN dekuplajı ayırıcı sonrası |
| REN1 | 64.9k aynı | üst uç `/VOUT` → `/VSAFE` | R19: ayırıcı açıkken eFuse'lar da kapanır |
| RILIM1 | 301 Ω → **182 Ω** (TNPW0603182RBXEA) | — | TPS25982 p.9 garantili nokta 7.23–9.07 A; [`POWER-STAGE.md` §5](POWER-STAGE.md) |
| RILIM2 | 604 Ω → **300 Ω** (TNPW0603300RBXEA) | — | garantili 4.36–5.66 A; toplam min 11.59 A ≥7.5 A |
| RUV1 | 180k → **174k** (TNPW0603174KBEEA, 0.1 %) | — | 20 V restart: 17.365–19.623 V ([`power-results.json`](power-results.json)) |
| RUV2 | 10.0k → 10.0k TNPW 0.1 % (TNPW060310K0BEEA) | — | tolerans 1 % → 0.1 % |
| RCOMP | 9.53k → **16.9k** | — | [`LOOP-STABILITY.md`](LOOP-STABILITY.md): PM min 66.9°, GM 11.7 dB |
| CCOMP | 4.7n → **10n** | — | aynı |
| CHF | 47p → **22p** (C0G) | — | aynı |
| RFB1 | 130k ERA3AEB134V aynı | üst uç `/VOUT` → `/FB_INJ` | FRA enjeksiyonu için R_INJ düşük empedanslı `/VOUT` tarafında (G3 denetim E12) |
| D2, D3 | SS34 generic SMA → **SS34-E3/57T, SMC** | — | Vishay SS34 SMC paketlidir (doc 88751); **footprint D_SMA → D_SMC** |
| U5 | "LM74700" → **LM74700QDBVRQ1** | — | TI addendum orderable |
| RS1, RS2 | 7.5m → WSL25127L500FEA | — | 0.134 W / 1 W |
| L1, L2 | 6.8 µH → IHLP4040DZER6R8M01 | — | Vishay doc 34509 |
| COUT1–8 | aynı (C5750X7S2A226M280KB) | — | — |

## 2. Eklenen referanslar

| Ref | Değer / MPN | Ağlar (pin) | Gerekçe |
|---|---|---|---|
| COUT9–COUT16 | 8× C5750X7S2A226M280KB, PDU:TDK_C5750_2220_Recommended | `/VOUT`–`/GND` | O1 bütçesi: 8× → 12.006 V **FAIL**, 16× → 11.941 V (59 mV marj, HESAP) + yük adımı (F3) |
| RRAWBL | 10k CRCW1206 | `/VOUT`–`/GND` | ham bara boşaltma |
| Q2 | CSD19531Q5A (SON 5×6) | S(1–3)=`/VSAFE`, G(4)=`/ISO_GATE`, D(5–8)=`/VOUT` | ortak bara seri ayırıcı |
| U6 | LM74502HDDFR | 1 EN=`/ISO_EN`, 2 GND, 3 NC, 4 VCAP=`/ISO_VCAP`, 5 VS=`/VOUT`, 6 GATE=`/ISO_GATE`, 7 OV=`/ISO_OV`, 8 SRC=`/VSAFE` | sürücü (tOVP_OFF ≤1 µs koşullu) |
| C_ISO_VCAP, C_ISO_VS | 100n / 100n | VCAP–VS, VS–GND | LM74502H p.3–4 |
| R_GS | 100k | `/ISO_GATE`–`/VSAFE` | R13 |
| R_OVT, R_OVB | 8.25k / 2.32k TNPW1206 0.1 % 15 ppm (TNPW12068K25BXEA / TNPW12062K32BXEA) | `/VOUT`→`/OVP_SENSE`→GND | hassas eşik 11.259–11.537 V |
| U7 | TLV3601DCKR | 1 OUT=`/OVP_TRIP_N`, 2 VEE=GND, 3 IN+=`/OVP_REF`, 4 IN−=`/OVP_SENSE`, 5 VCC=`/P5V_PROT` | karşılaştırıcı |
| U8 | REF5025AQDRQ1 | 2 VIN=`/P5V_PROT`, 4 GND, 5 TRIM/NR=`/REF_NR`, 6 VOUT=`/OVP_REF`; 1/8 DNC, 3/7 NC | referans |
| U9 | SN74LVC1G74DCUR | 1 CLK=GND, 2 D=`/P5V_PROT`, 3 Q̄ NC, 4 GND, 5 Q=`/OVP_Q`, 6 CLR=`/CLR_N`, 7 PRE=`/OVP_TRIP_N`, 8 VCC=`/P5V_PROT` | mandal (set-dominant Q) |
| R_Q | 10k | `/OVP_Q`→`/ISO_OV` | mandal → OV pini |
| R_OV2T, R_OV2B | **60.4k / 19.6k** (CRCW060360K4FKEA / CRCW060319K6FKEA) | `/VOUT`→`/ISO_OV`→GND | kaba OV 11.58–13.74 V (bağımsız yol, hassas trip_max + ≥30 mV) |
| R_EN1, R_EN2 | 15k / 10k | `/P5V_PROT`→`/ISO_EN`→GND | 5 V ray geçerli değilse kapı kapalı (R08) |
| U10 | TPS7A1650QDGNRQ1 | 8 IN=`/VIN`, 5 EN=`/VIN`, 1 OUT=`/P5V_PROT`, 3 PG=`/CLR_N`, 4 GND, 7 DELAY=`/LDO_DELAY` | +5V_PROT (R21: VIN'den) |
| C_LDO_IN / C_LDO_OUT / C_LDO_DELAY (DNP) | 1u / 2.2u / 10n | — | TPS7A16 p.3 |
| C_CMP, C_LAT, C_REF_IN, C_REF_OUT, C_REF_NR (DNP) | 100n, 100n, 1u, 1u, 1u | — | dekuplaj |
| R_CLR, C_CLR | 100k / 1u | `/P5V_PROT`→`/CLR_N`→GND | POR ~120 ms |
| SW1 | reset butonu (MPN AÇIK) | `/CLR_N`–GND | R11 |
| R_BL5 | 1k CRCW1206 | `/P5V_PROT`–GND | R07 |
| R_BLS | 4.7k CRCW1206 | `/VSAFE`–GND | R16 |
| D_REV1, D_REV2 | SS34-E3/57T (SMC) | A=`/O1_11V`/`/S2E_11V`, K=`/VSAFE` | R16 OUT ≤ IN+0.3 V |
| R_INJ | 0 Ω CRCW06030000Z0EA (FRA'da 49.9 Ω) | `/VOUT`–`/FB_INJ` | tezgâh FRA (düşük Z tarafı) |

Silinen referans yok. F1, D1, J1–J3, MLCC'ler: MPN [`BOM-OPEN.md`](BOM-OPEN.md).

## 3. Test noktaları ve enjeksiyon padleri (BOM dışı, footprint)

| TP | Ağ | Kullanım |
|---|---|---|
| TP_VBAT, TP_ANODE, TP_VIN | girişler | UVLO / hot-plug |
| TP_VOUT (VRAW), TP_VSAFE, TP_O1, TP_S2E | baralar | F1/T5 enjeksiyon ölçümü |
| TP_ISO_GATE, TP_ISO_OV, TP_OVP_TRIP_N, TP_OVP_Q, TP_CLR_N, TP_OVP_SENSE, TP_OVP_REF, TP_P5V | koruma zinciri | gecikme ve eşik ölçümü |
| TP_FB_INJ_A (`/VOUT`), TP_FB_INJ_B (`/FB_INJ`) | FRA | R_INJ 49.9 Ω takılı iken |
| TP_COMP, TP_EN_BUCK, TP_SW1, TP_SW2, TP_ISNS1±, TP_ISNS2± (Kelvin) | buck | döngü/akım |
| TP_PG_O1, TP_PG_S2E, TP_IMON_O1, TP_IMON_S2E | eFuse | |
| TP_GND ×4 (prob dönüşü, her grup yanında) | GND | |
| **J_OVP_INJ_BUS** (2 pad + GND) | `/VOUT` | harici akım sınırlı OV enjeksiyon fixture'ı; buck devre dışı (EN_BUCK GND jumper) iken |
| JP_EN_BUCK (2 pin jumper, DNP) | `/EN_BUCK`–GND | enjeksiyon sırasında buck'ı kapatma |
| R_OVT DNP opsiyonu yok — artık risk testi için R_OVT sökülerek kaba yol denenir | | |

DNP seçenekleri: C_REF_NR, C_LDO_DELAY, JP_EN_BUCK; R_INJ (0 Ω ↔ 49.9 Ω); RCOMP/CCOMP/CHF tezgâh aralıkları (LOOP-STABILITY).
