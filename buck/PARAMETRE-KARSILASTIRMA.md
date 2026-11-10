# Sabit çıkış hedefinde L / f / C taraması

Analitik ön eleme: **11 V / 7,5 A / 82,5 W**. LTspice çalıştırılmadı; verim yüzdesi hesaplanmadı.

6272 kombinasyon incelendi; 2392 kombinasyon belirtilen analitik sınırları sağlıyor.
Giriş 20–26 V arasında 0,1 V adımla tarandı. Her noktada ideal duty Vo/Vin; gerçek kayıplı karşılaştırmada her kombinasyonun duty'si aynı 11 V çıkışı verecek şekilde ayrıca ayarlanmalı.

## Varsayımlar

- L ve her iki C aynı anda nominalden %20 düşük kabul edildi.
- Bobin akım ripple sınırı: 2,25 A p-p (%30 Iout).
- Çıkış ripple sınırı: 55 mV p-p; giriş ripple üst sınır hesabı: 200 mV p-p.
- ESRIN=15 mΩ ve ESROUT=20 mΩ bütün adaylarda sabit varsayıldı. Bunlar parça verisi değil.
- Giriş ripple hesabı, kondansatörün anahtarlama AC akımını taşıdığı üst sınır yaklaşımıdır. İdeal gerilim kaynağına doğrudan paralel bir CIN'in gerilim ripple'ı bu hesapla aynı olmaz; kaynak empedansı tanımlanmalı.
- Kalkış, yük adımı, sıcaklık, doyum ve kayıpların çıkış gerilimine etkisi bu taramada yok.

## Her frekansta en küçük L ile bulunan örnekler

Bu liste verim sıralaması değildir. Kapasitörler, aday listesinden sınırları sağlayan en küçük nominal değerlerdir; sınırdaki değerler nihai seçim değildir.

- **50 kHz / 82 µH / CIN 680 µF / COUT 470 µF**: ΔIL ≤ 1.935 A p-p, çıkış ripple ≤ 51.6 mV p-p, giriş ripple hesabı ≤ 194.6 mV p-p.
- **75 kHz / 56 µH / CIN 470 µF / COUT 330 µF**: ΔIL ≤ 1.889 A p-p, çıkış ripple ≤ 49.7 mV p-p, giriş ripple hesabı ≤ 191.8 mV p-p.
- **100 kHz / 39 µH / CIN 330 µF / COUT 330 µF**: ΔIL ≤ 2.034 A p-p, çıkış ripple ≤ 50.3 mV p-p, giriş ripple hesabı ≤ 197.4 mV p-p.
- **150 kHz / 27 µH / CIN 220 µF / COUT 150 µF**: ΔIL ≤ 1.959 A p-p, çıkış ripple ≤ 52.8 mV p-p, giriş ripple hesabı ≤ 196.8 mV p-p.
- **200 kHz / 18 µH / CIN 220 µF / COUT 220 µF**: ΔIL ≤ 2.204 A p-p, çıkış ripple ≤ 51.9 mV p-p, giriş ripple hesabı ≤ 181.1 mV p-p.
- **250 kHz / 15 µH / CIN 150 µF / COUT 150 µF**: ΔIL ≤ 2.115 A p-p, çıkış ripple ≤ 51.1 mV p-p, giriş ripple hesabı ≤ 189.5 mV p-p.
- **300 kHz / 12 µH / CIN 150 µF / COUT 150 µF**: ΔIL ≤ 2.204 A p-p, çıkış ripple ≤ 51.7 mV p-p, giriş ripple hesabı ≤ 179.9 mV p-p.

## Önceki referansın ek tolerans kontrolü

100 kHz / 39 µH / CIN 470 µF / COUT 220 µF için L ve C birlikte −%20 olduğunda çıkış ripple hesabı 55.13 mV p-p. Önceki 52,24 mV hesabı COUT nominal kalırken yapılmıştı. 55 mV sınırı bu ek köşede az farkla aşılır; COUT 220 µF henüz kesin seçim değildir.

## Verimi sıralamak için gereken model

η = Pout / Pin; her adayda Pout = 82,5 W korunmalı. İdeal kayıpsız elemanlar %100 verir ve fiziksel verim kazananı göstermez.

Bobin bakır kaybı IL_rms²·DCR, kondansatör kaybı IC_rms²·ESR ve anahtarlama kaybı E_cycle·f ile değişir. Büyük L'nin DCR ve çekirdek kaybı, düşük frekansın gerektirdiği daha büyük parçalar, gerçek parça verileriyle birlikte değerlendirilmelidir. JSON'da DCR başına bakır kaybı ve çevrim enerjisi başına anahtarlama kaybı katsayıları tutulur; toplam verim olarak sunulmaz.

Örneğin çevrim başına 1 µJ kayıp 50 kHz'te 0,05 W; 100 kHz'te 0,10 W; 200 kHz'te 0,20 W eder. Bu bir MOSFET'e atanmış kayıp değeri değil, duyarlılık hesabıdır.

Verim için gereken parça verileri:

- MOSFET RDS(on,T), Qg, Coss ve geçiş enerjisi
- Diyot Vf(I,T), kapasitans ve varsa ters toparlanma
- Her bobin adayının DCR(T), çekirdek/AC kaybı, Isat ve Irms verisi
- Kondansatörlerin ESR(f,T), etkin kapasitans ve ripple akımı sınırı
- Sürme enerjisi ve tanımlı giriş gücü ölçüm sınırı

İlk eleme sonrası gerçek kayıp verileriyle kısa liste oluşturulacak; ardından birlikte kurulacak LTspice güç katında aynı çıkış gücü ve kararlı durum koşullarıyla karşılaştırılacak.

Kaynaklar: [ADI — An Efficiency Primer](https://www.analog.com/en/resources/technical-articles/an-efficiency-primer-for-switchmode-dcdc-converter-power-supplies.html), [TI — How the Switching Frequency Affects the Performance of Buck Converter](https://www.ti.com/lit/an/slvaed3a/slvaed3a.pdf).
