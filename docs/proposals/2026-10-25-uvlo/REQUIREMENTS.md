# WP2 2026-10-25-uvlo – Gereksinimler

Kapsam: 6S LiPo girişi (VIN 20–26 V) → LM70880 ×2 buck (RAW) → WP1 OVP (TPS48000 + TLV3601, değiştirilmeden) → VOUT 11 V bus → O1 ve S2E korumalı çıkışlar (U3/U4 eFuse). Motor kapsam dışı.
Sınıflar: **G** = veri sayfası garanti (MIN/MAX), **T** = tipik, **V** = varsayım, **Ç** = çıkarım. Simülasyon silikon kanıtı değildir. LTspice bulut ortamında çalıştırılmadı.

## Değişmeyen sert kriterler (gevşetilmedi)
| # | Kriter | Değer | Kontrol |
|---|---|---|---|
| H1 | O1 anlık tepe, tüm senaryolarda (0 … tran sonu) | ≤ 12,0 V | `verify_uvlo.py` `O1_PEAK_MAX` |
| H2 | Normal rejimde bus (VOUT) ve O1 maks | ≤ 11,1605 V | `BUS_NORMAL_MAX`; pencereler RUN/PRE/POST |
| H3 | 11,22 V | Yalnızca WP1 OVP yanlış-tetik uyaranı. Bu pakette eşik olarak kullanılmadı | — |
| H4 | WP1 OVP hibrit bloğu | Değiştirilmedi. Yalnızca VLDO=5 sabiti {V5_P} parametresine çevrildi (TPS7A1650 ±2 % köşesi) | `gen_uvlo.py derive()` assert |

## WP2 gereksinimleri
| # | Gereksinim | Sayısal ölçüt | Sınıf / gerekçe |
|---|---|---|---|
| R1 | 20,0 V'ta garantili ilk açılış ve yeniden açılış | Batarya EMF'i (açık devre) E = 20,0 V iken, tüm tolerans/sıcaklık/yaşlanma köşelerinde V_r,max ≤ 20,0 V − I_Q·R. Açılıştan sonra 7,5 A yükte çalışma sürer: VIN_op(20 V) − V_f,max ≥ 0,10 V | V: "20 V giriş" en katı biçimde EMF olarak okundu. Ölçüm VIN'de yapılsaydı kriter daha gevşek olurdu |
| R2 | Aşırı deşarjdan önce temiz kapanma | V_f,min ≥ **18,0 V** (3,00 V/hücre, yük altında VIN'de ölçülür) | V: 6S LiPo için yaygın yük-altı alt sınır 3,0 V/hücre. Yük altındaki 3,0 V, dinlenme sonrası yaklaşık 3,2–3,3 V'a toparlanır (Ç). Hücre üreticisi verisi yok. Kullanıcı farklı bir sınır isterse `REQ['V_FALL_MIN']` değiştirilir ve bütçe yeniden koşulur |
| R3 | Motorboating / chattering yok | Her köşede H − (P_IN/V_f)·R_total ≥ 0,10 V dinamik marj. Kapanıştan sonra EMF = V_f + I·R ve V_r'ye ulaşmamalı | Ç (fizik) + V (0,10 V marj) |
| R4 | Ortam | 7,5 A / 82,5 W, η ≥ 0,88 (V), housekeeping 0,30 W (V), R_total ≤ 0,25 Ω (V; döküm `uvlo_budget.py R_BREAKDOWN` = 0,237 Ω) | V |
| R5 | Sıralama: buck EN, WP1 OVP FET açıldıktan sonra gelmeli | Soğuk açılışta VIN OK → EN gecikmesi ≥ **60 ms** (TPS48000 TDRV_EN en kötü 50,8 ms, WP1 window-budget, + yaklaşık %18) ve ≤ 300 ms | Ç + V. P0-03 (açılış çınlaması / yanlış tetik) bağlamında FET açıkken buck soft-start'ı başlar. **Kısa dip sonrası** zamanlayıcı tam boşalmayabilir, bu yüzden 60 ms garanti edilmez (bkz. RESULTS.md). O durumda gerçek ölçüt "FET buck EN'den önce açık" olur ve doğrulayıcıda P0_03 INFO olarak raporlanır |
| R6 | EN seviye uyumu | EN yüksek ≥ 2 V ve EN düşük ≤ 0,4 V, tüm köşelerde (bütçe ayrıca EN yüksek ≥ VEN,max + 0,5 V = 1,55 V'u kontrol eder) | LM70880 SNVSBX7A s.13 §7.3.3 (açıklama metni, EC tablosu değil) |
| R7 | Brown-out, yavaş rampa (10 V/s, 1 V/s), hot-plug (≤ 26 V, 0,03 Ω), dip sonrası yeniden başlatma | Yukarıdaki sınırlar korunur. Dip sonrası POST rejimi düzenli (RAW 10,8–11,1605 V, FET açık, OVP INP yüksek). Tek bir yeniden başlatma olur, salınım olmaz | — |
| R8 | 26 V'ta komparatör giriş sınırı | S_UV,max ≤ V5,min = 4,90 V (girişler VCC üstüne çıkmaz; ek marj tanımlanmadı). TMUX1102 D ≤ VDD + 0,5 V (abs max) | G SBOS561C s.11, SCDS410D |
| R9 | Etkileşimler | U3/U4 eFuse UVLO, U10 TPS48000 EN/UVLO (VIN 100k/10k), U11 TPS7A1650 LDO ve U12 REF35 aynı VIN'den beslenir. UVLO bloğu V5_OVP ve VREF_OVP'yi paylaşır; REF yükü bütçede | — |
| R10 | Minimum müdahale | Ana şema/PCB/BOM/baseline netlist/sonuçlar değiştirilmez. Öneri yalnızca `proposals/` altında | Kullanıcı kuralı |

## Kabul (simülasyon tarafı)
- `uvlo_budget.py` exit 0 (tüm analitik marjlar ≥ 0; regresyonlar FAIL üretmeli).
- `run_uvlo.py` exit 0 (tüm deck'ler tamamlandı) ve `verify_uvlo.py` exit 0 (tüm kabul case'leri PASS, tüm regresyonlar FAIL olarak yeniden üretildi).
- Simülasyon PASS kanıt değil, yalnızca gerekli koşuldur. Tezgâh testleri: `BENCH-TEST.md`.

## WP3 devri: R-DIP (Tur 1 P1, açık)
Durum: **açık risk, kapatılmadı.** WP2, H2'yi (≤ 11,1605 V) yalnız normal rejim pencerelerinde (PRE/RUN/POST) uygular. Kısa VIN diplerinden (≈100–250 µs, 0 V) sonraki yeniden başlatma geçişinde bus geçici olarak 11,1605 V'u aşar: dip0v-200us-typ-ttyp BUS_GLOBAL_MAX 11,412 V, RAW 11,625 V; O1 10,978 V (H1 ≤ 12,0 V korunur; O1 WP1 OVP ile korunur). Değerler: RESULTS.md §5.

- Bu aşım **kabul edilmiş bir sınır değildir**. H2 gevşetilmedi. "Normal rejim dışı" sınıflandırması bir sistem gereksinimi kararıdır ve kullanıcı/sistem onayı gerektirir.
- Aşımın **süresi ölçülmedi** (deck'lerde 11,1605 V üstü süre .meas'i yok). WP3, geçiş için genlik **ve** süre sınırı tanımlamalı ve ölçmelidir.
- Önerilen WP3 kapsamı: (1) buck COMP kenetleme veya VIN-kaybı algısıyla anında EN kesme (CFU gecikmesinden bağımsız), (2) RAW'da akım çekici / aktif deşarj, (3) geçiş için ayrı sert kriter önerisi (genlik + süre), (4) tezgâh B-U15.
- WP3 tamamlanana kadar R-DIP, PR gövdesinde ve ChatGPT yanıtında açık P1 olarak taşınır.
