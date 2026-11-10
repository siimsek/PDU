# D-004 — hesapların karşılaştırma öncesi kaydı

- Hesap tarihi: 2026-11-07
- Model: tek faz üst anahtar kısa devresi; ikinci faz fault kaynağı sayılmadı.
- Girdi: V_IN=26 V, V_BUS(0)=11.1605 V, C_eff=370.6 µF, R_source=20 mΩ, I_phase(0)=5.58 A (D-004 paketindeki G5 yanıt girdisi), I_trip,max=13.6 A (tasarım zarfı).
- L modeli: L=6.8 µH × 0.8 × f; f∈{0.05,0.10,0.15,0.20,0.25,0.30,0.40,0.50}. f alt sınırı bu taramada fault başlangıcından kapamaya kadar sabit tutuldu; Vishay 16 A üstü tipik grafik dışı akıma ekstrapolasyon yapılmadı.
- Diferansiyel denklem: dI/dt=(26−V_BUS−0.020I)/L; dV_BUS/dt=I/C_eff. ODE, RK4 ve 2 ns adımla çözüldü.
- Not: Bu hesap fiziksel ölçüm değildir. f-floor taraması verilen sınır senaryolarıdır; gerçek L(I) eğrisi veya üretim garantisi değildir.

## OVP eşik üst sınırı

R_OVT=8.25 kΩ ±0.1%, R_OVB=2.32 kΩ ±0.1%, REF5025A=2.5 V ±0.1%; TLV3601 için |V_OS|≤5 mV, |I_B|≤5 µA ve V_HYST≤5 mV. R_TH=R_OVT||R_OVB=1.810 kΩ. Yükselen trip için tüm hata payları eşiği yukarı taşıyacak yönde toplandı:

V_trip,max=(2.5025+0.005+5 µA×1.810 kΩ+0.005)×(1+8.25825/2.31768)=11.5062 V.

Nominal eşik: 2.5×(1+8.25/2.32)=11.3901 V. Üretici sınırları: TI REF5025A-Q1 ve TLV3601 veri sayfaları.

## Sonuçlar

| L alt sınırı f | Akım yolu: kapama gecikmesi 2.048 µs, V_O1,peak | Ölçülen yol: gerçek gecikme 3.1 µs, V_O1,peak | Yalnız gerilim yolu: C_eff=370.6 µF, V_trip,max, V_O1,peak | Yalnız gerilim yolu için gereken C_eff | 11.58125 µF/adet ile adet |
|---:|---:|---:|---:|---:|---:|
| 0.05 | 11.5267 V | 11.9162 V | 12.3606 V | 842.60 µF | 73 |
| 0.10 | 11.3906 V | 11.6140 V | 12.0784 V | 467.16 µF | 41 |
| 0.15 | 11.3464 V | 11.5104 V | 11.9602 V | 370.60 µF | 32 |
| 0.20 | 11.3256 V | 11.4591 V | 11.8920 V | 370.60 µF | 32 |
| 0.25 | 11.3148 V | 11.4297 V | 11.8467 V | 370.60 µF | 32 |
| 0.30 | 11.3089 V | 11.4113 V | 11.8137 V | 370.60 µF | 32 |
| 0.40 | 11.3041 V | 11.3908 V | 11.7687 V | 370.60 µF | 32 |
| 0.50 | 11.3044 V | 11.3815 V | 11.7391 V | 370.60 µF | 32 |

Akım yolunun 13.6 A eşiğinden sonra izin verilen en büyük gecikmesi f=0.05'te 3.29 µs; sırasıyla f=0.10…0.50 için 4.45, 5.27, 5.94, 6.49, 6.97, 7.76 ve 8.40 µs. Bu nedenle ölçülen gerçek gecikme ≤3.1 µs sınırı en kötü tarama noktasında 0.19 µs sayısal pay bırakır. Ölçüm belirsizliği U≤0.1 µs ise tezgâh göstergesi kabul sınırı ≤3.0 µs seçildi.

## Garantili sensör alternatifi için sınır

TI INA301A1-Q1'in total alert propagation max değeri, 1 mV giriş overdrive ve veri sayfası varsayılan test koşullarında 1 µs. 7.5 mΩ şöntte 1 mV=0.1333 A'dır. Bu nedenle cihazın gerçek en yüksek trip eşiği 13.467 A'yı aşmamalıdır ki 13.6 A'da en az 1 mV overdrive oluşsun; 13.3 A tasarım üst sınırı daha fazla pay bırakır. Mevcut hesaplanan 13.5344 A üst köşe bu koşulu karşılamaz. Ayrıca 1 µs tablosu tüm sıcaklık aralığı için açık bir guaranteed max vermediğinden bu alternatif tek başına çevresel köşeleri kapatmaz. Hesap tablosunda 2.048 µs tam zincir bütçesi varsayıldı (INA301 1 µs + D-004'te verilen 1.048 µs kalan yol); bu, tezgâh doğrulamasıyla teyit edilmelidir.

## BUILDER karşılaştırması (hesaptan sonra)

- `reports/g4/n1-results.json`: OVP-only worst 12.146355 V, OCP-closed worst 11.410643 V, existing chain delay 2.556067 µs, model Ceff=378.7056 µF, `v_guarantee=11.764650 V`.
- Aynı nominal OVP eşik 11.3901 V ve Ceff 370.6 µF ile benim f=0.05 sonucu 12.147988 V (+0.001633 V, +0.0134%).
- Worst-high threshold 11.5062 V ile benim f=0.05 OVP sonucu 12.360621 V; builder'a göre +0.214266 V (+1.764%). Bu fark doğrudan karşılaştırılabilir değil: benim ODE f-floor'ı tüm fault boyunca sabit tutuyor; BUILDER tipik 0–16 A eğrisini 16 A'dan öteye eğimle ekstrapole ediyor ve farklı Ceff/threshold kullanıyor. Her iki koşum da 12.0 V'u geçiyor.
- Benim INA301 öneri modeli (2.048 µs) OCP worst 11.526685 V, BUILDER mevcut-chain sonucu 11.410643 V'a göre +0.116042 V (+1.017%); sensör zamanı/L(I) modeli aynı olmadığı için bu da apples-to-apples değildir.
- Körlük koşulu tam korunmadı: BUILDER sonuç dosyalarından bazıları, bağımsız hesap kaydı yazılmadan önce yanlışlıkla açıldı. Sonuçlar hesapları kurmak için kullanılmadı; bu kıyas bölümü hesap kaydı sonrasında eklendi.
