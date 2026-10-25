# WP2 2026-10-25-uvlo – KiCad aktarım adımları (UYGULANMADI)

Bu paket hiçbir `.kicad_sch`, `.kicad_pcb` veya `.kicad_pro` dosyasını, ana BOM'u ya da baseline netlist'i değiştirmez. Adımları kullanıcı KiCad'de uygulamalıdır. **Önkoşul: WP1 (o1-ovp rev3) aktarımı yapılmış olmalıdır**, çünkü V5_OVP (U11) ve VREF_OVP (U12) buradan beslenir.
Referanslar: `simulation/proposals/2026-10-25-uvlo/pdu-uvlo-block.inc`, `pdu-circuit-uvlo.inc`, `hardware/proposals/2026-10-25-uvlo/candidate-bom.csv`.
KiCad sembol, ayak izi ve ped eşleşmeleri bu pakette **doğrulanmadı** (KiCad dosyası açılmadı).

## 1. Baseline değişikliği
1. **RUV1 (180k, VIN → EN_BUCK): DNP.** Ayak izi kalır, parça dizilmez. BOM'da "DNP" olarak işaretlenir.
   Not: RUV1 geri takılırsa baseline davranışı geri gelir ve FAIL verir (regresyon `reg-baseline-180k10k-*`).
2. **RUV2 (10,0k, EN_BUCK → GND):** değişmez. Artık RDEN/RUV2 bölücüsünün alt bacağıdır ve U20 beslemesizken EN'i aşağı çeker.
3. EN_BUCK ağı, U1 ve U2 LM70880 EN/UVLO pinlerine (netlist'te XU1/XU2 alan 9) bağlı kalır. Pin numarasını SNVSBX7A pin tablosundan ayrıca doğrulayın.

## 2. Yeni ağlar
| Ağ | Bağlananlar |
|---|---|
| S_UV | RTU.2, RBU.1, RXU.1, CFU.1, U20.3 (1IN+) |
| REFD_UV | RR1U.2, RR2U.1, CRU.1, U20.2 (1IN−) |
| SWD_UV | RXU.2, U21.1 (D) |
| OUTA_UV | U20.1 (1OUT), U21.4 (SEL), RTT.1, RDIS.2 |
| T_UV | RTT.2, CTT.1, DTT anot, RHB.2, U20.5 (2IN+) |
| DTK_UV | DTT katot, RDIS.1 |
| KTH_UV | RK1.2, RK2.1, CK.1, U20.6 (2IN−) |
| OUTB_UV | U20.7 (2OUT), RHB.1, RDEN.1 |
| EN_BUCK (mevcut) | RDEN.2, RUV2.1, U1/U2 EN/UVLO (RUV1.2 DNP) |
| VIN (mevcut) | RTU.1 |
| V5_OVP (WP1) | U20.8 (VCC), U21.5 (VDD), RK1.1, C20.1, C21.1 |
| VREF_OVP (WP1) | RR1U.1 |
| GND | RBU.2, RR2U.2, CFU.2, CRU.2, CTT.2, RK2.2, CK.2, C20.2, C21.2, U20.4, U21.2 (S), U21.3 (GND), RUV2.2 |

## 3. Pin tabloları
### U20 TLV3202AIDGKR (VSSOP-8, DGK) – SBOS561C pin tablosu
| Pin | Ad | Ağ |
|---|---|---|
| 1 | OUT1 | OUTA_UV |
| 2 | IN1− | REFD_UV |
| 3 | IN1+ | S_UV |
| 4 | GND | GND |
| 5 | IN2+ | T_UV |
| 6 | IN2− | KTH_UV |
| 7 | OUT2 | OUTB_UV |
| 8 | VCC | V5_OVP (C20 100 nF pinin yanında) |

### U21 TMUX1102DBVR (SOT-23-5, DBV) – SCDS410D pin tablosu, mantık tablosu s.19 (SEL = 0 → AÇIK)
| Pin | Ad | Ağ |
|---|---|---|
| 1 | D | SWD_UV |
| 2 | S | GND |
| 3 | GND | GND |
| 4 | SEL | OUTA_UV |
| 5 | VDD | V5_OVP (C21 100 nF pinin yanında) |
Ped numaralarını TI DBV/DGK çizimleriyle karşılaştırın. SPICE düğüm sırası pin numarası değildir.

### Pasifler (iki uçlu: .1 → .2)
| Ref | Değer / MPN | .1 | .2 |
|---|---|---|---|
| RTU | 39,2k ERA-3ARB3922V | VIN | S_UV |
| RBU | 8,87k ERA-3ARB8871V | S_UV | GND |
| RXU | 90,9k ERA-3ARB9092V | S_UV | SWD_UV |
| CFU | 100 nF X7R ≥ 16 V | S_UV | GND |
| RR1U | 10,0k ERA-3ARB1002V | VREF_OVP | REFD_UV |
| RR2U | 46,4k ERA-3ARB4642V | REFD_UV | GND |
| CRU | 10 nF | REFD_UV | GND |
| RTT | 11,0k ERA-3ARB1102V | OUTA_UV | T_UV |
| CTT | 10 µF GRM31CR71E106KA12L | T_UV | GND |
| DTT | 1N4148WS-7-F (SOD-323) | anot = T_UV | katot = DTK_UV |
| RDIS | 100 Ω %1 | DTK_UV | OUTA_UV |
| RHB | 1 M RC0603FR-071ML | OUTB_UV | T_UV |
| RK1 | 10,0k ERA-3ARB1002V | V5_OVP | KTH_UV |
| RK2 | 40,2k ERA-3ARB4022V | KTH_UV | GND |
| CK | 10 nF | KTH_UV | GND |
| RDEN | 10k %1 | OUTB_UV | EN_BUCK |
| C20 / C21 | 100 nF X7R | V5_OVP | GND |

## 4. Yerleşim notları
- RTU'yu U20'ye yakın koyun. S_UV yüksek empedanslıdır (≈ 7,2 kΩ), anahtarlama düğümlerinden (SW_PH1/2) ve indüktörlerden uzak tutun. CFU, U20 pin 3'e yakın olmalıdır.
- RBU, RR2U ve RK2 dönüşleri U20 GND pinine giden sessiz sinyal toprağına bağlanmalıdır (REF35 GND ile aynı nokta).
- ERA-3ARB lehim ısısı: ±%0,1 bütçeye dahil. Elle lehimlemede B-U7 testini yapın.
- U11 yük artışı: U20 + U21 ≤ ~0,2 mA (65 µA/kanal maks + bölücüler). REF35 ek yükü 73,5 µA.
- ERC: OUTA_UV ve OUTB_UV push-pull çıkıştır. Başka sürücü bağlanmamalıdır.

## 5. Doğrulama (aktarım sonrası)
1. KiCad'de netlist'i dışa aktarın ve §2 tablosuyla ağ ağ karşılaştırın.
2. Netlist'ten `pdu-circuit.inc` yeniden üretilirse `simulation/proposals/2026-10-25-uvlo/run_uvlo.py` + `verify_uvlo.py` tekrar koşulmalıdır.
3. Tezgâh testleri: `BENCH-TEST.md`.
