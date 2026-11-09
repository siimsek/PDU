# T-053 — F5 enable modelinin kontrollü yakınsama analizi

**Sonuç: AÇIK. `design/pdu_v2.cir` değiştirilmedi, 76 koşu yeniden yapılmadı.** Bu dosyadaki koşular deneydir ve resmi F5 sonucu değildir. Eski FAIL/AÇIK kayıtları olduğu gibi durur. Simülasyon fiziksel kanıt değildir.

## EN ile iç düğüm ayrımı

| Katman | Deck | Kaynak | Değer |
|---|---|---|---|
| Fiziksel EN/UVLO | `BVEN`, `BENS` içindeki `VEN_R`, `VEN_H` | DATASHEET TI SNVSBX7A s.6, s.13 §7.3.3 | VEN_R 0,95/1,00/1,05 V; VEN_H 0,1 V tipik, garantili aralık değil |
| İç durum `ens` | `BENS`, `CENS` | Model | VARSAYIM: 1 mA/1 nF, τ = 1 µs |
| İç çözümleme | `V(ens)>0.5` (`BSS`, `BEA`, `BSW1`, `BSW2`) | Model | VARSAYIM: TI belgesinde karşılığı yok |

Hiçbir varyant VEN_R veya VEN_H değerini değiştirmez. Varyantlar yalnız iç `V(ens)>0.5` çözümlemesinin önüne eklenir.

## Kilitlenme kanıtı

Köşe başına deck, SHA-256, komut, süre, simülatör, dalga ve çıkış `origin/wp/T-038` dalında `reports/g5/T-038/stall/` altındadır. İki köşede t_son 2.141142112e-04 ve 2.141142112e-04 s, çıkış timeout, kabul edilmiş son pencerede işaret değişimi yok. Reddedilen adımlar görünmediği için tek nedenli mekanizma **kanıtlanmadı**; `V(ens)>0.5` hipotezi desteklendi ama ispat edilmedi.

## İzole EN deneyi

[run_isolated.py](run_isolated.py), [isolated.json](isolated.json). Deck'in dört satırı değiştirilmeden kullanıldı; girişler idealdir.

VEN_R taraması, temel model (HESAP oran 18,4; direnç toleransı yok):

| VEN_R V | İdeal yükselen VIN | Ölçülen | İdeal düşen VIN | Ölçülen |
|---|---:|---:|---:|---:|
| 0,95 | 17,48 | 17,480 | 15,64 | 15,639 |
| 1 | 18,40 | 18,416 | 16,56 | 16,549 |
| 1,05 | 19,32 | 19,326 | 17,48 | 17,459 |

VEN_R 1,0 V, varyant etkisi:

| Varyant | Yükselen VIN | Düşen VIN |
|---|---:|---:|
| base | 18,416 | 16,549 |
| rc0.05us | 18,427 | 16,539 |
| rc0.2us | 18,428 | 16,537 |
| rc1us | 18,436 | 16,529 |
| rc2us | 18,445 | 16,520 |
| rc5us | 18,471 | 16,494 |
| schmitt0.45_0.55 | 18,442 | 16,523 |
| schmitt0.4_0.6 | 18,442 | 16,523 |
| schmitt0.3_0.7 | 18,442 | 16,523 |

26→10 V kısa düşüşte durumu kapatan en küçük genişlik:

| Varyant | µs |
|---|---:|
| base | 1,0 |
| rc0.05us | 2,0 |
| rc0.2us | 2,0 |
| rc1us | 5,0 |
| rc2us | 5,0 |
| rc5us | 5,0 |
| schmitt0.45_0.55 | 2,0 |
| schmitt0.4_0.6 | 2,0 |
| schmitt0.3_0.7 | 2,0 |

Yani varyantlar eşiği en çok onlarca mV kaydırır ama kısa düşüş bağışıklığını değiştirir. TI belgesinden EN deglitch süresi bu kartta alınmadı; karşılaştırma ölçütü **AÇIK**.

## Tam devre matrisi

[run_t053.py](run_t053.py), [variants.json](variants.json). 9 senaryo × 8 varyant, koşu başı 120 s limit. Netlist SHA-256 öneki `f6351423677407fb`. Senaryolar: 2 kilitlenen köşe, 3 F5 komşusu, f1_worst, hotplug, UVLO rampası, 22→15 V düşüş.

| Varyant | Köşe çıkışları | Tamamlanan | Kriter FAIL | En yüksek vraw_max_fault V | Komşu sapması en çok V |
|---|---|---:|---:|---:|---:|
| rc0p05us | -9/-9 | 6/9 | 0 | 34,763 | 0,000 |
| rc0p2us | 0/0 | 9/9 | 0 | 34,763 | 0,000 |
| rc1us | 0/0 | 9/9 | 1 | 63,517 | 42,462 |
| rc2us | 0/0 | 8/9 | 0 | 34,763 | 0,000 |
| rc5us | -9/-9 | 7/9 | 0 | 34,763 | 0,000 |
| sch0p45_0p55 | 0/0 | 9/9 | 0 | 31,662 | 3,101 |
| sch0p4_0p6 | 0/0 | 9/9 | 2 | 158,699 | 3,101 |
| sch0p3_0p7 | 0/0 | 9/9 | 0 | 31,662 | 4,954 |

Komşu sapması `vin_max` dışındaki kriter ölçümlerinin orijinalden en büyük mutlak farkıdır.

**OLGU:**
- Yakınsama τ ile tek yönlü değişmez: 0,05 µs zaman aşımı, 0,2 ve 1 µs biter, 5 µs zaman aşımı.
- Kriter FAIL: rc1us: vraw_max_fault @ f5_vt11.487_…p_r200m_l1.2; sch0p4_0p6: vraw_max_fault @ f5_vt11.487_…p_r200m_l0.8, vraw_max_fault @ f5_vt11.765_…p_r200m_l0.8.
- Tekrarlanabilirlik: [recheck.json](recheck.json). rc1us: 63,5174, 63,5174, 63,5174 V; sch0p3_0p7: 26,0088, 26,0088 V. Sapmalar deterministiktir.
- f2_dip çıkış 1: rc0p05us: çıkış 1, `doAnalyses: TRAN:  Timestep too small; time = 0.0162391, timestep = 2.24499e-18: trouble with node "pdiss"`; rc2us: çıkış 1, `doAnalyses: TRAN:  Timestep too small; time = 0.0162407, timestep = 1.68375e-18: trouble with node "pdiss"`.
- f1_worst, Schmitt 0,45/0,55 varyantında `vraw_max_fault` 31,6618 V (fark -3,1008 V). Mevcut geçen bir F1 ölçümü de iç çözümlemeye duyarlıdır.

Tüm dokuz senaryoyu kriter FAIL olmadan bitiren varyantlar: rc0p2us, sch0p45_0p55, sch0p3_0p7. Bunların komşu varyantları başarısızdır, yani geçiş dar bir sayısal aralıktadır.

## Kapı kararı

Ana deck değişikliği için üç koşul arandı: fiziksel veya sayısal gerekçe, varyant değerinden bağımsız sonuç, geçen senaryolarda değişmezlik. Hiçbiri sağlanmadı. Kart durdurma koşulu uygulandı: T-038 RC denemesi ve bu matris olmak üzere iki kontrollü denemede güvenilir karşılaştırma yok. İki F5 köşesi **AÇIK** kalır; 21,107 V gibi varyant sayıları F5 sonucu olarak kullanılmaz.

Yeni bulgu: vraw ve VDS tepe değerleri iç `ens` çözümlemesine duyarlıdır. Geçmiş F5/F1 değerlerinin bu duyarlılığı kapsamlı biçimde ölçülmedi, **AÇIK**.

## Tezgâh gereksinimi

Sayılar model veya hesaptır, tezgâh limiti değildir. Akım sınırı ve test sırası bu raporla belirlenmez.

| Büyüklük | Değer | Etiket |
|---|---|---|
| Fault sonrası faz 1 tepe akımı | 60,08 A (1 µs seyreltilmiş dalga) | SİM, kilitlenen koşu |
| VIN minimum | 12,09 V | SİM |
| VIN yeniden etkinleşme | yaklaşık 18,43 V | SİM, kilitlenme noktası |
| Yükselen/düşen UVLO (VEN_R tipik, VEN_H tipik) | 18,4 / 16,56 V | HESAP |
| L enerji üst sınırı, ½·5,44 µH·I² | 9,8 mJ | HESAP, doygunluk yok sayıldı |
| CIN enerji, ½·18,8 µF·26² | 6,4 mJ | HESAP, Ceff VARSAYIM |
| COUT enerji, ½·659,9 µF·11² | 39,9 mJ | HESAP, tipik Ceff |

UVLO civarında kısa devre maddesi `tasks/backlog.md` içinde (R-026) korunur. Ölçülecekler: VIN/EN, iki faz akımı, VOUT/VSAFE/O1, koruma süresi, yeniden başlatma, ısı. Akım sınırlı kaynakla, düşük akımdan başlanmalıdır. Model bu davranışı doğrulayamadı.

## THINKER'a açık soru

İki köşe için seçenekler: (a) yeniden etkinleşme anı için fiziksel gerekçeli alt model, (b) AÇIK tutup tezgâh testine bırakmak. Karar D-kartı ile verilmelidir; bu kart seçmez.
