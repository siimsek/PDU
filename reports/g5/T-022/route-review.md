# T-022 — Güç yolları (D-010 geçerli kısımları + D-011, R-018 Tur 1 düzeltmeleri)

**Durum: Done; R-020 Tur 2 revizyonu.** T-023 faz 1 Kelvin paralelliği için RS1 180° döndürüldü ve RS1 güç yolu (`F_VOUT_RS1`, B.Cu bara, L1.2 → RS1.1, U1 ölçüm kolları) bu kartın betiğiyle yeniden üretildi; R-021 ile U1.11 ve U2.11 sense vialarının yeri ve `F_VOUT_RS2` konturu değişti, sense vialar güç bakırından ayrıldı; önceki kayıt git geçmişinde. KiCad 10.0.7: DRC hatası **0**, parite **0**, boş kart DRC hatası **0**. Güç ağlarında açık uç yalnız T-023'e devredilen Kelvin, FB ve gate uçlarındadır.

Kaynak: [`scripts/pcb_route_power.py`](../../../scripts/pcb_route_power.py), T-021 kartından üretilir. Ham çıktı: [power-route-audit.json](power-route-audit.json), [route-items.json](route-items.json), [drc.json](drc.json), [drc-empty.json](drc-empty.json). Netclass, `PDU.kicad_dru` ve `PDU.kicad_pro` değişmedi.

Uyarılar: `{'warning:via_dangling': 6, 'warning:silk_overlap': 2}`. `via_dangling`, zone tap bağlama vialarıdır (ve D_REV1.2 çevresindeki iki via); bağlantı denetiminde açık uç vermez.

Boş kart DRC: ayak izleri ve tüm bakır çıkarılmış kopya (T-013 anlamı). Aynı dosyayı bağımsız denetlemek için: `python.exe scripts/pcb_route_power.py --audit --empty-board <dosya>`, sonra `kicad-cli pcb drc --severity-all --refill-zones <dosya>` (dosya `PDU.kicad_pro` ve `PDU.kicad_dru` ile aynı dizinde olmalı).

## R-018 Tur 1 yanıtı

**1. TP_SW1/TP_SW2 (engelleyici):** TP_SW1 (45,4; 71,6), TP_SW2 (38,1; 12,4) konumuna taşındı; SW dökümüne 2,15 mm'lik kısa dolgu kolu ile bağlı. SW bakırı anten gibi uzamadı. Her iki pad üstten erişilebilir; yanında yüksek bobin gövdesi olduğu için fiziksel prob erişimi **doğrulanamadı** (kart yok).

**2. ISNS güç yolu (engelleyici):** L1.2 → RS1.1 ve L2.2 → RS2.1 2,6 mm izle bağlıydı; açık kalan U1.11 ve U2.11 denetleyici uçları artık RS1.1/RS2.1 iç kenarına bağlı. Aynı turda U1.12/U2.12 de RS1.2/RS2.2 iç kenarına ayrı kolla bağlandı (çift, güç akımı taşımaz, aralarında 0,6 mm HV).

**3. CEFIN2 (engelleyici):** U4 yerindeyken F.Cu bağlantı 0,6 mm HV kuralına sığmıyordu ve yalnız via ile bağlı kalıyordu. Bu nedenle U4 1,15 mm doğuya taşındı, CEFIN2 U4 IN 1–3 / GND 4–5 pinlerinin batısına (104,99; 41,2) alındı; CEFIN1 ile aynı düzen. IN yolu via'sız F.Cu dökümü.

| Döngü (geometrik yaklaşık) | Alan (mm²) | Pin → kapasitör (mm) | GND → pin (mm) | Dönüş |
|---|---:|---:|---:|---|
| U3/CEFIN1 | 2,08 | 1,51 | 1,48 | F.Cu track to GND pins 4/5 |
| U4/CEFIN2 | 2,08 | 1,51 | 1,48 | F.Cu track to GND pins 4/5 |

Endüktans ölçülmedi; bu tablo geometrik karşılaştırmadır (TPS25982 §11.1, IN/GND yakınlığı ve küçük döngü niyeti).

**Zone tap geçici akım:** D_REV ve CEFOUT kolları 1,5 mm'ye genişletildi. Ölçülen bakır: 1,52 / 1,52 mm. HESAP: 3 A D_REV değeri için IPC-2221 uyumu (routing-g2 sabitleri) 1,0 mm; 40,0 mm kol için 14,6 mΩ, 43,7 mV. CEFOUT geçici akım tepe değeri simüle edilmedi: **doğrulanamadı**. TP, bölücü, LDO ve pull-up uçları mA seviyesindedir (VARSAYIM).

**Neck açıklığı (gerçek kenar):**

| Çift | Kenar aralığı (mm) | HV kuralı (mm) |
|---|---:|---:|
| U3.16 VSAFE neck <-> U3.17 O1 stub | 0,602 | 0,6 |
| U4.16 VSAFE neck <-> U4.17 S2E stub | 0,602 | 0,6 |

Pay çok küçüktür; DRC temizdir. Üretici toleransı **doğrulanamadı** (DFM varsayımı PCB-HANDOFF §7, min 0,15/0,15 mm).

## Q2 ve yerel L3 (D-011)

- Q2 90°; T-021'in 12 viası Q2 ile taşındı. L3_VSAFE konturu 90° kaynak via alanına göre yeniden çizildi, REN1 için y 3,5'e uzatıldı. L3_VOUT konturu değişmedi.
- Q2–U6 gate: **5,469 mm**, 0,4 mm, F.Cu, sınır 10,0 mm. Gate döngüsü ve seri elemanlar T-023.

## Ağlar

| Ağ | Tracks | Genişlik (mm) | Katman | Uzunluk (mm) | Via | Zone | Açık uç | Nerede kapanır |
|---|---:|---|---|---:|---:|---:|---:|---|
| `/ANODE` | 6 | 0,5, 3,3 | B.Cu, F.Cu | 13,62 | 17 | 2 | 0 | — |
| `/VIN` | 6 | 0,25 | F.Cu | 6,33 | 45 | 4 | 0 | — |
| `/VOUT` | 16 | 0,25, 5,5, 7,0 | B.Cu, F.Cu | 139,49 | 132 | 7 | 6 | T-023: U11.1/U12.1 INA296 Kelvin, TP_ISNS1N/2N, R_INJ, TP_FB_INJ_A |
| `/VSAFE` | 7 | 0,25, 5,5 | B.Cu, F.Cu | 14,78 | 43 | 7 | 0 | — |
| `/O1_11V` | 5 | 0,25, 5,3 | B.Cu, F.Cu | 27,16 | 37 | 4 | 0 | — |
| `/S2E_11V` | 5 | 0,25, 3,3 | F.Cu | 15,6 | 2 | 3 | 0 | — |
| `/SW_PH1` | 0 | — | — | 0 | 0 | 1 | 0 | — |
| `/SW_PH2` | 0 | — | — | 0 | 0 | 1 | 0 | — |
| `/ISNS1` | 3 | 0,25, 2,6 | F.Cu | 9,16 | 2 | 1 | 2 | T-023: U11.8 INA296 Kelvin and TP_ISNS1P |
| `/ISNS2` | 4 | 0,25, 2,6 | F.Cu | 8,65 | 2 | 1 | 2 | T-023: U12.8 INA296 Kelvin and TP_ISNS2P |
| `/ISO_GATE` | 3 | 0,4 | F.Cu | 5,0 | 0 | 0 | 2 | T-023 R_GS and TP_ISO_GATE (Q2-U6 gate itself is routed) |

`/VBAT` ağı netlistte yoktur.

## Via sayıları

| Geçiş | Via | routing-g2 hedefi | Sağlandı |
|---|---:|---:|---|
| Q2 drain (/VOUT) | 17 | 15 | evet |
| Q2 source (/VSAFE) | 15 | 15 | evet |
| U3 OUT -> B.Cu (/O1_11V) | 24 | 19 | evet |
| J1/Q1 (/ANODE) | 12 | 9 | evet |
| RS1 output (/VOUT) | 16 | 15 | evet |
| RS2 output (/VOUT) | 16 | 15 | evet |
| /VOUT bus -> L3 (COUT pin 1 under the bus) | 16 | 15 | evet |

CIN → L3: U1 tarafı 12, U2 tarafı 12 via (hedef 9). Faz ağları katman değiştirmediği için 12 via hedefi bu yollarda uygulanmadı. Via ölçüsü 0,6/0,3 mm ve via-in-pad **VARSAYIM**.

## Döküm kesitleri

`track_width` kuralı döküm görmez; gerçek dolgu üzerinde ölçüldü.

| Kesit | Bakır (mm) | Alt sınır (mm) | Karşılıyor |
|---|---:|---:|---|
| /S2E_11V U4 -> D3 channel | 3,38 | 2,97 | evet |
| /S2E_11V east drop | 4,06 | 2,97 | evet |
| /O1_11V pins -> field | 5,48 | 4,76 | evet |
| /VIN CIN3/4 -> U1 | 3,82 | 2,94 | evet |
| /VIN CIN7/8 -> U2 | 3,82 | 2,94 | evet |
| /SW_PH1 U1 -> L1 | 2,78 | 2,35 | evet |
| /SW_PH2 U2 -> L2 | 2,76 | 2,35 | evet |
| /VOUT RS2.2 -> field | 5,52 | 4,92 | evet |
| /VOUT RS1.2 -> field | 5,52 | 4,92 | evet |
| /VSAFE under U3 -> U4 | 6,56 | 4,92 | evet |
| /VSAFE around CEFIN2 GND via (sum of both sides) | 5,24 | 4,92 | evet |
| /O1_11V D_REV1 branch | 1,52 | 1,0 | evet |
| /S2E_11V D_REV2 branch | 1,52 | 1,0 | evet |

D_REV kollarının alt sınırı sınıf değil 3 A IPC ölçüsüdür. 0,25–0,5 mm izler yalnız ince adımlı pad necklerinde (neck audit ihlali 0).

## Sıcak döngü (geometrik yaklaşık)

geometrik yaklaşık: pad merkezleri arası düzlem poligonu, shoelace; akım çözümü değil. D-010'un akım çözümlü yöntemi uygulanmadı; gerçek döngü alanı **doğrulanamadı**.

| Döngü | Alan (mm²) | VIN pin → C (mm) | C GND → PGND (mm) | Dönüş |
|---|---:|---:|---:|---|
| U1/CIN1 | 7,33 | 2,7 | 2,7 | F.Cu PGND pour |
| U1/CIN2 | 16,98 | 6,23 | 6,23 | F.Cu PGND pour |
| U1/CIN3 | 11,5 | 2,65 | 7,03 | L2 GND via (F.Cu cap pad to L2) |
| U1/CIN4 | 18,78 | 6,2 | 10,5 | L2 GND via (F.Cu cap pad to L2) |
| U2/CIN5 | 7,33 | 2,7 | 2,7 | F.Cu PGND pour |
| U2/CIN6 | 16,98 | 6,23 | 6,23 | F.Cu PGND pour |
| U2/CIN7 | 11,5 | 2,65 | 7,03 | L2 GND via (F.Cu cap pad to L2) |
| U2/CIN8 | 18,78 | 6,2 | 10,5 | L2 GND via (F.Cu cap pad to L2) |
| U3/CEFIN1 | 2,08 | 1,51 | 1,48 | F.Cu track to GND pins 4/5 |
| U4/CEFIN2 | 2,08 | 1,51 | 1,48 | F.Cu track to GND pins 4/5 |

## Düzlemler

| Düzlem | Ada | En büyük dolu alan (mm²) |
|---|---:|---:|
| L2_GND | 1 | 9287,11 |
| L4_GND | 10 | 7558,39 |
| L3_VIN | 1 | 3571,31 |
| L3_VOUT | 1 | 2038,8 |
| L3_VSAFE | 1 | 1667,15 |

L2 tek ada. L4 ikincil GND, B.Cu güç yolları nedeniyle 10 adaya ayrıldı; dönüş referansı L2'dir.

## T-023'e açık devir (kart Kapsam eki)

`/VOUT`: U11.1, U12.1, TP_ISNS1N, TP_ISNS2N, R_INJ, TP_FB_INJ_A. `/ISNS1`: U11.8, TP_ISNS1P. `/ISNS2`: U12.8, TP_ISNS2P. `/ISO_GATE`: R_GS.1, TP_ISO_GATE. Kart genelinde 199 açık uç var; `/GND` sinyal padleri ve sinyal ağları T-023'tedir.

## Olgu / hesap / varsayım

- **KiCad çıktısı:** DRC, parite ve bağlantı. Simülasyon veya fiziksel kanıt değildir.
- **HESAP:** kesitler, uzunluklar, IPC taraması, geometrik döngü alanları. Akım, ısınma ve 50 mV düşüm bu kartta ölçülmedi.
- **VARSAYIM:** 1 oz tüm katman, via-in-pad dolgulu, via akım paylaşımı. Doğrulanamadı.
