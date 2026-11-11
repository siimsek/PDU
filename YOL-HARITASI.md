# Yol Haritası ve Durum

Bu dosya projenin **nerede olduğunu** ve **sırada ne olduğunu** gösterir. Bir yapay zekâ aracı veya yeni biri depoyu açtığında önce burayı, sonra [AGENTS.md](AGENTS.md) dosyasını okur.

**Son güncelleme:** 11 Kasım 2026

## Şu anki durum

| | |
|---|---|
| **Proje** | Tekne için güç dağıtım kartı (PDU): 6S bataryadan (20–26 V) 11 V / 7,5 A üreten tek faz asenkron buck dönüştürücü |
| **Beslenecek yükler** | T3 Gemstone O1 (5–12 V) ve SLAMTEC RPLIDAR S2E (9–28 V) |
| **Aktif adım** | **Adım 2 — Gerçek parçaların bulunması** (aday listesi hazır, 1. sıra adaylar simülasyonda doğrulandı; kesin seçim yapılmadı) |
| **Bekleyen iş** | Kullanıcı: aday listesinden kesin parçaları belirlemek; kesinleşen parçaların değerlerini üretici veri sayfasından teyit etmek. Sonra Adım 2 kapanır |
| **Sıradaki adım** | Adım 3 — Kayıp ve ısı. Adım 4 ve sonrası (sürücü, PWM, geri besleme, PCB) **kullanıcı isteyene kadar başlatılmaz** |
| **Devrenin hâli** | Açık çevrim, soft-start yok. LTspice'ta doğrulandı; **fiziksel devre ve ölçüm yok** |
| **Güvenlik** | Gerçek O1 / S2E **bağlanmaz**: açık çevrim 12 V üst sınırını garanti etmez |
| **Dal / etiket** | Çalışma `main` dalında. Adım 1'in dondurulmuş hâli: `ANA-GUC-DEVRESI` dalı, `ana-guc-devresi-v2` etiketi |
| **GitHub** | Milestone: [ANA GÜÇ DEVRESİ](https://github.com/siimsek/PDU/milestone/1) (açık; Adım 2 bitince kapanır) |

### Şematikteki değerler (tek bakışta)

| Eleman | Şematik | 1. sıra aday (kesin değil) | Kabul aralığı |
|---|---|---|---|
| Giriş | 24,6 V (ana nokta) | 6S batarya | 20–26 V |
| Çıkış | 11 V / 7,5 A | — | — |
| Anahtarlama | 100 kHz, Ton 4,61 µs | — | — |
| L1 | 33 µH, DCR 14,5 mΩ | Würth 74435583300 | 33–47 µH, Isat ≥ 12 A, DCR ≤ 15 mΩ |
| Cout | 1000 µF, ESR 35 mΩ | Nichicon UHE1E102MHD6TO | 1000 µF, ESR 15–35 mΩ, ≥ 25 V |
| Cin | 2 × 1000 µF, ESR 15 mΩ | 2 × TDK B41859D7108M000 | toplam ripple akımı ≥ 4,5 A, ≥ 35 V |
| S1 | Ron 5,6 mΩ | STP100N6F7 | RDS(on) ≤ 12 mΩ, VDS ≥ 55 V |
| D1 | 0,38 V + 8 mΩ | STPS40M60CT (iki bacak paralel) | VF ≤ 0,58 V @ 7,5 A, VRRM ≥ 45 V |

LTspice sonucu (24,6 V, 7,5 A): çıkış 11,000 V, ripple 64,4 mV t-t, bobin akımı 6,56–8,44 A, iletim kaybı 2,75 W.
Adayların sırası ve gerekçesi, doğrulama durumu ve kriterlerin nedenleri: [buck/PARCA-HEDEFLERI.md](buck/PARCA-HEDEFLERI.md). Kanıt: [buck/OPTIMIZASYON.md](buck/OPTIMIZASYON.md).

## Adımlar

Sıra takvim değildir. Her adımın bir tamamlanma ölçütü vardır; ölçüt sağlanmadan adım "tamam" sayılmaz. Bir sonraki adıma yalnız kullanıcı istediğinde geçilir.

| # | Adım | Durum |
|---|---|---|
| 0 | Gereksinimler ve yükler | ✅ Tamam |
| 1 | Ana güç devresi: değerler ve doğrulama | ✅ Tamam |
| 2 | Gerçek parçaların bulunması | 🔄 Sürüyor |
| 3 | Kayıp ve ısı; güç katının dondurulması | ⏳ Bekliyor |
| 4 | Kapı sürücüsü | ⛔ Kapsam dışı (kullanıcı başlatır) |
| 5 | PWM üretimi ve yumuşak kalkış | ⛔ Kapsam dışı |
| 6 | Geri besleme ve kompanzasyon | ⛔ Kapsam dışı |
| 7 | Korumalar | ⛔ Kapsam dışı |
| 8 | Tezgâh prototipi ve ölçüm | ⛔ Kapsam dışı |
| 9 | PCB | ⛔ Kapsam dışı |
| 10 | Gerçek yüklerin bağlanması | ⛔ Kapsam dışı |

### 0. Gereksinimler ve yükler — ✅ tamam

- Yükler belirlendi ve üretici belgelerinden doğrulandı: O1 DC girişi 5–12 V / 5 A; S2E 9–28 V, 12 V'ta en çok 0,22 A çalışma ve 1,5 A kalkış, ripple sınırı %3.
- 11 V iki yükün aralığında. Yük zarfı 6,64 A; 7,5 A hedefi yeterli.
- **Açık kalan:** O1'in gerçek tüketimi, kalkış akımı ve mutlak maksimum gerilimi yayımlanmamış (4 / 10 W değerleri tahmindir).
- Çıktı: [buck/OPTIMIZASYON.md](buck/OPTIMIZASYON.md) §2.

### 1. Ana güç devresi: değerler ve doğrulama — ✅ tamam

- Güç katı değerleri gerçek yük senaryolarına (sabit güç yükü) göre seçildi ve LTspice'ta doğrulandı: 5 giriş noktası, yük adımları, yük atma, kalkış, giriş değişimi, tolerans köşeleri.
- Kabul aralıkları doğrulandı: L 33–47 µH, Cout 1000 µF, ESR 15–35 mΩ.
- Bulunan temel sorunlar: sabit güç yüküyle eski değerler salınıyordu; açık çevrim hafif yükte ve giriş değişiminde 11 V'u tutamıyor; sert kalkışta 52 A / 17 V.
- Çıktılar: [buck/ltspice/buck_guc_kati.asc](buck/ltspice/buck_guc_kati.asc), [buck/OPTIMIZASYON.md](buck/OPTIMIZASYON.md), [buck/hesap.py](buck/hesap.py), [buck/dogrula.py](buck/dogrula.py).
- **Ölçüt (sağlandı):** şematik değerleriyle `dogrula.py secilen` ve `pencere` koşuldu; yük adımlarında çıkış 9–12 V içinde, ripple ≤ 165 mV.

### 2. Gerçek parçaların bulunması — 🔄 sürüyor (aday listesi hazır, kesin seçim bekliyor)

- **Yapıldı:**
  - Her parça için ölçülebilir kriterler ve nedenleri yazıldı.
  - Kriterlerle dış araştırma yapıldı; adaylar kriterlerle karşılaştırıldı.
  - Dört bobin/kondansatör kombinasyonu LTspice köşe testinden geçirildi. Araştırmanın önerdiği 47 µH + 18 mΩ kombinasyonu **kaldı** (12,83 V, 3 V salınım); 33 µH + 35 mΩ **geçti**.
  - Adaylar öncelik sırasına dizildi; kullanıcı kararıyla liste "olabilir" listesidir, kesin seçim değildir.
  - 1. sıra adayların değerleri şematiğe, `hesap.py` ve `dogrula.py` içine yazıldı; `dogrula.py secilen` yeniden koşuldu ve sınırların içinde.
- **Kalan (kullanıcı):**
  - Aday listesinden kesin parçaların belirlenmesi (bulunurluk, fiyat, delikli/yüzey montaj tercihi).
  - Kesinleşen parçaların değerlerinin üretici veri sayfasından teyidi (şu an yalnız TDK giriş kondansatörü doğrulandı).
  - Kesinleşen parça 1. sıradan farklıysa değerlerin şematiğe yazılıp testlerin yeniden koşulması.
- **Ölçüt:** beş parçanın her biri **kesinleşmiş**, parça numarası, veri sayfası kaynağı ve kullanılan değerler tabloda; değerler üretici veri sayfasından teyitli; bu değerlerle `dogrula.py secilen` sınırların içinde.

### 3. Kayıp ve ısı; güç katının dondurulması — ⏳ bekliyor

- Bobin çekirdek kaybı (modelde yok) üretici verisiyle hesaplanır.
- S1 ve D1 eklem sıcaklıkları kayıp ve ısıl dirençten hesaplanır; soğutucu ihtiyacı belirlenir.
- Anahtarlama kaybı için ilk kestirim (gerçek parçanın kapı yükü ve geçiş süreleriyle).
- Sönümleyici (snubber) ve giriş/çıkış seramik kondansatörlerinin gerekip gerekmediğine karar verilir.
- **Ölçüt:** sıcaklık dahil kayıp bütçesi yazılı; güç katı eleman listesi değişmeyecek şekilde kayıtlı.

### 4. Kapı sürücüsü — ⛔ kapsam dışı

Şematikteki `PULSE` kaynağının yerini gerçek sürücü alır. Üst taraftaki N-MOSFET için sürme yöntemi (bootstrap), sürücü entegresi, kapı direnci, sürücü beslemesi.
**Ölçüt:** sürücülü simülasyonda verim ve gerilim zorlanmaları Adım 1 sonuçlarıyla karşılaştırılmış.

### 5. PWM üretimi ve yumuşak kalkış — ⛔ kapsam dışı

PWM kontrolcü seçimi, frekans ayarı, duty rampası. Sert kalkıştaki 52 A / 17 V sorununu bu adım kapatır.
**Ölçüt:** kalkışta çıkış 12 V'u aşmıyor; bobin tepe akımı doyma payının içinde.

### 6. Geri besleme ve kompanzasyon — ⛔ kapsam dışı

Çıkış gerilimi algılama, hata yükselteci, kompanzasyon. Tasarım verileri: Ton aralığı 2,3–5,7 µs, DCM/CCM geçişi ≈ 0,95 A, f0 ≈ 0,88 kHz, ESR sıfırı 4,5–10,6 kHz (ESR penceresine göre), yük sabit güç karakterli, yük atma bütçesi ≈ 0,7 V.
**Ölçüt:** 20–26 V ve 0,24–7,5 A aralığında çıkış 11 V toleransında; 12 V üst sınırı her koşulda korunuyor; faz ve kazanç payları belgelenmiş.

### 7. Korumalar — ⛔ kapsam dışı

Aşırı akım, çıkış aşırı gerilim (anahtar kısa devre kalırsa çıkış giriş gerilimine çıkar; O1 için bağımsız koruma), giriş düşük gerilim, sigorta ve ters polarite, batarya takma anındaki ani akım.
**Ölçüt:** her arıza senaryosu için O1 girişi 12 V altında kaldığı gösterilmiş.

### 8. Tezgâh prototipi ve ölçüm — ⛔ kapsam dışı

Direnç yükle kurulum; kararlı durum, ripple, verim, sıcaklık, kalkış ve yük adımı ölçümleri. Simülasyonla karşılaştırma.
**Ölçüt:** ölçümler belgelenmiş; simülasyondan sapmalar açıklanmış.

### 9. PCB — ⛔ kapsam dışı

Şematik çizimi, yerleşim, tasarım kuralı denetimi. Kurallar: [AGENTS.md](AGENTS.md) "PCB aşaması" bölümü.
**Ölçüt:** elektriksel ve tasarım kuralı denetimleri hatasız; akım yolları ve ısı hesapları belgelenmiş.

### 10. Gerçek yüklerin bağlanması — ⛔ kapsam dışı

Yalnız Adım 6, 7 ve 8 tamamlandıktan ve O1 girişinde 12 V üst sınırı ölçümle gösterildikten sonra.

## Karar günlüğü

Yeni kararlar en üste eklenir. Bir değeri değiştirmeden önce burada ve [buck/PARCA-HEDEFLERI.md](buck/PARCA-HEDEFLERI.md) içinde nedenine bakılır.

| Tarih | Karar | Neden |
|---|---|---|
| 11.11.2026 | Parçalar kesin seçim değil, öncelik sıralı aday listesidir; şematik 1. sıra adayların değerlerini taşır (Würth 74435583300, Nichicon UHE1E102MHD6TO, 2 × TDK B41859D7108M000, STP100N6F7, STPS40M60CT) | Kullanıcı kararı. 1. sıra: dış araştırma adayları arasından LTspice köşe testini en geniş payla geçen set |
| 11.11.2026 | Cout için 18 mΩ değil 35 mΩ'luk kondansatör | Veri sayfası ESR'si en yüksek değerdir; 18 mΩ'luk parçanın gerçek ESR'si sönüm alt sınırının altına inebilir (47 µH ile 12,83 V) |
| 11.11.2026 | S1 için en düşük dirençli değil en düşük kapı yüklü aday (30 nC) | İletim kaybı zaten 0,15 W; düşük kapı yükü sürücü aşamasını kolaylaştırır |
| 11.11.2026 | Parçayı araç seçmez; kriterler yazılır, kullanıcı bulur ve kesinleştirir | Kullanıcı kararı: önce Türkiye'de kolay bulunan değerler |
| 11.11.2026 | Cout 680 → 1000 µF | 680 µF en kötü tolerans köşesinde 12,06 V; 1000 µF aynı köşede 11,81 V ve daha yaygın değer |
| 11.11.2026 | L1 kabul aralığı 33–47 µH; 22 µH elendi | 22 µH'de tipik yük kesintili iletimde, çıkış 8,78 V'a düşüyor |
| 11.11.2026 | Cout ESR'sine alt sınır kondu (15–35 mΩ) | ESR, LC'nin sönüm direncidir; çok düşük ESR sabit güç yüküyle salınım yaratır |
| 11.11.2026 | Daha büyük L / Cout'a gidilmedi | Giriş değişiminin çıkışa etkisi L/C'den bağımsız; büyük LC geçişi kötüleştiriyor |
| 11.11.2026 | Cout 330 → 680 µF, Cin ve diğerleri aynı | Eski değerler 57,6 W sabit güç yükünde 2,9 V t-t salınıyordu |
| 11.11.2026 | Ana çalışma noktası 22,2 → 24,6 V | Normal çalışma gerilimi; test noktaları 20 / 22,2 / 24,6 / 25,2 / 26 V |
| 11.11.2026 | fsw 100 kHz'de kaldı | Hedefler sağlanıyor; frekans artışının bedeli ideal modelle ölçülemiyor |

## Bu dosya nasıl güncellenir

- Bir adım ilerlediğinde veya bittiğinde: "Şu anki durum" tablosu, adım tablosundaki durum ve ilgili adımın "yapıldı / yapılacak" satırları aynı değişiklikte güncellenir.
- Şematik değeri değiştiğinde: "Şematikteki değerler" tablosu ve karar günlüğü güncellenir.
- "Son güncelleme" tarihi değiştirilir.
- Yapılmamış iş "tamam" yazılmaz; koşulmamış test sonucu yazılmaz.
