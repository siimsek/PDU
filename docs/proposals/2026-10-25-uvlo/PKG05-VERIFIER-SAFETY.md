# PKG-05 — UVLO verifier güvenli kilitli koşu seçimi

Tarih: 2026-11-05 (Europe/Istanbul). Dal: `wp/baseline-2026-10-24`. **Yalnız doğrulayıcı güvenlik alt paketi tamamlandı; tam verifier entegrasyon kapısı AÇIK.** Yeni ngspice koşusu veya ürün kabulü yok.

## İspatlanmış ön-hata

`verify_uvlo.py` üzerinde `--run-id ID` seçimi, `results/runs/ID` yoksa **sessizce eski `results/logs` ve `results/run-manifest.json` yollarına geri dönüyordu**. Ardından doğrulayıcının varsayılan yazma hedefi eski ve depoda izlenen `results/uvlo-verify.json` olarak kalıyordu. Çıktı üretme aşamasına ulaşan bir çağrı tarihi kanıtı yeniden yazabilirdi; kod yolunun güvenli olduğu varsayılamaz. Yabancı/simgesel bağlantılı dizin için de doğrulayıcı tarafında açık bir ret yoktu. Bu davranış P0 elektrik kabul hatası değil, **P1 kanıt bütünlüğü/güvenli çalıştırma kusurudur**.

## Uygulanan düzeltme

- `test_pkg05_run_selection.py` **önce commit**: `25c59f5a`. Bulunmayan run-id, manifest/log/staged eksikliği, kötü ID, symlink kök/manifests/staged/çıktı hedefi ve geçerli izolasyon.
- `verify_uvlo.py` commit: `53aeddff`. Yeni `select_locked_run(ID)` yalnız geçerli `results/runs/ID` yolunu seçer; ilgili `results`, `runs`, run kökü, log/staged, manifest ve verifier çıktısındaki symlink'leri reddeder. Seçim başarısızsa **exit 2** ile `LOCKED_RUN_PRECHECK` raporlar, eski sonuçlara **geri düşmez ve hiçbir yazma işlemi yapmaz**.
- `test_locked_verifier.py` için eklenen tamamlayıcı entegrasyon negatif testi: `66c39e68`. Olmayan ID çağrısının gerçek `verify_uvlo.py` sürecinde exit 2 olması ve tarihsel çıktı sentinel'ının değişmemesi beklenir. **Henüz çalıştırılmadı** (tam özel repo klonu yok).
- `PKG02-PROTOCOL-LOCK.json` verifier Git blob SHA-1 yenilemesi: `2c1dcffd`; 259 deck ve öteki kaynaklar sabit.

## Gerçek yürütülen testler ve sınırları

Yerel container'da çalıştırıldı:

| Sınama | Sonuç | Kapsam |
|---|---:|---|
| `test_pkg05_run_selection.py` | **9/9 PASS** | Yerel eşdeğer test dosyası ve GitHub'a yazılan helper ile aynı kaynaklı **izole helper**; **tam doğrulayıcı değil** |
| `test_study_integrity.py` | **27/27 PASS** | PKG-01 testi, Decimal/provenance yardımcı modülü |
| `test_locked_runner.py` | **9/9 PASS** | PKG-03 yapay 259 deck, sahte ngspice |
| `test_verifier_provenance.py` | **7/7 PASS** | PKG-03 tarihsel `provenance()` işlevinin çıkarılmış kopyası; tam doğrulayıcı değil |
| **Tam `test_locked_verifier.py`** | **KOŞULMADI** | Güncel `verify_uvlo.py` özel depo çalışma ağacı bu container'da yok |
| **Gerçek ngspice kabul koşusu** | **KOŞULMADI** | `ngspice` çalıştırıcısı yok; kabul kanıtı yok |

Testlerde eski kanıt dosyaları değiştirilmedi; izole çalışma dışındaki kullanıcı bilgisayarına erişilmedi. GitHub üzerinde **25/25 kilitli girdi ve 259/259 deck blob SHA eşleşmesi**, yeni verifier commit'i sonrası yeniden doğrulandı. Bu kontrol Git blob SHA-1 karşılaştırmasıdır; fiziksel doğrulama değildir.

## Açık işler

1. GitHub'a eklenen **tam** `test_locked_verifier.py` (artık 8 test), `test_pkg05_run_selection.py` (9 test) ve eski UVLO testlerinin gerçek, temiz depo ağacında entegrasyon yürütmesi; testin **dosyayla birebir aynı** sürümünün kullanıldığı da SHA ile gösterilmeli. Tam entegrasyon **kapanmadı**.
2. `verify_uvlo.py --historical` geçmiş `results/uvlo-verify.json` dosyasına yazabilir; **tarihsel modun varsayılan salt-okunur çıktısı** ayrıca test-önce düzeltme gerektiriyor. Bu turda davranışı değiştirilmedi.
3. İzole `--run-id` doğrulamasının **gerçek** 259 Gear/100 ns sonuçlarında ve 23 beklenen regresyonda sınanması; 0 missing/abort koşulu. GitHub Actions kapalı.
4. Tam 20×2 tarihsel yeniden değerlendirme **6/20** (yalnız Decimal düzeltmesi). **6 farklı vakada 9 abort** ve O3 POST_O1_AVG farkı açık; 50/25 ns yakınsama yapılmadı.
5. Elektrik mimari sorunlar: M3 53 ek negatif, iki büyük negatif; WP1 dört ESL; G28; U27 CLR#; O3 sürekliliği; Bpath güç akışı — açık.

**Karar:** Kod koruma alt paketi uygulandı; **verifier entegrasyonu = AÇIK, WP1/WP2 kabul = HAYIR, merge = HAYIR, üretim/tezgâh doğrulaması = YOK.**
