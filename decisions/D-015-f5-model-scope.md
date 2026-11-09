# D-015 — F5 yeniden etkinleşme ve geçmiş tepe değerlerinin kapsamı

- **Kart:** tasks/D-015.md
- **Yazan:** Codex, 2026-11-09
- **Fiziksel iş gerekli mi:** Evet; güvenli, akım sınırlı UVLO/kısa devre tezgâh doğrulaması. Önce test planı ve korumalar hazırlanır.

## Soru

İki tamamlanmamış F5 köşesi ve iç model duyarlılığı bulunan eski F1/F5 tepe değerleri nasıl ele alınmalı?

## Seçenekler

| Seçenek | Kanıt ve risk | Karar |
|---|---|---|
| A: fiziksel gerekçeli yeniden etkinleşme alt modeli | TI LM70880-Q1 SNVSBX7A s.6 ve s.13 EN yükselişi ve tipik histerezisi verir; model iç düğümünün gecikme/deglitch davranışını ve garanti toleranslarını bu kaynak belirlemez. T-053 sonuçları varyant seçimine duyarlı. | Araştırmaya devam; mevcut verilerle resmi deck'e alınamaz. |
| B: iki F5 köşesini AÇIK tut, güvenli sınırlı tezgâh ile doğrula | Koruma davranışı ve gerçek tepe deneysel olarak ayrıca sınanır. Tezgâh yokken eksiklik kapanmaz. | **SEÇİLDİ.** |

## Öneri

Mevcut deck'i ve eski FAIL/AÇIK kayıtlarını koru. İki köşeyi AÇIK tut; fiziksel alt model ancak üretici kaynaklarıyla veya ölçümle temellendirildikten, hassasiyet ve bağımsız regresyon kapılarını geçtikten sonra aday olur. Aykırı tepe sayıları fiziksel gerilim olarak sunulmaz. Tezgâh için kaynak akım sınırı, enerji ve hata güvenliği önceden hesaplanmadan deney yapılmaz.

## Kapsam kararı

- F1 ve F5 ailelerinin **tüm** senaryolarındaki VRAW, VDS ve bunlara bağlı gerilim, akım, enerji ve koruma sonuçları model duyarlılığı bakımından yeniden sınıflandırılır. Eski sayısal kayıtlar silinmez; eski simülasyon koşusu altında geçerli tarihsel çıktıdır, bu duyarlılık giderilene kadar güvenilir nihai worst-case veya fiziksel uygunluk kanıtı değildir.
- Diğer ailelerde aynı iç modelin ilgili metrikleri etkileyip etkilemediği bağımlılık taramasıyla belirlenir; kanıtsız tüm sonuçları FAIL ilan etme. Kanıtlanan FAIL'ler korunur.
- Eksik iki F5 köşesi AÇIK; hiçbir varyantın başarı sonucu bu iki köşenin resmi PASS'i değildir. Başka modellere, tam toleranslara ve tezgâha yayılım ayrıca doğrulanır.

## Kanıt

- **KOD:** main design/pdu_v2.cir:31–35,42,52,65 ve analysis/g2/sim_runner.py:59: gerçek EN histerezisi ile iç ens eşiği ayrı.
- **SİM, BUILDER:** cbd0c5b:reports/g5/T-053/run_t053.py 8 varyant ve 9 senaryo tanımlar; reports/g5/T-053/report.md değişmiş sonuç ve sınırları açıklar. 63,5174 V ve 158,699 V ilgili varyantların sayısal çıktılarıdır, yeniden bağımsız koşturulmadı.
- **KOMUT:** cbd0c5b:reports/g5/T-053/run/f5_vt11.487_td300ns_ctyp_r200m_l0.8__sch0p4_0p6.log VRAW 158,699 V ve VDS 147,918 V kaydeder; gözlenen sayısal duyarlılık fiziksel olay ispatı değildir.
- **DATASHEET:** [TI LM70880-Q1 SNVSBX7A](https://www.ti.com/lit/ds/symlink/lm70880-q1.pdf), s.6 ve s.13 §7.3.3; 0,1 V EN histerezisi tipiktir.
- **KOMUT:** analysis.g2.sim_runner.family_cases() main c69c77c: F1 7, F5 49, tüm aileler 76. Bu yalnız senaryo sayımıdır.

## Açık varsayımlar

- Model varyantlarının hangisinin fiziksel davranışı temsil ettiği AÇIK; yakınsayanı seçmek yeterli değildir.
- Tezgâh koşulları, donanım koruması ve cihaz limitleri ayrıca tasarlanır; kısa devre enerjisi güvenli sanılmaz.

## Doğrulanamayanlar

- Gerçek EN deglitch ve iç yeniden etkinleşme dinamiği; fiziksel F1/F5 tepe değerleri; üretici histerezis uç sınırları; tezgâh sonuçları. Kullanıcıdan teknik karar veya dış iletişim istenmez.
