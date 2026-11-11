# Yol haritası — güç katından nihai PCB'ye

Bu dosya sırayı gösterir, takvim değildir. Her adımın bir tamamlanma ölçütü vardır; ölçüt sağlanmadan sonraki adıma geçilmez. [CLAUDE.md](../CLAUDE.md) gereği sonraki adıma yalnız kullanıcı istediğinde geçilir.

**Şu anki konum:** Adım 2 tamamlandı, Adım 3 bekliyor.

Adım 5'ten itibaren işler, `CLAUDE.md`'deki güncel kapsamın (yalnız açık çevrim güç katı) dışındadır. O adımlara geçmeden önce kapsam kuralı kullanıcı tarafından güncellenmelidir.

## Tamamlanan

### 1. Gereksinim ve analitik hesap — tamam
- 20–26 V giriş, 11 V / 7,5 A (82,5 W), tek faz asenkron buck.
- Çıktılar: [PROJE-TANIMI.md](PROJE-TANIMI.md), [TASARIM-HESABI.md](TASARIM-HESABI.md), [PARAMETRE-KARSILASTIRMA.md](PARAMETRE-KARSILASTIRMA.md).

### 2. Açık çevrim güç katının LTspice doğrulaması — tamam
- 100 kHz, 33 µH, BSZ065N06LS5, RBR40NS60A, CIN 2 × 220 µF, COUT 330 µF.
- Simülasyon verimi %97,1–97,7; ripple ve gerilim zorlanmaları hedef içinde.
- Çıktılar: [ltspice/SONUC.md](ltspice/SONUC.md), [ltspice/buck_guc_kati.asc](ltspice/buck_guc_kati.asc).
- Bu adımdan devreden açık konular aşağıdaki adımlara dağıtıldı.

## Sıradaki adımlar

### 3. Parçaların veri sayfasıyla doğrulanması
LTspice kütüphane kayıtları üretici verisiyle karşılaştırılır; şu an hiçbir parça doğrulanmış değildir.
- M1: Rds(on) sıcaklık eğrisi, Qg, Vgs sınırları, kılıf ve termal direnç.
- D1: Vf(I, T), ters kaçak akımın sıcaklıkla artışı, kılıf.
- L1: Isat ve Irms (sıcaklıkla), DCR, çekirdek kaybı verisi, boyut.
- CIN / COUT: ESR(f, T), ripple akımı derecesi, ömür, gerilim payı.
- Temin edilebilirlik ve maliyet; gerekirse eşdeğer parça ve simülasyonun yeniden koşulması.

**Ölçüt:** her parça için MPN, veri sayfası kaynağı ve kullanılan değerlerin tablosu; kütüphane değerinden sapan parametrelerle güç katı simülasyonu yeniden koşulmuş.

### 4. Kayıp ve ısı modelinin tamamlanması, güç katının dondurulması
- Bobin çekirdek kaybı üretici verisiyle hesaplanır (LTspice modelinde yok).
- M1 ve D1 eklem sıcaklıkları, kayıplar ve termal dirençlerden hesaplanır; soğutma ihtiyacı belirlenir.
- RC sönümleyici (2,2 Ω + 1 nF) ile giriş/çıkış MLCC'lerinin ana şematiğe alınıp alınmayacağına karar verilir. Simülasyon, bunlar olmadan diyot ters geriliminin kırılma sınırına çıktığını gösteriyor.
- Yerleşim endüktansı varsayımları (3–5 nH) hedef olarak kayda geçirilir.

**Ölçüt:** sıcaklık dahil kayıp bütçesi; güç katı eleman listesi ve değerleri değişmeyecek şekilde kayıtlı.

### 5. Kapı sürücüsü
Simülasyondaki yüzer PULSE kaynağının yerini gerçek devre alır.
- Yüksek taraftaki N-MOSFET için sürme yöntemi (bootstrap veya yalıtımlı besleme) ve sürücü entegresi.
- Kapı direnci, gerçek kenar hızlarıyla zil ve anahtarlama kaybının yeniden simülasyonu.
- Sürücü beslemesi ve en yüksek duty sınırı.

**Ölçüt:** sürücülü güç katı simülasyonunda verim ve gerilim zorlanmaları Adım 2 sonuçlarıyla karşılaştırılmış.

### 6. PWM üretimi ve yumuşak kalkış
- PWM kontrolcü veya üreteç seçimi, anahtarlama frekansı ayarı.
- Duty rampası (soft-start). Simülasyonda sert kalkış çıkışı ~18 V'a aşırıyor ve bobin akımını ~36 A'ya çıkarıyor; bu adım o sorunu kapatır.

**Ölçüt:** kalkışta çıkış 12 V'u aşmıyor, bobin tepe akımı Isat payının içinde.

### 7. Geri besleme ve kompanzasyon
- Çıkış gerilimi algılama, hata yükselteci, kompanzasyon ağı.
- Çevrim kazancı: faz ve kazanç payı, tüm giriş/yük aralığında.
- Hat ve yük adımı cevabı; hafif yükte (DCM) davranış.

**Ölçüt:** 20–26 V ve %10–120 yük aralığında çıkış 11 V toleransında, 12 V üst sınırı her koşulda korunuyor, kararlılık payları belgelenmiş.

### 8. Korumalar
- Aşırı akım / kısa devre, çıkış aşırı gerilimi, giriş düşük gerilim kilidi (6S LiPo için), ters bağlantı, aşırı sıcaklık.
- Her korumanın eşiği ve arıza anındaki davranışı.

**Ölçüt:** her arıza senaryosu simülasyonda denenmiş; hiçbirinde parça sınırı aşılmıyor.

### 9. Tüm sistemin simülasyonu
- Kapalı çevrim devrenin tolerans, sıcaklık ve giriş köşelerinde koşulması.
- Kalkış, kapanış, yük adımı, kısa devre ve batarya gerilimi düşüşü senaryoları.

**Ölçüt:** tek bir rapor; bütün köşelerde gereksinimler sağlanıyor veya sapmalar gerekçeli.

### 10. Şematik ve malzeme listesinin dondurulması
- EDA aracında tam şematik (konnektörler, test noktaları, sigorta dahil).
- Malzeme listesi: MPN, kılıf, alternatifler.
- Tasarım gözden geçirmesi.

**Ölçüt:** şematik elektriksel kural denetiminden hatasız geçiyor; malzeme listesi tam.

### 11. Prototip kart ve laboratuvar ölçümü
- Ölçüme uygun ilk kart (bol test noktası, sönümleyici için boş yerler).
- Ölçümler: verim, çıkış/giriş ripple'ı, anahtar düğümü zili, kalkış, yük adımı, parça sıcaklıkları.
- Simülasyonla karşılaştırma; sönümleyici ve kompanzasyon değerlerinin ölçüme göre ayarlanması.
- Gerçek O1 ve RPLIDAR S2E yükleri ancak bu ölçümler geçtikten sonra bağlanır.

**Ölçüt:** ölçüm raporu; simülasyonla farklar açıklanmış, gereksinimler kart üzerinde doğrulanmış.

### 12. Nihai PCB tasarımı
- Prototip bulgularının işlendiği son yerleşim: sıcak çevrimin küçültülmesi, toprak ve güç düzlemleri, ısı dağıtımı, akım taşıma genişlikleri, kaçak/yalıtım mesafeleri.
- Mekanik sınırlar, konnektörler, montaj delikleri.
- Tasarım kural denetimi, üretim dosyaları (Gerber, delme, yerleşim, malzeme listesi).

**Ölçüt:** üretime gönderilebilir dosya seti ve son gözden geçirme onayı.
