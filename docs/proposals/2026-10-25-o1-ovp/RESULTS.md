# WP1 rev2 – Simülasyon sonuçları (2026-10-25-o1-ovp)

**Ortam:** Bulut kutusu, Debian 13, Python 3.13.5, **ngspice-44.2** (apt `44.2+ds-1`, KLU; ikili sha256 `5854f6506e3e54e0553b687401a5d82aec82229c2c28a93b7eb37b6e079dda84`), `-D ngbehavior=ltpsa` ile koşuldu. **LTspice bulut ortamında çalıştırılmadı** (PDU_LTSPICE yok → SKIPPED; LTspice sonucu iddia edilmez). Modeller davranışsal/ideal – bkz. `MODELS.md`. **Sim ≠ silikon/tezgâh kanıtı.**

**rev2 değişiklikleri (devre):** RAW bankı 8 → **16 × C5750X7S2A226M280KB** (COUT21–COUT28). Bağımsız inceleme (99a541a) sonrası: COUT11 2,2 µF → **10 µF/1206**, CREF12 → **1 µF**, yeni ESL (2 nH) ve 176 µF / 165 µF dürüst-minimum köşeleri, normal-bus sınırı **11,1605 V** ayrı kontrol, 11,22 V yalnız yanlış-tetik **test seviyesi**.

**Koşu:** etiket `wp1-rev2-2`, 2026-10-25 01:59:52 → 02:07:49 TSİ, **154 ngspice deck** (+154 LTspice deck üretildi, çalıştırılmadı).

```
cd simulation/proposals/2026-10-25-o1-ovp
python3 gen_o1ovp.py                         # 154 case, 308 deck (deterministik; yeniden üretim birebir aynı – diff -rq boş)
python3 window_budget.py --json window-budget.json   # min garanti marjı 71,96 mV (ömür dahil 57,15 mV); cmp OK
python3 gate_discharge_wc.py                 # P0-3: en kötü oran 0,9685, conclusion_ok=True; cmp OK
PDU_NGSPICE=/usr/bin/ngspice python3 run_o1ovp.py --label wp1-rev2-2   # exit 1 (2 kabul FAIL = 2 yakınsamayan deck)
python3 verify_candidate.py                  # exit 2: 1182 yeniden kontrol, 0 FAIL, 2 kanıt sorunu (aynı 2 eksik log)
python3 verify_candidate.py --baseline-regression   # exit 1 (beklenen: O1_PEAK 16,89 V)
```

## Özet
| | rev1 (`wp1-final-1`, 99a541a öncesi) | rev2-1 (`wp1-rev2-1`) | **rev2-2 (`wp1-rev2-2`, son)** |
|---|---|---|---|
| Deck (ngspice) | 126 | 136 | **154** |
| Kabul kontrolü PASS (runner) | 1370 | 1447 | **1799** |
| Kabul kontrolü FAIL (runner) | 1 (O1 12,0368 V) | 0 | **2 (yakınsamama, O1 FAIL değil)** |
| Bilgi/izleme FAIL (kabul dışı) | 6 | 7 | **8** (3 bilgi + 5 WP3 izleme) |
| Eksik/yakınsamayan | 0 | 0 | **3** (2 kabul + 1 bilgi) |
| Bağımsız doğrulayıcı | 853 / 1 FAIL | 890 / 0 FAIL | **1182 / 0 FAIL / 2 kanıt sorunu** |

### AÇIK – 2 kabul FAIL (gizlenmedi, silinmedi, bilgiye çevrilmedi)
`buck-short-c185-esr12m5-esl2n-typ` ve `buck-short-c165-esr12m5-esl2n-typ`: ngspice `Timestep too small; time = 0.0122646 … trouble with node "pu_ovp"` ile **açılışta** (12,26 ms; kısa devre 30 ms'de) durdu. 12,26 ms, startup koşularındaki FET açılma anıdır (`fet_on_t` 12,32 ms) → davranışsal TPS48000 PU/kapı sürücüsünün sert anahtarlaması + 2 nH ideal ESL'in **sayısal** etkileşimi. Aynı ESL ile `-wchi` köşeleri tamamlandı ve geçti (aşağıda).

Teşhis (yalnız `/workspace/scratch` kopyalarında; repo deck'leri değiştirilmedi, sonuçlar resmi koşuya **eklenmedi**):
- ESL'siz (0 V kaynakla) c185 typ → tamamlanıyor (O1 11,474 V).
- ESL'e paralel 1 Ω sönümleme: c185 typ tamamlandı (O1 **11,4718 V**), c165 typ yine aynı anda durdu; 0,3/0,5/2/3/10 Ω da durdu.
- `.options` varyantları (maxord=2, itl4=100, trtol=1, vntol=10u, abstol=10n, chgtol=1e-12, gmin=1e-10, rshunt=1e9, method=trap, reltol=2e-4, maks. adım 50n/200n), ESL'i toprak tarafına taşıma, ESL 2,001 nH → hepsi aynı anda durdu.
- PU düğümüne 10/100 pF → tamamlandı ama FET hiç açılmadı (O1 ≈ 6 mV) → **geçersiz**, kullanılmadı.
Sonuç: tutarlı bir sayısal yardım bulunamadı → **bloklayıcı/açık** (WP1 tamamlandı denmez). Not: rev2-1'de tamamlanan `rev1-c92-wchi` bilgi deck'i de rev2-2'de (COUT11/CREF12 değişikliğinden sonra) 45,126 ms'de `xu4.ena` düğümünde durdu → davranışsal modelin sayısal kırılganlığı genel bir risk (MODELS.md).

## B. O1 anlık tepe – test grubu başına (kabul, sınır 12,0 V)
| Grup | Deck | En yüksek O1 | Case | 12 V marjı |
|---|---|---|---|---|
| Kısa devre (buck HS short 26 V), tüm kabul köşeleri | 22 (20 tamam, **2 yakınsamadı**) | **11,9026 V** | buck-short-c165-esr12m5-wchi | 97,4 mV |
| eFuse-OVP rampa 0,07/0,17/0,23 V/µs | 6 | 11,8368 V | efuse-ovp-s017-wchi | 163,2 mV |
| tDOFF tarama (0,3625–1,0545 µs, kabul) | 3 | 11,6492 V | sweep-tdoff1p0545u-s023-wchi | 350,8 mV |
| Overdrive tarama 0/50 mV (kabul) | 2 | 11,6492 V | sweep-od50-s023-wchi | 350,8 mV |
| MC rampa (40, seed 20261025) | 40 | 11,5921 V | mc-ramp-s023-00 | 407,9 mV |
| MC kısa devre (20, c185) | 20 | 11,7656 V | mc-short-c185-03 | 234,4 mV |
| Startup (8) | 8 | 10,9836 V (o1_max) | – | – |

### Kısa devre ayrıntı (O1 tepe wchi / typ)
| RAW C / ESR / ESL | wchi | typ | VDS max (wchi) | Sonuç |
|---|---|---|---|---|
| 185,3 µF / 1 mΩ | 11,8767 | 11,4752 | 26,18 V | PASS |
| 185,3 µF / 12,5 mΩ | 11,8886 | 11,4775 | 24,53 V | PASS |
| 185,3 µF / 12,5 mΩ / 2 nH | 11,8893 | **yakınsamadı** | 24,52 V | wchi PASS / typ **FAIL (yürütme)** |
| 176 µF / 1 mΩ | 11,8867 | 11,4741 | 26,24 V | PASS |
| 176 µF / 12,5 mΩ | 11,8937 | 11,4794 | 24,62 V | PASS |
| **165 µF / 1 mΩ** (dürüst min) | 11,8929 | 11,4742 | 26,33 V | PASS |
| **165 µF / 12,5 mΩ** | **11,9026** | 11,4814 | 24,74 V | PASS (sim en kötü) |
| 165 µF / 12,5 mΩ / 2 nH | 11,8994 | **yakınsamadı** | 24,73 V | wchi PASS / typ **FAIL (yürütme)** |
| 483 µF / 1 mΩ | 11,7894 | 11,4444 | 24,73 V | PASS |
| 483 µF / 12,5 mΩ | 11,8085 | 11,4530 | 22,49 V | PASS |
| 185 µF / 100 mΩ (−40 °C stres) | 11,5919 | 11,5921 | 23,65 V | O1 PASS; **bus 13,04 V** (O1 portu değil, U3 OVP); toparlanma değerlendirilmedi |
| 130 µF / 12,5 mΩ (bilgi) | 11,9341 | 11,4898 | 25,15 V | bilgi |
| 120 µF / 12,5 mΩ (bilgi) | 11,9579 | 11,4920 | 25,26 V | bilgi |
| rev1 92,65 µF / 1 mΩ (bilgi) | **yakınsamadı** | 11,5028 | – | bilgi-FAIL (yürütme) |
| rev1 92,65 µF / 12,5 mΩ (bilgi) | **12,0391** | 11,5046 | 25,62 V | bilgi-FAIL (rev1 P0'ın yeniden üretimi) |

Sim wchi en kötü (11,9026 V / 97,4 mV) analitik garanti bütçesiyle (c165-esr12m5: 94,2 mV garanti, 76,7 mV ömür dahil; BUDGET.md §4) tutarlı; ESL 2 nH etkisi küçük: sim wchi O1 değişimi c185 +0,7 mV, c165 −3,2 mV; analitik bütçede marj +2,1 mV (di/dt'yi Lfault 2,72 µH sınırlar; 2 nH × ~5,4 A/µs ≈ 11 mV ESL gerilimi).

## C. Normal bus maks. (sınır 11,1605 V, R2b)
281 `NORMAL_BUS_MAX` kontrolü (o1_pre, normal, o1_normal, bus_max, bus_avg) → **281/281 PASS**. En kötü: **11,0314 V** (kısa devre öncesi normal işletme, tüm buck-short/mc-short deck'leri) → marj 129,1 mV. Startup bus_max en kötü 11,0286 V (startup-20v-chi, 483 µF). (2 yakınsamayan deck'te bu kontroller ölçülemedi → yukarıdaki FAIL kapsamında.)

## D. Yanlış tetik (11,22 V test seviyesi; normal-bus sınırı değil)
`no-false-trip`, `no-false-trip-ron5m28`, `mc-nofalse-00…19` (22 deck): `FALSE_TRIP_TEST_LEVEL_reached` RAW max 11,22 V **22/22 PASS** (uyaranın geçerliliği), `no_false_trip` INP min 4,9995 V, VGS min 11,60 V → **22/22 PASS** (tetik yok). Analitik: alt trip sınırı 11,2929 V → 11,22 V'a 72,9 mV (ömür dahil 58,4 mV).

## Diğer
| Case | Sonuç |
|---|---|
| Yük basamağı 0,45→4,5 A (ron 1,8/3,3/5,28 mΩ, c165, chi) | bus 10,8115–10,9945 V → PASS (10,78–11,22) |
| load-step-par1-ron5m28 | bus min 10,7878 V → PASS |
| Startup 20/22,2/26 V, IBST min, wchi, c165, chi | O1 max 10,984 V, RAW max 11,057 V, bus max 11,029 V → PASS |

U13 IN− giriş akımı ≤ 10 mA, INP_FAULT < 0,8 V, U3/U4 IN ≤ 30 V – tamamlanan tüm case'lerde PASS (doğrulayıcı bağımsız yeniden kontrol etti).

## Bilgi / izleme FAIL'leri (kabul kriteri değil; gevşetme yok)
- `sweep-od200-s023-wchi`: 200 mV overdrive duyarlılık → O1 12,0676 V (bilgi, veri sayfası noktası dışı).
- `buck-short-rev1-c92-esr12m5-wchi` → 12,0391 V; `buck-short-rev1-c92-wchi` → yakınsamadı (yalnız karşılaştırma).
- `load-step-7p5a-*` (5): 7,5 A izleme penceresi 10,78–11,22 V; bus min 10,6491–10,7584 V → **WP3 takip** (repo kriteri değil).

## Baseline regresyonu
`simulation/pdu-efuse-ovp.ng.cir` (sha256 `7529ff25…ca7d`, koşu öncesi = sonrası) → **O1_PEAK = 16,89 V → FAIL (beklenen)**. Baseline dosyaları değişmedi.

`o1ovp-results.json` deck_sha256'ları mevcut 154 deck ile birebir (0 uyuşmazlık).
