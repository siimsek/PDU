# G1 ile PR #1 WP1/WP2 kanıtlarının karşılaştırması

## Kaynak ve yöntem

G1 dalı `main`/19 Ekim tabanı `a1dbeeb46e806ff65dbb4bea20fa9cabb5691bb2` üzerinde oluşturuldu; bu dalın mevcut G1 dosyaları korunmuştur. PR #1 dalı `wp/baseline-2026-10-24` için uzak HEAD `9d8f5e198d4c8523f22ecce95514767903cd200d` ile yerel ref eşleşti. Karşılaştırma Git nesnelerinden `git show` ile salt okunur yapıldı; dal değiştirilmedi, dosyalar kopyalanmadı ve sim/test çalıştırılmadı.

## Kanıt karşılaştırması

| Alan | PR #1 mevcut kanıtı | G1 kanıtı | G1 yorumu / kapanmayan durum |
|---|---|---|---|
| O1 OVP / buck kısa devre | WP1 rev3, ngspice-44.2: 154 deck; 2.534 kabul kontrolü PASS, **4 ESL deck tamamlanmadı**; runner ve doğrulayıcı exit 2. Tamamlanan vakalarda O1 küresel tepe 11,90318 V, normal bus tepe 11,09192 V. Baseline 16,89 V beklenen FAIL. | Windows ngspice-47 baseline 16,89 V; fark 0,0 V. G1 ideal bağımsız comparator/latch modeli 11,9741 V PASS (yalnız model). | 11,90318 ve 11,9741 V farklı topoloji/varsayımlardan gelir; doğrudan karşılaştırmalı silikon kanıtı değildir. WP1’in 4 yakınsamayan vakası başarısız/incomplete olarak kalır. Baseline 16,89 V FAIL iki kayıtta da korunur. |
| WP1 açılış ve eFuse mandalı | P0-03 açık: 4 ESL koşusu açılışta/tetik çevresinde `timestep too small` ile durdu. 10 Ω açılış direnciyle RAW yaklaşık 13,33 V çınlama ve yanlış OVP tetiklemesi görüldü; 330 Ω/1 kΩ bazı açılışları tamamladı fakat toparlanma VGS koşulu FAIL oldu. N-01: gerçek U3 açılmama davranışı bilinmiyor; güvenli üst sınır varsayımında buck kısa devrede VOUT 13,03882 V, ölçülen O1 11,59151 V. | G1 family 2 basitleştirilmiş behavioral buck kısa devre koşusu tamamlandı; O1 18,8039 V, ≤12,0 V **FAIL**. G1 family 5 eFuse kısa/hot-plug sonucu yalnız model. | G1 simülasyonları WP1’in ayrıntılı ESL/açılış/U3 belirsizliklerini kapatmıyor. U3’ün O1’i ayırdığı varsayımıyla kabul yok; hata enjeksiyonu ve O1 konektöründe ölçüm gerekli. |
| Normal regülasyon / yük adımı | WP1 normal rejim bus tepe 11,09192 V. Ancak post-fault bilgi penceresinde bus 11,29486–11,47708 V; B17 ölçümü açık. 7,5 A bus-min 10,649–10,7584 V WP3’e devredilmiş. | G1 FB statik köşesi 10,8333–11,1605 V HESAP; G1 family 4 düşük Ceff/kompanzasyon koşusunda bus min 10,7109 V → G1 kriteri **FAIL**. | WP1’in normal pencere PASS’i, post-fault ölçümünü veya WP3 yük/kararlılık açıklığını kapatmaz. G1 minimum geçici değer FAIL olarak korunur. |
| 20 V UVLO ve dip sonrası yeniden başlama | WP2 aday C3+U22/C3+O3 devreleri farklı mimaridir. Tarihsel Tur 5: 259 durum, 214 PASS / 16 FAIL / 6 abort. Tur 6 katı doğrulayıcısı aynı eski logları yeniden değerlendirince 161 PASS / **69 FAIL** / 6 eksik verdi; 53 ek M3 negatif EN gecikmesi FAIL-closed. 20×2 sayısal yakınsama tanısı: 100 ns’de **4/20**, 6 abort ve tolerans dışı farklar; 20 V açılış garantisi kanıtlanmadı. | G1 174 kΩ/10 kΩ pasif bölücü hesabı üst açma eşiği 19,689 V verir; EN sızıntısı/TCR dahil değil. G1 family 3 davranışsal modelde 20→26 V ve 20 V yeniden kalkışı tamamlandı. | 19,689 V yalnız G1 statik köşe taramasıdır; WP2’nin V_f, EN gecikmesi (≥60 ms), her EN yükselişi M1 ve dip/multiple-restart koşullarını doğrulamaz. G1 family 3 WP2 devresi veya bu kapıları modellemez; WP2 FAIL’leri kapanmış sayılmaz. |
| Mevcut test ve kanıt durumu | PR #1 HEAD 9d8f5e1 PKG-11: temiz snapshot ve yerel verifier/fixture testleri geçti; standart ngspice CLI yok. Yeni 259-deck kabul, 23 regresyon, OVP/UVLO elektriksel tekrar veya fiziksel tezgâh testi yapılmadı. CI kapalı, PR draft. | G1’e özel 5 simülasyon ailesi tamamlandı; 3 model kriteri PASS, family 2 ve family 4 FAIL. Bu sonuçlar fiziksel kabul değildir. | Test kodu/snapshot bütünlüğü PASS, elektriksel kabul PASS anlamına gelmez. CI, fiziksel test, WP1/WP2 kabul ve üretim onayı açık kalır. |

## Tasarım kararlarına etkisi

- G1 OVP kararı PR #1 WP1 hibritini tamamlanmış çözüm diye devralmaz. Bağımsız comparator/latch/seri kesme mimarisi tezgâhta daha kolay enjekte edilip ölçülebilir adaydır; G1 ideal modeli 11,9741 V gösterse de parça gecikmesi, kablo/PCB paraziti ve FET kapanma davranışı eksiktir. WP1’in 13,03882 V güvenli üst sınır senaryosu ayrıca sınanmalıdır.
- G1’in 174 kΩ/10 kΩ UVLO değişikliği yalnız statik yükselen eşik için en basit adaydır. WP2’nin 20 V başlatma garantisi, V_f≥18,0 V kapanma, VIN-OK sonrası ≥60 ms gecikme ve her EN yükselişi M1 kapısı ayrı gereksinimlerdir; mevcut G1 bölücü/model bunları kanıtlamaz. Batarya cutoff politikası ve sızıntı/TCR kapatılmadan 20 V garantisi iddia edilmeyecek.
- WP1’deki 4 solver incomplete, U3/N-01 üst-sınır FAIL’i, WP2’deki tarihsel 69 FAIL/6 eksik, 20×2 yakınsama eksikleri ve açık fiziksel doğrulamalar kapatılmadı. G1 sonuçları önceki sayıları değiştirmez veya yeniden sınıflandırmaz.

## Kaynaklar

PR #1 ref: `wp/baseline-2026-10-24` @ `9d8f5e198d4c8523f22ecce95514767903cd200d`.

- `docs/proposals/2026-10-25-o1-ovp/RESULTS.md`
- `docs/proposals/2026-10-25-uvlo/RESULTS.md`
- `docs/proposals/REVIEW-WORK-STATUS.md` (PKG-11/PKG-10)
- `docs/proposals/PLAN.md`
- G1: [`calc-results.md`](calc-results.md), [`SIMULATION-RESULTS.md`](SIMULATION-RESULTS.md), [`sim-results.json`](sim-results.json), [`BENCH-ACCEPTANCE.md`](BENCH-ACCEPTANCE.md)
