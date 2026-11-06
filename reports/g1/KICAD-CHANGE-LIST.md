# Sonraki KiCad fazına aktarılacak değişiklik listesi

Bu liste taslak değişiklik emridir; bu G1 dalında hiçbir `*.kicad_*` dosyası değiştirilmedi.

| Ref/net | Eski → öneri | Footprint/işlem | Gerekçe ve kanıt |
|---|---|---|---|
| RUV1, VIN/EN_BUCK | 180 kΩ → 174 kΩ; RUV2 10 kΩ korunur | 0603; TCR/toleransı exact seçilecek | 20 V worst-case rising 19.69 V HESAP; EN leakage/TCR AÇIK. `calc-results.json`, OVP-UVLO decision. |
| RILIM1/RILIM2, ILIM_O1/S2E | 301/604 Ω → yalnız gerçek yük split'ini karşılayan ve datasheet guaranteed-min sum ≥7.5 A + ölçüm marjı veren değerler; exact values AÇIK | 0603; tolerance/TCR per vendor and TI supported value range | Nominal formulas sum7.4877 A <7.5 A by12.3 mA; exact-value current-limit guarantee unavailable. `calc-results.json/port_capacity_screen`. |
| O1_11V / U3 çıkışı | U3 sonrası bağımsız comparator+latch+back-to-back series disconnect ekle; eşik üst corner ≤11.46 V, toplam gecikme hedef ≤0.5 µs | Yeni comparator, reference, latch, 2×FET; exact refs/MPN/footprint/stok bu fazda AÇIK | O1 12 V limiti; mevcut U3 eFuse 16.9 V; OVP decision ve sim family-1. MPN uydurulmadı. |
| F1 / VBAT | “10A” placeholder → source fault/I²t/DC interrupt ile seçilen fuse + holder/footprint | F1 footprint ve servis/clearance alanı ekle; MPN açık | Batarya/kablo dirençleri yok; akım, I²t ve interrupt capacity hesaplanamaz. HESAP/AÇIK. |
| L1/L2, SW_PH1/2 | 6.8 µH korunabilir; candidate MPN IHLP4040DZER6R8M01; BOM/onay/stok open | IHLP-4040 generic land yerine exact vendor land karşılaştır | Ripple2.916 A p-p, phase peak5.583 A (+10% share); Vishay p1 Isat13.5 A (~20% L drop), heat-current8 A (40°C rise). |
| RS1/RS2, ISNS1/2 | 7.5 mΩ korunabilir; ≤1%/≤100 ppm/K varsayımını sağlayan exact low-ohm part | 2512, ≥0.5 W tavsiye; Kelvin ayrı pad/escape | HESAP worst share'de ~0.13 W/faz ve sense limit6.6–8.5 A; current error ve TCR açık. |
| COUT1–8, VOUT/GND | 8× C5750X7S2A226M280KB korunur; etkin Ceff/aging/ESR BOM notuna ekle | Mevcut özel 2220 land; üretici land/termal/flex kabulü korunur | DC-bias typical164.98 µF; sensitivity min92.65/max241.53 µF, yaşlanma %10 varsayım. |
| D1, VIN/GND | SMCJ33A family → üretici exact MPN; TVS/F1 ile koordinasyon | SMC footprint; gerçek standoff/clamp current/pulse energy ve placement kontrol | 53.3 V datasheet-family clamp varsayımı; transient/energy open. |
| D2/D3, O1/S2E/GND | SS34 generic → exact vendor MPN/rating; kullanılacağı fault akımı doğrula | SMA pad family check; path 7.5A ise 3A family yeterli değildir | BOM MPN/rating boş; topology/fault path açığı. |
| J1/J2/J3 | 43045-0200 family → header + matching housing/crimp/contact/cable exact MPN | Horizontal Micro-Fit 3.0 2-circuit; footprint pin pitch, keying, polarization and clearance verify | Molex W-B 18AWG 8.5A, W-W 7A; J2 7.5A hedefe W-W sınırı yetmez. |
| U5/Q1 | LM74700 generic MPN + BSC160N10NS3G value → exact orderable BOM fields, SOA/thermal-reviewed assembly | U5 SOT23-6, Q1 PG-TDSON-8 adapted land; final land/paste/thermal acceptance | 53.3V conditional margin; Q1 hot SOA/fault waveform open; `calc-results.json`. |
| U1/U2 + RCOMP/CCOMP/CHF | Mevcut değerleri doğrudan onaylama; RCOMP/CCOMP/CHF için bench-adjustable pad seçenekleri | 0603; RCOMP 6.8–27k, CCOMP 2.2–10nF, CHF 22–100pF test seçenekleri; default values DNP/jumper plan | Gerçek loop crossover/phase margin hesaplanamadı. FRA T3 pass ≥45°/6 dB ile seç. |

## Test noktaları / enjeksiyon padleri

- `TP_VBAT` (F1 öncesi), `TP_ANODE`, `TP_VIN`, `TP_VOUT`, `TP_O1_PRE` (U3 öncesi), `TP_O1` (son OVP sonrası), `TP_S2E`, `TP_GND` (probe return), `TP_EN_BUCK`, `TP_COMP`, `TP_SW1`, `TP_SW2`, `TP_ISNS1+/-`, `TP_ISNS2+/-` Kelvin, `TP_PG_O1`, `TP_PG_S2E`, `TP_IMON_O1`, `TP_IMON_S2E`.
- O1 OVP için `J_OVP_INJ` iki pad, korumalı external pulse fixture'a bağlanır; test sırasında normal power path'ten izolasyon ve limitli seri direnç fixture dışında yapılır. PCB'de O1 sonrası `R_OVP_BYPASS` footprinti DNP kalır ve normal durumda jumper takılmaz; bypass sökülü olarak fault-test yapılır. Aşırı gerilimde yük bağlama yok.
- `RINJ_FB` footprinti (default 0 Ω, 0603, FRA için 10–49.9 Ω opsiyon) FB üst koluna seri yerleştir; `TP_FB_UP/DOWN` ile FRA injection. Seri direnç DC oran etkisi ve noise ile şematik incelemede teyit edilir.
- EN/OVP comparator fault injection için `RFAULT_EN` DNP ≥100 kΩ seri pull-up/pull-down padleri; doğrudan batarya/rail injection yok.
- Akım şöntü için RS padlerinde ayrı Kelvin force/sense bağlantıları; hiçbir sense via/load-current via ortak boyun kullanmaz.

## PCB zorunlu yönlendirme girdileri

- **4 katman önerilir:** L1 komponent/switch kısa döngü; L2 kesintisiz GND dönüş; L3 güç dağıtım (VIN/VOUT, net alanları); L4 sinyal/yardımcı. 2 katmanda tam GND referansı ve termal yayılım bozulur. 2L/4L IR-drop karşılaştırması yalnız varsayımlıdır; stackup/fab copper bilgisi alınmadan plane sharing credit yok.
- 31.5 µm hesap bakırında, ΔT=20°C IPC-2221 dış iz taraması: BUS_POWER 7.5 A ve O1/S2E ayrı 7.5 A zarfı için 2L/4L minimumlarını `routing-comparison.json` satırlarından al. Akım bölüşümü ölçülmediği için port dalı zarfı ayrı ayrı tam kapasitedir. Her 50 mm güç segmentinde 50 mV IR-drop bütçesi; eski 6 mm bus class üretim garantisi değildir. `routing-input.json` varsayımları/akım değerlerini taşır.
- Güç via geçişlerinde G1 minimum sayı 0.5 A/via varsayımıyla routing JSON'da; sonraki fazda üreticinin plating/drill ve termal relief verisiyle yeniden hesaplanmadan DRC minimumuna çevrilmez. En az iki plane stitching sırası, gerekirse daha çok sayıda, via-in-pad açıkça üreticiye onaylatılır.
- U1/U2 high-frequency CIN–VIN–PGND döngüsü en küçük alan; SW bakırı kısa ve IC/FB/COMP'tan uzakta; SW node test padini min alan yap. Her iki şönt Kelvin, ortak GND dönüşüne güç padinden ayrı; COMP ve FB gürültülü bakır altından geçmez.
- EFuse/FET/O1 akım döngüsü konektöre kısa-geniş; test noktaları yüksek akım taşımaz. O1 disconnect MOSFET'leri / eFuse / F1 ısı dağılımı ile TVS/F1 loop geometrisi birlikte incelenir.

Önceki fazda KiCad'e aktarım öncesi onay: exact MPN, pad/pin map, net parity, clearance, power-loop ve DRC/short kontrolleri.
