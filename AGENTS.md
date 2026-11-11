# Çalışma Kuralları (tüm yapay zekâ araçları için)

Bu dosya depodaki **tek kural kaynağıdır**. Codex, Claude Code, ChatGPT ve diğer araçlar için aynen geçerlidir; `CLAUDE.md` yalnız buraya yönlendirir. Kurallarla bir belge çelişirse bu dosya geçerlidir; bu dosyayla kullanıcının o anki açık isteği çelişirse kullanıcıya sorulur.

## 1. İlk okuma sırası

1. [YOL-HARITASI.md](YOL-HARITASI.md) — proje nerede, aktif adım ne, sırada ne var, hangi karar neden alındı.
2. Bu dosya — neyin nasıl yapılacağı.
3. [buck/PARCA-HEDEFLERI.md](buck/PARCA-HEDEFLERI.md) — her parçanın kriteri ve nedeni.
4. [buck/OPTIMIZASYON.md](buck/OPTIMIZASYON.md) — yükler, seçim süreci, test sonuçları, açık riskler.

İşe başlamadan önce `git status` ve `git log -5` ile güncel durumu doğrula; belgelerdeki "şu anki durum" ile depo uyuşmuyorsa önce bunu kullanıcıya bildir.

## 2. Proje özeti

- **Ne:** tekne için güç dağıtım kartı (PDU). 6S bataryadan (20–26 V, ana nokta 24,6 V) 11 V / 7,5 A (82,5 W) üreten tek faz, asenkron buck dönüştürücü, 100 kHz.
- **Yükler:** T3 Gemstone O1 (DC giriş 5–12 V / 5 A) ve SLAMTEC RPLIDAR S2E (9–28 V; 12 V'ta 0,22 A çalışma, 1,5 A kalkış).
- **En kritik sınır:** O1 girişi hiçbir koşulda 12 V'u aşmamalıdır. Mutlak maksimumu yayımlanmamıştır; 12 V üstü için dayanım varsayılmaz.
- **Şu anki hâl:** açık çevrim güç katı, yalnız LTspice'ta. Fiziksel devre, ölçüm, PWM, geri besleme, PCB yok.

Güncel değerler ve aktif adım burada tekrar edilmez; [YOL-HARITASI.md](YOL-HARITASI.md) dosyasındadır.

## 3. Dosya haritası

| Dosya | İçerik | Kim günceller |
|---|---|---|
| `YOL-HARITASI.md` | Durum, adımlar, tamamlanma ölçütleri, karar günlüğü | Her adım/karar değişikliğinde |
| `AGENTS.md` | Kurallar (bu dosya) | Yalnız kullanıcı isteyince |
| `CLAUDE.md` | `AGENTS.md`'ye yönlendirme | Değişmez |
| `README.md` | İnsan için özet, şematik görseli, deneme adımları | Değer veya sonuç değişince |
| `buck/PARCA-HEDEFLERI.md` | Parça kriterleri, nedenleri, bulunurluk, arama istemi | Kriter veya parça değişince |
| `buck/OPTIMIZASYON.md` | Yükler, seçim süreci, test tabloları, riskler | Testler yeniden koşulunca |
| `buck/ltspice/buck_guc_kati.asc` / `.svg` | LTspice şematiği ve görseli (**üretilir**, elle yazılmaz) | `sematik_uret.py` ile |
| `buck/ltspice/sematik_uret.py`, `asc_gorsel.py` | Şematik ve görsel üreteci | Değer değişince |
| `buck/ltspice/anahtar.asy`, `diyot.asy`, `idealler.lib` | İdeal anahtar/diyot tanımları | Değişmez |
| `buck/hesap.py` | Analitik hesap | Değer değişince |
| `buck/dogrula.py` | LTspice doğrulama koşuları | Değer veya test değişince |
| `buck/grafik/*.svg` | Dalga şekilleri (**üretilir**) | `dogrula.py grafik` ile |

## 4. Temel kurallar

### 4.1 Kapsam
- Aktif kapsam [YOL-HARITASI.md](YOL-HARITASI.md) içindeki **aktif adımdır**. "Kapsam dışı" işaretli adımlara (kapı sürücüsü, PWM, geri besleme, soft-start, korumalar, PCB) kullanıcı açıkça istemeden başlanmaz; bu adımlara ait devre, dosya veya kod eklenmez.
- Devre kapsamı şu an: DC kaynak, anahtar S1, diyot D1, bobin L1, giriş/çıkış kondansatörleri, direnç yükü. Anahtar LTspice `PULSE` kaynağıyla sürülür.
- İstenmeyen ek özellik, yeniden düzenleme veya "iyileştirme" yapılmaz. Daha iyi bir yol görülürse önerilir, uygulanmaz.

### 4.2 Değerler ve parçalar
- **Tek doğruluk kaynağı:** şematik değerleri `buck/ltspice/sematik_uret.py`, `buck/hesap.py` ve `buck/dogrula.py` (`SECILEN`) içinde aynı olmalıdır. Biri değişirse üçü birlikte değişir, testler yeniden koşulur, belgelerdeki sayılar yenilenir.
- Bir değeri değiştirmeden önce nedenini oku ([buck/PARCA-HEDEFLERI.md](buck/PARCA-HEDEFLERI.md), yol haritasındaki karar günlüğü). Bilerek alınmış kararlar: Cout ESR'sinin **alt sınırı** vardır; 22 µH ve 680 µF **elenmiştir**; Cout/L büyütmek giriş değişimi etkisini düzeltmez.
- Şematik parça numarasından bağımsız **hedef değerleri** taşır. Belirli parça numarası (MPN) seçilmez ve şematiğe yazılmaz; parçayı kullanıcı bulur. Parça araması yalnız kullanıcı isterse yapılır ve sonuç "kriteri tutan örnek" olarak yazılır.
- Kullanıcı bir parça getirdiğinde: veri sayfası değerlerini kriterlerle tek tek karşılaştır → uyuyorsa değerleri üç dosyaya yaz → `dogrula.py secilen` ve `pencere` koş → belgeleri güncelle. Veri sayfasında bulunmayan değer tahmin edilmez; "doğrulanamadı" yazılır.

### 4.3 Şematik
- Ana şematik yalnız değer tabanlıdır: ideal anahtar/diyot, L/C + ESR/DCR. `.param`, `.meas`, `.ic`, `.model`, açıklama notu veya gerçek parça SPICE modeli eklenmez. Şematikteki tek yönerge `.tran` satırıdır.
- S1 ve D1 değerleri (`Ron=`, `Vf=`) parçanın üstünde yazar; tanımları `anahtar.asy` / `diyot.asy` / `idealler.lib` içindedir.
- `.asc` elle düzenlenmez; `python buck/ltspice/sematik_uret.py [Ton_us]` ile üretilir ve `.svg` görseli aynı anda yenilenir. Kullanıcı şematiği LTspice'ta elle değiştirirse `python buck/ltspice/asc_gorsel.py` koşulur; ikisi birlikte commit edilir.
- Test için gereken ölçüm, yük modeli veya değişken duty **yalnız** `dogrula.py`'nin ürettiği geçici netlistlerde bulunur.

### 4.4 Doğruluk ve dürüstlük
- Dört bilgi türü ayrı tutulur ve etiketlenir: **DATASHEET** (üretici belgesi), **HESAP** (analitik), **SİM** (LTspice), **ÖLÇÜM** (fiziksel). Ayrıca **TAHMİN** ve **ÇIKARIM** açıkça işaretlenir.
- Koşulmamış simülasyon için sonuç, "tamamlandı" veya "PASS" yazılmaz. Değer, sonuç veya ölçüm uydurulmaz.
- İdeal modelin kapsamadıkları (anahtarlama kaybı, çekirdek kaybı, doyum, parazitikler, ısı) doğrulanmış gibi gösterilmez.
- Başarısız test silinmez veya ölçütü gevşetilerek geçirilmez; nedeniyle yazılır.
- Kaynak gösterilen her değer için belge adı ve bağlantı verilir.

### 4.5 Güvenlik
- Gerçek O1, RPLIDAR S2E veya başka hassas yük bağlanması **önerilmez**: açık çevrim devre 11 V regülasyonunu ve 12 V üst sınırını garanti etmez. Gerçek yük ancak yol haritasındaki Adım 10 koşulları sağlanınca gündeme gelir.

### 4.6 Dosya düzeni
- Dosya yapısı sade tutulur. Yeni rapor, betik, sonuç klasörü veya arşiv kullanıcı istemeden oluşturulmaz. Geçici dosyalar depoya girmez (`*.raw`, `*.log`, `*.net` yok sayılır).
- Belgeler Türkçe yazılır; dosyalar UTF-8'dir. Windows kabuğunda Türkçe karakterli metni heredoc ile Python'a verme (bozulur); dosyaya yazıp çalıştır.
- Her belge güncel durumu anlatır; eski sürümlerin anlatısı belgede biriktirilmez (geçmiş `git log`'da ve karar günlüğündedir).

### 4.7 Git
- Çalışma dalı `main`. Tamamlanan adımlar ayrı dalda dondurulur (`ANA-GUC-DEVRESI`, etiket `ana-guc-devresi-v2`); dondurulmuş dala yeni iş yazılmaz.
- Commit ve push yalnız kullanıcı isteyince yapılır. Commit mesajı Türkçe, ne değiştiğini ve nedenini söyler.
- Geçmiş yeniden yazılmaz (`push --force`, `reset --hard` yok); dal veya etiket silmeden önce kullanıcıya sorulur.
- GitHub işlemleri için `gh` kullanılır (bu makinede `C:\Program Files\GitHub CLI\gh.exe`).

## 5. Araçlar

| Komut | Ne yapar | Süre |
|---|---|---|
| `python buck/ltspice/sematik_uret.py [Ton_us]` | `.asc` ve `.svg` üretir | anlık |
| `python buck/hesap.py` | Analitik özet (LTspice değildir) | anlık |
| `python buck/dogrula.py secilen` | Şematik değerleriyle tüm testler: 5 giriş, gerçek yük senaryoları, yük adımı, yük atma, kalkış, giriş değişimi, tolerans köşeleri, giriş tarafı | ≈ 15 dk |
| `python buck/dogrula.py pencere` | L / Cout / ESR kabul aralıklarının kenarları | ≈ 12 dk |
| `python buck/dogrula.py tarama` | İlk 9 adaylık L × Cout karşılaştırması | ≈ 15 dk |
| `python buck/dogrula.py mevcut` | En baştaki eski değerlerle aynı testler | ≈ 15 dk |
| `python buck/dogrula.py grafik` | `buck/grafik/*.svg` | ≈ 2 dk |

- LTspice yolu `LTSPICE` ortam değişkeniyle verilebilir (varsayılan `C:\Program Files\ADI\LTspice\LTspice.exe`).
- `dogrula.py` LTspice'ı görünmeyen ayrı bir Windows masaüstünde başlatır; kullanıcının pencere odağını almaz. Bu davranış bozulmamalıdır.
- Uzun koşular arka planda çalıştırılır; aynı anda iki koşu başlatılmaz (birbirini yavaşlatır).
- Kabul ölçütü: yük adımlarında çıkış 9–12 V içinde, ripple ≤ 165 mV t-t (`dogrula.py` içindeki `VO_MIN`, `VO_MAX`, `RIPPLE_MAX`).

## 6. Bir iş nasıl yapılır

1. Yol haritasında aktif adımı ve ölçütünü oku; istenen iş o adıma ait mi bak.
2. Değişikliği yap; değer değiştiyse §4.2'deki üç dosyayı birlikte güncelle.
3. Etkilenen testleri **gerçekten** koş; sonucu ölçütle karşılaştır.
4. Belgeleri güncelle: `README.md` (değer/sonuç), `buck/OPTIMIZASYON.md` (test tabloları), `buck/PARCA-HEDEFLERI.md` (kriter), `YOL-HARITASI.md` (durum, karar günlüğü).
5. Depoda eski değerden kalan ifade var mı diye ara.
6. Kullanıcıya ne değişti, ne doğrulandı, ne doğrulanamadı açıkça yaz. Commit/push için onay al.

## 7. PCB aşaması (Adım 9) için kurallar

Bu bölüm ileriye dönüktür. PCB işine kullanıcı açıkça başlatmadan girilmez; başlatıldığında aşağıdakiler geçerlidir. Sayısal iz genişliği, açıklık ve bakır kalınlığı burada **verilmemiştir**: seçilen kart üreticisinin kurallarına ve hesaplara göre o aşamada belirlenir ve belgelenir.

### 7.1 Başlamadan önce
- Güç katı dondurulmuş (Adım 3), sürücü, PWM, geri besleme ve korumalar tasarlanmış (Adım 4–7) ve tezgâhta ölçülmüş (Adım 8) olmalıdır. Eksik adımla PCB'ye geçilecekse kullanıcıya açıkça söylenir.
- Araç, katman sayısı, bakır kalınlığı ve kart üreticisinin tasarım kuralları kullanıcıyla netleştirilir (önceki tasarımda KiCad kullanılmıştı; varsayılmaz, sorulur).
- Her parçanın kılıfı ve ayak izi **seçilen parçanın veri sayfasından** alınır; kütüphane ayak izi veri sayfası ölçüleriyle karşılaştırılır.

### 7.2 Tasarım girdileri (bu depodan)
- Akımlar: çıkış 7,5 A sürekli; bobin tepe 8,9 A; giriş ortalama ≈ 4,3 A (20 V'ta); Cin ripple akımı 3,8 A RMS; S1 5,7 A RMS; D1 4,2 A ortalama. Sert kalkış ve arıza akımları ayrıca (Adım 5 ve 7 sonuçlarıyla) ele alınır.
- Gerilimler: giriş 26 V, batarya takma anında ≈ 28 V; anahtar düğümü 0 ↔ giriş gerilimi arasında 100 kHz'de salınır.
- Isı: D1 ≈ 2,3 W, S1 ≈ 0,3 W iletim + anahtarlama, L1 ≈ 0,85 W bakır + çekirdek. Güncel değerler Adım 3 çıktısından alınır.

### 7.3 Yerleşim
- **Sıcak çevrim** (Cin → S1 → D1 → Cin) mümkün olan en küçük alanda kurulur; Cin, S1 ve D1 birbirine bitişik yerleştirilir. Bu çevrim önce yerleştirilir, diğer her şey ona göre.
- **Anahtar düğümü** (S1–D1–L1 birleşimi) akımı taşıyacak kadar geniş ama gereğinden büyük olmayan bir bakır alanıdır; altından ve yanından duyarlı sinyal geçirilmez.
- Güç yolları iz yerine **bakır alan** (polygon) ile taşınır. Genişlik IPC-2221 veya üreticinin hesaplayıcısıyla, seçilen bakır kalınlığı ve izin verilen sıcaklık artışı için hesaplanır; hesap belgeye yazılır.
- **Toprak:** güç toprağı (Cin eksi, D1 anot, Cout eksi) kısa ve geniş tutulur. Kontrol/ölçüm toprağı güç toprağına **tek noktada**, Cout eksi ucunda bağlanır.
- **Geri besleme algılama** Cout uçlarından (yük tarafından) Kelvin bağlantıyla alınır; anahtar düğümünden ve bobinden uzak, toprak üstünde yönlendirilir.
- **Akım ölçümü** varsa şönt uçlarından Kelvin bağlantıyla, iki iz yan yana alınır.
- Cout, yük konnektörüne yakın; çıkış akımı önce Cout uçlarından geçip sonra konnektöre gider.
- Soğutucu gerektiren parçalar (S1, D1) kart kenarına ve aynı soğutucuya bağlanabilecek şekilde hizalanır; gövdeleri farklı potansiyeldedir (S1 drain, D1 katot), yalıtım pedi öngörülür. Isıl geçiş delikleri ve bakır alanı ısı hesabına göre konur.
- Elektrolitik kondansatörler ısı kaynaklarından (L1, D1, S1) uzak tutulur.
- O1 ve S2E çıkışları ayrı konnektörlerle, kutupları kart üzerinde yazılı olarak çıkarılır; O1 hattındaki koruma (Adım 7) konnektöre yakın yerleştirilir.
- Tezgâh ölçümü için test noktaları: giriş, anahtar düğümü, çıkış, kapı, geri besleme, toprak (osiloskop toprak yayı için kısa bağlantı imkânı).

### 7.4 Denetim ve teslim
- Şematikten karta geçmeden elektriksel kural denetimi (ERC), kart bitince tasarım kuralı denetimi (DRC) **gerçekten koşulur**; hata ve uyarılar tek tek kapatılır veya gerekçesiyle belgelenir. Koşulmamış denetim "temiz" diye raporlanmaz.
- Şematikle kart ağ listesi eşleşmesi doğrulanır; LTspice şematiğindeki değerlerle kart şemasındaki değerler aynı olmalıdır.
- Üretim dosyaları (Gerber, delik, yerleşim, malzeme listesi) kullanıcı istemeden üretilmez ve gönderilmez.
- Kart üzerinde: kutup işaretleri, giriş/çıkış gerilim etiketleri, sürüm ve tarih.
- İlk kart gerçek yüke bağlanmaz; önce direnç yükle Adım 8 ölçümleri tekrarlanır.

## 8. Yapılmayacaklar (kısa liste)

- Kullanıcı istemeden sonraki adıma geçmek, yeni dosya açmak, commit/push yapmak.
- Şematiğe yönerge, parça modeli veya parça numarası eklemek.
- Koşulmamış test için sonuç yazmak; tahmini veri sayfası değeri gibi sunmak.
- Bir değeri nedenini okumadan değiştirmek (özellikle Cout ESR, L1, Cout).
- Üç dosyadan (üreteç, hesap, doğrulama) yalnız birini güncellemek.
- Gerçek O1 / S2E bağlanmasını önermek.
