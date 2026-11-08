# T-022 — Güç yolları (D-010 geçerli kısımları + D-011)

**Durum: T-022 tamamlanmadı (InProgress).** KiCad 10.0.7: DRC hatası **0**, parite **0**, boş kart DRC hatası **0**. Ana güç yolları bağlı; ancak aşağıdaki açık uçlar kapanmadan D-011'e göre rota tamamlanmış sayılmaz.

Kaynak: [`scripts/pcb_route_power.py`](../../../scripts/pcb_route_power.py), T-021 kartından üretilir. Ham çıktı: [power-route-audit.json](power-route-audit.json), [route-items.json](route-items.json), [drc.json](drc.json), [drc-empty.json](drc-empty.json). Netclass, `PDU.kicad_dru` ve `PDU.kicad_pro` değişmedi.

Boş kart: ayak izleri ve tüm bakır çıkarılmış kopya (T-013 anlamı). Uyarılar: `{'warning:via_dangling': 6}`. Bu 6 `via_dangling`, zone tap bağlama vialarıdır (ve D_REV1.2 çevresindeki iki via); bağlantı denetiminde açık uç vermez.

## Q2 ve yerel L3 (D-011)

- Q2 90°; T-021'in 12 viası Q2 ile birlikte taşındı.
- L3_VSAFE konturu 90° kaynak via alanına (x 90,6–97,6, y 49,3–52,1) bağlanacak şekilde yeniden çizildi ve REN1 için y 3,5'e uzatıldı; L3_VOUT konturu değişmedi. `pcb_zones.py` değişmedi.
- Q2–U6 gate: **5,469 mm** (U6.6 → Q2.4 pad merkezi), 0,4 mm, F.Cu, sınır 10,0 mm. Gate dönüşü ve seri elemanlar T-023.

## Ağlar (power-route-audit.json)

| Ağ | Tracks | Genişlik (mm) | Katman | Uzunluk (mm) | Via | Zone | Açık uç | Açık uç nerede kapanır |
|---|---:|---|---|---:|---:|---:|---:|---|
| `/ANODE` | 6 | 0,5, 3,3 | B.Cu, F.Cu | 13,62 | 17 | 2 | 0 | — |
| `/VIN` | 6 | 0,25 | F.Cu | 6,33 | 45 | 4 | 0 | — |
| `/VOUT` | 14 | 0,25, 5,5, 7,0 | B.Cu, F.Cu | 128,49 | 128 | 4 | 8 | T-023 Kelvin and feedback sense pads |
| `/VSAFE` | 7 | 0,25, 5,5 | B.Cu, F.Cu | 14,78 | 43 | 6 | 0 | — |
| `/O1_11V` | 5 | 0,25, 5,3 | B.Cu, F.Cu | 27,16 | 37 | 4 | 0 | — |
| `/S2E_11V` | 5 | 0,25, 3,3 | F.Cu | 15,6 | 2 | 3 | 0 | — |
| `/SW_PH1` | 0 | — | — | 0 | 0 | 1 | 1 | TP_SW1 placement decision |
| `/SW_PH2` | 0 | — | — | 0 | 0 | 1 | 1 | TP_SW2 placement decision |
| `/ISNS1` | 2 | 2,6 | F.Cu | 5,72 | 0 | 0 | 3 | T-023 Kelvin / test pad |
| `/ISNS2` | 3 | 2,6 | F.Cu | 7,89 | 0 | 0 | 3 | T-023 Kelvin / test pad |
| `/ISO_GATE` | 3 | 0,4 | F.Cu | 5,0 | 0 | 0 | 2 | T-023 R_GS and TP_ISO_GATE (Q2-U6 gate itself is routed) |

`/VIN`, `/ANODE`, `/VSAFE`, `/O1_11V`, `/S2E_11V` tamamen bağlı. `/VBAT` ağı netlistte yoktur.

Yollar: /VOUT Q2 → B.Cu 7,0 mm → COUT orta bölgesi; RS1 ve RS2 çıkışları ayrı 5,5 mm B.Cu ile bankaya. /VSAFE Q2 → B.Cu 5,5 mm → U3/U4 altı döküm. /O1_11V U3 → 24 via → B.Cu 5,3 mm → J2.1 ve D2. /S2E_11V U4 → F.Cu 3,3 mm → J3.1; D3'e D2–D3 kanalından. /ANODE J1.1 → B.Cu 3,3 mm → Q1 via alanı. /VIN Q1 → L3 → CIN. Dönüş L2 GND; 32 COUT, CIN, TVS ve eFuse GND vialı.

## Via sayıları

| Geçiş | Via | routing-g2 hedefi | Hedef sağlandı |
|---|---:|---:|---|
| Q2 drain (/VOUT) | 17 | 15 | evet |
| Q2 source (/VSAFE) | 15 | 15 | evet |
| U3 OUT -> B.Cu (/O1_11V) | 24 | 19 | evet |
| J1/Q1 (/ANODE) | 12 | 9 | evet |
| RS1 output (/VOUT) | 16 | 15 | evet |
| RS2 output (/VOUT) | 16 | 15 | evet |
| /VOUT bus -> L3 (COUT pin 1 under the bus) | 16 | 15 | evet |

CIN → L3: U1 tarafı 12, U2 tarafı 12 via (hedef 9). Faz ağları (SW, ISNS) katman değiştirmediği için 12 via hedefi bu yollarda uygulanmadı. Via ölçüsü 0,6/0,3 mm ve via-in-pad **VARSAYIM**, üretici onayı AÇIK (PCB-HANDOFF §7).

## Döküm kesitleri

`track_width` kuralı döküm görmez; bu yüzden gerçek dolgu üzerinde ölçüldü.

| Kesit | Bakır (mm) | Sınıf min (mm) | Karşılıyor |
|---|---:|---:|---|
| /S2E_11V U4 -> D3 channel | 3,38 | 2,97 | evet |
| /S2E_11V east drop | 4,06 | 2,97 | evet |
| /O1_11V pins -> field | 5,48 | 4,76 | evet |
| /VIN CIN3/4 -> U1 | 3,82 | 2,94 | evet |
| /VIN CIN7/8 -> U2 | 3,82 | 2,94 | evet |
| /SW_PH1 U1 -> L1 | 2,78 | 2,35 | evet |
| /SW_PH2 U2 -> L2 | 2,76 | 2,35 | evet |
| /VOUT RS2.2 -> field | 5,52 | 4,92 | evet |
| /VSAFE under U3 -> U4 | 5,08 | 4,92 | evet |

0,25–0,5 mm izler yalnız ince adımlı pad necklerinde (neck audit ihlali 0). CIN1/CIN2 ve CIN5/CIN6 kolları 1,45 mm genişliğinde yerel dekuplaj koludur; bu kapasitörler L3 /VIN'e ayrı vialarla da bağlıdır.

## Düzlemler

| Düzlem | Ada | En büyük dolu alan (mm²) |
|---|---:|---:|
| L2_GND | 1 | 9296,32 |
| L4_GND | 10 | 7835,89 |
| L3_VIN | 1 | 3584,16 |
| L3_VOUT | 1 | 2038,8 |
| L3_VSAFE | 1 | 1667,15 |

L2 tek ada. L4 ikincil GND, B.Cu güç yolları nedeniyle 10 adaya ayrıldı; dönüş referansı L2'dir. Q1 ve Q2 termal bakırı hedefi (≥645,16 mm²) L3_VIN ve L3_VOUT ile karşılanıyor; aynı termal davranış kanıtlanmadı.

## Kapanmayanlar (rota tamamlandı sayılmaz)

1. **T-023'e bırakılan hassas uçlar:** `/VOUT` 8 (U1.12, U2.12, U11.1, U12.1, TP_ISNS1N/2N, R_INJ, TP_FB_INJ_A), `/ISNS1` 3, `/ISNS2` 3 (Kelvin, T-023 kriteri), `/ISO_GATE` 2 (R_GS, TP). Kart genelinde 205 açık uç var; `/GND` sinyal padleri ve diğer sinyal ağları T-023'tedir.
2. **TP_SW1 ve TP_SW2 bağlanmadı (karar gerekli):** padler kartın batı kenarında, SW düğümünden yaklaşık 40 mm uzakta. Bu izi çekmek SW bakırını anten gibi uzatır; D-010 "geniş SW dolgusu varsayılan çözüm değildir" diyor. Yerleşim kararı THINKER'da.
3. **CEFIN2 yalnız vialarla U4 IN'e bağlı:** U4.16 → CEFIN2 F.Cu izi U4.17 /S2E_11V bakırına karşı 0,6 mm HV kuralını sağlamıyor; bağlantı B.Cu dökümü üzerinden. CEFIN1 F.Cu ile doğrudan bağlı. CEFIN2 yerel döngüsü daha uzun.
4. **U3.16 ve U4.16 neck izleri 0,6 mm HV kuralına küçük payla oturuyor:** iz pad kenarına çok yakın başlıyor. DRC temiz; R-kartında değerlendirilmeli.
5. **VIN–CIN–PGND gerçek döngü alanı doğrulanamadı:** D-010 yöntemi akım çözümü ister; pad merkezi yerine kullanılmadı.

## Olgu / hesap / varsayım

- **KiCad çıktısı:** DRC, parite ve bağlantı sayıları. Bunlar simülasyon veya fiziksel kanıt değildir.
- **HESAP:** kesit genişlikleri ve uzunluklar. Akım, ısınma ve 50 mV düşüm bu kartta ölçülmedi.
- **VARSAYIM:** 1 oz tüm katman, via-in-pad dolgulu, via akım paylaşımı. Akım paylaşımı **doğrulanamadı**.
