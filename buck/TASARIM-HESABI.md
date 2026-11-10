# Tasarım Hesabı: Topoloji Kararı ve Güç Katı Değerleri

**Tarih:** 10 Kasım 2026. **Giriş:** 20–26 V (nominal 22,2 V). **Çıkış:** 11 V, tasarım akımı 7,5 A (hedef yük 7 A).

Bu belgedeki sayılar `buck/hesap.py` ve `buck/ltspice_sina.py` çıktılarından üretilir. Hepsi hesap ve simülasyondur, fiziksel ölçüm yoktur.

## 1. Sonuç

**Karar: tek faz asenkron buck, 100 kHz.** Hocanın gösterdiği devrenin kendisidir: S1, FD, L, C.

Güç katı için parçaların sağlaması gereken değerler:

| Eleman | Değer | Akım | Gerilim | Diğer şartlar |
|---|---|---|---|---|
| L1 bobin | **33 µH** ±%20 | Isat ≥ 11,3 A, Irms ≥ 9,0 A | Anahtarlama düğümü 26 V | DCR ≤ 20 mΩ |
| Cout | **2 × 680 µF** (1360 µF), yanına 2 × 10 µF seramik | Her biri ≥ 0,35 A RMS | ≥ 35 V | Her birinin ESR'si ≤ 40 mΩ |
| Cin | **2 × 220 µF** (440 µF), yanına 2 × 4,7 µF seramik | Her biri ≥ 1,88 A RMS | ≥ 50 V | Her birinin ESR'si ≤ 50 mΩ |
| S1 MOSFET | Rds ≤ 30 mΩ, Qg ≤ 100 nC | 8,70 A tepe, 5,56 A RMS, Id ≥ 20 A seçilir | VDS ≥ 60 V | Toplam ısıl direnç ≤ 38,9 K/W |
| FD Schottky | Vf ≤ 0,6 V (7,5 A'de) | 8,70 A tepe, 4,33 A ortalama, ≥ 15 A sınıfı | VR ≥ 60 V | Toplam ısıl direnç ≤ 30,1 K/W |
| Test yükü | 1,467 Ω | 7,5 A | 11 V | 82,5 W; 7 A için 1,571 Ω, 77 W |

Duty oranı Vin 20 / 22,2 / 26 V için ideal 0,550 / 0,495 / 0,423, kayıplı modelde 0,577 / 0,520 / 0,445.

Gerilim sınıfları için çalışma geriliminin yaklaşık iki katı alındı, çünkü anahtarlama düğümünde ringing oluşur. Seramik kapasitör adetleri hesapla değil, yüksek frekans yolu için seçimle konuldu.

**Henüz kesin olmayanlar:** S1'in P-MOS mu N-MOS mu olacağı, kapı sürücüsü, PWM üreteci, geri besleme ve yumuşak başlatma. Bunlar hocaya sorulacak sorulara bağlıdır (PROJE-TANIMI Bölüm 7) ve L ile C değerlerini değiştirmez.

**Önemli sınır:** Tepe akım 8,70 A kararlı durum değeridir. Yumuşak başlatma olmadan ilk açılışta bobin akımı çok daha yükselir (PROJE-TANIMI T7).

## 2. Seçeneklerin karşılaştırması

Dört seçenek aynı girdiler ve aynı varsayımlarla hesaplandı. Çift fazda bobin başına DCR 40 mΩ alındı, böylece toplam bakır kaybı tek fazla eşit tutuldu.

| Ölçüt | A: Tek faz asenkron | B: Tek faz senkron | C: Çift faz 180° asenkron | D: Çift faz 180° senkron |
|---|---|---|---|---|
| Bobin | 1 × 33 µH | 1 × 33 µH | 2 × 68 µH | 2 × 68 µH |
| Faz başına tepe akım | 8,70 A | 8,70 A | 4,33 A | 4,33 A |
| Toplam bobin enerjisi | 1,25 mJ | 1,25 mJ | 1,28 mJ | 1,28 mJ |
| Giriş kapasitörü RMS | 3,75 A | 3,75 A | 1,35 A | 1,35 A |
| Çıkış dalgalanması | 50,3 mV | 50,3 mV | 6,4 mV | 6,4 mV |
| En kötü kayıp | 5,55 W | 4,12 W | 5,18 W | 3,27 W |
| En kötü verim | %93,7 | %95,2 | %94,1 | %96,2 |
| MOSFET / Schottky | 1 / 1 | 2 / 0 | 2 / 2 | 4 / 0 |
| Kapı sürücü kanalı | 1 | 2 | 2 | 4 |
| Ölü zaman gerekir mi | Hayır | Evet | Hayır | Evet |
| 180° PWM gerekir mi | Hayır | Hayır | Evet | Evet |
| Akım paylaşım devresi | Hayır | Hayır | Evet | Evet |
| Göreli maliyet | 12,0 | 13,8 | 20,8 | 23,4 |
| Tasarım ve hata ayıklama | **En kolay** | Orta | Zor | En zor |

Göreli maliyet tahmindir, teklif değildir. Parça seçilince gerçek fiyatla güncellenir. Birim ağırlıklar `hesap.py` içindeki `MALIYET` tablosundadır.

**Neden tek faz asenkron:**

- **Çift faz bobinde tasarruf etmiyor.** Aynı yüzde dalgalanmada toplam bobin enerjisi 1,25 mJ yerine 1,28 mJ çıkıyor. Yani yalnızca iki ayrı daha küçük bobin alıyoruz.
- **Çift fazın kazancı küçük, bedeli büyük.** Asenkron çift fazda en kötü verim %93,7 yerine %94,1 oluyor, çünkü kaybın büyük kısmı diyotta ve o azalmıyor. Göreli maliyet ise 12,0 yerine 20,8 oluyor.
- **Çift fazın gerçek faydası kapasitörlerde.** Giriş RMS akımı 3,75 A yerine 1,35 A, çıkış dalgalanması 50,3 mV yerine 6,4 mV oluyor. 82,5 W için bu, birkaç kapasitörle zaten çözülüyor.
- **Çift faz akım paylaşım devresi ister.** LTspice'te fazlar arasında yalnız 0,005 duty farkı (50 ns) akımları 2,87 A / 4,66 A yapıyor, 0,01 farkta 2,03 A / 5,54 A oluyor. Basit gerilim modlu kontrolle dengede kalmaz.
- **Senkron bir sonraki adımdır.** Diyot yerine MOSFET kullanmak en kötü kaybı 5,55 W yerine 4,12 W yapar, fakat ölü zaman ve ikinci kapı sürücüsü gerekir, yanlış ayar iki MOSFET'i birden yakar. Aynı L ve C ile sonradan yapılabilir.

**Elenen diğer seçenekler:**

- **Doğrusal regülatör:** 26 V'ta 112,5 W ısı, verim %42,3.
- **SEPIC / buck-boost:** Çıkış her zaman girişten düşük olduğu için gerekmiyor. Anahtar 37 V ve yaklaşık 11,6 A görür, iki bobin ve ek kuplaj kapasitörü ister.
- **Hazır modül veya buck entegresi:** Hocanın kararıyla kapsam dışı.

## 3. Hesap adımları

**Varsayımlar** (parça seçilince gerçek değerlerle değişir): Vf = 0,6 V, Rds = 30 mΩ, DCR = 20 mΩ, kenar başına geçiş 60 ns, kaynak direnci 50 mΩ, ortam 50 °C, Tj üst sınırı 125 °C.

**Frekans.** Yükseldikçe bobin küçülür, kayıp artar. 100 kHz, kaybı ve bobin boyutunu dengeler; 26 V'ta iletim süresi 4,23 µs olur ve elle kurulan sürücüye yeterli pay kalır.

| f | Gereken L | Seçilen L | Bobin enerjisi | Anahtarlama kaybı | Toplam kayıp | Verim |
|---|---|---|---|---|---|---|
| 50 kHz | 56,4 µH | 68 µH | 2,55 mJ | 0,58 W | 4,97 W | %94,3 |
| 75 kHz | 37,6 µH | 39 µH | 1,53 mJ | 0,88 W | 5,26 W | %94,0 |
| **100 kHz** | 28,2 µH | 33 µH | 1,25 mJ | 1,17 W | 5,55 W | %93,7 |
| 150 kHz | 18,8 µH | 22 µH | 0,83 mJ | 1,75 W | 6,14 W | %93,1 |
| 200 kHz | 14,1 µH | 15 µH | 0,58 mJ | 2,34 W | 6,72 W | %92,5 |

**Bobin.** %30 dalgalanma seçildi:

```text
L ≥ Vo·(1 − Dmin) / (r·Io·f) = 28,2 µH  →  33 µH
ΔI = 1,92 A,  L −%20 iken ΔI = 2,40 A
Ipk = Io + ΔI/2 = 8,70 A
Isat ≥ 1,3 · Ipk = 11,3 A
Irms = √(Io² + ΔI²/12) = 7,52 A,  1,2 pay ile 9,0 A
CCM sınırı: Io > ΔI/2 = 0,96 A
```

| Dalgalanma | Seçilen L | ΔI | Tepe akım | Gereken Isat | Bobin enerjisi |
|---|---|---|---|---|---|
| %20 | 47 µH | 1,35 A | 8,34 A | 10,85 A | 1,64 mJ |
| %30 | 33 µH | 1,92 A | 8,70 A | 11,31 A | 1,25 mJ |
| %40 | 22 µH | 2,88 A | 9,30 A | 12,09 A | 0,95 mJ |

**Çıkış kapasitörü.** İki şart var, büyük olan belirler:

```text
Dalgalanma (110 mV hedef): C ≥ 273 µF,  ESR ≤ 41,2 mΩ
Yük adımı 7 → 0,75 A, kesim 10 kHz:  ΔV ≈ ΔI/(2π·fc·C) + ΔI·ESR
                                     = 73,1 mV + 125,0 mV = 198,1 mV
```

Yük adımı hedefi ±%2 (220 mV), yani bu da bir öneridir. Dalgalanma için 273 µF yeterken 2 × 680 µF seçilmesinin nedeni yük adımıdır. Bu seçim PROJE-TANIMI'ndaki 1000 µF başlangıç değerinin yerine geçer. Sonuç: dalgalanma üst sınırı 50,3 mV, LC kutbu 751 Hz, ESR sıfırı 5851 Hz.

**Giriş kapasitörü.**

```text
ICin,rms = Io·√(D(1−D)) = 3,75 A  (en kötü, D ≈ 0,5)
C ≥ Io·D(1−D) / (f·ΔV) = 187,5 µF  (100 mV için)
440 µF ile: 42,6 mV kapasitif + 218 mV ESR
```

**Kayıplar ve ısı** (tek faz asenkron):

| Kalem | Vin = 20 V | Vin = 26 V |
|---|---|---|
| FD iletimi | 1,90 W | 2,50 W |
| S1 anahtarlama | 0,90 W | 1,17 W |
| Bobin DCR | 1,13 W | 1,13 W |
| S1 iletimi | 0,98 W | 0,76 W |
| **Toplam / verim** | **4,91 W, %94,4** | **5,55 W, %93,7** |

Çekirdek kaybı, kapı sürme, ringing ve diyot toparlanması dahil değildir. Isıl dirençler `(125 − 50) / P` ile bulundu; FD ve S1 için soğutucu gerekir.

## 4. LTspice doğrulaması

Devre: seçilen L ve C, ESR ve DCR, 50 mΩ kaynak direnci, 30 mΩ davranışsal anahtar, 0,6 V diyot. Anahtarlama kaybı modelde yoktur.

| Durum | Vo | ΔVo | ΔIL | Cin RMS | Verim (anahtarlama hariç) |
|---|---|---|---|---|---|
| Tek faz, 20 V | 10,967 V | 29,3 mV | 1,48 A | 2,47 A | %94,1 |
| Tek faz, 22,2 V | 10,966 V | 33,3 mV | 1,69 A | 2,50 A | %94,1 |
| Tek faz, 26 V | 10,965 V | 38,7 mV | 1,96 A | 2,49 A | %94,0 |
| Tek faz, 26 V, L −%20 | 10,965 V | 48,4 mV | 2,45 A | 2,50 A | %94,0 |
| Çift faz, 20 V | 10,994 V | 3,9 mV | — | 0,92 A | %94,8 |
| Çift faz, 22,2 V | 10,997 V | 1,4 mV | — | 0,54 A | %94,8 |
| Çift faz, 26 V | 10,994 V | 3,7 mV | — | 0,79 A | %94,7 |

- 26 V, L −%20 için ΔIL hesapta 2,40 A, LTspice'te 2,45 A. Dalgalanma hesapta en çok 50,3 mV, LTspice'te 48,4 mV.
- Cin RMS LTspice'te 2,50 A çıkıyor, hesapta 3,75 A. Modeldeki kaynak salt dirençtir ve akımın bir kısmını paylaşır. Gerçekte batarya kablosu endüktiftir, bu yüzden kapasitör 3,75 A'e göre seçilir.
- Geri besleme yok, duty elle verildi. Bu nedenle Vo 11 V'un biraz altındadır.

## 5. Sıradaki adım: parça seçimi

Bölüm 1'deki tablo, parça ararken filtre olarak kullanılır. Seçilen her parça için üretici verisindeki gerçek Vf, Rds, DCR, ESR ve geçiş süreleri `hesap.py` içine girilir, hesaplar ve LTspice yeniden koşulur.
