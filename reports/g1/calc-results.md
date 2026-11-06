# G1 hesap sonuçları

Birimli ve parametreli hesap kodu: `analysis/pdu_calc.py`. Her çift yolda mutlak ve yüzde fark raporlanır. Bu yolların çoğu aynı bağıntının aritmetik çapraz kontrolüdür; bağımsız fiziksel model doğrulaması değildir. Köşe enumerasyonu ile kapalı form yalnız algoritma çapraz kontrolüdür. Üretici silikonu veya ölçülmüş kartla bağımsız doğrulama sayısı sıfırdır; hesaplar fiziksel doğrulama değildir.

## İki yol doğrulama kapsamı

65 sayısal çift yol kaydı: 59 aynı denklem aritmetik çapraz kontrolü, 6 aynı denklem üzerinde farklı algoritma karşılaştırması, 0 bağımsız fiziksel model doğrulaması.
Bu sınıflandırma `calc-results.json` içindeki `validation_scope` alanında her satır için ayrıca bulunur.

## Güç katı

- 26 V, 400 kHz, Lmin=5.44 µH: bobin ripple 2.9164 A p-p (iki yol farkı 0 A).
- 7.5 A toplam ve varsayılan +10% faz paylaşım sapmasında tepe 5.5832 A; Vishay tabloda Isat 13.5 A ile marj 7.917 A. Exact aday var, BOM/stock onayı açık.
- Faz başı bobin bakır kaybı: 25°C DCR taraması 0.413 W; 125°C TCR varsayımı 0.575 W.
- RS: eşit olmayan paylaşım altında 0.136 W/faz; ≤50% güç kullanımı için parça en az 0.271 W olmalı. MPN/TCR/tolerans açık.
- COUT etkin kapasite taraması 92.65–241.53 µF; 10% yaşlanma ek varsayımdır. Aligned-ripple konservatif hesap 19.67 mVpp, ESR/ESL dahil değil.

## Regülasyon, döngü ve UVLO

- Nominal FB 10.996078 V; -40..125°C statik köşe 10.8333–11.1605 V (datasheet koşullu referans/bias ve direnç varsayımları).
- RCOMP 40 kHz varsayılan formülde 10.01–26.08 kΩ. Faz marjı ve gerçek crossover doğrulanamadı; COMP değerlerini fiziksel FRA ile ayarlayın.
- UVLO mevcut 180k/10k açma 17.711–20.332 V. 174k/10k varsayılan değişiklik 19.689 V üst köşe verir; EN sızıntısı ve TCR ayrıca açık. 20 V=3.33 V/hücre.

## eFuse, giriş koruması ve termal

- O1/S2E nominal ILIM formül değerleri 4.960/2.527 A; kesin dirençlerde datasheet garantili min/max doğrulanamadı.
- 53.3 V TVS clamp değeri varsayımsal sistem zarfıdır. Mutlak maksimum karşılaştırması pozitif marj verir, fakat transient/ESL/enerji/SOA koordinasyonu kanıtlanmadı. F1 akım/I²t/DC kesme değeri giriş empedansı bilinmediğinden hesaplanamadı.
- 82.5 W çıkışta varsayım verimleri: 80%: 20.62 W, 90%: 9.17 W, 95%: 4.34 W. Kart θ ve ortam koşulu açık olduğundan junction sıcaklık sonucu yok.

## Yönlendirme

Mevcut `calculate_routing_rules.py` girdi profili ve IPC-2221/Ohm yöntemi, G1 akımlarıyla `analysis/pdu_calc.py` içinde yeniden hesaplandı; `routing-input.json` kaynağı, `routing-comparison.json` sonucu taşır. O1 ve S2E yük bölüşümü ölçülmediğinden iki dal ayrı ayrı 7.5 A zarfında boyutlandı; eşzamanlı 15 A çalışma iddiası yoktur.
| Sınıf | Akım zarfı | 2L min iz | 2L IR drop | 4L min iz/yol | 4L IR drop | Via/geçiş 2L→4L |
|---|---:|---:|---:|---:|---:|---:|
| INPUT_POWER | 5.16 A | 3.38 mm | 50.00 mV | 1.69 mm | 50.00 mV | 11 / 12 |
| BUS_POWER | 7.50 A | 4.91 mm | 50.00 mV | 2.46 mm | 50.00 mV | 15 / 16 |
| PHASE_POWER | 5.58 A | 3.66 mm | 50.00 mV | 1.83 mm | 50.00 mV | 12 / 12 |
| O1_POWER | 7.50 A | 4.91 mm | 50.00 mV | 2.46 mm | 50.00 mV | 15 / 16 |
| S2E_POWER | 7.50 A | 4.91 mm | 50.00 mV | 2.46 mm | 50.00 mV | 15 / 16 |
| AUX_LOCAL | 0.60 A | 0.11 mm | 36.27 mV | 0.04 mm | 47.18 mV | 2 / 2 |
| CONTROL_SENSE | 0.05 A | 0.03 mm | 50.00 mV | 0.02 mm | 50.00 mV | 1 / 2 |

31.5 µm bakır, ΔT=20°C, 50 mm ve 50 mV varsayımı; 0.5 A/via ve 25 µm kaplama doğrulanmış fab değerleri değildir. 4L iç katman için dış iz fit'i yalnız duyarlılık taramasıdır.

## Çift yol kayıtları

| Hesap | Yöntem 1 | Yöntem 2 | Doğrulama kapsamı | Mutlak fark | % fark |
|---|---|---|---|---:|---:|
| inductor ripple at 26 V, minimum L and frequency | Vout*(1-Vout/Vin)/(Lmin*fmin) | (Vin-Vout)*D/(Lmin*fmin) | same_equation_arithmetic_crosscheck | 0 A p-p | 0% |
| phase peak current at 7.5 A total, +10% share | Iphase_avg + deltaIL/2 | Iout*(1+share_error)/2 + deltaIL/2 | same_equation_arithmetic_crosscheck | 0 A | 0% |
| two-phase output ripple, aligned conservative capacitor-only | (2*deltaIL)/(8*f*Cmin) | deltaIL/(4*f*Cmin) | same_equation_arithmetic_crosscheck | 0 V p-p | 0% |
| nominal feedback setpoint | Vref*(1+Rtop/Rbottom) | Vref*(Rtop+Rbottom)/Rbottom | same_equation_arithmetic_crosscheck | 0 V | 0% |
| cycle sense threshold lower-current corner | 50mV/(Rmax incl. TCR) | 50mV/(7.5mΩ*1.01*1.01) | same_equation_arithmetic_crosscheck | 0 A | 0% |
| cycle sense threshold upper-current corner | 62mV/(Rmin incl. TCR) | 62mV/(7.5mΩ*0.99*0.99) | same_equation_arithmetic_crosscheck | 0 A | 0% |
| Q1 conduction loss at 82.5 W, 20 V, 80% efficiency | I²*RDS(on), 25C datasheet max used as screen | (Pout/(Vin*η))²*16mΩ | same_equation_arithmetic_crosscheck | 0 W | 0% |
| COUT bank low sensitivity | vendor-summary Ceff × tolerance × X7S temp × assumed aging | per-part vendor Ceff × 8 × tolerance × X7S temp × assumed aging | same_equation_arithmetic_crosscheck | 0 F | 0% |
| COUT bank typical at 11 V | local vendor summary bank value | per-part vendor model × 8 | same_equation_arithmetic_crosscheck | 0 F | 0% |
| COUT bank upper sensitivity | vendor-summary upper bank sensitivity | per-part Ceff × 8 × tolerance × X7S temperature | same_equation_arithmetic_crosscheck | 2.71051e-20 F | 1.12224e-14% |
| FB lower static corner | 16-corner vertex enumeration | monotonic closed-form corner | independent_algorithm_same_equation | 0 V | 0% |
| FB upper static corner | 16-corner vertex enumeration | monotonic closed-form corner | independent_algorithm_same_equation | 0 V | 0% |
| existing 180k/10k lower UVLO | corner vertex enumeration | monotonic closed form | independent_algorithm_same_equation | 0 V | 0% |
| existing 180k/10k upper UVLO | corner vertex enumeration | monotonic closed form | independent_algorithm_same_equation | 0 V | 0% |
| candidate 174k/10k lower UVLO | corner vertex enumeration | monotonic closed form | independent_algorithm_same_equation | 0 V | 0% |
| candidate 174k/10k upper UVLO | corner vertex enumeration | monotonic closed form | independent_algorithm_same_equation | 0 V | 0% |
| O1 nominal ILIM formula | 1460/R(ohm)+0.11 | 1.460/R(kΩ)+0.11 | same_equation_arithmetic_crosscheck | 0 A | 0% |
| O1 dV/dt pin current | typical pin current / C_DVDT | 4.6 V/ms converted to V/s | same_equation_arithmetic_crosscheck | 0 V/s | 0% |
| O1 port capacitor energy 0 to 11 V | 0.5*C*V² | Q*V/2 where Q=C*V | same_equation_arithmetic_crosscheck | 0 J | 0% |
| O1 eFuse short pulse FET energy sensitivity | (Vin*Ishort)*t | Vin*t*Ishort | same_equation_arithmetic_crosscheck | 0 J | 0% |
| S2E nominal ILIM formula | 1460/R(ohm)+0.11 | 1.460/R(kΩ)+0.11 | same_equation_arithmetic_crosscheck | 0 A | 0% |
| S2E dV/dt pin current | typical pin current / C_DVDT | 4.6 V/ms converted to V/s | same_equation_arithmetic_crosscheck | 0 V/s | 0% |
| S2E port capacitor energy 0 to 11 V | 0.5*C*V² | Q*V/2 where Q=C*V | same_equation_arithmetic_crosscheck | 0 J | 0% |
| S2E eFuse short pulse FET energy sensitivity | (Vin*Ishort)*t | Vin*t*Ishort | same_equation_arithmetic_crosscheck | 0 J | 0% |
| O1 EN nominal bus threshold | Vth*(Rtop+Rbottom)/Rbottom | Vth*(1+Rtop/Rbottom) | same_equation_arithmetic_crosscheck | 1.77636e-15 V | 1.97636e-14% |
| O1 PG divider at 11V | Vin*Rbottom/(Rtop+Rbottom) | Vin/(1+Rtop/Rbottom) | same_equation_arithmetic_crosscheck | 0 V | 0% |
| S2E EN nominal bus threshold | Vth*(Rtop+Rbottom)/Rbottom | Vth*(1+Rtop/Rbottom) | same_equation_arithmetic_crosscheck | 1.77636e-15 V | 1.97636e-14% |
| S2E PG divider at 11V | Vin*Rbottom/(Rtop+Rbottom) | Vin/(1+Rtop/Rbottom) | same_equation_arithmetic_crosscheck | 0 V | 0% |
| sum of nominal O1 and S2E current limits | sum calculated channel limits | independent per-channel formula then sum | same_equation_arithmetic_crosscheck | 0 A | 0% |
| RCOMP for assumed 40 kHz target, low assumed Ceff | 2π*fc*(Vout/Vref)*(Rs/N*10/gm)*Ceff | (fc*2π*Ceff)*(Vout/Vref)*(Rs/(N*gm))*10 | same_equation_arithmetic_crosscheck | 1.81899e-12 ohm | 1.81797e-14% |
| RCOMP for assumed 40 kHz target, vendor typical | 2π*fc*(Vout/Vref)*(Rs/N*10/gm)*Ceff | (fc*2π*Ceff)*(Vout/Vref)*(Rs/(N*gm))*10 | same_equation_arithmetic_crosscheck | 0 ohm | 0% |
| RCOMP for assumed 40 kHz target, high assumed Ceff | 2π*fc*(Vout/Vref)*(Rs/N*10/gm)*Ceff | (fc*2π*Ceff)*(Vout/Vref)*(Rs/(N*gm))*10 | same_equation_arithmetic_crosscheck | 0 ohm | 0% |
| inductor copper loss per phase, hot DCR sensitivity | I_rms² × hot DCR | (I_DC² + deltaI²/12) × hot DCR | same_equation_arithmetic_crosscheck | 1.11022e-16 W | 1.92988e-14% |
| shunt power per phase, tolerance/TCR sensitivity | I_rms² × Rmax(T) | (I_DC² + deltaI²/12) × Rnom × tolerance × TCR | same_equation_arithmetic_crosscheck | 0 W | 0% |
| battery input current at 82.5 W / 80% | Pout/(Vin×efficiency) | Pin/Vin | same_equation_arithmetic_crosscheck | 0 A | 0% |
| proposed comparator high trip corner | Vtrip_nom × (1+tolerance) | nominal threshold plus relative error | same_equation_arithmetic_crosscheck | 0 V | 0% |
| O1 capacitive overshoot at 10 A / 0.5 us / 10 uF | I×t/C | (I×t) charge / C | same_equation_arithmetic_crosscheck | 0 V | 0% |
| INPUT_POWER 2-layer thermal width | IPC-2221 area then copper conversion | area in mil² divided by copper thickness in mil | same_equation_arithmetic_crosscheck | 0 mm | 0% |
| INPUT_POWER 2-layer IR-drop width | rho*length*current/(copper*allowed_drop) | rho*length/(copper*(allowed_drop/current)) | same_equation_arithmetic_crosscheck | 4.44089e-16 mm | 1.31522e-14% |
| INPUT_POWER 4-layer path thermal width | IPC-2221 area then copper conversion | area in mil² divided by copper thickness in mil | same_equation_arithmetic_crosscheck | 1.11022e-16 mm | 1.37199e-14% |
| INPUT_POWER 4-layer path IR-drop width | rho*length*current/(copper*allowed_drop) | rho*length/(copper*(allowed_drop/current)) | same_equation_arithmetic_crosscheck | 2.22045e-16 mm | 1.31522e-14% |
| BUS_POWER 2-layer thermal width | IPC-2221 area then copper conversion | area in mil² divided by copper thickness in mil | same_equation_arithmetic_crosscheck | 0 mm | 0% |
| BUS_POWER 2-layer IR-drop width | rho*length*current/(copper*allowed_drop) | rho*length/(copper*(allowed_drop/current)) | same_equation_arithmetic_crosscheck | 8.88178e-16 mm | 1.80842e-14% |
| BUS_POWER 4-layer path thermal width | IPC-2221 area then copper conversion | area in mil² divided by copper thickness in mil | same_equation_arithmetic_crosscheck | 0 mm | 0% |
| BUS_POWER 4-layer path IR-drop width | rho*length*current/(copper*allowed_drop) | rho*length/(copper*(allowed_drop/current)) | same_equation_arithmetic_crosscheck | 4.44089e-16 mm | 1.80842e-14% |
| PHASE_POWER 2-layer thermal width | IPC-2221 area then copper conversion | area in mil² divided by copper thickness in mil | same_equation_arithmetic_crosscheck | 0 mm | 0% |
| PHASE_POWER 2-layer IR-drop width | rho*length*current/(copper*allowed_drop) | rho*length/(copper*(allowed_drop/current)) | same_equation_arithmetic_crosscheck | 4.44089e-16 mm | 1.21464e-14% |
| PHASE_POWER 4-layer path thermal width | IPC-2221 area then copper conversion | area in mil² divided by copper thickness in mil | same_equation_arithmetic_crosscheck | 0 mm | 0% |
| PHASE_POWER 4-layer path IR-drop width | rho*length*current/(copper*allowed_drop) | rho*length/(copper*(allowed_drop/current)) | same_equation_arithmetic_crosscheck | 2.22045e-16 mm | 1.21464e-14% |
| O1_POWER 2-layer thermal width | IPC-2221 area then copper conversion | area in mil² divided by copper thickness in mil | same_equation_arithmetic_crosscheck | 0 mm | 0% |
| O1_POWER 2-layer IR-drop width | rho*length*current/(copper*allowed_drop) | rho*length/(copper*(allowed_drop/current)) | same_equation_arithmetic_crosscheck | 8.88178e-16 mm | 1.80842e-14% |
| O1_POWER 4-layer path thermal width | IPC-2221 area then copper conversion | area in mil² divided by copper thickness in mil | same_equation_arithmetic_crosscheck | 0 mm | 0% |
| O1_POWER 4-layer path IR-drop width | rho*length*current/(copper*allowed_drop) | rho*length/(copper*(allowed_drop/current)) | same_equation_arithmetic_crosscheck | 4.44089e-16 mm | 1.80842e-14% |
| S2E_POWER 2-layer thermal width | IPC-2221 area then copper conversion | area in mil² divided by copper thickness in mil | same_equation_arithmetic_crosscheck | 0 mm | 0% |
| S2E_POWER 2-layer IR-drop width | rho*length*current/(copper*allowed_drop) | rho*length/(copper*(allowed_drop/current)) | same_equation_arithmetic_crosscheck | 8.88178e-16 mm | 1.80842e-14% |
| S2E_POWER 4-layer path thermal width | IPC-2221 area then copper conversion | area in mil² divided by copper thickness in mil | same_equation_arithmetic_crosscheck | 0 mm | 0% |
| S2E_POWER 4-layer path IR-drop width | rho*length*current/(copper*allowed_drop) | rho*length/(copper*(allowed_drop/current)) | same_equation_arithmetic_crosscheck | 4.44089e-16 mm | 1.80842e-14% |
| AUX_LOCAL 2-layer thermal width | IPC-2221 area then copper conversion | area in mil² divided by copper thickness in mil | same_equation_arithmetic_crosscheck | 1.38778e-17 mm | 1.28108e-14% |
| AUX_LOCAL 2-layer IR-drop width | rho*length*current/(copper*allowed_drop) | rho*length/(copper*(allowed_drop/current)) | same_equation_arithmetic_crosscheck | 0 mm | 0% |
| AUX_LOCAL 4-layer path thermal width | IPC-2221 area then copper conversion | area in mil² divided by copper thickness in mil | same_equation_arithmetic_crosscheck | 6.93889e-18 mm | 1.66632e-14% |
| AUX_LOCAL 4-layer path IR-drop width | rho*length*current/(copper*allowed_drop) | rho*length/(copper*(allowed_drop/current)) | same_equation_arithmetic_crosscheck | 0 mm | 0% |
| CONTROL_SENSE 2-layer thermal width | IPC-2221 area then copper conversion | area in mil² divided by copper thickness in mil | same_equation_arithmetic_crosscheck | 0 mm | 0% |
| CONTROL_SENSE 2-layer IR-drop width | rho*length*current/(copper*allowed_drop) | rho*length/(copper*(allowed_drop/current)) | same_equation_arithmetic_crosscheck | 6.93889e-18 mm | 2.11924e-14% |
| CONTROL_SENSE 4-layer path thermal width | IPC-2221 area then copper conversion | area in mil² divided by copper thickness in mil | same_equation_arithmetic_crosscheck | 0 mm | 0% |
| CONTROL_SENSE 4-layer path IR-drop width | rho*length*current/(copper*allowed_drop) | rho*length/(copper*(allowed_drop/current)) | same_equation_arithmetic_crosscheck | 3.46945e-18 mm | 2.11924e-14% |

Tüm sayısal sınırlar `AÇIK` maddeler çözülmeden bileşen seçimi veya üretim onayı oluşturmaz.
