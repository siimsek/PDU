# Tasarım Hesabı — Açık Çevrim Buck

**Tarih:** 10 Kasım 2026
**Sınıf:** analitik hesap ve model varsayımları; LTspice sonucu veya fiziksel ölçüm değildir.

Akım dalgalanması, tepe/RMS akımı ve kondansatör ripple denklemleri [Analog Devices Buck Power Stage Design Equations](https://www.analog.com/en/resources/app-notes/buck-power-stage-design-equations.html) uygulama notundaki buck güç katı ilişkileriyle tutarlıdır. Buradaki hesaplar belirtilen açık çevrim hedeflerine uygulanmıştır.

Bu dosya ilk referans noktasının hesabını tutar. Güncel [L / f / C karşılaştırması](PARAMETRE-KARSILASTIRMA.md), aynı çıkış gücünde farklı adayları ve L/C toleranslarını inceler. Referans noktası verim bakımından seçilmiş bir optimum değildir.

## Girdiler ve seçim yaklaşımı

| Girdi | Değer |
|---|---:|
| Vin | 20 / 22,2 / 26 V |
| Vo hedefi | 11 V |
| Iout | 7,5 A |
| Pout | 82,5 W |
| fsw | 100 kHz |
| Bobin tolerans köşesi | −%20 |
| İzin verilen nominal bobin ripple hedefi | ≤ %25 × Iout |
| Çıkış ripple tasarım kontrolü | ≤ 55 mV p-p (%0,5 Vo) |
| Giriş ripple kontrolü | ≤ 1% × 20 V = 0,20 V p-p |

Küçük ve büyük bileşen seçimi arasında tek bir evrensel “en iyi” değer yoktur. Buradaki ilk aday; ripple hedefleri, makul standart değerler ve 100 kHz açık çevrim davranışıyla seçildi. Boyut, kayıp, sıcaklık, tolerans ve kalkış sonuçları LTspice ve gerçek parça verileriyle incelenmeden nihai tasarım değildir.

## Duty ve bobin akımı

İdeal sürekli iletim (CCM) kararlı durumunda:

```text
D = Vo / Vin
T = 1 / fsw = 10 us
ΔIL_pp = Vo · (1 − D) / (L · fsw)
IL_peak = Iout + ΔIL_pp / 2
IL_rms = sqrt(Iout² + ΔIL_pp² / 12)
```

Bobin ripple'ı yüksek girişte en büyüktür. 26 V ve %25 ripple hedefi için:

```text
L_min = Vo · (1 − Vo / Vin_max) / (0.25 · Iout · fsw)
      = 33.85 uH
```

Bir sonraki yaygın standart değer olarak **39 µH** aday alındı. Bu değer için en kötü girişte nominal ripple yaklaşık 1,627 A p-p (%21,7). Bobin −%20 toleransla 31,2 µH olduğunda ripple yaklaşık 2,034 A p-p (%27,1), kararlı tepe akımı 8,517 A olur.

| Vin (V) | İdeal duty | ΔIL, L=39 µH (A p-p) | IL tepe (A) |
|---:|---:|---:|---:|
| 20 | 0,5500 | 1,269 | 8,135 |
| 22,2 | 0,4955 | 1,423 | 8,212 |
| 26 | 0,4231 | 1,627 | 8,314 |

−%20 bobin toleransındaki kararlı tepeye %30 tasarım payı eklenirse Isat ölçütü yaklaşık **11,07 A** çıkar. Bu yalnızca kararlı durum ölçütüdür; kalkış tepe akımı daha yüksek olabilir ve simülasyonla ayrıca görülmelidir. Bu sayı gerçek bobin seçimi değildir.

## Kondansatör kontrolü

İdeal buck giriş akımı darbeli olduğundan CIN'in RMS ripple akımı önemlidir. Üçgen bobin ripple'ı dahil yaklaşık RMS kontrolü:

```text
ICIN_rms ≈ sqrt(D(1−D)·Iout² + D·ΔIL_pp²/12)
```

En büyük değer çalışma noktalarımızda yaklaşık **3,76 A RMS**. Gerçek kondansatör bankasının toplam ripple akımı derecesi bu değeri sıcaklık ve ömür payıyla karşılamalıdır.

Giriş ripple'ı için kullanılan yaklaşık model:

```text
ΔVCIN ≈ Iout·D·(1−D) / (fsw·CIN)
ΔVESR_IN ≈ (Iout + ΔIL_pp/2) · ESRIN
ΔVIN_pp ≈ ΔVCIN + ΔVESR_IN
```

CIN = **470 µF**, ESRIN = **15 mΩ** varsayımıyla ve −%20 bobin toleransı dahil en yüksek hesaplanan giriş ripple'ı yaklaşık **0,167 V p-p** olur. Bu, 20 V girişin %1'i olan 0,20 V hedefinin altındadır. ESR yalnızca analiz varsayımıdır; gerçek ESR ve ripple akımı veri sayfasından alınmalıdır.

Çıkış ripple'ının kapasitif ve ESR bileşenleri:

```text
ΔVCOUT ≈ ΔIL_pp / (8·fsw·COUT)
ΔVESR_OUT ≈ ΔIL_pp · ESRout
ΔVOUT_pp ≈ ΔVCOUT + ΔVESR_OUT
```

COUT = **220 µF**, ESRout = **20 mΩ** varsayımıyla L=39 µH ve Vin=26 V'ta ripple yaklaşık **41,8 mV p-p**; bobin −%20 köşesinde yaklaşık **52,2 mV p-p** çıkar. Bu değer 55 mV hedefinin altındadır. Bu basit kararlı ripple hesabı yük adımı/kalkış cevabını kanıtlamaz.

COUT da aynı anda −%20 olduğunda ripple yaklaşık **55,13 mV p-p** olur. Bu ek tolerans köşesinde 55 mV sınırı az farkla aşılır. Tarama bu köşeyi içerir; örneğin 100 kHz / 39 µH için 330 µF çıkış adayı, aynı ESR varsayımıyla yaklaşık 50,3 mV p-p verir.

## Yük ve açık çevrim davranışı

```text
RLOAD = Vo / Iout = 11 / 7.5 = 1.467 ohm
PLOAD = Vo · Iout = 82.5 W
```

RLOAD LTspice'ta yükü temsil eder. Gerçek direnç olarak kurulursa 82,5 W ısıtır; fiziksel yük bileşeni seçilmedi.

Nominal Vin=22,2 V duty'si `D=0,4955` sabitlenirse ideal çıkış yaklaşık `D·Vin` olur:

| Vin (V) | Sabit duty ile ideal Vo (V) | 1,467 Ω yükün akımı (A) |
|---:|---:|---:|
| 20 | 9,91 | 6,76 |
| 22,2 | 11,00 | 7,50 |
| 26 | 12,88 | 8,78 |

Dolayısıyla açık çevrim devrede sabit duty ile giriş değişirken 11 V regülasyonu yoktur. 26 V girişte 12 V üzerinde çıkış oluşabileceği için gerçek cihaz/yük bağlanmaz.

## Sonraki doğrulama

Önce kullanıcıyla LTspice'ta ideal güç katı sıfırdan çizilecek. Bağlantılar ve değerler doğrulandıktan sonra 20 / 22,2 / 26 V nominal yükte çalıştırılır; bobin akımı, çıkış ripple'ı ve kalkış incelenir. Ardından kayıplı model, sabit duty giriş değişimi ve bobin toleransı eklenir. Gerçek bileşen seçimi için MPN veri sayfaları ayrıca değerlendirilir.
