# Yol Haritası ve Durum

Bu dosya projenin **nerede olduğunu** ve **sırada ne olduğunu** gösterir. Bir yapay zekâ aracı veya yeni biri depoyu açtığında önce burayı, sonra [AGENTS.md](AGENTS.md) dosyasını okur.

**Son güncelleme:** 13 Kasım 2026 (kontrol mimarisi ile güç katı parçalarının birlikte değerlendirilmesi iş sırasına alındı)

**13 Kasım 2026 kanıt notu:** Dondurma geçmiş kullanıcı kararıdır; denenmiş model ve senaryoların dışına genellenmez. 200 ms testleri birden fazla model setinde, 500 ms testi ise ayrı bir pencere köşesi senaryosunda koşuldu. Kısa darbelerde sönüm kararı verilemez; sıfır süreç çıkış kodu elektriksel geçme anlamına gelmez. Ayrıntı: [OPTIMIZASYON.md](buck/OPTIMIZASYON.md) §13.

**Güncel çalışma sırası:** Önce kalan teknik denetim ve sistem gereksinimleri; ardından PWM, geri besleme, sürücü ve korumaların **mimari ve arayüz gereksinimleri**; sonra kontrolcü ve güç katı adaylarının birlikte değerlendirilmesi, kesin seçim, doğrulama ve prototip. Bobin için 33 µH, 7,5–10 mΩ @20 °C başlangıç hedefidir ([parça hedefleri](buck/PARCA-HEDEFLERI.md)); gerçek çekirdek ve sarım ölçülmeden ve kontrolcü uyumu görülmeden nihai değildir. Örnek 48,0 V sıcak takma hesabına karşı 50 V Cin payı açık risktir.

## Şu anki durum

| | |
|---|---|
| **Proje** | Tekne için güç dağıtım kartı (PDU): 6S bataryadan (20–26 V) 11 V / 7,5 A üreten tek faz asenkron buck dönüştürücü |
| **Modül zarfı** | 0–7,5 A / 82,5 W; dirençli, sabit akımlı ve sabit güçlü yükler. Kullanıcı kararıyla (12.11.2026) ayrı genel modül sınırı tanımlanmadı; dondurma O1/S2E uyumluluk ölçütleriyle yapıldı |
| **Referans yükler** | T3 Gemstone O1 (5–12 V) ve SLAMTEC RPLIDAR S2E (9–28 V); cihaza özgü uyumluluk testi olarak, modülün tek tasarım sınırı olarak değil |
| **Aktif iş** | Adım 2–3 hazırlığı ve Adım 4–7 için **mimari / gereksinim çalışması**. Kontrol devresi tasarımı, uygulaması ve parça seçimi henüz yapılmadı. |
| **Dondurma durumu** | **FROZEN** (açık çevrim simülasyon dondurması, 12.11.2026): örneklenen koşullar sınandı, `Cd = 470 µF + seri Rd = 0,22 Ω` ve gerilim sınıfı hedefleri onaylandı. Kapalı çevrim ve gerçek parçalar doğrulanmadı ([buck/OPTIMIZASYON.md](buck/OPTIMIZASYON.md) §12.1). |
| **Bekleyen iş** | Kalan kod/hesap denetimi; ortam, kaynak ve genel çıkış şartları; kontrol mimarisi ve güç katı uyumluluğu; ardından kullanıcıyla parça seçimi ve doğrulama |
| **Sıradaki iş** | Gereksinimleri ve kontrol mimarisini belirlemek; kapalı çevrim tasarımı ve gerçek parçalarla doğrulama daha sonra, PCB henüz kapsam dışı |
| **Devrenin hâli** | Açık çevrim, soft-start yok. LTspice'ta örnek senaryolar sınandı; **fiziksel devre ve ölçüm yok** |
| **Güvenlik** | Gerçek O1 / S2E **bağlanmaz**: açık çevrim 12 V üst sınırını garanti etmez |
| **Ana aşama** | **A — Ana güç devresi** sürüyor; B kontrol aşamasının arayüz ve mimari hazırlığı paralel ele alınacak |
| **Dal** | Bütün iş `main` dalında. Güncel hâl her zaman `main`'dedir |
| **Aşama kaydı** | Aşama A: `ANA-GUC-DEVRESI` dalı (ara kayıt: hedef değerlerin doğrulandığı hâl, etiket `ana-guc-devresi-v2`) ve [ANA GÜÇ DEVRESİ](https://github.com/siimsek/PDU/milestone/1) milestone'u (açık). İkisi de Aşama A kapanınca (Adım 3 sonu) güncellenir/kapatılır |

### Şematikteki değerler (tek bakışta)

| Eleman | Şematik | 1. sıra aday (kesin değil) | Kabul aralığı |
|---|---|---|---|
| Giriş | 24,6 V (ana nokta) | 6S batarya | 20–26 V |
| Çıkış | 11 V / 7,5 A | — | — |
| Anahtarlama | 100 kHz, Ton 4,59 µs | — | — |
| L1 | 33 µH el sarım, DCR 7,81 mΩ (HESAP) | Magnetics Kool Mµ 40µ `0077536A7` 22 sarım (2. sıra: satın alma, Würth 74435583300) | **33 µH** (el sarım 30,7–36,1 µH; satın alma ±%20 de geçti); DCR 6,5–15 mΩ (el sarım hedefi 7,5–10 mΩ) |
| Cout | 1000 µF, ESR 35 mΩ | Nichicon UHE1E102MHD6TO *(R/C referansı; kesin parça ≥35 V seçilecek)* | 1000 µF ±%20, ESR ≤ 35 mΩ, **≥ 35 V** (S1 kısa devresinde 27,3–31,1 V) |
| Cd + Rd | **470 µF + seri 0,22 Ω** | — (dondurma sonrası seçilecek) | Cd: 470 µF ±%20, **≥ 35 V**; Rd: 0,22 Ω (Rd + Cd_ESR toplamı **0,15–0,60 Ω**), ≥ 0,25 W |
| Cin | 2 × 1000 µF, ESR 15 mΩ | 2 × TDK B41859D7108M000 *(R/C referansı; kesin parça ≥50 V seçilecek)* | toplam ripple akımı ≥ 4,5 A, **≥ 50 V**; örnek sıcak takma hesabı 48,0 V, gerçek kaynak ve pay doğrulanmadı |
| S1 | Ron 5,6 mΩ | STP100N6F7 | RDS(on) ≤ 12 mΩ, VDS ≥ 55 V |
| D1 | 0,38 V + 8 mΩ | STPS40M60CT (iki bacak paralel) | VF ≤ 0,58 V @ 7,5 A, VRRM ≥ 45 V |

LTspice sonucu (24,6 V, 7,5 A): çıkış 11,000 V, ripple 55,7 mV t-t, bobin akımı 6,56–8,44 A, iletim kaybı 2,38 W (Rd kaybı ≈ 1,3 mW); anahtarlama, çekirdek ve kondansatör kayıplarıyla kestirim ≈ 3,24 W (HESAP).
Adayların sırası ve gerekçesi, doğrulama durumu ve kriterlerin nedenleri: [buck/PARCA-HEDEFLERI.md](buck/PARCA-HEDEFLERI.md). Kanıt: [buck/OPTIMIZASYON.md](buck/OPTIMIZASYON.md).

## İş akışı

Sıra (13.11.2026 güncellemesi): **gereksinimleri ve kalan denetimi tamamla → kontrol / sürücü / koruma mimarisini belirle → kontrolcü ve güç katı adaylarını birlikte değerlendir → kullanıcıyla parçaları kesinleştir ve bobini ölç → gerçek değerlerle güç katı ve kapalı çevrimi doğrula → tezgâh → PCB**. Adım numaraları bağımlılıkları anlatır, katı yürütme sırası değildir. 12.11.2026 açık çevrim simülasyon dondurması tarihî bir referans olarak korunur; kapalı çevrim uyumu veya fiziksel doğrulama değildir. Uyum sorunu çıkarsa değişiklik kullanıcı kararıyla ve yeniden doğrulanarak ele alınır.

### Sıradaki iş

Güç katının **simülasyon dondurması (`FROZEN`, §12.1 #1–12)** tamamlandı:
- Çıkışa paralel **`Cd = 470 µF + seri Rd = 0,22 Ω`** sönüm dalı eklendi; tarihli koşular ve senaryo bazındaki sonuçları [OPTIMIZASYON.md](buck/OPTIMIZASYON.md) içindedir. 200 ms model setleri ile tek 500 ms köşesi ayrı değerlendirilir; açık çevrim kalkış ve giriş değişimi güvenli regülasyon sağlamaz.
- Gerilim sınıfları **Cout ve Cd ≥ 35 V**, **Cin ≥ 50 V** olarak belirlendi; dondurma kullanıcı tarafından onaylandı.

1. Kalan kod/hesap denetimini bitir; çalışma sıcaklığı, batarya/kablo, genel çıkış toleransı ve geçici durum şartlarını kullanıcıyla belirle. Önceki genel sınır kararını kendiliğinden değiştirme.
2. Kontrol yöntemini, üst taraf sürme, frekans ve duty sınırlarını, hafif yük, soft-start, akım sınırı ve bağımsız aşırı gerilim koruması arayüzlerini belirle. Çıktı devre seçimi değil, karşılaştırılabilir gereksinimlerdir.
3. Kontrolcü adaylarının 33 µH, Cout ve Cd–Rd filtresi, CPL yük, S1 kapı yükü ve çalışma köşeleriyle uyumunu değerlendir; uyumsuzluk varsa kullanıcıya sun. 33 µH için deneme sarımı yapılabilir; 22 sarım yalnız belirtilen çekirdeğe ait örnektir.
4. Kullanıcıyla kontrolcü ve güç katı parçalarını tek tek seç; bobin ve parçaları ölç. Gerçek değerlerle güç katı testlerini ve kapalı çevrim kararlılık, kalkış, yük/giriş değişimi ile koruma senaryolarını doğrula. Fiziksel devre ve ölçüm yapılmadan sonuçları ölçüm olarak sunma.

## Ana aşamalar

Adımlar dört ana aşamada toplanır. **Dal ve milestone yalnız ana aşama düzeyinde açılır**; tek tek adımlar, parça güncellemeleri ve belge düzeltmeleri için açılmaz (yalnız `main`'e commit). Kurallar: [AGENTS.md](AGENTS.md) §4.7.

| Ana aşama | Adımlar | Dal | Milestone | Durum |
|---|---|---|---|---|
| **A — Ana güç devresi** | 0–3 | `ANA-GUC-DEVRESI` (var) | [ANA GÜÇ DEVRESİ](https://github.com/siimsek/PDU/milestone/1) (açık) | 🔄 Sürüyor; parça seçimi kontrol mimarisiyle birlikte değerlendirilecek |
| **B — Kontrol** | 4–7 (sürücü, PWM ve yumuşak kalkış, geri besleme, korumalar) | açılmadı | açılmadı | ⏳ Mimari / arayüz hazırlığı sırada; tasarım yapılmadı |
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
| 2 | Gerçek parçaların bulunması | 🔄 Adaylar var; kesin seçim kontrol mimarisiyle birlikte |
| 3 | Kayıp ve ısı; güç katının dondurulması | ⏳ Bekliyor |
| 4 | Kapı sürücüsü | ⏳ Mimari ve arayüz gereksinimleri sırada |
| 5 | PWM üretimi ve yumuşak kalkış | ⏳ Mimari ve arayüz gereksinimleri sırada |
| 6 | Geri besleme ve kompanzasyon | ⏳ Mimari ve arayüz gereksinimleri sırada |
| 7 | Korumalar | ⏳ Mimari ve arayüz gereksinimleri sırada |
| 8 | Tezgâh prototipi ve ölçüm | ⛔ Kapsam dışı |
| 9 | PCB | ⛔ Kapsam dışı |
| 10 | Gerçek yüklerin bağlanması | ⛔ Kapsam dışı |

### 0. Gereksinimler ve yükler — ✅ tamam

- Yükler belirlendi ve üretici belgelerinden doğrulandı: O1 DC girişi 5–12 V / 5 A; S2E 9–28 V, 12 V'ta en çok 0,22 A çalışma ve 1,5 A kalkış, ripple sınırı %3.
- 11 V iki yükün aralığında. Yük zarfı 6,64 A; 7,5 A hedefi yeterli.
- **Açık kalan:** O1'in gerçek tüketimi, kalkış akımı ve mutlak maksimum gerilimi yayımlanmamış (4 / 10 W değerleri tahmindir).
- Çıktı: [buck/OPTIMIZASYON.md](buck/OPTIMIZASYON.md) §2.

### 1. Ana güç devresi: değerler ve doğrulama — ✅ tamam

- Güç katı değerleri referans yük senaryolarına (sabit güç yükü) göre seçildi ve LTspice'ta sınandı: 5 giriş noktası, yük adımları, yük atma, kalkış, giriş değişimi, örneklenen tolerans köşeleri. Bazı senaryolar sınır dışıdır; aşağıya bakınız.
- Kabul aralıkları: L 33 µH el sarım (DCR 6,5–15 mΩ, hedef 7,5–10 mΩ); Cout 1000 µF ±%20, ESR ≤ 35 mΩ, ≥ 35 V; çıkışa paralel sönüm dalı **Cd 470 µF ±%20 (≥ 35 V) + seri Rd 0,22 Ω** (Rd + Cd_ESR toplamı 0,15–0,60 Ω); Cin ≥ 50 V, ≥ 4,5 A ripple. Örneklenen model setlerinin 200 ms sonuçları ve bir 500 ms köşe senaryosu 9–12 V içinde sönümlü raporlandı ([buck/OPTIMIZASYON.md](buck/OPTIMIZASYON.md) §4.4, §5, §6, §10).
- Bulunan temel sorunlar: sabit güç yüküyle eski değerler ve dalsız tolerans köşesi salınıyordu (`Cd + Rd` dalıyla kapandı); açık çevrim hafif yükte ve giriş değişiminde 11 V'u tutamıyor; sert kalkışta 61,4 A / 16,6 V.
- Çıktılar: [buck/ltspice/buck_guc_kati.asc](buck/ltspice/buck_guc_kati.asc), [buck/OPTIMIZASYON.md](buck/OPTIMIZASYON.md), [buck/hesap.py](buck/hesap.py), [buck/dogrula.py](buck/dogrula.py).
- **Ölçüt:** şematik değerleriyle `dogrula.py secilen` ve `pencere` koşuldu; yük adımlarında çıkış 9–12 V içinde, ripple ≤ 165 mV ve 200 ms darbede sönümlü. **12.11.2026 kaydı:** sınanan anma ve tolerans senaryolarında sonuçlar sağlandı (`pencere` 3/3, `kararlilik` 27/27 satır); tüm tolerans kombinasyonları sınanmadı.

### 2. Gerçek parçaların bulunması — 🔄 sürüyor (aday listesi hazır, kesin seçim bekliyor)

- **Yapıldı:**
  - Her parça için ölçülebilir kriterler ve nedenleri yazıldı.
  - Kriterlerle dış araştırma yapıldı; adaylar kriterlerle karşılaştırıldı.
  - Dört bobin/kondansatör kombinasyonu LTspice köşe testinden geçirildi. Araştırmanın önerdiği 47 µH + 18 mΩ kombinasyonu **kaldı** (12,83 V, 3 V salınım); 33 µH + 35 mΩ **geçti**.
  - Adaylar öncelik sırasına dizildi; kullanıcı kararıyla liste "olabilir" listesidir, kesin seçim değildir.
  - 1. sıra adayların değerleri ve `Cd = 470 µF + Rd = 0,22 Ω` sönüm dalı şematiğe, `hesap.py` ve `dogrula.py` içine yazıldı; `dogrula.py secilen` yeniden koşuldu: sınanan anma ve tolerans senaryolarında sonuçlar sınırların içinde ve sönümlü (12.11.2026).
  - ST veri sayfaları okundu (STPS40M60C Doc ID 018813 Rev 1; STB100N6F7 DocID027210 Rev 2, STP100N6F7'nin D²PAK kardeşi) ve Magnetics `0077536A7` çekirdek veri sayfası (rev. 6/1/2022) doğrulandı.
  - Çıkış sönümü (`Cd = 470 µF + Rd = 0,22 Ω`) ve gerilim sınıfları (**Cout/Cd ≥ 35 V**, **Cin ≥ 50 V**) kararlaştırıldı.
  - Yeni gerilim sınıflarına (`Cout ≥ 35 V`, `Cd ≥ 35 V`, `Rd 0,22 Ω`, `Cin ≥ 50 V`) ve yardımcı elemanlara (giriş MLCC, ortak soğutucu + TO-220 yalıtım, D1 RC sönümleyici) uygun Türkiye ve yurt dışı stoklu adaylar üretici veri sayfalarından doğrulandı, 5 kondansatör seti geçici LTspice köşe testinden geçirildi (5/5 geçti) ve [buck/PARCA-HEDEFLERI.md](buck/PARCA-HEDEFLERI.md) aday listesine eklendi (şematik 1. sıra değerleri kullanıcı seçim yapana kadar değiştirilmedi, 12.11.2026).
- **Kalan (kullanıcı — dondurma sonrası §12.2):**
  - Dondurulan hedef aralıklara göre kesin parçaların belirlenmesi (`Cout` ve `Cd` ≥ 35 V, `Cin` ≥ 50 V, `Rd` 0,22 Ω dahil; bulunurluk, fiyat, delikli/yüzey montaj tercihi).
  - Kesinleşen parçaların değerlerinin üretici veri sayfasından teyidi; [STP100N6F7 TO-220 veri sayfası](https://www.st.com/resource/en/datasheet/stp100n6f7.pdf) erişilebilir, Nichicon / TDK ESR yayımlamıyor.
  - L1 bobininin sarılması; L1, Cout ve Cd fiziksel ölçümü; soğutucu ve seramik kondansatör parça seçimi ([buck/OPTIMIZASYON.md](buck/OPTIMIZASYON.md) §9.5, §11, §12.2).
  - Gerçek parça ve sarım değerlerinin şematiğe yazılıp testlerin yeniden koşulması.
- **Ölçüt:** tüm güç katı parçaları (`L1`, `Cout`, `Cd`, `Rd`, `Cin`, `S1`, `D1`) **kesinleşmiş**, parça numarası, veri sayfası kaynağı ve kullanılan değerler tabloda; değerler üretici veri sayfasından/ölçümden teyitli; bu değerlerle `dogrula.py secilen` sınırların içinde.

### 3. Kayıp ve ısı; güç katının dondurulması — ⏳ bekliyor (hesap kısmı yapıldı, adım kapanmadı)

- **Yapıldı (12.11.2026, HESAP ve ideal olmayan SİM; ölçüm yok):** kayıp bütçesi (toplam ≈ 2,8–3,4 W, verim ≈ %96,1–96,8), çekirdek kaybı (≈ 0,09–0,14 W, B² varsayımıyla kestirim; üst sınır değil), D1 / S1 / L1 ısıl denge ve soğutucu hedefi (ortak, Rth(s-a) ≤ 12 K/W; D1 soğutucusuz ısıl kaçağa gider), anahtarlama zili duyarlılığı (seramik dekuplaj olmadan D1 ters gerilimi 60 V'u aşabiliyor), sıcak takma ve S1 kısa devre gerilimleri ([buck/OPTIMIZASYON.md](buck/OPTIMIZASYON.md) §9).
- **Kalan:** parçalar kesinleşince yeniden hesap; soğutucu, seramik kondansatör ve sönümleyici parça seçimi; fiziksel ölçümler; dondurma kapısının kapanması (§12).

- Bobin çekirdek kaybı (modelde yok) üretici verisiyle hesaplanır.
- S1 ve D1 eklem sıcaklıkları kayıp ve ısıl dirençten hesaplanır; soğutucu ihtiyacı belirlenir.
- Anahtarlama kaybı için ilk kestirim (gerçek parçanın kapı yükü ve geçiş süreleriyle).
- Sönümleyici (snubber) ve giriş/çıkış seramik kondansatörlerinin gerekip gerekmediğine karar verilir.
- **Ölçüt:** sıcaklık dahil kayıp bütçesi yazılı; güç katı eleman listesi değişmeyecek şekilde kayıtlı.

### 4. Kapı sürücüsü — ⏳ mimari hazırlığı sırada

Şematikteki `PULSE` kaynağının yerini gerçek sürücü alır. Üst taraftaki N-MOSFET için sürme yöntemi (bootstrap), sürücü entegresi, kapı direnci, sürücü beslemesi.
**Ölçüt:** sürücülü simülasyonda verim ve gerilim zorlanmaları Adım 1 sonuçlarıyla karşılaştırılmış.

### 5. PWM üretimi ve yumuşak kalkış — ⏳ mimari hazırlığı sırada

PWM kontrolcü seçimi, frekans ayarı, duty rampası. Sert kalkıştaki 61,4 A / 16,6 V sorununu bu adım kapatır.
**Ölçüt:** kalkışta çıkış 12 V'u aşmıyor; bobin tepe akımı doyma payının içinde.

### 6. Geri besleme ve kompanzasyon — ⏳ mimari hazırlığı sırada

Çıkış gerilimi algılama, hata yükselteci, kompanzasyon. Tasarım verileri: Ton aralığı 2,1–5,6 µs, DCM/CCM geçişi ≈ 0,94 A, ana LC f0 ≈ 0,88 kHz, Cd–Rd köşesi ≈ 1,54 kHz, ESR sıfırı ≥ 4,5 kHz (3. derece çıkış filtresi), yük sabit güç karakterli, yük atma bütçesi ≈ 0,75 V (soğuk ESR'de 3 periyot gecikmeyle 11,76 V). Devredilen şartların tam listesi: [buck/OPTIMIZASYON.md](buck/OPTIMIZASYON.md) §11; açık çevrim köşe sönümü `Cd + Rd` dalıyla sağlanmıştır, kapalı çevrim faz/kazanç payları bu adımda gösterilmelidir.
**Ölçüt:** 20–26 V ve 0,24–7,5 A referans yük aralığında çıkış belirlenecek 11 V toleransında; genel modül zarfının 0 A dahil gereksinimleri kullanıcıyla ayrıca belirlenip doğrulanmış; O1 girişinde 12 V üst sınırı her koşulda korunuyor; faz ve kazanç payları belgelenmiş.

### 7. Korumalar — ⏳ mimari hazırlığı sırada

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
| 13.11.2026 | Kesin parça seçiminden önce kontrol ve koruma mimarisinin gereksinimleri belirlenir; kontrolcü ile güç katı adayları birlikte değerlendirilir | Kullanıcı isteği: PWM/geri besleme ile L, çıkış filtresi ve MOSFET sürme gereksinimleri birbirine bağlıdır. 12.11 tarihli açık çevrim dondurması ve aday sırası korunur; yeni kapalı çevrim tasarımı veya seçim yapılmadı. |
| 12.11.2026 | Güç katı simülasyon dondurması **FROZEN** olarak onaylandı (§12.1 #1–12 tamamlandı) | Kullanıcı onayı. Sırada §12.2 (dondurulan hedef aralıklara göre kesin parça seçimi, bobin sarımı ve gerçek değerlerle yeniden doğrulama) var |
| 12.11.2026 | Gerilim sınıfları: **Cout ve Cd ≥ 35 V**, **Cin ≥ 50 V**. Genel modül için ayrı sınır tanımlanmadı (dondurma O1/S2E uyumluluk ölçütleriyle yapılır) | Kullanıcı kararı. S1 kısa devresinde çıkış 27,3–31,1 V'a çıkıyor (25 V aşılıyor); düşük dirençli kaynakla sıcak takmada Cin 45–46,5 V'a çıkabiliyor (35 V aşılıyor). Kesin parçalar §12.2'de bu sınıflara göre seçilecek |
| 12.11.2026 | Çıkışa paralel **`Cd = 470 µF + seri Rd = 0,22 Ω` sönüm dalı** eklendi (`sematik_uret.py`, `hesap.py`, `dogrula.py`, `AGENTS.md` §4.1) | Kullanıcı kararı. Dalsız devrede `L +%20 / Cout −%20 / ESR 15 mΩ` köşesi 200 ms darbede salınıyordu (9,91–12,05 V). Sınanan model setlerinde `Pkritik ≥ 126 W > 82,5 W`, `pencere` 3/3 ve `kararlilik` 27/27 GEÇTİ; `Rd` kaybı 1,3 mW. Diğer ESR ve tolerans kombinasyonları için belirsizlik sürüyor. |
| 12.11.2026 | Sıra: önce simülasyonda dondurma, sonra parça seçimi / bobin sarımı, sonra gerçek değerlerle test, sonra PCB. Dondurma kapısı iki basamağa ayrıldı | Kullanıcı kararı: elde bobin ve parça yok; bobin dondurulan değerlere göre sarılacak. Fiziksel ölçüm dondurmanın ön koşulu sayılmaz |
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
