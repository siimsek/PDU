# Yol Haritası ve Durum

Bu dosya projenin **nerede olduğunu** ve **sırada ne olduğunu** gösterir. Bir yapay zekâ aracı veya yeni biri depoyu açtığında önce burayı, sonra [AGENTS.md](AGENTS.md) dosyasını okur.

**Son güncelleme:** 12 Kasım 2026 (dondurma hazırlığı doğrulama turu)

## Şu anki durum

| | |
|---|---|
| **Proje** | Tekne için güç dağıtım kartı (PDU): 6S bataryadan (20–26 V) 11 V / 7,5 A üreten tek faz asenkron buck dönüştürücü |
| **Modül zarfı** | 0–7,5 A / 82,5 W; dirençli, sabit akımlı ve sabit güçlü yükler. Genel gerilim toleransı / ripple / geçici durum sınırları **kullanıcı onayı bekliyor** |
| **Referans yükler** | T3 Gemstone O1 (5–12 V) ve SLAMTEC RPLIDAR S2E (9–28 V); cihaza özgü uyumluluk testi olarak, modülün tek tasarım sınırı olarak değil |
| **Aktif adım** | **Adım 2 — Gerçek parçaların bulunması** (aday listesi hazır; kesin seçim yapılmadı). Adım 3'ün hesap kısmı (kayıp, ısı, gerilim stresi) kullanıcı isteğiyle 12.11.2026'da yapıldı; adım **kapanmadı** |
| **Dondurma durumu** | **BLOCKED** (12.11.2026): tolerans köşesinde 73–82,5 W sabit güç yükü sönümlenmiyor; L1 ve Cout ölçülmedi; parçalar kesin değil; Cout 25 V / Cin 35 V sınıfları arıza ve sıcak takmada açık. Kapı listesi: [buck/OPTIMIZASYON.md](buck/OPTIMIZASYON.md) §12 |
| **Bekleyen iş** | Kullanıcı kararları: (1) çıkış sönümü — sönüm dalı eklemek, ölçümle mevcut hâli doğrulamak veya kapalı çevrime bırakmak ([buck/OPTIMIZASYON.md](buck/OPTIMIZASYON.md) §10); (2) genel modül sınırları; (3) Cout ve Cin gerilim sınıfı; (4) kesin parçalar, soğutucu ve seramik kondansatör. Ölçümler: L1 (L0, L(I), DCR, sıcaklık), Cout ESR / empedans (0,9 kHz ve 100 kHz, sıcak ve soğuk), kaynak iç direnci ve kablo endüktansı. Sonra Adım 2 kapanır |
| **Sıradaki adım** | Adım 3 — Kayıp ve ısı. Adım 4 ve sonrası (sürücü, PWM, geri besleme, PCB) **kullanıcı isteyene kadar başlatılmaz** |
| **Devrenin hâli** | Açık çevrim, soft-start yok. LTspice'ta doğrulandı; **fiziksel devre ve ölçüm yok** |
| **Güvenlik** | Gerçek O1 / S2E **bağlanmaz**: açık çevrim 12 V üst sınırını garanti etmez |
| **Ana aşama** | **A — Ana güç devresi** (Adım 0–3); Adım 2'deyiz |
| **Dal** | Bütün iş `main` dalında. Güncel hâl her zaman `main`'dedir |
| **Aşama kaydı** | Aşama A: `ANA-GUC-DEVRESI` dalı (ara kayıt: hedef değerlerin doğrulandığı hâl, etiket `ana-guc-devresi-v2`) ve [ANA GÜÇ DEVRESİ](https://github.com/siimsek/PDU/milestone/1) milestone'u (açık). İkisi de Aşama A kapanınca (Adım 3 sonu) güncellenir/kapatılır |

### Şematikteki değerler (tek bakışta)

| Eleman | Şematik | 1. sıra aday (kesin değil) | Kabul aralığı |
|---|---|---|---|
| Giriş | 24,6 V (ana nokta) | 6S batarya | 20–26 V |
| Çıkış | 11 V / 7,5 A | — | — |
| Anahtarlama | 100 kHz, Ton 4,59 µs | — | — |
| L1 | 33 µH el sarım, DCR 7,81 mΩ (HESAP) | Magnetics Kool Mµ 40µ `0077536A7` 22 sarım (2. sıra: satın alma, Würth 74435583300) | 33 µH; DCR 6,5–15 mΩ (el sarım hedefi 8–10 mΩ). 39 µH ve 47 µH kaldı; 33 µH de tolerans köşesinde (L +%20) 200 ms'lik 73 W darbesinde kalır |
| Cout | 1000 µF, ESR 35 mΩ | Nichicon UHE1E102MHD6TO | 1000 µF, ESR 15–35 mΩ (alt kenar köşede yetmiyor; ESR ölçülmedi), ≥ 25 V (S1 kısa devresinde aşılır) |
| Cin | 2 × 1000 µF, ESR 15 mΩ | 2 × TDK B41859D7108M000 | toplam ripple akımı ≥ 4,5 A, ≥ 35 V (düşük dirençli kaynakla sıcak takmada aşılabilir) |
| S1 | Ron 5,6 mΩ | STP100N6F7 | RDS(on) ≤ 12 mΩ, VDS ≥ 55 V |
| D1 | 0,38 V + 8 mΩ | STPS40M60CT (iki bacak paralel) | VF ≤ 0,58 V @ 7,5 A, VRRM ≥ 45 V |

LTspice sonucu (24,6 V, 7,5 A): çıkış 11,000 V, ripple 64,3 mV t-t, bobin akımı 6,56–8,44 A, iletim kaybı 2,38 W; anahtarlama, çekirdek ve kondansatör kayıplarıyla kestirim ≈ 3,3 W (HESAP).
Adayların sırası ve gerekçesi, doğrulama durumu ve kriterlerin nedenleri: [buck/PARCA-HEDEFLERI.md](buck/PARCA-HEDEFLERI.md). Kanıt: [buck/OPTIMIZASYON.md](buck/OPTIMIZASYON.md).

## Ana aşamalar

Adımlar dört ana aşamada toplanır. **Dal ve milestone yalnız ana aşama düzeyinde açılır**; tek tek adımlar, parça güncellemeleri ve belge düzeltmeleri için açılmaz (yalnız `main`'e commit). Kurallar: [AGENTS.md](AGENTS.md) §4.7.

| Ana aşama | Adımlar | Dal | Milestone | Durum |
|---|---|---|---|---|
| **A — Ana güç devresi** | 0–3 | `ANA-GUC-DEVRESI` (var) | [ANA GÜÇ DEVRESİ](https://github.com/siimsek/PDU/milestone/1) (açık) | 🔄 Sürüyor (Adım 2) |
| **B — Kontrol** | 4–7 (sürücü, PWM ve yumuşak kalkış, geri besleme, korumalar) | açılmadı | açılmadı | ⛔ Kullanıcı başlatır |
| **C — Prototip ve ölçüm** | 8 | açılmadı | açılmadı | ⛔ Kullanıcı başlatır |
| **D — PCB ve gerçek yük** | 9–10 | açılmadı | açılmadı | ⛔ Kullanıcı başlatır |

- Bir ana aşamaya başlanırken kullanıcı isterse milestone açılır; aşama kapanırken dal `main`'in o anki hâline getirilir ve milestone kapatılır.
- Dal ve milestone adlarını kullanıcı verir.

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
- Kabul aralıkları: Cout 1000 µF, ESR 15–35 mΩ (35 mΩ maks. empedanstır, ESR varsayımı); L 33 µH el sarım (kullanıcı kararı, 12.11.2026; DCR 6,5–15 mΩ). Güncel şematik değerleriyle, düzeltilmiş ölçüm altyapısı ve 200 ms'lik darbeyle `secilen`, `pencere`, `kararlilik`, `zarf` koşuldu: anma değerleri sönümlü; **tolerans köşesinde 33 µH dahil üç endüktans da kaldı** (33 µH: 9,91–12,05 V; 39 / 47 µH: 12,59 / 12,86 V) ([buck/OPTIMIZASYON.md](buck/OPTIMIZASYON.md) §4.4, §5, §6).
- Bulunan temel sorunlar: sabit güç yüküyle eski değerler salınıyordu; açık çevrim hafif yükte ve giriş değişiminde 11 V'u tutamıyor; sert kalkışta 53 A / 17 V.
- Çıktılar: [buck/ltspice/buck_guc_kati.asc](buck/ltspice/buck_guc_kati.asc), [buck/OPTIMIZASYON.md](buck/OPTIMIZASYON.md), [buck/hesap.py](buck/hesap.py), [buck/dogrula.py](buck/dogrula.py).
- **Ölçüt:** şematik değerleriyle `dogrula.py secilen` ve `pencere` koşuldu; yük adımlarında çıkış 9–12 V içinde, ripple ≤ 165 mV. **Güncel durum (12.11.2026): anma değerlerinde sağlanıyor, tolerans köşesinde sağlanmıyor** (`pencere` üç satırda da KALDI; `secilen` §8 "sönüm en zayıf" köşesi kaldı). Adım, 11.11.2026'da 20 ms'lik darbe testiyle "tamam" sayılmıştı; bu test yavaş büyüyen salınımı kaçırıyordu. Adımın yeniden açılıp açılmayacağı ve çözüm (bkz. Bekleyen iş) kullanıcı kararıdır.

### 2. Gerçek parçaların bulunması — 🔄 sürüyor (aday listesi hazır, kesin seçim bekliyor)

- **Yapıldı:**
  - Her parça için ölçülebilir kriterler ve nedenleri yazıldı.
  - Kriterlerle dış araştırma yapıldı; adaylar kriterlerle karşılaştırıldı.
  - Dört bobin/kondansatör kombinasyonu LTspice köşe testinden geçirildi. Araştırmanın önerdiği 47 µH + 18 mΩ kombinasyonu **kaldı** (12,83 V, 3 V salınım); 33 µH + 35 mΩ **geçti**.
  - Adaylar öncelik sırasına dizildi; kullanıcı kararıyla liste "olabilir" listesidir, kesin seçim değildir.
  - 1. sıra adayların değerleri şematiğe, `hesap.py` ve `dogrula.py` içine yazıldı; `dogrula.py secilen` yeniden koşuldu: anma değerlerinde sınırların içinde, sönüm en zayıf tolerans köşesinde değil (12.11.2026).
  - ST veri sayfaları okundu (STPS40M60C Doc ID 018813 Rev 1; STB100N6F7 DocID027210 Rev 2, STP100N6F7'nin D²PAK kardeşi) ve Magnetics `0077536A7` çekirdek veri sayfası (rev. 6/1/2022) doğrulandı.
- **Kalan (kullanıcı):**
  - Aday listesinden kesin parçaların belirlenmesi (bulunurluk, fiyat, delikli/yüzey montaj tercihi).
  - Kesinleşen parçaların değerlerinin üretici veri sayfasından teyidi (STP100N6F7'nin TO-220 belgesi açılamadı; Nichicon / TDK ESR yayımlamıyor).
  - L1 ve Cout fiziksel ölçümü; sönüm, gerilim sınıfı, soğutucu ve seramik kondansatör kararları ([buck/OPTIMIZASYON.md](buck/OPTIMIZASYON.md) §9.5, §10, §11).
  - Kesinleşen parça 1. sıradan farklıysa değerlerin şematiğe yazılıp testlerin yeniden koşulması.
- **Ölçüt:** beş parçanın her biri **kesinleşmiş**, parça numarası, veri sayfası kaynağı ve kullanılan değerler tabloda; değerler üretici veri sayfasından teyitli; bu değerlerle `dogrula.py secilen` sınırların içinde.

### 3. Kayıp ve ısı; güç katının dondurulması — ⏳ bekliyor (hesap kısmı yapıldı, adım kapanmadı)

- **Yapıldı (12.11.2026, HESAP ve ideal olmayan SİM; ölçüm yok):** kayıp bütçesi (toplam ≈ 2,8–3,4 W, verim ≈ %96,1–96,8), çekirdek kaybı (≤ 0,14 W), D1 / S1 / L1 ısıl denge ve soğutucu hedefi (ortak, Rth(s-a) ≤ 12 K/W; D1 soğutucusuz ısıl kaçağa gider), anahtarlama zili duyarlılığı (seramik dekuplaj olmadan D1 ters gerilimi 60 V'u aşabiliyor), sıcak takma ve S1 kısa devre gerilimleri ([buck/OPTIMIZASYON.md](buck/OPTIMIZASYON.md) §9).
- **Kalan:** parçalar kesinleşince yeniden hesap; soğutucu, seramik kondansatör ve sönümleyici parça seçimi; fiziksel ölçümler; dondurma kapısının kapanması (§12).

- Bobin çekirdek kaybı (modelde yok) üretici verisiyle hesaplanır.
- S1 ve D1 eklem sıcaklıkları kayıp ve ısıl dirençten hesaplanır; soğutucu ihtiyacı belirlenir.
- Anahtarlama kaybı için ilk kestirim (gerçek parçanın kapı yükü ve geçiş süreleriyle).
- Sönümleyici (snubber) ve giriş/çıkış seramik kondansatörlerinin gerekip gerekmediğine karar verilir.
- **Ölçüt:** sıcaklık dahil kayıp bütçesi yazılı; güç katı eleman listesi değişmeyecek şekilde kayıtlı.

### 4. Kapı sürücüsü — ⛔ kapsam dışı

Şematikteki `PULSE` kaynağının yerini gerçek sürücü alır. Üst taraftaki N-MOSFET için sürme yöntemi (bootstrap), sürücü entegresi, kapı direnci, sürücü beslemesi.
**Ölçüt:** sürücülü simülasyonda verim ve gerilim zorlanmaları Adım 1 sonuçlarıyla karşılaştırılmış.

### 5. PWM üretimi ve yumuşak kalkış — ⛔ kapsam dışı

PWM kontrolcü seçimi, frekans ayarı, duty rampası. Sert kalkıştaki 53 A / 17 V sorununu bu adım kapatır.
**Ölçüt:** kalkışta çıkış 12 V'u aşmıyor; bobin tepe akımı doyma payının içinde.

### 6. Geri besleme ve kompanzasyon — ⛔ kapsam dışı

Çıkış gerilimi algılama, hata yükselteci, kompanzasyon. Tasarım verileri: Ton aralığı 2,1–5,6 µs, DCM/CCM geçişi ≈ 0,95 A, f0 ≈ 0,88 kHz, ESR sıfırı 4,5–10,6 kHz (ESR penceresine göre), yük sabit güç karakterli, yük atma bütçesi ≈ 0,7 V (soğuk ESR'de daha az). Devredilen şartların tam listesi: [buck/OPTIMIZASYON.md](buck/OPTIMIZASYON.md) §11; tolerans köşesinde 82,5 W sabit güç yüküyle kararlılık bu adımda gösterilmelidir (sönüm dalı eklenmezse).
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
| 12.11.2026 | Doğrulama düzeltmesi (değer değişmedi): test netlistlerinde anahtar yumuşak geçişli (`Vh=-0.5`); Ton ayarı yeniden yazıldı; yük adımı darbesi 200 ms ve sönüm ölçümü kabul kararına eklendi | Kullanıcı isteği (dondurma hazırlığı). `Vh=0` LTspice'ta ±1 ns titreme ve sahte ripple (70 mV yerine 64 mV) üretiyordu; 20 ms'lik darbe, zaman sabiti ≈ 0,2 s olan büyüyen salınımı kaçırıyordu. Sonuç: tolerans köşesinde 33 µH dahil hepsi **kaldı**; dondurma BLOCKED |
| 12.11.2026 | Şematik: L1 DCR 14,52 → 7,81 mΩ (el sarım, HESAP @20 °C), Ton 4,61 → 4,59 µs. Cout 35 mΩ ve Cin 15 mΩ "maks. empedans, ESR varsayımı" olarak işaretlendi; polimer Cin (VINATech) ve Panasonic FR seçilmedi; STPS40M60CT korundu | Kullanıcı kararı. `secilen` ve `pencere` yeniden koşuldu: 33 µH geçti; 39 ve 47 µH kaldı |
| 12.11.2026 | L1 için 1. sıra el sarım (Magnetics Kool Mµ 40µ `0077536A7`, 22 sarım, ≈ 33,4 µH), 2. sıra satın alma | Kullanıcı kararı (hocanın önerisi: hazır bobinlerin Isat değeri garanti edilmiyor). SİM: DCR 6,5–9,5 mΩ ile köşe testi geçti; 47 µH el sarım kaldı (12,61 V). Şematik DCR değeri ölçüm sonrası kesinleşir |
| 12.11.2026 | L1: 33 µH ve 47 µH iki seçenek olarak kalır; 39 µH kabul edilmez | Kullanıcı kararı. Güncel `pencere`: 39 µH köşede 12,06 V ile kaldı; 47 µH 0,04 V payla geçti ve S2E kalkış süresine (yayımlanmamış, eşik ≈ 32 ms) bağlı |
| 11.11.2026 | Dal ve milestone yalnız ana aşamalarda (A–D) açılır; adımlar ve küçük değişiklikler yalnız `main`'e commit | Kullanıcı kararı: her değişiklikte yeni dal/milestone istenmiyor |
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
- Yeni dal, etiket veya milestone yalnız bir ana aşama açılır/kapanırken ve kullanıcı isteyince oluşturulur; "Ana aşamalar" tablosu o zaman güncellenir.
- Yapılmamış iş "tamam" yazılmaz; koşulmamış test sonucu yazılmaz.
