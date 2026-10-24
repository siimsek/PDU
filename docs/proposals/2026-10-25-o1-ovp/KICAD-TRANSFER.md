# WP1 rev2 – KiCad aktarım adımları (UYGULANMADI)

Bu paket hiçbir `.kicad_sch/.kicad_pcb/.kicad_pro` dosyasını değiştirmez. Aşağıdaki adımlar kullanıcı tarafından, **WP2 kararından sonra** KiCad'de uygulanmalıdır. Referans: `simulation/proposals/2026-10-25-o1-ovp/pdu-o1ovp-block.inc` ve `net-split-changes.json`.

## 1. Net ayrımı (RAW / VOUT)
1. Yeni net **RAW** oluştur: buck çıkışı (L1/L2 sonrası, RS1/RS2 akım algılama dirençlerinin VOUT ucu) artık RAW.
2. Şu bağlantıları VOUT → RAW taşı (`net-split-changes.json`, 13 eleman):
   - COUT1…COUT8 (çıkış kapasitörleri) → RAW
   - RS1, RS2 (pin 2) → RAW
   - RFB1 (üst geri besleme direnci) → RAW (buck RAW'ı regüle eder; VOUT değil – wind-up önlemi)
   - XU1/XU2 buck kontrolcü algılama pinleri (netlist alanı 6 ve 12) → RAW
3. **rev2:** 8 yeni kapasitör **COUT21…COUT28** = TDK **C5750X7S2A226M280KB** (22 µF / 100 V / X7S), ayak izi **PDU:TDK_C5750_2220_Recommended** (COUT1–8 ile aynı), pin 1 = **RAW**, pin 2 = **GND**; COUT1–8'in yanına, RAW bankının parçası olarak yerleştir. (COUT11 refdes'i OVP LDO kapasitörü için kullanıldığından yeni parçalar COUT21'den başlar.) Sonuç: RAW'da 16 × 22 µF, min. efektif 185,30 µF / maks. 483,05 µF.
4. VOUT (bus) yalnız OVP çıkışı + U3/U4 eFuse girişleri + mevcut VOUT yükleri olarak kalır.

## 2. Yeni parçalar (`hardware/proposals/2026-10-25-o1-ovp/candidate-bom.csv`)
| Ref | Bağlantı |
|---|---|
| Q10, Q11 (paralel) | D = RAW, S = SRC_OVP, G = G_OVP |
| Q12, Q13 (paralel) | D = VOUT, S = SRC_OVP, G = G_OVP (sırt sırta: ortak kaynak) |
| U10 TPS48000-Q1 | VS = VIN; EN/UVLO = REN10 (VIN→EN 100k) / REN11 (EN→GND 10k); OV = ROV10 (RAW→OV 90,9k) / ROV11 (10k); INP = U13 çıkışı; BST–SRC arası CBST10 0,47 µF; PU → RPU10 10 Ω → G_OVP; **PD → G_OVP doğrudan** (simde 10 mΩ); SRC = SRC_OVP; kullanılmayan pinler: bkz. §2b (SLUSEZ1B Tablo 4-1) |
| U11 TPS7A1650 | IN (8) = VIN (CIN11 1 µF / 50 V / 0805); OUT (1) = V5_OVP (**COUT11 10 µF / 25 V / X7R / 1206 – rev2, 2,2 µF'tan büyütüldü**); EN (5) = IN (8) = VIN (aynı ağ, rev3 P1-05 netleştirme); FB/DNC (2) **bağlanmaz** (sabit 5 V sürüm); PG (3), DELAY (7), NC (6) açık; GND (4) + termal ped → GND; RBLD11 499 Ω V5_OVP→GND |
| U12 REF35409 | VIN (4) = V5_OVP; **EN (3) = VIN (4) = V5_OVP** (aynı ağ; rev3 P1-05: "EN → VIN" ifadesi U10/üst VIN ile karıştırılabiliyordu); VREF (6) = VREF_OVP (**CREF12 1 µF / 16 V / X7R – rev2, 0,1 µF'tan büyütüldü**); NR (5) açık; GND (1, 2) → sinyal toprağı |
| RSNS10A / RSNS10B / RSNS11 (rev3 P0-01) | RAW → SNS_MID 1,0 k (ERA-8ARB102V) → SNS_OVP 1,05 k (ERA-8ARB1051V) = 2,05 k toplam, oran değişmedi / SNS_OVP → GND 1,15 k (ERA-8ARB1151V); hepsi 0,1 %, 1206 (R_1206_3216Metric); SNS_MID yeni yerel ağ (yalnız iki direnç arası); CSNS10 100 pF C0G SNS_OVP→GND |
| COUT21–COUT28 (rev2) | RAW ↔ GND, COUT1–8 ile paralel; 8 × C5750X7S2A226M280KB, PDU:TDK_C5750_2220_Recommended |
| RIN10 | SNS_OVP → U13 IN− (1 k) |
| U13 TLV3601 | IN+ = VREF_OVP, IN− = RIN10 ucu, VCC = V5_OVP, OUT → U10 INP (OUT yüksek = FET'ler açık; besleme yokken kapalı) |

## 2b. rev2 P1-3 – Pin doğrulaması (veri sayfası pin tablosu ↔ SPICE ↔ KiCad sembol/ayak izi)

Sembol, ayak izi ve SPICE alt devresi **ayrı ayrı** doğrulanmalıdır: SPICE düğüm sırası pin numarası değildir; KiCad sembol pin numarası ayak izi ped numarasıyla, ped numarası veri sayfası pin numarasıyla eşleşmelidir. KiCad tarafı bu pakette **doğrulanmadı** (KiCad dosyası değiştirilmedi/açılmadı).

### U10 TPS48000-Q1, DGX (19 pin; pin 16 yok) – SLUSEZ1B Tablo 4-1
| Pin | Ad | Bağlantı (bu öneri) | SPICE (XU10) |
|---|---|---|---|
| 1 | EN/UVLO | REN10/REN11 bölücü (VIN) | EN |
| 2 | OV | ROV10/ROV11 bölücü (RAW) – yalnız yedek OV (11,80–12,92 V RAW, garanti değil) | OV |
| 3 | INP | U13 OUT | INP |
| 4 | FLT_GD | açık-drenaj; kullanılmıyorsa açık (veya pull-up) | modellenmedi |
| 5 | FLT | açık-drenaj; kullanılmıyorsa **GND** | modellenmedi |
| 6 | GND | GND | GND |
| 7 | CS_SEL | **GND** (high-side) | modellenmedi |
| 8 | ISCP | kısa devre koruması kullanılmıyor → **GND** | modellenmedi |
| 9 | TMR | kullanılmıyor → **GND** | modellenmedi |
| 10 | SCP_TEST | kullanılmıyor → **GND** | modellenmedi |
| 11, 19 | N.C | açık | – |
| 12 | BST | CBST10 → SRC | BST |
| 13 | SRC | SRC_OVP | SRC |
| 14 | PD | G_OVP (doğrudan) | PD |
| 15 | PU | RPU10 10 Ω → G_OVP | PU |
| 17 | CS− | CS+/CS−/VS birbirine (SCP kullanılmıyor) | modellenmedi |
| 18 | CS+ | 〃 | modellenmedi |
| 20 | VS | VIN; CS+/CS− ile bağlı | VS |
Abs-max: PU/PD/BST–SRC 19 V; ISCP/TMR 5,5 V (SLUSEZ1B §6.1). **Ayak izi:** TI DGX (VSSOP-19) KiCad standart kütüphanesinde bulunduğu doğrulanamadı → TI mekanik çizimine göre oluşturulmalı (PCB blokörü).

### U13 TLV3601, DCK (SC-70-5) – SNOSDB1E Tablo 5-1
| Pin | Ad | Bağlantı | SPICE XU13 düğüm sırası |
|---|---|---|---|
| 1 | OUT | U10 INP | 1. (INP_OVP) |
| 2 | VEE | GND | 2. (0) |
| 3 | IN+ | VREF_OVP | 3. (VREF) |
| 4 | IN− | RIN10 → SNS_OVP | 4. (IN−) |
| 5 | VCC | V5_OVP; **CBYP13 100 nF** (rev2, pin 5–pin 2 arasına, pine bitişik; SPICE'ta yok) | 5. (V5) |
SPICE sırası pin 1–5 ile birebir aynı. **Uyarı:** KiCad'deki genel SC-70-5 komparatör sembollerinin pin düzeni farklı olabilir (ör. IN+/IN− yer değişimi) → TLV3601 için sembol SNOSDB1E'ye göre kontrol edilmeli. Ayak izi: Package_TO_SOT_SMD:SOT-353_SC-70-5 (KiCad adı; ped numaralandırması doğrulanmalı).

### U12 REF35409, DBV (SOT-23-6) – SNAS809C
| Pin | Ad | Bağlantı | SPICE XU12 (V5 VREF GND) |
|---|---|---|---|
| 1, 2 | GND | sinyal toprağı | GND |
| 3 | EN | **VIN'e bağla** (SPICE'ta modellenmedi) | – |
| 4 | VIN | V5_OVP | V5 |
| 5 | NR | açık (izin verilir) | – |
| 6 | VREF | VREF_OVP, CREF12 1 µF (CL 0,1–10 µF) | VREF |
Ayak izi: Package_TO_SOT_SMD:SOT-23-6 (doğrulanmalı).

### U11 TPS7A1650, DGN (MSOP-8 PowerPAD) – SBVS171F
| Pin | Ad | Bağlantı | SPICE XU11 (VIN OUT GND) |
|---|---|---|---|
| 1 | OUT | V5_OVP, COUT11 10 µF (≥ 2,2 µF efektif gerekli) | OUT |
| 2 | FB/DNC | **bağlanmaz** (sabit sürüm) | – |
| 3 | PG | açık | – |
| 4 | GND | GND | GND |
| 5 | EN | IN'e bağla (VEN ≤ VIN) | – |
| 6 | NC | açık | – |
| 7 | DELAY | açık | – |
| 8 | IN | VIN, CIN11 1 µF (≥ 0,1 µF) | VIN |
| PAD | termal | GND bakır alanı | – |
Isıl: ~17 mA × (26 − 5) V ≈ 0,36 W × RθJA 66,2 °C/W ≈ +24 °C (tahmin; IOUT 100 mA nominal, ILIM 101/225/400 mA). Ayak izi: KiCad MSOP-8-1EP varyantı TI DGN ped ölçüsüyle karşılaştırılmalı.

### Q10–Q13 CSD18540Q5B (SON 5×6) – SLPS488B
Pinler: 1–3 S, 4 G, 5–8 + ped D. KiCad ayak izi TI land pattern'iyle doğrulanmalı (PCB blokörü). SPICE: davranışsal O1OVP_NFET (TI modeli ngspice'ta fiziksel olmayan sonuç verdi, MODELS.md).

### Özet tablo – doğrulama durumu
| Parça | Veri sayfası pinleri | SPICE düğümleri | KiCad sembol | KiCad ayak izi |
|---|---|---|---|---|
| U10 TPS48000 | doğrulandı (Tablo 4-1) | 9 pin modellendi, 10 pin modellenmedi (yukarıda) | doğrulanmadı | **oluşturulmalı** |
| U11 TPS7A16 | doğrulandı | 3 pin; EN/PG/DELAY/FB modellenmedi | doğrulanmadı | doğrulanmadı |
| U12 REF35 | doğrulandı | 3 pin; EN/NR modellenmedi | doğrulanmadı | doğrulanmadı |
| U13 TLV3601 | doğrulandı | 5/5, sıra eşleşiyor | doğrulanmadı (pin düzeni riski) | doğrulanmadı |
| Q10–Q13 | doğrulandı | davranışsal 3 uç | doğrulanmadı | doğrulanmadı |

## 3. Yerleşim notları (simülasyonda yok)
- **rev3 P1-03 – yalnız simülasyon elemanları (KiCad'e parça olarak aktarılmaz):** `RPD10` (PD_OVP→G_OVP, 10 mΩ) fizikselde **doğrudan bağlantıdır** (PD pini kapı ağına iz ile; 10 mΩ izi/via direncini temsil eder ve `gate_discharge_wc.py` en kötü kapı deşarj hesabına dahildir). `RSRC10` (SRC_OVP→0, 10 MΩ) yalnız yakınsama/DC yol elemanıdır; fiziksel kartta **yoktur** (sızıntı ≈ 1,1 µA @ 11 V, sonuçlara etkisi ihmal edilebilir – varsayım; tezgâhta ayrıca doğrulanmaz). BOM'da bu iki eleman yer almaz.
- Bölücü toprağı (RSNS11, CSNS10, CREF12, U12/U13 GND) için Kelvin/sinyal toprağı; RAW algılama ucu COUT bankının yanından ayrı iz.
- PD–G_OVP–SRC döngüsünü minimumda tut (tPD(INP_L) 1,05 µs garantisi düşük endüktanslı sürüşe dayanır).
- 4× CSD18540Q5B termal: RDS(on) max 2,2 mΩ @ VGS = 10 V, 25 °C (SLPS488B p3). Yol: 2 paralel (1,1 mΩ) × 2 seri = 2,2 mΩ → 7,5 A'da ≈ 7,5² × 2,2 mΩ ≈ 0,12 W (25 °C; sıcakta RDS artışı ile ~0,2 W mertebesi – tahmin). VGS gerçek değeri (BST–SRC) 10 V'tan düşükse RDS artar; bakır alanı WP5'te doğrulanmalı.
- U3/U4 girişindeki mevcut kapasitörler VOUT'ta kalır; FET'ler açılırken inrush TPS48000'in yavaş kapı açılışıyla sınırlanır (CBST 0,47 µF, en kötü 50,8 ms).

- **rev2 alan:** 8 ek 2220 kılıf, her biri 7,85 × 6,20 mm courtyard (≈ 3,9 cm² toplam, yalnız courtyard). RAW–GND akım döngüsü COUT1–8 ile aynı düzlemde, kısa ve simetrik; buck çıkış endüktörü (L1/L2) → bank → OVP FET (Q10/Q11) akış sırası korunmalı.
- **rev2 WP3 uyarısı:** Buck kompanzasyonu (RCOMP 9,53k / CCOMP 4,7n / CHF 47p) ~88 µF için seçilmişti; 185–483 µF ile döngü kararlılığı, başlangıç (soft-start) şarj akımı ve akım sınırı WP3'te doğrulanmadan kompanzasyon değiştirilmemeli/üretime geçilmemelidir.

## 4. Aktarım sonrası kontrol
1. ERC/DRC temiz.
2. Netlist'i dışa aktar; RAW/VOUT ayrımının `pdu-circuit-o1ovp.inc` ile aynı olduğunu karşılaştır (rev2: 22 düzenleme = 14 net taşıma + 8 COUT eklemesi; `net-split-changes.json`).
3. `run_o1ovp.py` + `verify_candidate.py` yeniden çalıştır.
