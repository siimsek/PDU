# WP2 2026-10-25-uvlo – Simülasyon sonuçları (C3 + U22 EN kapısı)

**Durum: öneri. Tezgâh testi yapılmadı. "Üretime hazır" DEĞİLDİR.**

## 1. Koşu bilgisi
> **WP2 Tur 3 notu:** Commit'li `results/` artık Tur 3 koşusunu (`box-tur3b-20261025-1522`, 121 deck, temiz HEAD dbe4690, C3 + O3, CTT hızlı reset adayı) içerir; doğrulama **exit 1** (yalnız rsweep-r350/r450). Ayrıntılar §11. **CI:** GitHub Actions `proposal-ngspice` kullanıcı tarafından devre dışı bırakıldı; CI kapısı etkin değildir, kanıt yerel koşu + `run-manifest.json` hash'leridir.
>
> **WP2 Tur 2 notu:** Aşağıdaki §1 tablosu Tur 1 koşusudur (58 deck, HEAD a0dea91, verify exit 0) ve karşılaştırma için tutuldu. Commit'li `results/` artık Tur 2 koşusunu (`box-tur2-20261025T1230`, 101 deck, C3 + O3) içerir; Tur 2 doğrulaması daha sıkı kapılarla **exit 1** verir. Ayrıntılar §10.

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
- 0,35 Ω: yük altında VIN 18,256 V ≤ V_f (typ) 18,259 V. Buck kapanır. **Düzeltme (Tur 3):** "salınım yok (tek kapanma)" ifadesi Tur 2 ve Tur 3 deck'lerinde yanlıştır: kapanmadan sonra EMF > V_r olduğu için OUTA yeniden yükselir ve EN tekrar tekrar yükselir (hiccup/motorboat; Tur 2'de ~80 ms, Tur 3'te ~119 ms periyot). Tur 2'de bu durum INFO olduğu için engelleyici değildi (UVLO-T3-01); Tur 3'te zorunlu kapılar INFO'ya da uygulandığından FAIL'dir (§11).
- 0,45 Ω: VIN 17,993 V. Buck kapanır.
- Bunlar garanti dışıdır (gereksinim ≤ 0,25 Ω). Kapanma, aşırı deşarj korumasının beklenen davranışıdır.

## 9. Varsayımlar (seçme)
- TMUX1102 anahtarlama gecikmesi modellenmedi (V).
- TLV3202 VCC < 2,7 V çıkışları düşük kabul edildi (V).
- 18,0 V hücre sınırı V.
- Davranışsal LM70880 / TPS48000 / LiPo modelleri (MODELS.md).
- Parazitik L yok.
- Simülasyon fiziksel doğrulamanın yerini tutmaz. BENCH-TEST.md'deki B-U1…B-U15 testlerinin **hiçbiri yapılmadı**.

## 10. WP2 Tur 2 koşusu (C3 + O3 aday varyantı) – simülasyon, fiziksel ölçüm değil
| Alan | Değer |
|---|---|
| Koşu | `python3 run_uvlo.py -j 8 --run-id box-tur2-20261025T1230`, 2026-10-25 12:30:57 – 13:01:03 TSİ, temiz HEAD `873a94a` (`package_inputs_dirty_at_run: false`), ngspice-44.2, 101/101 deck rc 0, `runner_exit_code` 0. Koşu öncesi eski log/manifest silindi |
| Doğrulama | `python3 verify_uvlo.py` (HEAD `53495e2`; arada yalnız WP1 doküman commit'i, WP2 paket girdisi farkı yok → `provenance_errors: []`). **Çıkış kodu 1** |
| Testler | `test_uvlo_gates.py` 13/13, `test_uvlo_tur2.py` 31/31, `test_uvlo_o3.py` 10/10 |
| Sayım | 101 durum, 86 PASS; kabul FAIL 6 (C3 3, O3 3); eksik 0; regresyon 5/5 beklenen FAIL |

**Sert sınırlar (H1/H2, regresyon dışı tüm durumlar, PASS ve INFO):**
| Ölçüt | C3 | O3 | Sınır |
|---|---|---|---|
| O1 anlık tepe maks | 11,16998 V (seq-delay-tmin-typ-ibst100u) | 10,99836 V (o3-deepdip0v-50ms-light-typ) | ≤ 12,0 V |
| Kararlı pencere bus maks | 11,03144 V (seq-delay, RUN) | 10,99517 V (o3-deepdip, PRE) | ≤ 11,1605 V |
| Kararlı pencere O1 maks | 11,02334 V | 10,99463 V | ≤ 11,1605 V |
| En kısa soğuk açılış gecikmesi (VIN-OK → EN) | 77,74 ms (hotplug-26p0v-vrmax-tmin) | 77,81 ms (o3-start20-vrmax-tmin) | ≥ 60 ms |
| En dar FET ↑ → EN ↑ | 37,9 ms | 37,0 ms | FET önce |
| En düşük kapanma VIN (rampdown) | 18,012 V | 18,073 V | ≥ 18,0 V |
(O3 deck kümesinde seq-delay/ibst ve rsweep durumları yok; C3/O3 sütunları doğrudan aynı küme değildir.)

**Kısa dip yeniden başlatma – 60 ms kapısı (UVLO-05, yeni):** VIN-OK (son OUTA ↑) → EN ↑.
| Dip (0 V) | Köşe | C3 | O3 |
|---|---|---|---|
| 300 µs | typ | **15,90 ms FAIL** | 62,47 ms PASS |
| 300 µs | mbmin | **1,39 ms FAIL** | **37,56 ms FAIL** |
| 250 µs | typ | **0,00 ms FAIL** (21 µs EN darbesi) | **38,63 ms FAIL** |
| 250 µs | mbmin | geçti (rode-through, EN düşmedi) | **24,33 ms FAIL** |
| 200 µs | typ / mbmin (INFO) | rode-through | **0,00 / 0,00 ms FAIL** (INFO durumunda da kapı uygulanır) |
| 100 µs | typ / mbmin (INFO) | rode-through | rode-through |
| 1 ms | typ / mbmin | 140,06 / 67,37 ms | 134,37 / 66,18 ms |
| 15 V 20 ms / 19 V 50 ms / 0 V 50 ms hafif | mbmin | 74,24 / 75,73 / 75,81 ms | 74,24 / 75,76 / 75,80 ms |

Yorum: zamanlayıcı (RTT/CTT, değişmedi) ≲ 1 ms diplerde tam sıfırlanmıyor; bu nedenle iki varyantta da 60 ms kapısı kısa diplerde sağlanmıyor. O3'ün farklı UV eşik zamanlaması yalnız hangi dip süresinin rode-through/yeniden başlatma olacağını kaydırıyor. Bu **yeni, açık bir tasarım P0'ıdır** (zamanlayıcı sıfırlama / VIN-kaybında CTT hızlı deşarjı WP2 Tur 3 işi). Sınır gevşetilmedi. Davranışsal U10 TDRV_EN modellenmediği için silikon davranışı değildir (§6).

**Geçici R-DIP taraması (rapor amaçlı, gereksinim DEĞİL; REQUIREMENTS.md):** ≤ 11,50 V tepe, ≤ 1 ms 11,1605 V üstü, dip sonundan ≤ 5 ms'de dönüş.
| Durum | Tepe | 11,1605 V üstü süre | Dönüş (dip sonundan) | Sonuç |
|---|---|---|---|---|
| C3 dip0v-200us-typ (INFO) | 11,41426 V | 18,1 µs | **10,32 ms** | FAIL (dönüş > 5 ms) |
| C3 dip0v-200us-mbmin (INFO) | 11,35498 V | 8,4 µs | **42,24 ms** | FAIL |
| C3 dip0v-250us-mbmin | 11,34552 V | 9,0 µs | **81,52 ms** | FAIL |
| C3 dip0v-100us-typ | 11,12123 V | 0 | – | PASS |
| O3 tüm 16 dip durumu | maks 11,12314 V (o3-dip0v-100us-typ) | 0 | – | PASS |
Toplam: 29 PASS, 3 FAIL, 0 UNDETERMINED. Not: "dönüş" ölçümü 11,1605 V eşiğinin **son aşağı yönlü geçişini** (Tur 3 T3-09 adlandırması; eski metinde "son aşım anı") dip sonuna göre alır; C3'te tepe süresi kısa (≤ 18 µs) ama geç ikincil aşımlar dönüş süresini uzatıyor. O3'te R-DIP'in görülmemesi, bu dip sürelerinde O3'ün yeniden başlatmaya geçmesinin (ve 60 ms kapısında FAIL vermesinin) sonucudur; R-DIP sorununun çözüldüğü anlamına gelmez.

**Regresyonlar (beklenen FAIL, hepsi FAIL):** reg-baseline-180k10k-worst, reg-baseline-180k10k-typ-rampdown, reg-misset-rbu-8k66-vrmax, seq-ref-nodelay-typ-ibst100u, o3-reg-misset-rbu-5k23-vrmax.

**Tur 1 ile karşılaştırma (C3, aynı deck'ler):** dip0v-200us-typ BUS_GLOBAL_MAX 11,41249 → 11,41426 V; mbmin 11,35757 → 11,35498 V (deck'lere R-DIP ölçümleri eklendi; küçük sayısal fark). Tur 1 verify exit 0 idi çünkü 60 ms kapısı dip yeniden başlatmalarına uygulanmıyordu; Tur 2'deki exit 1 sınırın sıkılaştırılmasının değil, eksik kapının eklenmesinin sonucudur.

## 11. WP2 Tur 3 koşusu (CTT hızlı reset adayı, C3 + O3) – simülasyon, fiziksel ölçüm değil
| Alan | Değer |
|---|---|
| CI | GitHub Actions `proposal-ngspice` (id 395474051) kullanıcı tarafından 2026-10-25'te **devre dışı** bırakıldı; yeniden etkinleştirilmedi, YAML tutuldu. **CI kapısı etkin değildir.** Kanıt: aşağıdaki yerel koşu, `run-manifest.json` (deck/log SHA-256) ve `uvlo-verify.json` (`input_sha256`, `log_sha256`) |
| Koşu | `python3 run_uvlo.py -j 8 --run-id box-tur3b-20261025-1522`, 2026-10-25 15:22:03 – 15:52:43 TSİ, kutu (8 CPU), ngspice-44.2 `-b -D ngbehavior=ltpsa`, temiz HEAD **dbe4690** (`package_inputs_dirty_at_run: false`), 121/121 deck rc 0, `runner_exit_code` 0. Koşu sırasında commit yapılmadı. LTspice / kullanıcı PC'si kullanılmadı |
| Doğrulama | `python3 verify_uvlo.py --run-id box-tur3b-20261025-1522` (HEAD dbe4690 = manifest HEAD) → `provenance_errors: []`, **çıkış kodu 1**. Sonuçlar e35b3bb'de commit'lendi |
| Önceki deneme | `box-tur3-20261025-1432` (a86add6): koşu sırasında doküman commit'i yapıldığı için `--run-id` HEAD eşleşmesi FAIL (exit 2) + 8 çift-dip deck'inde doğrulayıcı çapası hatası → kanıt sayılmadı; çapa dbe4690'da düzeltildi, koşu yinelendi |
| Testler | `test_uvlo_gates.py` 13/13, `test_uvlo_o3.py` 10/10, `test_uvlo_tur2.py` 31/31, `test_uvlo_tur3.py` 45/45 |
| Sayım | 121 durum, 110 PASS; kabul FAIL 2 (**rsweep-r350, rsweep-r450**, INFO, zorunlu kapı); eksik 0; regresyon **9/9** beklenen FAIL |

**Zorunlu kapılar (M1 60 ms her EN yükselişinde, son OUTA ↑'tan; M2 V_f ≥ 18,0 V) ve sert sınırlar (H1/H2) – regresyon dışı tüm durumlar, PASS ve INFO:**
| Ölçüt | C3 | O3 | Sınır |
|---|---|---|---|
| O1 anlık tepe maks | 11,16998 V (seq-delay-tmin-wclo-ibst100u) | 10,99836 V (o3-deepdip0v-50ms-light-typ) | ≤ 12,0 V |
| En kısa VIN-OK → EN (tüm EN yükselişleri) | **86,00 ms** (dip0v-300us-mbmin, dbldip0v-300us-20ms-mbmin) | **85,94 ms** (o3-dip0v-200us-mbmin) | ≥ 60 ms (geçici hedef 65 ms) |
| Soğuk açılış (dip deck'leri, EN_R1) | typ 195,25 / mbmin 87,21 ms | aynı | bütçe 77,7–255,5 ms |
| En düşük kapanma VIN (rampdown) | 18,00483 V (rampdown-10vps-vfmin-tmin) | 18,06563 V | ≥ 18,0 V |
| Bırakmada CTT (VT_AT_REL) | 46,0–49,0 mV | 46,0–49,0 mV | bütçe ≤ 53,5 mV |

**Kısa dip yeniden başlatma (son OUTA ↑ → EN ↑), Tur 2 ile karşılaştırma:**
| Dip (0 V) | Köşe | C3 Tur 3 | C3 Tur 2 | O3 Tur 3 | O3 Tur 2 |
|---|---|---|---|---|---|
| 300 µs | typ / mbmin | 193,99 / 86,00 ms | **15,90 / 1,39 ms FAIL** | 194,31 / 86,53 ms | 62,47 / **37,56 ms FAIL** |
| 250 µs | typ / mbmin | 193,44 ms / rode-through | **0,00 ms FAIL** / rode-through | 194,14 / 86,32 ms | **38,63 / 24,33 ms FAIL** |
| 200 µs (artık PASS-kapılı) | typ / mbmin | rode-through | rode-through (INFO) | 193,88 / 85,94 ms | **0,00 / 0,00 ms FAIL** (INFO) |
| 100 µs | typ / mbmin | rode-through | rode-through | rode-through | rode-through |
| 1 ms | typ / mbmin | 194,90 / 86,93 ms | 140,06 / 67,37 ms | 194,87 / 86,92 ms | 134,37 / 66,18 ms |
| 50 ms (tam yük, yeni) | typ / mbmin | 195,23 / 87,19 ms | – | 195,23 / 87,19 ms | – |
| 15 V 20 ms / 19 V 50 ms / 0 V 50 ms hafif | mbmin | 87,17 / 87,19 / 87,19 ms | 74,24 / 75,73 / 75,81 ms | 87,17 / 87,19 / 87,19 ms | 74,24 / 75,76 / 75,80 ms |

**Çift dipler (yeni, T3-02):** son OUTA ↑'tan ölçülür. 300 µs + 20 ms: C3 193,99 / 86,00 ms, O3 194,31 / 86,53 ms; 1 ms + 40 ms: C3 194,90 / 86,93, O3 194,87 / 86,92 ms; 1 ms + 30 ms + 50 ms (ikinci OUTA kaybı sayım sırasında): C3 195,23 / 87,19, O3 195,32 / 87,28 ms (typ / mbmin). Hepsi PASS. 2. dip VIN-OK'u düşürmediğinde gecikme, yalnız ngspice kanıtı varsa (OUTA_F2 ve OUTA_R3 'failed', OUTA_RLAST == OUTA_R2) son OUTA ↑'tan ölçülür (dbe4690); diğer belirsiz durumlar fail-closed.

**Regresyonlar (beklenen FAIL, 9/9 FAIL):** reg-baseline-180k10k-worst, reg-baseline-180k10k-typ-rampdown, reg-misset-rbu-8k66-vrmax, seq-ref-nodelay-typ-ibst100u, o3-reg-misset-rbu-5k23-vrmax ve reset devresi olmadan (Tur 2 zamanlayıcısı) `noreset` deck'leri: C3 300 µs mbmin **1,295 ms**, 250 µs typ **0,000 ms**; O3 250 µs mbmin **24,296 ms**, 200 µs typ **0,000 ms** (< 60 ms → FAIL, eski hatayı yeniden üretir).

**Dürüst not – OUTA ↑ anında CTT:** incelemenin geçici hedefi "her dip sonrası OUTA ↑ anında V_CTT ≤ 1,0 V" bu aday mimaride **harfiyen sağlanmıyor**: CTT, OUTA döndükten sonraki gerdirici tutma penceresinde (bütçe 7,93–26,26 ms) boşaltılır; OUTA ↑ anında CTT C3'te 4,37 V'a (dip0v-250us-typ), O3'te 3,50 V'a (o3-dip0v-200us-typ) kadar görülür. Bırakmada CTT ≤ 49,0 mV (simülasyon) / ≤ 53,5 mV (bütçe) ve gecikme son OUTA ↑'tan ölçüldüğünde ≥ 85,94 ms'dir; asıl ≥ 60 ms sınırı ve 65 ms geçici hedefi bu koşuda sağlanır. Hedefin harfiyen istenmesi durumunda reset-baskın mandal (OUTA ↓ ile kurulan, CTT boşalınca bırakılan) alternatifi açıktır.

**Açık – rsweep-r350/r450 (INFO, gereksinim dışı R ≥ 0,35 Ω; gereksinim ≤ 0,25 Ω):** yük altında VIN 18,2557 / 18,0114 V ≤ V_f (typ) 18,2588 V; kapanmadan sonra EMF > V_r olduğundan ~119 ms periyotla hiccup (4'ten fazla EN yükselişi, doğrulayıcı ara yükselişleri izleyemediği için fail-closed M1). Her izlenen yükselişte gecikme ≥ 60 ms olsa da sistem çalışmıyor. Tur 2'de aynı hiccup (~80 ms periyot, gecikme ~48 ms) INFO olduğu için engelleyici değildi; T3-01 ile artık görünür FAIL. Sınır/test gevşetilmedi; bu bir **açık bulgudur** (öneri: tekrar deneme sayacı/kilitleme ya da R_TOTAL sınırının sistem gereksinimi olarak sabitlenmesi – kullanıcı kararı).

**Açık – µs darbeler:** OUTA'nın ~1,6 ms'den kısa düşük kalması Schmitt alt eşiğine kadar deşarjı garanti etmez; 100/200 µs dipler bu yüzden rode-through. Reset-baskın mandal önerisi açık; TDRV_EN silikon davranışı modellenmedi (§6, tezgâh B-U10/B-U15).

**Geçici R-DIP taraması (rapor amaçlı, gereksinim DEĞİL):** 49 PASS, 3 FAIL (C3): dip0v-200us-typ 11,41297 V / 18,1 µs üstte / son aşağı yönlü geçiş dip sonundan 9,69 ms; dip0v-200us-mbmin 11,35635 V / 8,2 µs / 41,26 ms; dip0v-250us-mbmin 11,34331 V / 8,2 µs / 79,46 ms. O3 dipleri PASS, ama bu diplerde O3 yeniden başlatır (yükü keser); R-DIP çözülmüş sayılmaz (WP3).

## 12. WP2 Tur 4 koşusu (U26 doğrudan EN yolu, M3/M4, µs dipleri, TDRV_EN, RDSC 180) – simülasyon, fiziksel ölçüm değil
| Alan | Değer |
|---|---|
| CI | GitHub Actions `proposal-ngspice` (id 395474051) kullanıcı tarafından **devre dışı**; yeniden etkinleştirilmedi, YAML tutuldu. **CI kapısı etkin değildir.** Kanıt: yerel koşu + `run-manifest.json` / `uvlo-verify.json` SHA-256 |
| Koşu | `python3 run_uvlo.py -j 8 --run-id tur4-6f0ad2f`, 2026-10-25 18:10:53 – 19:18:48 TSİ, kutu (8 CPU), ngspice-44.2 `-b -D ngbehavior=ltpsa`, temiz HEAD **6f0ad2f** (`package_inputs_dirty_at_run: false`), koşu sırasında commit yok. 173 deck: 170 rc 0, **3 deck "Timestep too small" ile yarıda** (dip0v-50us-typ, o3-dip0v-50us-typ, o3-dip0v-50us-mbmin; düğüm `imon_o1`, dip bitişinden ~18 µs sonra) → `runner_exit_code` 2 |
| Doğrulama | `python3 verify_uvlo.py --run-id tur4-6f0ad2f` (HEAD 6f0ad2f = manifest HEAD) → **çıkış 2** (yalnız runner exit 2 + 3 tamamlanmamış deck; run-id/HEAD/hash eşleşmesi tamam). Sonuçlar d538a8d'de commit'lendi |
| Testler | gates 13/13, o3 10/10, tur2 31/31, tur3 45/45, **tur4 257/257** (önce 6f0ad2f öncesi 243/251 → tasarım testleri D41–D46 FAIL; W05j–n/D48 f75bcba'da önce FAIL) |
| Sayım | 173 durum, **86 PASS**; kabul FAIL 75 (yalnız M3 65, M3+M4 6, yalnız M4 2, rsweep 2); eksik 3; regresyon **9/9** beklenen FAIL |

**Kabul FAIL'lerinin dökümü (dürüst):**
| Sebep | Durum sayısı | Ayrıntı |
|---|---|---|
| **M3** (VIN-OK kaybı → EN düşük ≤ 1 µs) | 71 (VIN-OK'u düşüren tüm reset'li dip / çift dip deck'leri, C3 + O3, TDRV ve RDSC180 dahil) | Doğrudan TRIG/TARG ölçümü `EN_LAG_F1` **1,468–1,559 µs** (> 1,000 µs). U26 (SEL = OUTA_UV) eklenmesine rağmen: OUTA_UV'nin 2,5 V'tan TMUX eşiğine (~1,2 V) inmesi, CST 150 nF'nin DST üzerinden ve CTT'nin DTT+RDIS üzerinden karşılaştırıcı çıkışına (model Ro 10 Ω) boşalmasıyla yavaşlıyor (τ ≈ 10 Ω·150 nF). Gerçek TLV3202 çıkış akım sınırı ile daha da yavaş olabilir. Tasarım bulgusu, sınır gevşetilmedi |
| **M4** (EN ↑ anında VGS ≥ 6 V) | 8 (tdrv-*-mbmin-tmin, C3 + O3) | TDRV_EN 50,8 ms modeli (varsayım A) ile soğuk açılışta EN_R1 88,68 ms, FET_ON1 93,19 ms → VGS(EN_R1) = 0 V. Yeniden başlatmada (EN_R2 255,85 ms, FET_ON2 218,86 ms) sağlanıyor. typ köşesinde (EN_R1 196,8 ms) sağlanıyor. Zamanlayıcı başlangıcı FET-hazır sinyaline bağlı değil → açık tasarım bulgusu |
| rsweep-r350 / r450 | 2 | Tur 3 ile aynı (R ≥ 0,35 Ω hiccup; kapsam R_total ≤ 0,25 Ω) |
| Eksik (abort) | 3 | 0 V 50 µs dipleri; kazı (sonuç sayılmaz, depoda değil): aynı deck kenar 5 µs veya `.options gmin=1e-11` ile tamamlanıyor, 20 µs kenarla yine abort → sayısal hassasiyet (WP1 eFuse IMON düğümü); Tur 5 iş kalemi |

**Sağlanan kapılar:** M1 (her EN ↑, son OUTA ↑'tan ≥ 60 ms) regresyon dışı tüm tamamlanmış deck'lerde sağlandı: en kısa C3 **85,99 ms** (dbldip0v-300us-20ms-mbmin), O3 **85,94 ms** (o3-dip0v-200us-mbmin), TDRV C3/O3 86,94 / 86,92 ms, RDSC180 C3/O3 85,55 / 86,04 ms (65 ms hedefi de sağlanıyor). H1 O1 maks **11,16998 V** (seq-delay-tmin-wclo-ibst100u) ≤ 12,0 V; H2 / M0 / M2 / seq şeması ihlali yok. Rampdown kapanma VIN ≥ 18,0 V (Tur 3 ile aynı deck'ler).

**µs dipleri (0 V, typ + mbmin, C3 + O3):** 1 / 5 / 10 µs: VIN-OK düşmüyor (CFU 100 nF + karşılaştırıcı gecikmesi), EN hiç düşmüyor, rode-through PASS. 50 µs: C3 mbmin rode-through PASS, diğer 3 deck abort. 100 / 200 µs C3: rode-through PASS; O3 200 µs ve 225 µs (yeni, eşik yakını): VIN-OK düşüyor → yalnız M3 FAIL (M1 ≥ 85,9 ms). 20 ms: yeniden başlatma, M1 ≥ 87,17 ms, yalnız M3 FAIL. µs mertebesindeki kayıpta EN'in istenen ≤ 1 µs'de düşmesi bu modelde sağlanmıyor; incelemenin önerdiği asenkron reset-baskın mandal (VIN-OK kaybı ile kurulan, ≥ 65 ms + CTT ≤ 53,5 mV ile bırakılan) ya da OUTA_UV'nin CST/CTT yükünden ayrılması (DST/RDIS seri direnç + yakın-eşik M1 yeniden doğrulaması) Tur 5 adayıdır.

**TDRV_EN (yeni, `pdu-tdrv-en.inc`, INFO):** TPS48000 EN → kapı sürüş gecikmesi 50,8 ms (varsayım A: maks kabul edildi, her VIN-EN kaybında yeniden başlar). M1 ve dip sonrası M4 sağlanıyor (typ ve mbmin); mbmin soğuk açılışta M4 FAIL (yukarıda). Datasheet TDRV_EN değeri ve davranışı birincil kaynaktan doğrulanmadı; silikon B-U10/B-U15.

**RDSC 180 Ω keşfi (INFO, C3 + O3, 1 ms / 300 µs / 1 ms+30 ms+50 ms):** M1 ≥ 85,55 ms, bırakmada CTT davranışı beklenen; yalnız M3 FAIL (RDSC'den bağımsız). Bütçe: Ipk 29,2 mA, t_dsc 5,27 ms, ayrım 2,66 ms, V_rel 93,7 mV (> 53,5 mV hedefi) → aday 100 Ω kalır (BUDGET §4b).

**R-DIP (rapor amaçlı, `event` sınıflandırmalı):** 96 PASS / 5 FAIL; `counts_by_event`: rode_through/PASS 21, rode_through/FAIL 5, restart/PASS 75, restart/FAIL 0. FAIL'ler: C3 200 µs typ 11,41582 V / 10,46 ms; 200 µs mbmin 11,34318 V / 41,18 ms; 250 µs mbmin 11,34395 V / 79,23 ms; 225 µs typ 11,42170 V / 22,36 ms; 225 µs mbmin 11,35237 V / 59,17 ms (tepe/son aşağı geçiş dip sonundan). Restart (yük kesilen) deck'leri artık ayrı sayılıyor; yük atma ride-through PASS sayılmıyor.

**Regresyonlar (9/9 beklenen FAIL):** reg-baseline-180k10k-worst, reg-baseline-180k10k-typ-rampdown, reg-misset-rbu-8k66-vrmax, seq-ref-nodelay-typ-ibst100u, o3-reg-misset-rbu-5k23-vrmax, noreset C3 300 µs mbmin / 250 µs typ, O3 250 µs mbmin / 200 µs typ.
