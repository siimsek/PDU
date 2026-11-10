> Bu dosya alt ajan A'ya verilen **G3 durumu** girdisidir (G4 öncesi değerler bilinçli olarak G3'teki gibidir: RCOMP 16.9k, 16× COUT, RFB2 10.2k). Geçerli değerler: `analysis/g2/design.py`.

# G4 bağımsız yeniden türetme girdileri (sonuç içermez)

Bu tablo yalnız datasheet değerleri ve seçilmiş devre değerlerini verir. G3 sonuç dosyalarından türetilmemiştir.

## Gereksinimler
O1 anlık tepe ≤12.0 V; kararlı bara ≤11.1605 V; transient bant üst 11.22 V; yük adımı 0.75→7.0→0.75 A'da bara ≥10.78 V; eFuse IN <30 V abs. VIN 20–26 V (6S), nominal 22.2 V. Bara nominal setpoint 0.8 V × (1+130k/10.2k).

## Topoloji
VIN → 2 fazlı LM70880 buck (aynı COMP, 180° faz farkı) → ham bara VRAW (COUT) → seri N-MOSFET ayırıcı → VSAFE → 2× TPS259824L eFuse → O1 / S2E. Ayırıcı: VRAW bölücüsü → karşılaştırıcı (IN−) vs 2.5 V referans (IN+) → çıkış LOW = aşırı gerilim → D flip-flop PRE (asenkron set) → Q → 10 kΩ → LM74502H OV pini → kapı kapanır.

## Devre değerleri
| Ad | Değer |
|---|---|
| Faz bobini | 6.8 µH ±20 %, DCR maks 23.3 mΩ, Isat typ 13.5 A (%20 L düşüşü), Iheat typ 8 A (Vishay IHLP4040DZER6R8M01, doc 34509 p.1) |
| Şönt | 7.5 mΩ ±1 %, TCR ±75 ppm/K |
| COUT | 16× TDK C5750X7S2A226M280KB; parça başı Ceff min 11.581 µF, typ 20.622 µF, max 32.208 µF (11 V); ESR 1.92 mΩ/parça |
| VSAFE ek C (VARSAYIM) | 8.1 µF etkin |
| Eşik bölücüsü | Rt 8.25 kΩ, Rb 2.32 kΩ, ±0.1 %, ±15 ppm/K |
| Kompanzasyon | RCOMP 16.9 kΩ, CCOMP 10 nF, CHF 22 pF; FB bölücüsü 130 kΩ / 10.2 kΩ |
| UVLO bölücüsü | 174 kΩ / 10.0 kΩ, ±0.1 %, ±25 ppm/K |
| eFuse RILIM | O1 182 Ω, S2E 300 Ω |
| Ayırıcı FET | CSD19531Q5A |
| Kaynak + kablo direnci | 20–200 mΩ (VARSAYIM); +5 mΩ kart/sigorta |
| Sıcaklık sürüklenme aralığı | 25→125 °C (100 K) dirençler; referans kutu spec −40…125 °C (165 K) |
| fsw | 400–480 kHz (nom 435 kHz) |

## Datasheet değerleri (sayfa)
| Parça | Parametre | Değer | Kaynak |
|---|---|---|---|
| LM70880-Q1 (SNVSBX7A) | VFB | 794/800/806 mV | p.7 |
| | EA gm (harici komp.) | min 970 µS, typ 1200 µS, maks yayımlanmamış | p.7 |
| | CS kazancı | 10 V/V | p.8/p.17 |
| | CS eşiği | 50/56/62 mV | p.8 |
| | CS gecikmesi | 75 ns tipik | p.17 |
| | Eğim kompanzasyonu | L_sc[µH] = VOUT·RS[mΩ]/(24·Fsw[MHz]) iç eğimin bobin iniş eğimine eşit olduğu L | p.16 Eq.7 |
| | EN yükselen eşik | 0.95/1.0/1.05 V; histerezis 0.1 V tipik; EN kaçağı maks yayımlanmamış (1 µA tarama) | p.6 |
| | VOUT/ISNS+ abs maks | 60 V; BIAS abs maks 32 V | p.5 |
| TLV3601 (Rev E) | Vos | ±5 mV | p.7 |
| | Histerezis | 1.5–5 mV | p.7 |
| | IB | ±5 µA maks | p.7 |
| | tPD | 4.5 ns maks @50 mV overdrive, VCM=VEE+0.3 V | p.7 |
| REF5025A-Q1 | VOUT | 2.5 V ±0.1 %, 8 ppm/K maks (kutu) | p.5 |
| SN74LVC1G74 | PRE/CLR→Q | 6.4 ns maks (5 V, −40…125 °C) | p.7 |
| LM74502H | tOVP_OFF | 1 µs maks, OV'den VGS<1 V'a, C_GS=4.7 nF | p.6 |
| | OV eşiği | 1.165–1.333 V | p.6 |
| TPS25982 (SLVSEI3D) | ILIM (TJ −40…125 °C) | 182 Ω: 7.23/8.13/9.07 A; 300 Ω: 4.36/4.98/5.66 A | p.9 |
| | IN abs maks | 30 V; önerilen ≤24 V | p.7 |
| CSD19531Q5A | RDS(on) 10 V | 6.4 mΩ maks (25 °C) | p.3 |

## İstenen 10 sayı
1. Hassas eşik min/maks (tüm köşeler) ve garantili gecikme toplamı; ayırıcı açıldığında O1 tepe (üst anahtar kısası: arızalı faz bobini VIN'i doğrudan baraya bağlar, yük yok, VIN 26 V, ön-hata barası statik alt köşe, L −20 %, Ceff min, Rsrc 20 mΩ; karşılaştırıcı garanti gecikmesi için 50 mV overdrive'ın baraya yansıması eklenir).
2. U3/U4 IN tepe (VSAFE).
3. ILIM garantili-min toplam.
4. RUV1 yükselen eşik köşeleri.
5. Akım sınırında bobin tepe akımı (VCS maks, RS min soğuk, 75 ns gecikme, VIN 53.3 V) ve Isat marjı; üst anahtar kısasında ayırıcı açılırken faz akımı.
6. F1 kaynak kısa devre akımı (26 V, Rsrc 20 mΩ + 5 mΩ).
7. Döngü PM/GM en kötü köşe (Ridley tepe akım modu; iki faz ortak COMP → eşdeğer L/2, Ri/2; Ceff min/typ/max; L ±20 %; gm 970–1430 µS; VIN 20/26; yük 0.75/7.5 A; fsw 400/480 kHz).
8. Yük adımında bara min (birinci derece tahmin yeterli).
9. Kayıp bütçesi (%92 dönüştürücü verimi VARSAYIMI + ayrık parçalar).
10. Tam sistem tahmini O1 tepe (1 ile aynı köşe, kendi ODE/SPICE'ın).
