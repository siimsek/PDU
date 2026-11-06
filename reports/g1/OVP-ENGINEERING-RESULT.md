# O1 OVP — gerçek komponent zinciri ve hedefli kanıt

## Karar

**Durum: BLOKE / tasarım kabulü yok.** Aşağıdaki MPN zinciri tezgâh prototipi için somut bir adaydır. Datasheet koşullarından türetilen gecikme toplamı, gerçek devre için garantili kapanma süresi değildir; FET güvenli çalışma alanı, kaynak arıza akımı ve fiziksel Ceff sınırı kapatılmamıştır. Davranışsal SPICE sonuçları donanım PASS'i sayılmaz.

Kanıt etiketleri: **DATASHEET**, üretici limiti; **HESAP**, tekrar üretilebilir hesap; **SİM**, ngspice modeli; **VARSAYIM**, model girdisi; **AÇIK**, sınırlandırılmamış veya ölçülmemiş.

## Aday gerçek komponent zinciri

| İşlev | Tam MPN adayı | Paket | Belirleyici sınır / durum |
|---|---|---|---|
| Hızlı karşılaştırıcı | `TLV3601DCKR` | SC70-5 / DCK | **DATASHEET:** −40…125 °C; ±5 mV max offset, 5 µA max giriş biası; 4.5 ns max gecikme yalnız 50 mV overdrive koşulunda. Daha küçük overdrive/slew için üst sınır doğrulanamadı. |
| Referans | `REF5025AQDRQ1` | SOIC-8 / D | **DATASHEET:** 2.5 V, ±0.1% başlangıç, 8 ppm/K max drift; yük ve hat regülasyonu hesap girdilerine eklendi. |
| Hata latch'i | `SN74LVC1G74DCUR` | VSSOP-8 / DCU | **DATASHEET:** asenkron CLR/PRE; CLR→Q max 6.1 ns, 5 V ve −40…125 °C. Açılışta güvenli temizleme, referans kararlılığı, ARM/CLR çakışması ve manuel reset devresi henüz şematik olarak çözülmedi. |
| High-side gate sürücüsü | `LTC7001EMSE#PBF` | 10-lead MSOP, exposed pad | **DATASHEET:** VCC 3.5…15 V; 70 ns max input-output gecikmesi 1 nF yük koşulunda; 12 V koşulunda max 4 Ω pull-down. İki FET'in gerçek gate yükünde bu gecikme/direnç birlikte garanti edilmemiştir. |
| Seri anahtar | `CSD19536KTTT` ×2, ortak kaynak back-to-back | TO-263 / D2PAK | **DATASHEET:** her biri 100 V; 2.8 mΩ max, VGS=6 V; Qg 153 nC max, VGS=10 V. SOA grafiğindeki en kısa eğri 100 µs; 0.325 µs tahmini kapama noktasında SOA **doğrulanamadı**. |
| Sürücü 12 V besleme | `TPS7A1601QDGNRQ1` | HVSSOP-8 / DGN | **DATASHEET:** ayarlanabilir yüksek girişli LDO adayı; çıkış ayarı, startup ve reset sıralaması tasarlanmadı. |
| Karşılaştırıcı/latch 5 V | `TPS7A1650QDGNRQ1` | HVSSOP-8 / DGN | **DATASHEET:** sabit 5 V yüksek girişli LDO adayı; startup/reset sıralaması tasarlanmadı. |
| Eşik bölücüsü | 3.59 kΩ / 1.00 kΩ, 0.1%, ≤25 ppm/K sınıfı | paket/MPN seçilmedi | **VARSAYIM:** sınıf varsayımıdır; tam direnç MPN'si ve footprint onayı yoktur. Nominal eşik 11.475 V. |

Üretici veri sayfası bağlantıları ve sayfa referansları: [TLV3601](https://www.ti.com/lit/ds/symlink/tlv3601.pdf), [REF5025A-Q1](https://www.ti.com/lit/ds/symlink/ref5025a-q1.pdf), [SN74LVC1G74](https://www.ti.com/lit/ds/symlink/sn74lvc1g74.pdf), [LTC7001](https://www.analog.com/media/en/technical-documentation/data-sheets/ltc7001.pdf), [CSD19536KTT](https://www.ti.com/lit/ds/symlink/csd19536ktt.pdf), [TPS7A16-Q1](https://www.ti.com/lit/ds/symlink/tps7a16-q1.pdf), [TPS25982](https://www.ti.com/lit/ds/symlink/tps25982.pdf). Ayrıntılı limit/sayfa eşlemesi [OVP-COMPONENT-REVIEW.md](OVP-COMPONENT-REVIEW.md) içindedir. Bazı TI ürün sayfaları kontrol sırasında stok dışıydı; diğer MPN'ler için satın alınabilir stok doğrulanmadı. Stok durumu tasarım onayı değildir.

## Eşik, hata akımı ve gerekli Ceff

| Büyüklük | Sonuç | Yorum |
|---|---:|---|
| Nominal OVP eşiği | 11.475 V | HESAP: 2.5 V × (1 + 3.59k/1k) |
| Enumerated min…max | 11.3281…11.6232 V | HESAP: ref başlangıç/drift/yük/hat regülasyonu, direnç toleransı/TCR, karşılaştırıcı offset/histerezis/bias köşeleri |
| Bağımsız interval min…max | 11.3281…11.6233 V | HESAP: konservatif aralık yayılımı; enumerasyon farkı en çok 0.099 mV |
| Önceki provisional 11.46 V üst trip hedefi | Aday max 11.6232 V, hedefi 163.2 mV aşıyor | HESAP: 3.59 kΩ bölücü bu önceki tasarım hedefine uymaz; O1 hard limit 12.0 V aynıdır |
| Trip min ≥ 11.1605 V ve trip max ≤ 11.46 V için teorik Rtop aralığı | 3.52195…3.52569 kΩ; pencere 3.74 Ω | HESAP: Rbottom=1.00 kΩ, diğer aynı toleranslar; ripple/noise payı yok |
| Pencere ortası örneği | Rtop=3.52382 kΩ → 11.1651…11.4553 V | HESAP: yalnızca yaklaşık 4.6 mV iki yönlü marj; direnç MPN seçilmedi ve gerçek gürültü doğrulanmadı |
| Min trip'in kararlı bara üst sınırına payı | 167.6 mV | HESAP: 11.3281 − 11.1605 V; O1 gürültü/ripple dahil değil |
| Max trip'in 12.0 V'a payı | 376.8 mV | HESAP: parazit/ölçüm payı dahil değil |
| TPS259824O ILIM ekranı | 5.697 A | HESAP/VARSAYIM: 300 Ω high-temp datasheet max değeri 301 Ω, %1 düşük direnç köşesine ölçeklendi |
| 2.1× ILIM hızlı-trip ekranı | 11.965 A | DATASHEET eşik oranı + HESAP; **garantili akım tavanı değildir** |
| Ceff min, 11.965 A ve 325.4 ns için | 10.332 µF | HESAP: `C ≥ I·t/(12−Vtrip,max)`; kapalı form ve sayısal bisection çapraz kontrolü eşleşti |
| Aynı akım ekranı, 557.183 ns ideal switch akım kapanması için | 17.691 µF | HESAP duyarlılığı; fiziksel komponent gecikmesi değildir |
| 10 A ve 0.5 µs için, seçili max eşikte | 13.269 µF | HESAP senaryosu; 10 A bir garanti değil |
| 10 A ve 0.55 µs için, seçili max eşikte | 14.595 µF | HESAP senaryosu; Ceff artışı ESR/ESL/tail hariç |

TPS259824O'nun 2.1×ILIM hızlı-trip değeri sert akım kelepçesi değildir. 400 ns kısa-devre yanıtı bu hesapta garantili maksimum olarak kullanılmadı. Dolayısıyla kaynak/kablo/indüktans/eFuse davranışı için hata akımı ve süre zarfı yokken **fiziksel worst-case Ceff sonlu bir sayıyla kapatılamaz**. Ceff denklemine ESR, ESL, kapama kuyruğu, ölçüm belirsizliği ve doğrudan O1 geri beslemesi de dahil değil. Ceff fiziksel PASS değeri: **doğrulanamadı**.

## Kapanma zamanı: model ölçümü ile komponent tahmini ayrı

### İdeal Family 1 switch ölçümü

Family 1 behavioral deck'inde `CTRL` 1 V'tan düşer ve ideal switch açma sınırı `Vt−Vh=0.45 V` olur. 1 nF latch ve 1 mA sink ile analitik gecikme `(1.00−0.45) V / 1 mA × 1 nF = 550 ns` çıkar. ngspice ölçümü, trip eşiğinden seri akımın 1 mA altına inmesine **557.183 ns** verdi (**SİM**); fark +7.183 ns / +1.306%. Akım 4.48628 A'dan 4.93 pA'a düştü. Bu, ideal B kaynağı ve ideal SW içindir; fiziksel anahtarın ölçümü değildir. Deck/log: [ölçüm deck'i](sim/family1-switch-off-measurement.cir), [log](sim/family1-switch-off-measurement.log).

### Gerçek MPN'lerden türetilen tahmin

| Katkı | Ekran |
|---|---:|
| TLV3601 | 4.5 ns (yalnız 50 mV overdrive koşulu) |
| SN74LVC1G74 CLR→Q | 6.1 ns |
| LTC7001 giriş-output | 70 ns (1 nF yük koşulu) |
| İki FET için kapı yükü | 306 nC / (5 V / 4 Ω) = 244.8 ns |
| Toplam | **325.4 ns, garanti değil** |

5 V Miller platosu varsayımı, Qg'nin datasheet test koşulu ve LTC7001'in 1 nF gecikme koşulu gerçek iki-FET gate dalga şekli değildir. Comparator gecikmesi belirtilen overdrive dışında, gerçek Qgd, sürücü çıkışının sıcaklık/gerilim altında gate yükündeki akımı ve açılış/reset etkisi garanti sınırına bağlanmadı. Sonuç: gerçek komponent zincirinin kapanma süresi **doğrulanamadı**.

## Birleşik buck high-side-short + bağımsız OVP koşuları

Koşular aynı Family 2 davranışsal buck-short netlistine O1 dalında eşik/gecikme kontrollü seri anahtar ekler. FET'ler ideal switch'tir; yalnız RON datasheet ekranından alınmıştır. eFuse ideal 16.32 V OVP anahtarıdır; gerçek ILIM/fast-trip dinamiği ve parasitikler yoktur. 10 µF yükte 7 A (1.57 Ω), diğer koşuda 4 µF yüksüz senaryo kullanıldı.

| Koşu | Completed / exit | O1 tepe | S2E tepe | Bara tepe / model faz akımı | OVP kol akım tepe / kapanma ölçümü | Sonuç |
|---|---|---:|---:|---:|---|---|
| 10 µF, 7 A | Evet / 0 | 11.6900 V | 19.0809 V | 40.709 V / 67.7984 A | 9.6575 A / seri akım 1 mA altı 326.123 ns | SİM koşusunda O1≤12 V; tasarım kabulü BLOKE. 10 µF, 10.332 µF ideal Ceff ekranının altında. |
| 4 µF, yüksüz | Evet / 0 | 11.6857 V | 18.8274 V | 39.841 V / 63.7992 A | 0.7984 A / 1 mA akım eşiği trip öncesinde görüldüğü için ölçüm geçersiz; kontrol eşiği 325.262 ns | SİM koşusunda O1≤12 V; tasarım kabulü BLOKE. Bu koşu akım tabanlı kapanma süresini ölçmüyor. |

İki davranışsal koşu O1 ekran kriterini sağlasa da bu sonuçlar worst-case değildir: O1 eFuse akım sınırlaması yok, akım şekli/tepe akımı güvenilir şekilde sınırlanmamış, kapasitörler ideal, gate/FET ideal ve SOA yoktur. 10 µF koşusunda akım tepesinin 11.965 A hızlı-trip **eşik ekranından** 2.307 A düşük görünmesi garanti marjı sayılmaz. S2E yaklaşık 19 V görür; O1 dalındaki anahtar ortak bara arızasında S2E'yi ayırmaz ve S2E'nin sayısal izin verilen giriş/abs max sınırı belgelenmedi. S2E kabulü **AÇIK**.

Kanıtlar: [ölçüm JSON'u](ovp-component-sim.json), [validation record](OVP-VALIDATION-LOG.md), [10 µF/7 A deck/log](sim/family2-buck-short-independent-ovp-final-10uF-7A.cir), [4 µF/yüksüz deck/log](sim/family2-buck-short-independent-ovp-final-4uF-no-load.cir). Eski, ilk deneme ve kalibrasyon logları korunmuştur.

## FET ve önceden açık kalan FAIL'ler

İki CSD19536KTTT için datasheet test noktasında çift RDS(on) 5.6 mΩ; 7.5 A'da iletim kaybı 0.315 W. Bu oda sıcaklığı/test gerilimi hesabıdır; sıcak RDS(on), transient güç ve kart termali doğrulanmadı. Datasheet SOA en kısa 100 µs eğriden başlıyor; 0.325 µs tahmin ve gerçek arıza VDS/akım paylaşımı için **SOA doğrulanamadı**.

| Tarihsel sonuç | Korunan değer | Bu ek koşuların etkisi |
|---|---:|---|
| Bağımsız OVP'siz Family 2 buck-short | O1 18.8039 V — **FAIL** | Değişmedi; aday OVP'li iki yeni koşudan ayrı tutulur. |
| Family 4 düşük Ceff / düşük RCOMP yük adımı | BUS 10.7109 V — **FAIL** | Değişmedi. |
| WP1 | 4 ESL koşusu incomplete; N-01 açık | Değişmedi. |
| WP2 | 69 FAIL / 6 incomplete | Değişmedi. |

## Fiziksel mühendislik kapanış girdileri

1. O1/S2E konektörlerinde, kaynağın/kablonun empedansını ve O1 eFuse gerçek davranışını içeren fault-current waveform; downstream port geri-besleme senaryosu ayrı test edilmeli.
2. COUT parça MPN'siyle DC-bias, tolerans, yaşlanma ve sıcaklıkta minimum Ceff; ESR/ESL ve fixture/probe belirsizliği.
3. Comparator'ın seçilen overdrive/slew köşesinde propagation max'i veya ölçülmüş sınır; latch açılış/reset/ARM devresi; gerçek iki-FET gate dalga şekli ve toplam off zamanı.
4. FET açma sırasında VDS/I paylaşımı, clamp/snubber/harness indüktansı ve üretici SOA doğrulaması; 100 µs altındaki SOA'yı eğriden ekstrapole etmeyin.
5. S2E cihazının izin verilen giriş aralığı ve OVP/bus clamp politikası.
6. Üretici datasheet limitlerine göre tezgâh hata enjeksiyonu ve fiziksel ölçüm. Şu ana kadar fiziksel ölçüm **yapılmadı**.

## 2026-11-06 addendum — PR #2 comment 6683120653

The older sentence above that S2E's numeric input range was unverified is historical. The manufacturer's RPLIDAR S2E v1.5 table now verifies a **9–28 V powered input range**, **0.22 A maximum working current**, and **1.5 A maximum start current at 12 V** (p.12). The prior model result S2E=19.0809 V is inside that published powered range; the table does not specify transient absolute maximum or startup duration. The corrected S2E current screens and shared U3/U4 input fault results are in [PR2-REVIEW-6683120653.md](PR2-REVIEW-6683120653.md). Physical acceptance remains open.
