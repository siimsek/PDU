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
