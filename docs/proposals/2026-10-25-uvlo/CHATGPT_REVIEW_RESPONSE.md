# WP2 2026-10-25-uvlo – ChatGPT inceleme yanıtı

**Durum:** öneri. Tezgâh testi yapılmadı. Simülasyon fiziksel ölçüm değildir. "Üretime hazır" DEĞİLDİR.

## Tur 1 (inceleme yorumu 6395284882, WP1 Tur 7 ile birleşik)
Her bulgu önce eski kodda doğrulandı, sonra düzeltildi ya da gerekçeyle açık bırakıldı. Hiçbir sınır gevşetilmedi, hiçbir test silinmedi.

| ID | Önem | Bulgu (özet) | Doğrulama | Yanıt | Kanıt / commit | Durum |
|---|---|---|---|---|---|---|
| W2-P0-1 | P0 | TLV3202 VIO 4 mV yanlış; başlatma bütçesi G/T/A ayrımı yapmıyor | **Doğrulandı.** SBOS561C Rev C s.5 tablo 6.5: TLV3202 VIO maks 6 mV (−40…125 °C), 25 °C'de 5 mV. 4 mV TLV3201 satırıydı. Testler B1/B2 eski kodda FAIL | VIO 6 mV (G). Bütçe yeniden koşuldu: a +6,73 mV (eski +18,50), b +12,64 mV (eski +23,41; incelemede belirtilmemişti), c +27,87, d +145,22, e +71,04 mV. Yeni `start_guarantee_status()`: G dışı terimler (Hint maks yok, REF uzun dönem 400 ppm, REF TC ekstrapolasyonu, I_Q·R, REF termal histerezis) ayrı tabloda; sonuç `NOT_GUARANTEED_POSITIVE_UNDER_ASSUMPTIONS`. Başabaş: Hint_max 7,28 mV; ek REF hatası 338 ppm (a). Yalnız yeniden merkezleme +6,73 mV'tan iyi değil (mevcut değerler zaten optimum). Seçenekler: O1 REF hatası ×0,5 → +33,47 mV; O2 oran eşleşmeli direnç ağı → +63,48 mV; O3 ikisi → +84,86 mV. **Hiçbiri uygulanmadı** (kullanıcı/donanım kararı) | 4254a5d (testler), a0dea91 (bütçe + deck'ler), 0dcf9e1 (koşu); `uvlo-budget.json` → `start_guarantee`; BUDGET.md §3a | **Düzeltildi (VIO); 20 V başlatma garantisi AÇIK P0 bloklayıcı** |
| W2-P0-2 | P0 | INFO durumları CI'da fail-open (H1/H2 INFO'da uygulanmıyor; eksik ölçüm geçiyor) | **Doğrulandı.** `tests/test_uvlo_gates.py` eski kodda (f587c60) 4/13 OK; INFO'da 12,5 V O1 ve eksik ölçüm geçiyordu | `verify_uvlo.py` fail-closed: H1 (O1 ≤ 12,0 V) ve H2 (kararlı pencerelerde bus/O1 ≤ 11,1605 V) tüm regresyon dışı durumlara (PASS ve INFO) uygulanır; eksik/sonlu olmayan ölçüm hata; geçersiz `expect` FAIL; bilinmeyen durum türü hata. CI'da testler bütçe adımından önce koşar | 4254a5d; şimdi 13/13 OK; eski kanıt kaydı 4/13 | **Düzeltildi** |
| W2-P1-1 | P1 | R-DIP: kısa diplerden sonra bus 11,1605 V'u aşıyor (11,41249 V; RAW 11,62515; O1 10,97811) | **Doğrulandı** (yeni koşuda aynı: dip0v-200us-typ 11,4125 / 11,6251 / 10,9781 V; dip0v-200us-mbmin 11,3576 V) | H2 gevşetilmedi; aşım normal rejim dışı geçiş olarak raporlanır ama kabul edilmiş sınır değildir. Aşım süresi ölçülmedi. WP3 devri yazıldı (COMP kenetleme / anında EN kesme, RAW akım çekici, genlik+süre kriteri, B-U15) | REQUIREMENTS.md "WP3 devri: R-DIP"; RESULTS.md §5 | **Açık (WP3)** |
| W2-P1-2 | P1 | Kısa dip modelleri silikon değil (TDRV_EN yeniden kurma modellenmedi) | **Kabul.** Davranışsal U10 FET'i dipten ~µs sonra açar; gerçek parça ~50 ms bekleyebilir | Sonuçlar silikon kanıtı olarak sunulmuyor; RESULTS.md §6 ve MODELS.md'de açıkça not edildi. Tezgâh B-U10/B-U15 gerekli | RESULTS.md §6, MODELS.md §4 | **Açık (tezgâh)** |
| W2-P1-3 | P1 | KiCad aktarımı ve tezgâh testleri yapılmadı | **Kabul** | Kurallar gereği `.kicad_*` dosyalarına dokunulmadı; KICAD-TRANSFER.md ve BENCH-TEST.md (B-U1…B-U15) hazır, hiçbiri yapılmadı | — | **Açık** |
| W2-P2-1 | P2 | Kaynak izi: doğrulama HEAD bfec691'de kirli ağaçta yapıldı; 73/75 hash eşleşti | **Doğrulandı.** Eşleşmeyen 2 dosya öneri manifestleri dışındaki baseline model dosyalarıydı | Tam koşu ve doğrulama temiz paket girdileriyle HEAD a0dea91'de yeniden yapıldı (2026-10-25 11:24:55–11:37:02 TSİ). `uvlo-verify.json` artık `package_inputs_dirty` (WP2 dizini, results/ hariç) alanını taşır: **false**. Manifest yeniden üretildi, `sha256sum -c` OK | 4254a5d, 0dcf9e1; MANIFEST-SHA256.txt | **Düzeltildi** |

### Yeni koşu (0dcf9e1, deck'ler a0dea91)
- ngspice-44.2, `-j 7`, 58/58 deck tamamlandı (rc 0). `verify_uvlo.py` exit 0: 52 PASS, kabul FAIL yok, eksik yok, 4/4 regresyon beklenen FAIL, 7 INFO (hepsi H1/H2 kapısından geçti).
- O1 anlık tepe (tüm kabul/INFO): 11,170 V (≤ 12,0 V, pay +0,830 V).
- Kararlı pencerelerde (PRE/RUN/POST) bus maks 11,0314 V (≤ 11,1605 V, pay +0,129 V).
- En kısa açılış gecikmesi 77,8 ms (≥ 60 ms); FET ↑ → EN ↑ en dar 37,9 ms.
- Bütçe regresyonları beklenen FAIL: C2 −0,1117 V, yanlış Rb −0,3599 V, yanlış Rx −0,1025 V.

### Karar (Tur 1 sonrası)
WP2 **tamamlanmadı**. Açık bloklayıcı: 20 V başlatma garantisi (W2-P0-1, G dışı terimler). Açık: R-DIP (WP3), silikon/tezgâh doğrulaması, KiCad aktarımı. Tasarım değişikliği (O1–O3) kullanıcı onayı bekliyor.

## Tur 2 (inceleme yorumu 6395614957, WP1 Tur 8 ile birleşik; HEAD `f923347`)
Bulgular teknik olarak tek tek değerlendirildi (otomatik kabul yok); her doğrulayıcı/CI bulgusu önce eski kodda testle yeniden üretildi (`f923347`: 4/31 test geçti, kayıt `results/tur2-tests-on-f923347.txt`). Hiçbir sınır gevşetilmedi, hiçbir test silinmedi, KiCad/ana BOM değişmedi. Simülasyon fiziksel ölçüm değildir.

| ID | Önem | Bulgu (özet) | Doğrulama | Yanıt | Commit | Durum |
|---|---|---|---|---|---|---|
| UVLO-01 | P2 | Hint/IN+ bias ve TMUX kaçağı tek işaret değişkenini paylaşıyor | **Doğrulandı** | Bağımsız işaretler: 12 eksen, 2^12 = 4096 köşe. Marjlar değişmedi (a +6,73, b +12,64, c +27,87, d +145,22, e +71,04 mV) | 57af63b | **Düzeltildi** |
| UVLO-02 | P0 | Başlatma garantisi hükmü doğru ama açık; O3 en güçlü yön; REF5040IDGKT aday; TLV3602 araştırılmalı | **Kabul** | O3 aday varyantı gerçek parçalarla yeniden bütçelendi (BUDGET.md §3b): U23 REF5040IDGKT + ACAS 0606 AT DF grade U (N1, N2), Rx ERA-3ARB; a **+73,91** / b **+70,28** / c +75,54 / d +251,37 / e +182,14 mV. Durum yine `NOT_GUARANTEED_POSITIVE_UNDER_ASSUMPTIONS` (REF5040 uzun dönem + lehim kayması, TLV3202 Hint sınırsız). 43 `o3-` deck + regresyon (Rb 5,23k −0,3013 V FAIL). TLV3602 önerilmedi (VCM koşulu ~3,37 V'ta geçerli değil, 7 mA/kanal). Uygulama kullanıcı/donanım kararı | 873a94a, a2388d1 | **Açık P0 (garanti); O3 aday, uygulanmadı** |
| UVLO-03 | P0 | V_f ve başlatma gecikmesi eksik ölçümde atlanıyor | **Doğrulandı** (eski kodda testler FAIL) | `judge()`: durum türüne göre zorunlu, sonlu ölçüm; OUTA_R1 / VIN_AT_SHUTDOWN eksik/NaN/Inf → FAIL. Yeni testler eksik/NaN/Inf yollarını kapsar | 5911cdb | **Düzeltildi** |
| UVLO-04 | P0 | CI eski loglarla geçebilir | **Doğrulandı** | WP2 `uvlo` işinde kurulum hatası ölümcül (`|| true` ve `continue-on-error` kaldırıldı; WP1 `o1-ovp` işi değişmedi); `run_uvlo.py` koşu öncesi eski log/manifesti siler, ngspice yoksa hata manifesti yazar; manifest `run_id`, `git_head`, `cases_sha256`, deck/log hash'leri, `runner_exit_code` taşır; `verify_uvlo.py --run-id` CI'da manifest HEAD = checkout HEAD ister, aksi halde paket girdisi farkı yoksa kabul eder | 5911cdb | **Düzeltildi** (CI'da yeni koşu henüz gözlenmedi) |
| UVLO-05 | P0 | 60 ms kuralı kısa dip yeniden başlatmada uygulanmıyor | **Doğrulandı** | Kapı eklendi (VIN-OK → EN ≥ 60 ms, kabul + INFO; FET-önce-EN ayrıca). Gerçek koşuda **FAIL**: C3 300 µs typ 15,90 / mbmin 1,39 ms, 250 µs typ 0,00 ms; O3 300 µs mbmin 37,56, 250 µs typ 38,63 / mbmin 24,33, 200 µs (INFO) 0,00 ms. Verify exit 1. Zamanlayıcı CTT kısa dipte sıfırlanmıyor → yeni tasarım P0 | 5911cdb (kapı), a2388d1 (koşu) | **Açık P0 (tasarım)** |
| Kanıt denetimi | – | run-manifest HEAD kaydetmiyor | **Doğrulandı** | Manifest artık `git_head`, `run_id`, `started/finished_utc` taşır | 5911cdb | **Düzeltildi** |
| UVLO-06 | P1 | R-DIP süresi bilinmiyor; geçici tarama önerisi | **Kabul** (öneri olarak) | Ölçümler deck'lere eklendi; **geçici, rapor amaçlı** tarama (≤ 11,50 V, ≤ 1 ms, ≤ 5 ms dönüş), gereksinim değişikliği değil. Sonuç: C3 3 FAIL (200 µs typ 11,41426 V / 18,1 µs üstte / dönüş 10,32 ms; 200 µs mbmin 11,35498 V / 42,24 ms; 250 µs mbmin 11,34552 V / 81,52 ms), O3 16/16 PASS (O3'te bu dipler yeniden başlatmaya düşüyor, R-DIP çözülmüş sayılmaz) | 5911cdb, a2388d1 | **Açık (WP3)** |

### Yeni koşu (a2388d1; girdi HEAD 873a94a)
- `box-tur2-20261025T1230`, 12:30:57–13:01:03 TSİ, ngspice-44.2, 101/101 rc 0. `verify_uvlo.py` **exit 1**: 86 PASS, kabul FAIL 6 (hepsi 60 ms dip kapısı), eksik 0, 5/5 regresyon beklenen FAIL.
- O1 tepe maks: C3 11,16998 V, O3 10,99836 V (≤ 12,0). Kararlı bus maks: C3 11,03144 V, O3 10,99517 V (≤ 11,1605).
- En kısa soğuk açılış: C3 77,74 ms, O3 77,81 ms. Rampdown kapanma VIN min: C3 18,012 V, O3 18,073 V.

### Karar (Tur 2 sonrası)
WP2 **tamamlanmadı**. Açık P0: 20 V başlatma garantisi (O3 ile marjlar ~10× arttı ama sınırsız terimler kaldı), kısa dip 60 ms kapısı (zamanlayıcı sıfırlama). Açık: R-DIP (WP3), silikon/tezgâh (B-U), KiCad aktarımı, ACAS sipariş kodu/stok doğrulaması.
