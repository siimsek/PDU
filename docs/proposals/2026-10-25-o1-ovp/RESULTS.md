# WP1 rev3 – Simülasyon sonuçları (2026-10-25-o1-ovp)

**Ortam:** Bulut kutusu, Debian 13, Python 3.13.5, **ngspice-44.2** (apt `44.2+ds-1`, KLU ile derlenmiş; ikili sha256 `5854f6506e3e54e0553b687401a5d82aec82229c2c28a93b7eb37b6e079dda84`), `-D ngbehavior=ltpsa`. **LTspice bulut ortamında çalıştırılmadı** (PDU_LTSPICE yok → SKIPPED; LTspice sonucu iddia edilmez). Modeller davranışsal/ideal – bkz. `MODELS.md`. **Sim ≠ silikon/tezgâh kanıtı.**

**rev3 değişiklikleri:** ChatGPT Tur 2 (inceleme 6390966776) bulgularına yanıt – P0-01 RSNS10 üst kolu 2 × 1206 (1,0 k + 1,05 k) + RSNS11 1206; P0-02 her kabul deck'inde `O1_GLOBAL_PEAK` (0…tran sonu) ve toparlanma normal-bus pencereleri; **ayrı davranışsal model revizyonu rev3** (TPS48000 OV pin düğümü `ov`→`ovs`, rev1/rev2'de `.subckt` içindeki `ov` düğümü OV parametresiyle çakışıp OV yedeğini ölü bırakıyordu; rev2 kütüphanesi `model-compare/` altında korunur ve eski/yeni regresyonu tüm case'lerde koşulur); pre-fault/toparlanma rejim kontrolü (INP > 2,5 V, VGS > 6 V) runner ve doğrulayıcıda **kabul** kontrolü.

**Koşu (temiz, tek):** etiket `wp1-rev3`, git `c285d52` (package_inputs_dirty=False), 2026-10-25 08:16:23 → 08:23:12 TSİ, **154 ngspice deck**. Şeffaflık: aynı girdilerle bir önceki koşu (08:0x TSİ, `a4025eb` üzerinde) `model_compare.py` girdi hash'i değiştiği için geçersiz sayıldı; `c285d52` commit'lenip zincir baştan koşuldu. İki koşunun tüm ölçüm değerleri birebir aynıdır; yalnız ikinci (temiz) koşu commit'lendi (`4bde43a`). Zaman damgası-yalnız fark veren 2 log HEAD sürümüne geri alındı, json'daki log_sha256 buna göre düzeltildi (değerler aynı).

```
cd simulation/proposals/2026-10-25-o1-ovp
python3 gen_o1ovp.py                                               # exit 0 (154 case, deterministik)
PDU_NGSPICE=/usr/bin/ngspice python3 run_o1ovp.py --label wp1-rev3 --jobs 8   # exit 2 (4 eksik deck)
python3 verify_candidate.py                                        # exit 2 (1766 kontrol, 0 FAIL, 4 MISSING)
python3 verify_candidate.py --baseline-regression                  # exit 1 (beklenen: O1_PEAK 16,89 V)
python3 rsns_power.py --check                                      # exit 0 (seçilen 2×1206: %79,4 @125 °C)
PDU_NGSPICE=/usr/bin/ngspice python3 regime-selftest/regime_selftest.py   # exit 0 (negatif öz-test geçti)
```
Çıkış kodları (P2-02): runner **0** PASS / **1** kabul FAIL / **2** eksik-yakınsamayan deck (öncelikli); doğrulayıcı **0** PASS / **1** FAIL / **2** eksik kanıt (öncelikli); `--baseline-regression` 0/1, log yoksa 2.

## Özet
| | rev2-2 (`wp1-rev2-2`) | **rev3 (`wp1-rev3`, son)** |
|---|---|---|
| Deck (ngspice) | 154 | **154** |
| Kabul kontrolü PASS (runner) | 1799 | **2534** (P0-02 global tepe + rejim + toparlanma kontrolleri eklendi) |
| Kabul kontrolü FAIL (runner) | 2 | **4** (4 yürütme FAIL = 4 ESL deck; değer FAIL'i yok) |
| Eksik/yakınsamayan | 3 (2 kabul + 1 bilgi) | **4** (4 kabul ESL deck; `rev1-c92-wchi` bilgi deck'i artık tamamlanıyor) |
| Bağımsız doğrulayıcı | 1182 / 0 FAIL / 2 kanıt sorunu | **1766 / 0 FAIL / 4 kanıt sorunu** |
| Runner / doğrulayıcı exit | 2 / 2 | **2 / 2** |

### AÇIK – P0-03: 4 ESL deck yakınsamadı (gizlenmedi, silinmedi, bilgiye çevrilmedi)
| Deck | Durma anı | ngspice mesajı |
|---|---|---|
| buck-short-c185-esr12m5-esl2n-typ | 12,2645 ms | Timestep too small, `imon_s2e` |
| buck-short-c165-esr12m5-esl2n-typ | 12,2646 ms | Timestep too small, `imon_s2e` |
| buck-short-c185-esr12m5-esl2n-wchi | 12,2699 ms | Timestep too small, `imon_s2e` |
| buck-short-c165-esr12m5-esl2n-wchi | 12,2699 ms | Timestep too small, `imon_s2e` |

rev2'de yalnız 2 typ deck duruyordu, wchi ESL deck'leri geçiyordu; **rev3 modelinde wchi ESL deck'leri de duruyor (yeni FAIL)**. Kısa devre 30 ms'de; durma **açılışta, FET açılma anında**. KLU zaten etkin (ikili KLU ile derlenmiş; `solver-study/` KLU/SPARSE ve `.options` varyantlarını ayrıca dener).

**Bulgu – açılışta komparatör yanlış tetiklemesi (startup false trip):** `slew-study/` içindeki açılış sondası (durma anından hemen önce biten ve aynı devreyi kullanan deck kopyaları; tasarım değişikliği yok) şunu gösterdi:
| Sonda | INP min | INP düşüş | RAW maks | VGS maks | FET açılma |
|---|---|---|---|---|---|
| c185-ESL-typ (stop 12,2644 ms) | 0 V | 12,264226 ms | 13,332 V | – | 12,2644 ms |
| c165-ESL-typ (stop 12,2644 ms) | 0 V | 12,2643 ms | 13,337 V | – | – |
| c185-ESL-wchi (stop 12,2695 ms) | ≈5e-9 V | 12,2642 ms | 13,334 V | 8,61 V | 12,2644 ms |

Sert FET açılışı RAW bankı + 2 nH ESL ile ≈7,8 MHz'de çınlıyor; RAW ≈13,33 V'a çıkınca komparatör (doğru şekilde) INP'yi düşürüyor, FET açılırken kapatılıyor ve davranışsal modelde sayısal durma oluşuyor. Bu, gerçek devrede **açılışta istenmeyen OVP tetiklemesi / hıçkırık** riski demektir → tezgâh B18 ve WP2 kontrollü açılış (slew) seçeneği. ESL'siz tamamlanan tüm deck'lerde doğrulayıcı "start-up OVP trip" bilgi bulgusu **0**. Sonuç: **P0-03 açık bloklayıcı**.

## B. O1 anlık tepe – test grubu başına (kabul, sınır 12,0 V; rev3: O1_GLOBAL_PEAK 0…tran sonu)
| Grup | En yüksek O1 | Case | 12 V marjı |
|---|---|---|---|
| Kısa devre, kabul köşeleri (18 tamam, 4 ESL yakınsamadı) | **11,90318 V** | buck-short-c165-esr12m5-wchi | **96,8 mV** |
| eFuse-OVP rampa 0,07/0,17/0,23 V/µs | 11,84006 V | efuse-ovp-s017-wchi | 160,0 mV |
| Overdrive tarama (kabul) | 11,78864 V | sweep-od100 | 211,4 mV |
| tDOFF tarama (kabul) | 11,64916 V | – | 350,8 mV |
| MC rampa (40, seed 20261025) | 11,57673 V | – | 423,3 mV |
| MC kısa devre (20, c185) | 11,7582 V | – | 241,8 mV |
| Startup | 10,98361 V | – | – |
| Yük basamağı | 10,99818 V | – | – |

### Kısa devre ayrıntı (O1 global tepe, V)
| RAW C / ESR / ESL | wchi | typ |
|---|---|---|
| 185,3 µF / 1 mΩ | 11,88123 | 11,47384 |
| 185,3 µF / 12,5 mΩ | 11,89186 | 11,47923 |
| 185,3 µF / 12,5 mΩ / 2 nH | **yakınsamadı** | **yakınsamadı** |
| 176 µF / 1 mΩ | 11,88725 | 11,46968 |
| 176 µF / 12,5 mΩ | 11,89592 | 11,48176 |
| 165 µF / 1 mΩ | 11,89238 | 11,47344 |
| **165 µF / 12,5 mΩ** | **11,90318** | 11,48183 |
| 165 µF / 12,5 mΩ / 2 nH | **yakınsamadı** | **yakınsamadı** |
| 483 µF / 1 mΩ | 11,79014 | 11,44449 |
| 483 µF / 12,5 mΩ | 11,81012 | 11,4568 |
| 185 µF / 100 mΩ (−40 °C stres) | 11,59151 | 11,59208 |
| 130 µF / 12,5 mΩ (bilgi) | 11,93037 | 11,49206 |
| 120 µF / 12,5 mΩ (bilgi) | 11,95673 | 11,49063 |
| rev1 92,65 µF / 1 mΩ (bilgi, artık tamamlanıyor) | 11,99422 | – |
| rev1 92,65 µF / 12,5 mΩ (bilgi) | **12,03166 (bilgi-FAIL, rev1 P0 yeniden üretimi)** | – |

VDS maks (kabul) 26,705 V (c165-typ); bilgi deck'inde 27,37 V (rev1-c92-typ). VDS < 60 V tek başına SOA kanıtı değildir → `soa-study/` (P1-01).

## C. Normal bus maks. (sınır 11,1605 V, R2b) – kabul
| Ölçüm | En kötü | Case/pencere |
|---|---|---|
| bus_normal_max (kısa devre öncesi 24–29 ms) | 11,03144 V | buck-short / mc-short |
| bus_recov_max (toparlanma sonrası, P0-02) | **11,09192 V** | buck-short-c483-wchi |
| o1_recov_max | 11,03647 V | – |
| bus_max (startup/statik) | 11,02878 V | startup-20v-chi |
| bus_pre_max (rampa 0–14,9 ms) | 10,99984 V | – |
| **Genel** | **11,09192 V** → marj **68,6 mV** | |

Pre-fault rejim (104 deck): INP min 4,9995 V, VGS min 11,5998 V → hepsi geçerli normal rejim (FET açık). Rejim kontrolünün çalıştığı negatif öz-testle kanıtlandı (§G).

## D. Yanlış tetik (11,22 V test uyaranı; normal-bus sınırı değil)
`no-false-trip`, `no-false-trip-ron5m28`, `mc-nofalse-00…19` (22 deck): RAW maks 11,22 V'a ulaşıldı (22/22), INP min 4,9995 V, VGS min 11,6 V → **22/22 tetik yok**. mc-nofalse O1 ortalama en yüksek 11,19781 V (10,78–11,22 seviye penceresinde). Not: bu, açılış yanlış tetiklemesinden (§A, P0-03) ayrıdır.

## E. Bilgi / izleme (kabul kriteri değil; gevşetme yok, gizleme yok)
- **INFO postfault bus/O1** (24 deck, kısa devre sonrası yeniden açılış 45–80 ms): bus 11,29486–11,47708 V. Bu pencere RAW kaynağı yeniden 26 V→normal'e dönerken ideal kaynakla ölçülür; normal rejim değildir ama gerçek tezgâhta **B17** ile ölçülmelidir (11,1605 V üzerinde!).
- **INFO bench start-up bus** (0–24 ms, ideal LC tezgâh açılışı; 46 deck): 11,150–11,167 V; birçoğu 11,1605 V'u aşar → INFO-FAIL olarak raporlanır. Normal işletme penceresi değildir, ancak tezgâh açılışında **B18** ile ölçülmeli ve WP2/WP3'te değerlendirilmelidir.
- **TRACKING 7,5 A** (5 deck): bus min 10,649–10,7584 V (10,78–11,22 penceresi dışında) → WP3.
- `buck-short-rev1-c92-esr12m5-wchi` 12,03166 V (yalnız karşılaştırma).

## F. Baseline regresyonu
`simulation/pdu-efuse-ovp.ng.cir` (sha256 `7529ff25…ca7d`, koşu öncesi = sonrası) → **O1_PEAK = 16,89 V → FAIL (beklenen)**, exit 1. Baseline dosyaları değişmedi.

## G. Rejim negatif öz-testi (P0-03 isteği: FET hiç açılmazsa FAIL)
`regime-selftest/regime_selftest.py` – geçici blok kopyasında iki bozma (tasarım düzeltmesi değil):
| Deck | Bozma | O1 global | INP_PRE_MIN | VGS_PRE_MIN | runner rejim | doğrulayıcı rejim |
|---|---|---|---|---|---|---|
| buck-short-c185-esr12m5-wchi | INM→V5 10 Ω (INP düşük) | 7,3 mV | 5e-9 V | ≈0 V | FAIL | FAIL |
| buck-short-c185-esr12m5-wchi | PU 1 µF | 7,8 mV | 5,0 V | ≈0 V | FAIL | FAIL |
| efuse-ovp-s023-wchi | INM→V5 10 Ω | 7,3 mV | 5e-9 V | ≈0 V | FAIL | FAIL |
| efuse-ovp-s023-wchi | PU 1 µF | 42,7 mV | 5,0 V | −4,93 V | FAIL | FAIL |

Öz-test exit 0. Not: rev3 modelinde eski 100 pF PU-cap tanısı FET'i artık kapalı tutmuyor (O1 11,887 V), bu yüzden daha güçlü bozmalar kullanıldı. Böyle bir "düşük O1" artık PASS sayılamaz.
