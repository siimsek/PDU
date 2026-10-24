# WP1 – KiCad aktarım adımları (UYGULANMADI)

Bu paket hiçbir `.kicad_sch/.kicad_pcb/.kicad_pro` dosyasını değiştirmez. Aşağıdaki adımlar kullanıcı tarafından, **WP2 kararından sonra** KiCad'de uygulanmalıdır. Referans: `simulation/proposals/2026-10-25-o1-ovp/pdu-o1ovp-block.inc` ve `net-split-changes.json`.

## 1. Net ayrımı (RAW / VOUT)
1. Yeni net **RAW** oluştur: buck çıkışı (L1/L2 sonrası, RS1/RS2 akım algılama dirençlerinin VOUT ucu) artık RAW.
2. Şu bağlantıları VOUT → RAW taşı (`net-split-changes.json`, 13 eleman):
   - COUT1…COUT8 (çıkış kapasitörleri) → RAW
   - RS1, RS2 (pin 2) → RAW
   - RFB1 (üst geri besleme direnci) → RAW (buck RAW'ı regüle eder; VOUT değil – wind-up önlemi)
   - XU1/XU2 buck kontrolcü algılama pinleri (netlist alanı 6 ve 12) → RAW
3. VOUT (bus) yalnız OVP çıkışı + U3/U4 eFuse girişleri + mevcut VOUT yükleri olarak kalır.

## 2. Yeni parçalar (`hardware/proposals/2026-10-25-o1-ovp/candidate-bom.csv`)
| Ref | Bağlantı |
|---|---|
| Q10, Q11 (paralel) | D = RAW, S = SRC_OVP, G = G_OVP |
| Q12, Q13 (paralel) | D = VOUT, S = SRC_OVP, G = G_OVP (sırt sırta: ortak kaynak) |
| U10 TPS48000-Q1 | VS = VIN; EN/UVLO = REN10 (VIN→EN 100k) / REN11 (EN→GND 10k); OV = ROV10 (RAW→OV 90,9k) / ROV11 (10k); INP = U13 çıkışı; BST–SRC arası CBST10 0,47 µF; PU → RPU10 10 Ω → G_OVP; **PD → G_OVP doğrudan** (simde 10 mΩ); SRC = SRC_OVP; simde modellenmeyen pinler (kısa devre koruma, zamanlayıcı, FLT vb.) SLUSEZ1B pin fonksiyon tablosundaki "kullanılmıyorsa" önerisine göre bağlanmalı – WP2 şematik incelemesinde doğrulanacak |
| U11 TPS7A1650 | IN = VIN (CIN11 1 µF), OUT = V5_OVP (COUT11 2,2 µF), RBLD11 499 Ω V5_OVP→GND |
| U12 REF35409 | VIN = V5_OVP, OUT = VREF_OVP (CREF12 0,1 µF) |
| RSNS10 / RSNS11 | RAW → SNS_OVP 2,05 k (0,1 %) / SNS_OVP → GND 1,15 k (0,1 %); CSNS10 100 pF C0G SNS_OVP→GND |
| RIN10 | SNS_OVP → U13 IN− (1 k) |
| U13 TLV3601 | IN+ = VREF_OVP, IN− = RIN10 ucu, VCC = V5_OVP, OUT → U10 INP (OUT yüksek = FET'ler açık; besleme yokken kapalı) |

## 3. Yerleşim notları (simülasyonda yok)
- Bölücü toprağı (RSNS11, CSNS10, CREF12, U12/U13 GND) için Kelvin/sinyal toprağı; RAW algılama ucu COUT bankının yanından ayrı iz.
- PD–G_OVP–SRC döngüsünü minimumda tut (tPD(INP_L) 1,05 µs garantisi düşük endüktanslı sürüşe dayanır).
- 4× CSD18540Q5B termal: RDS(on) max 2,2 mΩ @ VGS = 10 V, 25 °C (SLPS488B p3). Yol: 2 paralel (1,1 mΩ) × 2 seri = 2,2 mΩ → 7,5 A'da ≈ 7,5² × 2,2 mΩ ≈ 0,12 W (25 °C; sıcakta RDS artışı ile ~0,2 W mertebesi – tahmin). VGS gerçek değeri (BST–SRC) 10 V'tan düşükse RDS artar; bakır alanı WP5'te doğrulanmalı.
- U3/U4 girişindeki mevcut kapasitörler VOUT'ta kalır; FET'ler açılırken inrush TPS48000'in yavaş kapı açılışıyla sınırlanır (CBST 0,47 µF, en kötü 50,8 ms).

## 4. Aktarım sonrası kontrol
1. ERC/DRC temiz.
2. Netlist'i dışa aktar; RAW/VOUT ayrımının `pdu-circuit-o1ovp.inc` ile aynı olduğunu (14 düzenleme) karşılaştır.
3. `run_o1ovp.py` + `verify_candidate.py` yeniden çalıştır.
