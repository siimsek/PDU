# WP1 – Simülasyon sonuçları (2026-10-25-o1-ovp)

**Ortam:** Bulut kutusu, Debian 13, Python 3.13.5, **ngspice-44.2** (apt `44.2+ds-1`, KLU; ikili sha256 `5854f6506e3e54e0553b687401a5d82aec82229c2c28a93b7eb37b6e079dda84`). **LTspice bulut ortamında çalıştırılmadı** (PDU_LTSPICE yok → SKIPPED; LTspice sonucu iddia edilmez). Modeller davranışsal/ideal – bkz. `MODELS.md`. Sim ≠ silikon/tezgâh kanıtı.

**Koşu:** etiket `wp1-final-1`, 2026-10-25 01:16:12 → 01:24:32 TSİ, 126 ngspice deck (+126 LTspice deck üretildi, çalıştırılmadı), 6 paralel iş.

```
cd simulation/proposals/2026-10-25-o1-ovp
python3 gen_o1ovp.py                       # 126 case, 252 deck, 14 include düzenlemesi (deterministik; yeniden üretim birebir aynı)
PDU_NGSPICE=/usr/bin/ngspice python3 run_o1ovp.py --jobs 6 --label wp1-final-1   # exit 1
python3 verify_candidate.py                 # exit 1
python3 verify_candidate.py --baseline-regression   # exit 1 (beklenen)
```

## Özet
| | Sayı |
|---|---|
| Kabul kontrolü PASS (runner) | 1370 |
| Kabul kontrolü FAIL (runner) | **1** |
| Bilgi/izleme FAIL (kabul dışı) | 6 |
| Eksik/yakınsamayan | 0 |
| Bağımsız doğrulayıcı (verify_candidate.py) | 853 yeniden kontrol, **1 FAIL**, 0 kanıt sorunu |

**Kabul FAIL:** `buck-short-c92-esr12m5-wchi` – O1 tepe **12,0368 V** > 12,0 V (buck üst FET kısa devresi 26 V, RAW 92,65 µF, 12,5 mΩ ESR, en kötü yüksek eşik köşesi).

## Önemli sonuçlar (O1 = port anlık tepe)
| Case | Köşe | O1 tepe | Bus tepe | VDS max | Sonuç |
|---|---|---|---|---|---|
| efuse-ovp 0,07 V/µs | wchi / typ | 11,717 / 11,420 V | 11,726 / 11,429 | 15,35 V | PASS |
| efuse-ovp 0,17 V/µs | wchi / typ | 11,841 / 11,471 V | 11,851 / 11,482 | 15,36 V | PASS |
| efuse-ovp 0,23 V/µs | wchi / typ | 11,649 / 11,400 V | 11,940 / 11,533 | 14,76 V | PASS |
| buck-short c92 1 mΩ | wchi / typ | **11,996** / 11,502 V | 11,999 / 11,504 | 27,37 V | PASS (4 mV marj) |
| buck-short c165 1 mΩ | wchi / typ | 11,896 / 11,474 V | 11,898 / 11,476 | 26,70 V | PASS |
| buck-short c92 12,5 mΩ | wchi / typ | **12,037** / 11,504 V | 12,041 / 11,508 | 26,09 V | **FAIL** / PASS |
| buck-short c92 100 mΩ (−40 °C stres, 45 ms'de kesildi) | wchi / typ | 11,595 / 11,595 V | 13,167 / 12,553 | 23,74 V | O1 PASS (U3 eFuse OVP yakaladı); bus > 12 V; toparlanma değerlendirilmedi |
| MC rampa (40, seed 20261025) | MC | 11,112–11,592 V | 11,657–**12,176** V | | O1 PASS; bus > 12 V'u görür (O1 portu değil) |
| MC kısa devre (20) | MC | 11,612–11,868 V | 11,615–11,871 | 27,27 V | PASS |
| MC yanlış tetik (20) | MC | RAW 11,22 V'ta INP min 4,9995 V | | | Tetik yok – PASS |
| Startup 20/22,2/26 V, IBST min | wclo/wchi | 10,984 V | bus max 10,995 V | | PASS (≤ 11,22) |

U13 IN− giriş akımı ≤ 4,78 mA (≤ 10 mA), INP_FAULT ≈ 5 nV (< 0,8 V), U3/U4 IN ≤ 30 V – tüm case'lerde PASS.

## Bilgi / izleme FAIL'leri (kabul kriteri değil; gevşetme yok)
- `sweep-od200-s023-wchi`: 200 mV overdrive (veri sayfası noktası dışında, duyarlılık) → O1 12,068 V.
- `load-step-par1-ron5m28`: tek FET çifti bilgi case'i, 0,45→4,5 A: 10,757–10,990 V (L79 alt sınır 10,78 V) → neden 2 paralel çift seçildiğini gösterir.
- `load-step-7p5a-*` (4 case): 7,5 A aşaması izleme penceresi 10,60–10,99 V → WP3 takip (repo kriteri değil).

## Baseline regresyonu
`simulation/pdu-efuse-ovp.ng.cir` (sha256 `7529ff25…ca7d`, koşu öncesi = sonrası) → **O1_PEAK = 16,89 V → FAIL (beklenen)**. Baseline dosyaları değişmedi.
