# WP2 2026-10-25-uvlo – Simülasyon sonuçları (C3 + U22 EN kapısı)

**Durum: öneri. Tezgâh testi yapılmadı. "Üretime hazır" DEĞİLDİR.**

## 1. Koşu bilgisi
| Alan | Değer |
|---|---|
| Simülatör | ngspice-44.2 (`ngspice -b -D ngbehavior=ltpsa`), 8 CPU, `-j 7`. LTspice: bulut ortamında çalıştırılmadı |
| Koşu | 2026-10-25 11:24:55 – 11:37:00 TSİ (Europe/Istanbul), `python3 run_uvlo.py -j 7` → 58/58 deck tamamlandı (rc 0, `completed: true`). Tur 1 sonrası yeniden koşu: deck'ler a0dea91'de VIO 6 mV (TLV3202 SBOS561C Rev C tablo 6.5) ile yeniden üretildi |
| Doğrulama | 2026-10-25 11:37:02 TSİ, `python3 verify_uvlo.py` (Tur 1 fail-closed sürüm, 4254a5d) → **çıkış kodu 0**; `package_inputs_dirty: false` (WP2 paket girdileri HEAD ile aynı) |
| Benzetim girdileri | commit a0dea91 (gen + blok + lib + deck'ler). Koşu ve doğrulama anında HEAD a0dea91; WP2 paket dizininde (results/ hariç) kirli dosya yok. Çalışma ağacındaki kirlilik yalnız doküman dosyalarıydı (`worktree_dirty_at_verify: true`, `package_inputs_dirty: false`). `input_sha256` uvlo-verify.json içinde. Önceki koşu (HEAD bfec691, kirli ağaç) bu koşuyla değiştirildi (Tur 1 P2 kaynak izi) |
| Dosyalar | `simulation/proposals/2026-10-25-uvlo/results/` → `logs/` (58), `run-all.out`, `run-manifest.json`, `uvlo-verify.json`, `verify-stdout.txt`, `uvlo-budget.json` |
| Düzeltme öncesi arşiv | `results/prefix-c3/` (HEAD b6b4b10, rc 1, 45/52 PASS) |

Özet (`uvlo-verify.json` → summary): 58 deck, 52 PASS; kabul FAIL **yok**; eksik/yarım deck **yok**; regresyonların 4'ü de beklenen şekilde FAIL (yeniden üretildi); 7 INFO. Tur 1'den itibaren INFO durumları da H1/H2 sert sınır kapısından geçer (`hard_limit_gate`); hiçbir INFO durumu H1/H2'yi ihlal etmedi.

Sert sınırlar (`verify_uvlo.py`, gevşetilmedi): O1 anlık tepe ≤ 12,0 V; normal rejim bus/O1 ≤ 11,1605 V (PRE/RUN/POST pencereleri); VIN < 18,0 V olmadan buck kapalı; VIN uygun (OUTA ↑) → buck EN ↑ ≥ 60 ms (T_SEQ_MIN) ve FET, buck EN'den önce açık. 11,22 V yalnızca WP1 OVP yanlış tetik uyarısıdır, burada sınır olarak kullanılmadı.

## 2. Tüm durumlar
Gerilimler V, süreler s. O1 = O1_GLOBAL_PEAK, Bus = BUS_GLOBAL_MAX (dip/geçiş anı dahil, tüm koşu), RAW = RAW_GLOBAL_MAX. "Gecikme" = VIN uygun (OUTA ↑) → EN ↑ (≥ 0,060 s olmalı); "Sıra payı" = FET ↑ → EN ↑ (> 0 olmalı); "VIN payı" = yük altında VIN min − V_f.

| Durum | Beklenen | Sonuç | O1 | Bus | RAW | Gecikme | Sıra payı | VIN payı |
|---|---|---|---|---|---|---|---|---|
| start20-vrmax-tmax | PASS | PASS | 10,978 | 10,994 | 11,005 | 0,2556 | 0,2487 | 0,2467 |
| start20-vrmax-tmin | PASS | PASS | 10,978 | 11,021 | 11,029 | 0,0778 | 0,0409 | 0,2467 |
| start20-vfmax-tmin | PASS | PASS | 10,978 | 11,021 | 11,029 | 0,0778 | 0,0401 | 0,2330 |
| start20-mbmin-tmin | PASS | PASS | 10,978 | 11,021 | 11,029 | 0,0778 | 0,0379 | 0,7074 |
| start20-vfmin-tmax | PASS | PASS | 10,978 | 10,994 | 11,005 | 0,2556 | 0,2458 | 0,7209 |
| start20-typ-ttyp | PASS | PASS | 10,978 | 11,006 | 11,016 | 0,1807 | 0,1713 | 0,4747 |
| rampup-10vps-mbmin-tmin | PASS | PASS | 10,978 | 11,006 | 11,016 | 0,0778 | 0,5134 | 1,7752 |
| rampup-10vps-vrmax-tmax | PASS | PASS | 10,978 | 11,006 | 11,016 | 0,2556 | 0,7443 | 1,3152 |
| rampup-10vps-typ-ttyp | PASS | PASS | 10,978 | 11,006 | 11,016 | 0,1807 | 0,6423 | 1,5432 |
| rampup-1vps-mbmin-tmin | PASS | PASS | 10,978 | 11,006 | 11,016 | 0,0778 | 0,7311 | 1,7752 |
| rampdown-10vps-vfmin-tmin | PASS | PASS | 10,978 | 11,006 | 11,016 | – | – | – |
| rampdown-10vps-mbmin-tmin | PASS | PASS | 10,978 | 11,006 | 11,016 | – | – | – |
| rampdown-10vps-typ-ttyp | PASS | PASS | 10,978 | 11,006 | 11,016 | – | – | – |
| rampdown-1vps-mbmin-tmin | PASS | PASS | 10,978 | 11,006 | 11,016 | – | – | – |
| mbhold-{mbmin-tmin, typ-ttyp, vfmax-tmin}-r250-{m50mv, p50mv} (6) | PASS | 6 × PASS | 10,978 | 11,006 | 11,016 | – | – | – |
| rsweep-r030 / r050 / r100 / r150 / r200 / r250 | PASS | PASS | 10,978 | 11,021 | 11,029 | 0,0778 | 0,0683–0,0684 | 1,598 / 1,501 / 1,255 / 1,002 / 0,742 / 0,474 |
| rsweep-r300 | INFO | PASS | 10,978 | 11,021 | 11,029 | 0,0778 | 0,0684 | 0,198 |
| rsweep-r350 | INFO | FAIL (kapanır) | 10,978 | 11,021 | 11,029 | 0,0778 | 0,0684 | −0,0031 |
| rsweep-r450 | INFO | FAIL (kapanır) | 8,837 | 11,021 | 11,029 | 0,0778 | 0,0684 | −0,2660 |
| dip19v-50ms-typ-ttyp / mbmin-tmin | PASS | PASS | 10,978 | 11,006 | 11,016 | – | – | – |
| dip0v-1ms-typ-ttyp / mbmin-tmin | PASS | PASS | 10,978 | 11,006 | 11,304 | – | – | – |
| dip0v-300us-typ-ttyp | PASS | PASS | 10,978 | 11,006 | 11,304 | – | – | – |
| **dip0v-300us-mbmin-tmin** | PASS | **PASS** (düzeltme öncesi FAIL) | 10,978 | 11,006 | 11,304 | – | – | – |
| dip0v-250us-typ-ttyp | PASS | PASS | 10,978 | 11,006 | 11,304 | – | – | – |
| dip0v-250us-mbmin-tmin | PASS | PASS (UV algılanmadı, bkz. §5) | 10,978 | **11,353** | 13,106 | – | – | – |
| dip0v-200us-typ-ttyp | INFO | PASS | 10,978 | **11,412** | 11,625 | – | – | – |
| dip0v-200us-mbmin-tmin | INFO | PASS | 10,978 | **11,358** | 12,189 | – | – | – |
| dip0v-100us-typ-ttyp | INFO | PASS | 10,978 | 11,122 | 11,304 | – | – | – |
| dip0v-100us-mbmin-tmin | INFO | PASS | 10,978 | 11,006 | 11,304 | – | – | – |
| dip15v-20ms-typ-ttyp / mbmin-tmin | PASS | PASS | 10,978 | 11,006 | 11,016 | – | – | – |
| deepdip0v-50ms-light-typ-ttyp / mbmin-tmin | PASS | PASS | 10,998 | 11,023 | 11,024 | – | – | – |
| hotplug-20p0v / 25p2v / 26p0v × {typ-ttyp, vrmax-tmin} (6) | PASS | 6 × PASS | 10,978 | 11,006 | 11,016 | 0,1809–0,1810 / 0,0781–0,0782 (typ / vrmax) | 0,1689–0,1690 / 0,0660–0,0661 | – |
| seq-delay-tmin-{typ, wchi, wclo}-ibst100u | PASS | 3 × PASS | 11,170 | – | – | – | – | – |
| reg-baseline-180k10k-worst | FAIL | FAIL (yeniden üretildi): EN 0,994 V, buck FET'ten önce, başlamaz | ≈0 | 0,011 | 0,011 | – | −0,0122 | – |
| reg-baseline-180k10k-typ-rampdown | FAIL | FAIL (yeniden üretildi): PRE'de EN 1,043 V | 10,978 | 10,986 | 11,025 | – | – | – |
| reg-misset-rbu-8k66-vrmax | FAIL | FAIL (yeniden üretildi): buck hiç açılmaz | ≈0 | 0,011 | 0,011 | – | – | – |
| seq-ref-nodelay-typ-ibst100u | FAIL | FAIL (yeniden üretildi): FET hiç açılmaz | ≈0 | – | – | – | – | – |

Tüm kabul durumlarında O1 anlık tepe ≤ 11,170 V (12,0 V'a pay ≥ 0,830 V). Normal rejim pencerelerinde (PRE/RUN/POST) bus maks 11,0314 V (11,1605'e pay +0,129 V). En kısa açılış gecikmesi 77,8 ms (rampup-10vps-mbmin-tmin; ≥ 60 ms, pay +17,8 ms; bütçe alt sınırı 77,7 ms ile uyumlu). FET ↑ → EN ↑ en dar 37,9 ms (start20-mbmin-tmin). Analitik bütçe (`uvlo-budget.json`, rc 0; Tur 1'de VIO 4 → 6 mV düzeltmesiyle yeniden koşuldu, a0dea91): marjlar a +0,0067 / b +0,0126 / c +0,0279 / d +0,1452 / e +0,071 V. **Uyarı:** a marjı yalnız G sınıfı terimlerle pozitiftir; 20 V başlatma garantisi kurulmadı (BUDGET.md §3a, açık P0 bloklayıcı); EN yüksek ≥ 2,289 V (+0,739 V), EN düşük ≤ 0,121 V (+0,279 V), U22 açıkken EN ≤ 2,58 mV (+0,397 V).

## 3. Düzeltme öncesi FAIL ve mekanizması (`results/prefix-c3/`)
`dip0v-300us-mbmin-tmin` (22,2 V → 0 V, 300 µs, 7,5 A, 0,25 Ω, mbmin/tmin, OVP wclo): POST rejiminde FET açık değil (VGS min 0 V), OVP karşılaştırıcısı düşük, RAW ort. 11,288 V regüle değil, bus maks 11,252 V > 11,1605 V. Bu bir kabul FAIL'iydi. Gizlenmedi; sınır gevşetilmedi.
Mekanizma (hata ayıklama dalga biçimleri, `dbg/`, commit edilmedi):
1. Dip başında (157,9 ms) U10 yükü ayırır. RAW 11,30 V'a çıkar ve OVP açar (FET kapalı).
2. Dip boyunca COMP ~3,9 V'a sarılır. UV 158,108 ms'de algılanır (OUTA ↓). Ama EN, CTT KTH altına inene kadar yüksek kalır (EN ↓ 158,245 ms).
3. VIN 158,124 ms'de geri gelir. OVP bu sırada bırakmıştır. Sarılmış buck RAW'ı 15,47 V'a iter ve OVP yeniden açar.
4. RAW yalnız RSNS bölücüsünden yavaş boşalır (320 ms'de 11,4 V). Regülasyon ~350 ms'de gelir, POST penceresi FAIL olur.

## 4. Düzeltme: U22 TMUX1102 EN kapısı (commit a8a5e0e)
U22 (D = EN_BUCK, S = GND, SEL = OUTA_UV, VDD = V5_OVP, C22 100 nF), OUTA_UV düşük olduğu anda EN_BUCK'ı GND'ye çeker. Buck, UV algılandığı anda durur ve soft-start'tan yeniden başlar. Schottky diyot yerine anahtar seçildi: diyot EN'i VOL + VF ≈ 0,35–0,55 V'ta bırakır, bu da < 0,4 V EN düşük mantığını (SNVSBX7A s.13, T/açıklama) garanti edemez. Eşik bütçesi değişmedi. WP1 OVP değişmedi.

| Durum | Bus maks önce → sonra | RAW maks önce → sonra | Sonuç önce → sonra |
|---|---|---|---|
| dip0v-300us-mbmin-tmin | 11,344 → 11,006 | 15,473 → 11,304 | FAIL → PASS |
| dip0v-300us-typ-ttyp | 11,431 → 11,006 | 12,870 → 11,304 | PASS → PASS (dip sonrası aşım kalktı) |
| Diğer 49 ortak durum | O1/Bus/RAW global maks değişmedi (en büyük fark: rsweep-r450 O1 8,895 → 8,837 V, kapanan INFO durumu) | değişmedi | aynı. Dip içi ara ölçümler (ör. dip0v-1ms-mbmin RAW_AT_DIP_END 9,060 → 9,554 V) buck daha erken durduğu için değişti |

Kalan RAW 11,304 V tepe, dip başındaki U10 yük ayırma olayıdır (WP1 OVP alanı, 1 ms dipte de aynı).

## 5. Artık risk R-DIP (kısa dip penceresi)
UV algılaması CFU filtresi nedeniyle gecikmelidir. Bu gecikmeden kısa dipler OUTA_UV'yi düşürmez, U22 devreye girmez, buck COMP sarılmış olarak devam eder.

| Dip (0 V) | Köşe | OUTA ↓ / EN ↓ | Yeniden başlatma bus maks | RAW maks | OVP (INP min) | POST |
|---|---|---|---|---|---|---|
| 300 µs | typ / mbmin | var / var | 11,006 / 11,006 | 11,016 / 11,016 | açmadı (5,00 / 4,90 V) | PASS |
| 250 µs | typ | 21 µs EN darbesi (soft-start sıfırlanır) | 11,006 | 11,016 | açmadı | PASS |
| 250 µs | mbmin | **yok** | **11,353** | 13,106 | **açtı (0 V)** | PASS |
| 200 µs | typ | **yok** | **11,412** | 11,625 | **açtı** | PASS (INFO) |
| 200 µs | mbmin | **yok** | **11,358** | 12,189 | **açtı (0 V)** | PASS (INFO) |
| 100 µs | typ | yok | 11,122 | 11,209 | açmadı | PASS (INFO) |
| 100 µs | mbmin | yok | 11,004 | 11,149 | açmadı | PASS (INFO) |

- Sınır, mbmin köşesinde 250–300 µs, typ köşesinde 200–250 µs arasındadır.
- Bu pencerede bus (VOUT) geçici olarak 11,1605 V'u **aşar** (maks 11,412 V, dip0v-200us-typ). REQUIREMENTS H2'ye göre bu normal rejim değildir (dip sonrası geçiş). Bu yüzden doğrulayıcı PASS verir. Yine de bu bir **risktir ve açıkça raporlanır**.
- O1 anlık tepe tüm durumlarda 10,978 V'tur (≤ 12,0 V). O1, WP1 OVP tarafından korunur.
- POST penceresinde (dip sonu + ~0,14–0,24 s) tüm durumlar regüledir. RAW boşalana kadar (onlarca–yüzlerce ms) regülasyon yoktur.
- Kök neden buck/OVP alanındadır (COMP windup, RAW'da akım çekici yok). WP2 bunu tek başına kapatamaz. Önerilen takip **WP3**: COMP kenetleme / VIN-kaybı algısı, ya da RAW akım çekici. Tezgâh: BENCH-TEST B-U15.
- Hata ayıklama deck'inde (`dbg/d200f`, mbmin, farklı .save) VOUT maks 11,347 V, RAW 12,50 V görüldü. Commit edilen deck'te (a0dea91) 11,358 / 12,189 V. Kayıt yalnız bilgi içindir; resmi sayı commit edilen deck'tir.

## 6. Yeniden başlatma süresi ve P0-03 / TDRV_EN riski (INFO)
| Dip | Köşe | EN ↓ → EN ↑ | FET ↑ (yeniden) − EN ↑ |
|---|---|---|---|
| 0 V 1 ms | typ / mbmin | 141,7 / 69,0 ms | FET önce (−141,0 / −68,2 ms) |
| 0 V 300 µs | typ / mbmin | **16,1 / 1,4 ms** | FET önce (−16,1 / −1,4 ms) |
| 15 V 20 ms | typ / mbmin | 191,8 / 94,5 ms | FET kapanmadı |
| 19 V 50 ms | typ / mbmin | 222,9 / 124,1 ms | FET kapanmadı |
| 0 V 50 ms hafif yük | typ / mbmin | 224,7 / 126,3 ms | FET önce (−175,5 / −77,1 ms) |

Kısa diplerden sonra zamanlayıcı kısmen boşalır, yeniden etkinleşme 60 ms'nin altına iner (300 µs: 1,4–16,1 ms). Simülasyonda FET, EN'den önce açıktır. Ancak TPS48000 yeniden kurma gecikmesi (TDRV_EN, en kötü 50,8 ms; WP1 bütçesi) bu davranışsal modelde kısa dip sonrası için gerçekçi olarak modellenmedi. Bu yüzden kısa dip sonuçları silikon davranışı değildir (Tur 1 P1, açık; tezgâh B-U10/B-U15) (FET, VIN döndükten ~2 µs sonra yeniden açılıyor). Gerçek parçada FET'in EN'den sonra açılması mümkündür. Bu durumda P0-03 (açılış yanlış tetiği) riski gerçekleşir. Açık madde: **P0-03**. Tezgâh B-U10.

## 7. seq-ref deck değişikliği (commit cb1df5e)
Eski `seq-ref-nodelay-typ` deck'i ngspice'ta yarıda kesiliyordu ("Timestep too small", 12,2646 ms, imon_s2e / pu_ovp düğümleri). Eski doğrulayıcı bunu "yeniden üretildi" sayıyordu. Bu yanlıştı. Doğrulayıcı artık yarıda kalan logu INCOMPLETE sayar. Deck, kabul edilen seq deck'leriyle aynı ayarda (yalnız gecikme 0) `seq-ref-nodelay-typ-ibst100u` olarak değiştirildi. Yeni deck tamamlanır ve "FET hiç açılmaz" sonucunu yeniden üretir. Eski log `results/prefix-c3/` içinde arşivlidir.

## 8. rsweep INFO
- R_total 0,30 Ω: çalışır, VIN payı +0,198 V.
- 0,35 Ω: yük altında VIN 18,256 V ≤ V_f (typ) 18,259 V. Buck kapanır, salınım yok (tek kapanma).
- 0,45 Ω: VIN 17,993 V. Buck kapanır.
- Bunlar garanti dışıdır (gereksinim ≤ 0,25 Ω). Kapanma, aşırı deşarj korumasının beklenen davranışıdır.

## 9. Varsayımlar (seçme)
- TMUX1102 anahtarlama gecikmesi modellenmedi (V).
- TLV3202 VCC < 2,7 V çıkışları düşük kabul edildi (V).
- 18,0 V hücre sınırı V.
- Davranışsal LM70880 / TPS48000 / LiPo modelleri (MODELS.md).
- Parazitik L yok.
- Simülasyon fiziksel doğrulamanın yerini tutmaz. BENCH-TEST.md'deki B-U1…B-U15 testlerinin **hiçbiri yapılmadı**.
