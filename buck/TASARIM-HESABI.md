# Aşama 1 — Buck Güç Katı Hesabı

**Tarih:** 10 Kasım 2026. **Geçerli kapsam:** tek faz, asenkron, açık çevrim buck. Bu metindeki sayılar analitik başlangıç hesaplarıdır; LTspice'ta yeni şematikler henüz çalıştırılmadı.

## Tasarım girdileri

| Girdi | Değer |
|---|---:|
| Kaynak | 6S LiPo, 20–26 V (nominal 22.2 V) |
| Çıkış hedefi | 11 V |
| Yük tasarımı | 7.5 A, 82.5 W (gerçek yük hedefi yaklaşık 7 A) |
| Anahtarlama frekansı | 100 kHz |
| Devre | S1 + D1 + L1 + CIN + COUT + RLOAD |
| Başlangıç L1 | 33 µH, DCR varsayımı 20 mΩ |
| Başlangıç CIN | 440 µF, ESR varsayımı 25 mΩ |
| Başlangıç COUT | 1360 µF, ESR varsayımı 20 mΩ |

**Neden bu topoloji?** Girişin tamamı 11 V üstünde olduğundan step-down buck yeterlidir. Tek faz asenkron güç katı için tek anahtar, tek serbest geçiş diyotu ve LC filtresiyle hesap yapılır; senkron/çift faz ve kontrolcü mimarisi bu aşamada analiz konusu değildir. 100 kHz, bobin boyutu ile anahtarlama kaybı arasında başlangıç tercihi olup optimize edilmiş/ölçülmüş nihai değer değildir.

## Hesap

İdeal kararlı hal volt-saniye dengesi:

```text
(Vin - Vo) · D · T = Vo · (1-D) · T
D = Vo/Vin,   T = 1/f = 10 us
L >= Vo · (1 - Vo/Vin_max) / (0.30 · Iout · f) = 28.205 uH
L = 33 uH secildi (ilk aday)
DeltaIL_pp = Vo · (1 - Vo/Vin) / (L · f)
IL_peak = Iout + DeltaIL_pp/2
Vout_ripple_pp ≈ DeltaIL_pp/(8 f Cout) + DeltaIL_pp · ESRout
```

| Vin (V) | D ideal | DeltaIL (A p-p) | IL tepe (A) | Vout dalgalanması yaklaşık (mV p-p) |
|---:|---:|---:|---:|---:|
| 20 | 0.55000 | 1.500 | 8.250 | 31.38 |
| 22.2 | 0.49550 | 1.682 | 8.341 | 35.19 |
| 26 | 0.42308 | 1.923 | 8.462 | 40.23 |

Bobin %20 düşükse en yüksek girişte yaklaşık **2.404 A p-p** ve **8.702 A** kararlı tepe oluşur. Bu kararlı hale göre %30 pay, Isat için yaklaşık **11.31 A** yapar. **Kalkış tepe akımı bundan çok daha büyük olabilir**, dolayısıyla yalnız bu sayıyla parça seçimi tamamlanmış sayılmaz.

26 V, 7.5 A durumunda giriş kondansatörü RMS akımı için ideal yaklaşık üst sınır **3.75 A** (D = 0.5 yakınında); bobin RMS yaklaşık 7.52 A. Direnç yükü **11/7.5 = 1.467 ohm**, bu güçte en az 82.5 W'lık ideal yük eşdeğeridir.

## Kayıplı aday

- `buck-kayipli.asc` kaynak direnci 50 mΩ, anahtar Ron 30 mΩ, Schottky eşdeğer Vf 0.6 V + Ron 33 mΩ, bobin DCR 20 mΩ, giriş ESR 25 mΩ, çıkış ESR 20 mΩ varsayar.
- Duty yaklaşık düşüm denkleminden hesaplanır; bu **geri besleme değildir**. Her giriş değeri için duty sabitlenerek ayrı analiz yapılır.
- `buck-ideal.asc` eşdeğer dirençleri ihmal edilecek kadar küçültür ve D = Vo/Vin alır.
- Bu anahtar modeli gerçek MOSFET kapı yükünü ve anahtarlama geçiş kaybını içermez. Analitik verim, LTspice enerji verimi ve fiziksel ölçüm aynı şey değildir.

## Deney ve kabul planı

1. İdeal devreyi Vin = 20, 22.2, 26 V ve 7.5 A yük ayarı için çalıştır; Vo, DeltaIL, Ipeak ve dalgalanmayı hesapla karşılaştır.
2. Kayıplı devrede aynı üç noktayı dene; model parametrelerini raporla. Hesapla farkın nedenini açıkla.
3. Nominal Vin için belirlenen duty oranını **sabit tutarak** Vin 20 ve 26 V yap; açık çevrimin regülasyon yapmadığını göster.
4. 26 V hafif yükte (ör. 0.75 A) giriş ve çıkış dalga şekillerini karşılaştır; DCM olasılığını ve çıkış aşımını kontrol et.
5. 0–45 ms penceresinde startup Vout ve bobin akım tepesini ayrıca incele. Gerçek yük bağlantısı yok.
6. 33 µH toleransını, 100 kHz frekansı, 1360 µF seçimini ve daha küçük kapasitör adaylarını simülasyonla karşılaştırıp nihai değeri **ancak sonuç gördükten sonra** belirle.

**Kabul:** Aktif .asc dosyaları açılıp görsel olarak incelenebilir olmalı; simülasyonların ölçüm çıktıları ve parametreleri kaydedilmeli; hesap–simülasyon farkları açıkça açıklanmalı. Şematiklerin sembol pin bağlantıları statik olarak kontrol edildi; bu ortamda gerçek LTspice çalıştırması yapılmadı.

Eski kapalı çevrim, PWM/geri besleme ve çift faz hesap/çalışmaları: [arşiv](../archive/buck-onceki-calisma-2026-11-10/README.md).
