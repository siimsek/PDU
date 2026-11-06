# O1 OVP ve UVLO mimari kararı

## Karar

**Öneri (aday mimari):** O1 çıkışında, TPS259824O'dan sonra çalışan bağımsız hızlı comparator + referans + set-dominant latch + seri back-to-back MOSFET disconnect. OVP eşiği nominal 11.35 V, tüm toleranslarda en çok 11.46 V hedefi; toplam algılama/gate kapanma gecikmesi ≤0.5 µs hedefi; O1 kapasitans en az mevcut 10 µF kabulü. Bu eşik ve gecikme henüz **tasarım girdisi/varsayım** düzeyindedir; tam MPN seçilmedi, kanıtlanmış OVP değildir.

**Yedek:** PR #1 hibrit mimarisini ancak bağımsız çözüm comparator/latch/MOSFET sıcaklık, gecikme veya hata enjeksiyonu kabulünü geçemezse tekrar değerlendir. Çok bileşenli yedek doğrudan öneri değildir.

Kararı fiziksel hata enjeksiyonunun kolaylığı ve ana güç katından bağımsız izolasyon belirledi. Crowbar+F1 seçeneği, F1'in DC kesme/I²t/arıza akımı bilinmediği için yedek bile olamayacak kadar koordinasyonsuzdur. Mevcut 16.9 V eFuse OVP'si ana şartı sağlamaz.

## Adayların karşılaştırması

| Aday | En kötü O1 tepe ve sonuç | Ek parça / sadelik | Tezgâh testi | Model güven sınırı |
|---|---|---|---|---|
| PR #1 hibrit (TPS48000-Q1, 4×CSD18540Q5B, TLV3601, REF35409, TPS7A1650, pasifler) | PR#1 raporunda seçilmiş model köşesi 11.90318 V (12 V'a 96.8 mV marj). Dört ESL deck abort etti; latch bypass/bağımsız köşelerde 12.412–12.418 V FAIL. Fiziksel pass yok. | En az 5 IC + 4 güç MOSFET'i + bias ve çok sayıda pasif; yüksek karmaşıklık. | Hata enjeksiyonu mümkün; çoklu latch/enable dalları ayrı ayrı test edilmeli. | PR modeli tamamlanmamış; ESL abortları kanıt değildir, silikon/transient/SOA yok. |
| LTC4365 adayı (repo geçmişi) | Yerel native-LTspice yüksek eşik kaydı 11.8302 V; buck high-side short kaydı **12.3818 V FAIL**; `PROJECT-STATE.md` başka corner 12.4055 V raporlar. Başarısız köşe korunur. | Tek kontrolcü + harici MOSFET/pasifler; PR#1'den basit, ama ek analog kontrol. | Gate/OVP trip ve buck kısa devre testleri yapılabilir. | Yerel LTspice macro-model + yaklaşık MOSFET; ana devrede yok, kayıtlar farklı köşeler. |
| Bağımsız comparator + latch + seri disconnect (öneri) | İdeal gecikme/akım modeli bu raporun hedefli family-1 SİM'inde; bu bir komponent sonucu değildir. Hedef üst köşe 11.46 V, 10 A/10 µF/0.5 µs basit üst sınır ≈11.96 V (HESAP, parazitik/turnoff akımı hariç). | 1 comparator + 1 referans + latch (tek/iki kapı) + 2 FET + bölücü/pasif; makul ve test edilebilir. Exact MPN/stok yok. | O1 ucuna akım sınırlı 11.5–16.9 V pulse uygula; trip, latch, reset ve kalan tepeyi aynı anda ölç. | SPICE yalnız ideal eşik/gecikme/FET temsil eder; comparator offset/overdrive, gate charge, FET SOA ve kablo endüktansı dahil değil. |
| O1 crowbar + F1 | Tepe crowbar tepki anında ≤12 V olabilir, fakat hata akımı/fuse açma davranışı bilinmediği için sayısal maksimum hesaplanamadı: AÇIK. | Crowbar anahtarı + sürüş + koordineli DC fuse; mevcut F1 seçimsiz. | Test edilebilir, ancak tek kullanımlık fuse, ark/enerji ve tekrar kurulumu gerekir. | Fuse açma eğrisi, batarya/kablo empedansı ve crowbar SOA yok; geçme iddiası mümkün değil. |

### OVP eşik/gecikme hesabı

| Varsayım | Hesap | Sonuç |
|---|---|---:|
| Eşik üst corner | 11.35 V nominal × (1 + 1%) | 11.4635 V |
| Kapasitif yükselme, 5 A ve 10 µF | ΔV = I·t/C; t=0.5 µs | 0.25 V; O1≈11.7135 V |
| Kapasitif yükselme, 10 A ve 10 µF | ΔV = I·t/C; t=0.5 µs | 0.50 V; O1≈11.9635 V |
| Hedefe kalan pay | 12.0−11.9635 | 36.5 mV; ESL/turnoff ve ölçüm belirsizliği hariç |

Bu senaryoda mevcut CEFOUT=10 µF yalnız nominal değer; DC-bias/derating ve FET turnoff akımı doğrulanmadı. 10 A arıza akımının gerçek sınırı bilinmiyor. Dolayısıyla öneri hesapta çok az marjla koşullu olarak mümkün görünür, **tasarım kanıtı değildir**. Kart için en az 100 MHz osiloskopla gerçek pulse ve hata enjeksiyonu zorunludur.

## UVLO politikası ve basit bölücü

20 V yeniden kalkış, dondurulmuş 20–26 V giriş zarfının alt ucuna ulaşabilmek için gereklidir. 6S için 20/6=3.333 V/hücre. Ancak batarya koruması tek başına bu UVLO'ya bırakılmamalıdır; yaklaşık 16.5 V tipik falling (0.9× rising varsayımı) 2.75 V/hücre olur ve batarya üretici kesim politikası bilinmiyor.

- Mevcut 180k/10k, eşik0.95–1.05 V ve iki direnç ±1% köşesinde yükselen eşik 17.711–20.332 V verir; 20 V restart FAIL.
- **En basit değişiklik:** RUV1 180 kΩ → 174 kΩ (RUV2=10 kΩ kalır). Aynı varsayımlarla açma yaklaşık17.14–19.69 V; nominal yaklaşık18.4 V; üst corner 3.28 V/hücre. EN leakage ve TCR dahil değil.
- EN leakage değişimi yaklaşık `I_EN × Rtop`; 174k için her 1 µA, açma eşiğinde 0.174 V değişim yapar. Garantili EN leakage sınırı doğrulanmadı.
- RUV1 için exact MPN/tolerans/TCR ve RUV2 matching seçimi açık; tasarım değişikliği öneridir, uygulanmış değildir.

PR#1 WP2'deki comparator/mux/reference'lı çok-IC UVLO ancak batarya histerezisi/pack-state işlevi 174k/10k pasif bölücüyle sağlanamazsa gerekçelendirilebilir; bugünkü G1 statik eşik hesabı bu karmaşıklığı tek başına gerektirmiyor. Bununla birlikte WP2'nin M1 ≥60 ms gecikme, V_f ≥18 V ve dip sonrası yeniden başlama kapıları pasif bölücü/modelle kanıtlanmıyor; bunlar bu kararla kapanmış sayılmaz.

## Güncel PR #1 WP1/WP2 karşılaştırması

PR dalı `wp/baseline-2026-10-24` @ `9d8f5e1` salt-okunur incelendi. WP1 rev3'ün tamamlanan O1 tepe sonucu 11.90318 V olsa da dört ESL deck'i incomplete, doğrulayıcı exit 2 ve N-01 güvenli üst sınır varsayımı 13.03882 V olarak kalıyor. G1 ideal modelindeki 11.9741 V, farklı model/topoloji ve eksik parazitler sebebiyle bunu kapatmıyor. WP2'nin 161 PASS / 69 FAIL / 6 eksik sayımı eski Tur-5 loglarının Tur-6 doğrulayıcısıyla yeniden değerlendirmesidir; yeni elektriksel kabul koşusu değildir. Tam farklar ve kanıt referansları [`PREVIOUS-WP-COMPARISON.md`](PREVIOUS-WP-COMPARISON.md) içindedir.

## Kaynaklar

- Ana OVP/UVLO açık durumu: [`docs/design.md`](../../docs/design.md), [`docs/PROJECT-STATE.md`](../../docs/PROJECT-STATE.md), [`docs/REVIEW-CHECKLIST.md`](../../docs/REVIEW-CHECKLIST.md).
- PR#1 hibrit önerisi ve sonuçlar: [PR #1](https://github.com/siimsek/PDU/pull/1) (yalnız girdi; tamamlanmış/merge edilmiş tasarım kabulü değildir).
- Hesap ayrıntısı: [`calc-results.json`](calc-results.json), [`calc-results.md`](calc-results.md); ideal aday koşusu: [`sim-results.json`](sim-results.json).
