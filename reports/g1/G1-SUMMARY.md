# G1 AI analiz özeti

Dal `wp/g1-ai-analysis`; 6S LiPo PDU için hesap/simülasyon/karar ve sonraki faz girdileri. `*.kicad_*` değiştirilmedi.

| Madde | Sonuç | Etiket | Kanıt dosyası | Durum |
|---|---|---|---|---|
| **G1 kapanış mimarisi** | Ortak bara seri ayırıcı (a) önerildi: COUT (`VOUT_RAW`) ile U3/U4 IN (`VOUT_PROT`) arasında tek latch-off back-to-back ayırıcı. Yedek: her eFuse önüne ayrı ayırıcı. Eski "U3 sonrası O1 ayırıcı" SUPERSEDED (U3/U4 IN 40.709 V'tan korumaz). Surge-stopper/HV eFuse (b) elendi. | SİM/HESAP/AÇIK | `OVP-UVLO-DECISION.md` (G1 kapanış kararı); `KICAD-CHANGE-LIST.md`; `USER-DECISIONS.md` | fiziksel kabul yok; kullanıcı girdileri bekleniyor |
| Gereksinimler | 20–26 V; 11 V/7 A; capacity7.5 A; O1≤12.0 V; ports not measured | REPO/AÇIK | `REQUIREMENTS.md` | frozen |
| Buck/FB | ΔIL2.916 A; phase peak5.583 A assumption; FB10.8333–11.1605 V; Vishay Isat13.5 A | HESAP/DATASHEET/VARSAYIM | `calc-results.json/.md` | phase share and exact L BOM approval open |
| Loop/UVLO | RCOMP sensitivity10.0–26.1k; 174k/10k UVLO upper19.69 V before leakage/TCR | VARSAYIM/AÇIK | `calc-results.json; OVP-UVLO-DECISION.md` | FRA and battery cutoff policy open |
| O1 OVP | Original Family 2 18.8039 V FAIL retained; MPN chain is lab candidate only. Divider max 11.6232 V exceeds prior 11.46 V target; combined model O1 11.6900/11.6857 V; Ceff screen 10.332 µF > 10 µF. S2E 19.0809 V is within its sourced 9–28 V powered range, not a transient abs-max | SİM/HESAP/FAIL/AÇIK | `OVP-ENGINEERING-RESULT.md; PR2-REVIEW-6683120653.md` | current envelope, physical Ceff, FET SOA and measured hardware turnoff open |
| Shared eFuse IN fault | Existing common VOUT reaches 40.709 V at U3/U4 IN; >24 V=731.759 µs, >30 V=161.124 µs. Common isolator screen keeps IN at 11.62–11.64 V and O1≤11.561 V in model only | SİM/DATASHEET/AÇIK | `PR2-REVIEW-6683120653.md; shared-bus-ovp-results.json; sim/family2-shared-bus-duration-legacy-overload-final-measures.log` | switch timing, FET SOA, input-side Ceff, parasitics and physical test open |
| Sense clamp / rail loss | Original divider 10.956 mA at 40.709 V/VCC=0 **FAIL**; new resistor screen 2.276 mA max; unpowered rail model 0.964 V (not latch-safe proof). At assumed 85C: LDO Tj about 92.75C at 11V, 111.80C at 26V, 130.49C if 40.709V were sustained; this exceeds the conservative 125C screen but is below TI 150C operating max. Fault-pulse Tj OPEN. | DATASHEET/HESAP/SIM/FAIL/OPEN | `PR2-REVIEW-6692825552.md; fail-safe-audit-results.json; sense-failsafe-results.json` | thermal transient, board thetaJA, comparator/latch/gate fail-off and physical proof open |
| Latch/driver/gates | SN74LVC1G74 Q is unspecified below 1.65V; LTC7001 INP 1Mohm pull-down and UVLO-to-TGDN path are datasheet-backed, but CLR/ARM/PG chain and per-FET G-S bleed are not wired or measured | DATASHEET/OPEN | `PR2-REVIEW-6692825552.md; fail-safe-audit-results.json` | driver-side rail-valid clamp, PG timing, Qg/two-gate turnoff and physical rearm test open |
| eFuse input loss | TPS259824O OUT max is VIN+0.3V (abs max min(30V, VIN+0.3V)); 11V precharge at VIN=0 would exceed the stated limit by 10.7V if retained. Reverse blocking is not specified; -44.547uC is an ideal bilateral-SW artifact | DATASHEET/OPEN | `PR2-REVIEW-6692825552.md; fail-safe-audit-results.json` | real output decay/reverse path requires vendor confirmation or hardware test |
| eFuse/protection | ILIM nominal4.9605/2.5272 A; sum7.487717 A <7.5 A by12.283 mA FAIL; legacy 12.006 A combined load reclassified overload; F1/I²t and Q1 SOA open | HESAP/SİM/FAIL/AÇIK | `calc-results.json; PR2-REVIEW-6683120653.md` | measured port split and source/cable/MPN evidence needed |
| Targeted sim | 5/5 families complete; 3 model gates pass; model FAIL: family2_buck_highside_short, family4_load_step_comp_corners; no physical proof | SİM | `SIMULATION-RESULTS.md` | family2/4 FAIL retained |
| Tests | G1 kapanışında `python -m pytest -q`: 63 passed, exit 0 (önceki kayıt: 42/42); includes fail-safe state, rail source, eFuse input-loss and fixture checks | HESAP | `TEST-RESULTS.md; analysis/test_ovp_fail_safe_audit.py` | behavioral and logic tests only; no hardware acceptance |
| Prior WP1/WP2 | WP1 4 ESL incomplete + N-01; WP2 historical 161/69/6, no new electrical run | SİM/FAIL/AÇIK | `PREVIOUS-WP-COMPARISON.md` | all open findings retained |
| BOM | 73/73 rows reviewed; exact MPN/stock/package gaps listed | DATASHEET/AÇIK | `bom-verification.csv; BOM-OPEN-ITEMS.md` | procurement open |
| Next phase | T0–T6 and schematic/PCB change list ready | HESAP/VARSAYIM | `BENCH-ACCEPTANCE.md; KICAD-CHANGE-LIST.md` | transfer input |

## Fiziksel kabul olmadan kapanmayanlar

- O1 anlık tepe ≤12.0 V OVP hata enjeksiyonu; mevcut 16.9 V eFuse FAIL.
- U3/U4 ortak IN pinlerini 30 V abs-max altında tutacak gerçek koruma anahtarı, gate/FET gecikmesi/SOA/Ceff ve eFuse current-limit transienti fiziksel olarak doğrulanmadı.
- WP1 dört ESL tamamlanmaması ve N-01 üst sınırı; WP2 katı tarihsel 69 FAIL / 6 eksik.
- Gerçek 7 A/7.5 A yük profili, iki faz current sharing ve 20 V yeniden kalkış.
- Döngü Bode: PM≥45°, GM≥6 dB ve transient testi.
- F1/kablo/batarya kısa devre akımı, DC kesme/I²t, TVS/Q1 SOA koordinasyonu.
- Kart termal dengesi, konektör/kablo, footprint ve üretim land/stencil.
- MPN/stok ve tasarım ortam sıcaklığı.

## Benden gereken girdiler/PDF'ler

**G1 kapanış:** Öncelikli en çok 6 karar/girdi [`USER-DECISIONS.md`](USER-DECISIONS.md) içindedir; aşağıdaki liste geçmiş kaydı olarak korunur.

1. O1 ve S2E ölçülmüş startup/continuous/peak akım dalga şekilleri ve yük bölüşümü.
2. Batarya iç direnci/kısa devre akımı, hücre üretici cutoff'u, kablo uzunluğu/kesiti/konnektör mating seti.
3. Ortam ve enclosure sıcaklığı, airflow ve kart copper stackup/fabricator minimum plating.
4. F1/holder, shunt RS, IHLP inductor, TVS ve generic C/R için onaylı MPN/vendor PDFs veya AVL.
5. OVP için izin verilen recovery/latch/reset davranışı ve 10 µF port capacitance minimum tolerans/DC-bias datasheet.
6. O1 ≤12 V sınırında ölçüm bandwidth/probe uncertainty payının kullanıcı tarafından onayı.
