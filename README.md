# Açık çevrim buck güç katı

20–26 V girişten (6S batarya, ana çalışma noktası 24,6 V) 11 V / 7,5 A (82,5 W) hedefleyen tek faz, asenkron, açık çevrim buck güç katı. Modül 0–7,5 A zarfında farklı uyumlu yükler içindir; T3 Gemstone O1 ve SLAMTEC RPLIDAR S2E referans yüklerdir.

**Aşama: ANA GÜÇ DEVRESİ.** Güç katının değerleri belirlendi ve LTspice'ta sınandı; parçalar için aday listesi var, kesin seçim yapılmadı. PWM, geri besleme ve soft-start henüz yok; fiziksel devre kurulmadı.

**Güncel yol:** Sabit 100 kHz tepe-akım + şönt yönü LT3844 referansıyla geçici LTspice netlistlerinde inceleniyor. 19 Kasım'da 20–26 V giriş/yük/eşik taraması ve 200 ms sabit güç yükü testi tamamlandı (12/12 koşu 10,78–11,19 V, ripple ≤ 60,6 mV, yavaş salınım sönmüş; SİM, [OPTIMIZASYON §16.19](buck/OPTIMIZASYON.md)). En düşük eşik köşesinde tam güç basamağı akım sınırına dokunuyor. Tolerans köşelerinde (§16.20) 16 koşunun 14'ü geçti. 20 V'ta L −%30 ile 41,25→82,5 W basamağında çıkış çöktü (KALDI); L ≥ 30,7 µH (el sarım alt sınırı) ile geçiyor, 26,4 µH (satın alma −%20) ile çöküyor. O1/S2E adımları tüm köşelerde geçti. Karar: bu yönde L1 tepe akımda ≥ 29,8 µH (el sarım); 29,8 ve 28,0 µH doğrulamada geçti. Gerçek sense gecikmesi, şönt termali, bobin L(I) ve bağımsız OVP hâlâ doğrulanmadı. LM5088 daha ucuz aday, fakat geçerli modeli yok ve TI hesabı erişim hatası nedeniyle TINA-TI kurulamadı. Kontrolcü/şönt seçilmedi. Bobinde 22 tur / 33 µH hedefi korunuyor; 12 A tasarım hedefidir, sert maksimum garantisi değildir. Gerçek bobin ölçümü ve fiziksel doğrulama yoktur. [Yol haritası](YOL-HARITASI.md) sırayı ve açık işleri gösterir.

**Dondurma durumu: FROZEN (12 Kasım 2026, simülasyon dondurması).** Çıkışa paralel `Cd = 470 µF + seri Rd = 0,22 Ω` sönüm dalı eklendi. Örneklenen model setlerinde 200 ms ve ayrı bir köşede 500 ms sabit güç darbeleri sönümlü raporlandı; bütün yük, sıcaklık ve tolerans kombinasyonları doğrulanmış değildir. Gerilim sınıfları **Cout ve Cd ≥ 35 V**, **Cin ≥ 50 V** olarak belirlendi. Açık çevrim güvenli 11 V regülasyonu sağlamaz; fiziksel ölçüm yoktur ve hassas yükler bağlanmamalıdır. Kanıt ve kalan işler: [buck/OPTIMIZASYON.md](buck/OPTIMIZASYON.md) §12–13.

**Kontrol yöntemi araştırması:** Depodaki açık çevrim testleri ile dışarıdaki kapalı çevrim model denemeleri ayrı tutuldu. İlk LT3844, Type-III ve ortalama-akım sonuçlarının tarihçesi [OPTIMIZASYON.md](buck/OPTIMIZASYON.md) §14–15'tedir; son tekrar, ön puan ve güç katı değişikliği hesabı §16'dadır.

**Öncelikli yöntem yönü (14 Kasım 2026):** Kullanıcı sonraki arayüz çalışması için sabit 100 kHz tepe-akım kipini ve şönt algılama yolunu geliştirme yönü olarak seçti (yöntem kararı; kontrolcü veya şönt parçası/değeri seçilmedi). 9,76 mΩ yalnız örnek varsayımdır; şöntte 7,5 A için yaklaşık 0,55 W nominal DC kayıp hesaplanır.

**Şönt testi ve taraması (15 Kasım 2026):** İlk taramada `Rfreq=191 kΩ` LT3844 makromodelinde 105,9 kHz çıktı; o sonuçlar 100 kHz doğrulaması değildi. Test netlisti makromodele göre 204,53 kΩ'a kalibre edilince ölçülen frekans 99,985–100,006 kHz oldu. Bu koşulda ±1% taranan örneklerin en dengelisi 9,77 mΩ: normal profil payı 0,28 mV, 12 A hedef payı 0,023 A (yaklaşık 0,223 mV). 7,5 A açılışında tepe 9,200 A, çıkış en az 10,965 V oldu. Bu geçici model sonucu; gecikme, bobin doyumu ve gerçek toleranslar doğrulanmadı. Kontrolcü/şönt seçilmedi. Ayrıntı [buck/OPTIMIZASYON.md](buck/OPTIMIZASYON.md) §16.12–16.15'tedir.

**Giriş/yük köşeleri (19 Kasım 2026):** `dogrula.py sunt_giris` 20 LTspice koşusunu tamamladı (20, 22,2, 24,6, 25,2, 26 V; profil, tam yük ve eşik uçları). Normal profil/tam yük örneklerinde Vout 10,957–11,169 V, ripple 44,9–58,7 mV t-t; yapay aşırı yükte akım tepesi 11,950–11,977 A ve Vout 8,270–8,354 V oldu. Eşik min/max değerleri ideal ölçeklemeyle temsil edildi; bu sonuçlar comparator gecikmesini, gerçek şönt/bobin termalini veya 12 A güvenliğini doğrulamaz. Ayrıntı [buck/OPTIMIZASYON.md](buck/OPTIMIZASYON.md) §16.18'dedir.

**Kontrolcü maliyet/kayıp ön elemesi (15 Kasım 2026):** LM5088-2, mevcut asenkron katla uyumlu düşük maliyet adayıdır (Mouser'da tek adet 5,07 USD); LT3844 tek adet 10,02 USD ve LTspice'ta daha güçlü referans kanıtıdır. TI boyutlama denkleminden çıkan 9,49 mΩ LM5088 şöntü serbest-dolaşım kolunda yaklaşık 0,31 W; LT3844'ün çıkışla seri 9,77 mΩ örneği yaklaşık 0,55 W HESAP kaybı verir. TI'nin şifresiz LM5088 geçici ve average makromodelleri LTspice'ta kullanılabilir sonuç vermedi. LM5088 için geçerli devre SİM kanıtı yoktur; eşik ve gecikme de 12 A sert üst sınırını garanti etmez. Kullanıcı TI hesabı açarken hata aldı; TINA-TI/PSpice erişimi yok. Şimdilik LT3844 yalnız LTspice test referansı; kontrolcü seçilmedi. Ayrıntı [buck/OPTIMIZASYON.md](buck/OPTIMIZASYON.md) §16.17'dedir.

**Kapalı çevrim son tekrar (14 Kasım 2026):** LT3844 F sabit-frekans tepe-akım makromodeli 20 µs yük rampasında 10,794–11,165 V, 20–26–20 V / 200 ms sabit-güç koşusunda 10,904–11,043 V verdi; bobin akımından yaklaşık 99,95 kHz sayıldı. Ancak depodaki aynı ayarlı örnek şematik (Rset 191 kΩ) 19 Kasım'da kapı darbelerinden 105,87 kHz verdi; 14 Kasım netlisti depoda olmadığından bu frekans iddiası **doğrulanamadı**. Örnek şematik 204,53 kΩ'a güncellendi (99,984 kHz, SİM). Modeldeki 9,76 mΩ seri akım algısı direnci dondurulmuş güç yolunda yok ve 7,5 A'ta 0,549 W HESAP kaybı ekler. Type-III Ki=200 / 9 A **ideal** akım kesimi 20 µs rampasında 9,809–11,478 V verdi; yüksüz 20 V için tamamlanmış 120 ms simülasyonda 48 ms referans rampasıyla çıkış 11,413 V tepe / 11,410 V geç değer oldu. Histeretik 25 mV modelinin çıkış aralığı daha dardı, ancak frekansı girişe göre 93,7–121,2 kHz değiştirdi. 100 kHz için LT3844 tipi kontrol en güçlü dinamik referans. DCR doğrudan bağlantısı başarısız; tamponlu DCR modeli seçilmiş koşullarda çalıştı ama sıcaklık/eşik/tolerans doğrulaması tamamlanmadı. Ön puan ve ara karşılaştırma [buck/OPTIMIZASYON.md](buck/OPTIMIZASYON.md) §16.4–16.10'dadır. Mimari/parça seçilmedi; bağımsız OVP doğrulanmadığından gerçek O1/S2E bağlanmaz.

**Nerede kaldık, sırada ne var:** [YOL-HARITASI.md](YOL-HARITASI.md) · **Çalışma kuralları (yapay zekâ araçları dahil):** [AGENTS.md](AGENTS.md)

![LTspice şematiği](buck/ltspice/buck_guc_kati.svg)

## Devre değerleri ve parçalar

| Eleman | Şematikteki değer | 1. sıra aday (kesin değil) | Kabul aralığı |
|---|---|---|---|
| V1 | 24,6 V | 6S batarya | 20–26 V |
| Vdrv | 100 kHz, Ton = 4,59 µs | — (sonraki aşamada sürücü + PWM) | — |
| L1 | 33 µH el sarım, DCR 7,81 mΩ (HESAP, 20 °C) | Magnetics Kool Mµ 40µ `0077536A7`, 22 sarım, 100 × 0,20 mm litz (2. sıra: satın alma, Würth 74435583300) | **33 µH** (el sarım 30,7–36,1 µH öngörü; satın alma ±%20 için örnek köşeler sınandı); DCR 6,5–15 mΩ (el sarım hedefi 7,5–10 mΩ); 12 A'de L ≈ %95 (HESAP) |
| Cout | 1000 µF, ESR 35 mΩ (**maks. empedans, ESR varsayımı**) | Nichicon UHE1E102MHD6TO *(elektriksel R/C referansı; kesin parça ≥35 V seçilecek)* | 1000 µF ±%20, ESR ≤ 35 mΩ, **≥ 35 V** (S1 kısa devresinde 27,3–31,1 V) |
| Cd + Rd | 470 µF + seri 0,22 Ω (çıkış sönüm dalı) | — (dondurma sonrası seçilecek) | Cd: 470 µF ±%20, **≥ 35 V**; Rd: 0,22 Ω (Rd + Cd_ESR toplamı **0,15–0,60 Ω**), ≥ 0,25 W |
| Cin1, Cin2 | 2 × 1000 µF, ESR 15 mΩ | 2 × TDK B41859D7108M000 *(elektriksel R/C referansı; kesin parça ≥50 V seçilecek)* | toplam ripple akımı ≥ 4,5 A, **≥ 50 V**; örnek sıcak takma hesabı 48,0 V, gerçek kaynak ve pay doğrulanmadı |
| S1 | ideal anahtar, `Ron=5.6m` | STP100N6F7 (60 V, TO-220) | RDS(on) ≤ 12 mΩ, VDS ≥ 55 V |
| D1 | ideal diyot, `Vf=0.38 Ron=8m` | STPS40M60CT (60 V, 2 × 20 A, iki bacak paralel) | VF ≤ 0,58 V @ 7,5 A, VRRM ≥ 45 V |
| Rload | 1,467 Ω | ≥ 100 W direnç yükü | — |

Şematik ideal elemanlıdır; değerler aday listesinin başındaki parçaların veri sayfasından alınmıştır. Bu bir satın alma kararı değildir. Adayların sırası ve nedeni, doğrulama durumu ve kriterlerin nedenleri: [buck/PARCA-HEDEFLERI.md](buck/PARCA-HEDEFLERI.md). Seçim süreci ve test sonuçları: [buck/OPTIMIZASYON.md](buck/OPTIMIZASYON.md).

LTspice sonucu (24,6 V giriş, kararlı durum, 19–20 ms): Vo = 11,000 V, çıkış ripple'ı 55,7 mV t-t, bobin akımı 6,56–8,44 A. Fiziksel ölçüm yoktur.

Açık çevrim: Ton sabitken giriş veya yük değişirse çıkış 11 V'ta kalmaz; soft-start yoktur (sert kalkışta LTspice 61,4 A / 16,6 V gösterir). **Gerçek O1 veya S2E bağlanmaz.**

## LTspice'ta deneme

1. `buck/ltspice/buck_guc_kati.asc` dosyasını aç, **Run** (koşan adam simgesi) düğmesine bas.
2. `out` telinin üstüne tıkla → çıkış gerilimi. L1'in gövdesine tıkla → bobin akımı.
3. İlk ~10 ms kalkış salınımıdır; kararlı durum için 19–20 ms arasını büyüt (fareyle sürükle).
4. Grafikte iz adına (`V(out)`) **Ctrl + sol tık** → ortalama ve RMS değeri.
5. Değer değiştirmek için parçanın üstündeki değere sağ tıkla, yaz, yeniden Run. S1 ve D1 de aynı şekilde değişir (`Ron=…`, `Vf=…`).

Şematikteki tek yönerge `.tran 20m` satırıdır (simülasyon süresi); LTspice bunu şematikte ister.

Beklenen (24,6 V giriş, 19–20 ms): V(out) ortalama ≈ 11,00 V, ripple ≈ 56 mV t-t, I(L1) ≈ 6,6–8,4 A.

## Dosyalar

| Dosya | Ne işe yarar |
|---|---|
| [YOL-HARITASI.md](YOL-HARITASI.md) | Güncel durum, adımlar ve tamamlanma ölçütleri, karar günlüğü |
| [AGENTS.md](AGENTS.md) | Çalışma kuralları: neyin nasıl yapılacağı, araçlar, PCB aşaması kuralları |
| [buck/ltspice/buck_guc_kati.asc](buck/ltspice/buck_guc_kati.asc) | LTspice şematiği (çift tıkla aç, Run) |
| [buck/PARCA-HEDEFLERI.md](buck/PARCA-HEDEFLERI.md) | Aday parçalar (öncelik sırasıyla), kriterler (en az/en çok değerler) ve nedenleri, Türkiye'de bulunurluk, parça arama istemi |
| [buck/OPTIMIZASYON.md](buck/OPTIMIZASYON.md) | Yük gereksinimleri, değerlerin nasıl seçildiği, test sonuçları, açık riskler |
| [buck/hesap.py](buck/hesap.py) | Analitik hesap: ripple, akımlar, LC dinamiği, sabit güç yükü kararlılığı, kayıp ve ısı bütçesi, gerilim sınıfları (`python buck/hesap.py`) |
| [buck/dogrula.py](buck/dogrula.py) | LTspice doğrulama koşuları (`python buck/dogrula.py secilen` / `pencere` / `kararlilik` / `zarf` / `stres` / `sunt` / `sunt_tarama` / `sunt_tol_tarama` / `sunt_giris` / `sayisal` / `tarama` / `grafik`) |
| `buck/grafik/*.svg` | `dogrula.py grafik` ile üretilen dalga şekilleri |
| `buck/ltspice/anahtar.asy`, `diyot.asy`, `idealler.lib` | İdeal anahtar ve diyot parçaları; şematikle aynı klasörde durmalı, elle açmak gerekmez |
| [buck/ltspice/sematik_uret.py](buck/ltspice/sematik_uret.py), [asc_gorsel.py](buck/ltspice/asc_gorsel.py) | Şematiği ve yukarıdaki görseli üretir |
| [CLAUDE.md](CLAUDE.md) | Claude Code için `AGENTS.md` ve `YOL-HARITASI.md` dosyalarına yönlendirme |
