# PKG-07 — Kilitli runner symlink kaçışı: bağımsız yeniden üretim ve düzeltme

Tarih: **2026-11-05**, Europe/Istanbul. Çalışma dalı `wp/baseline-2026-10-24`. İlk doğrulanan HEAD: `8c633d06b8805e6bc86505fa8bf1441189188f18`. PR #1 **draft**; CI kullanıcı tarafından devre dışı; **gerçek ngspice çalıştırılmadı**.

## Doğrulanan hata ve etkisi

`simulation/proposals/2026-10-25-uvlo/run_uvlo.py` eski blob SHA-1: `8a43e3cb5801ac9625e6e420a97733224b86e2ed`. Bu blob, yerel test edilen orijinal `/mnt/data/pdu-pkg03/run_uvlo.py` ile birebir eşleşiyordu.

`clean_status()` kasıtlı olarak `results/runs` yolunu Git dirty denetiminden çıkarıyor. Bununla birlikte `run_uvlo.py`, bu yolun bir sembolik bağlantı olup olmadığını **kontrol etmiyordu**. Yerel sentetik fikstürde `results/runs -> outside-evidence` symlink'i kuruldu. Tek bir `test_symlinked_run_root_fails_before_outside_writes` negatif testi, runner'ın **259 sahte deck'i dış konumdaki `outside-evidence/safe-a` içine yazıp yanlışlıkla exit 0** döndürdüğünü gösterdi. Test **RED (1 FAIL)**. Bu, geçmiş kanıtın depodan dışarı yazılması ve yanlış konumda başarı görünmesi riskidir. Elektriksel simülasyon kanıtı değildir.

Ayrıca `results/runs/safe-a` hedefi mevcut olmayan (**dangling**) sembolik bağlantıysa `Path.exists()` bunun varlığını algılamaz; kanıt akışı güvenli ön koşuldan geçmemelidir.

## Test-önce çözüm

1. İki yeni regresyon testi eklendi: `test_symlinked_run_root_fails_before_outside_writes`; `test_dangling_run_id_symlink_fails_before_lock_or_writes`. Test commit'i: `c3ee27f21ceb09c2b6cd95625a7e0b86b0dfaad4`.
2. Runner `results`, `results/runs` ve `results/runs/<run-id>` için `is_symlink()` kontrolü yapıyor; klasör dışı/dangling hedefte **exit 3**, işlem başlamadan ve geçmiş kanıta yazmadan çıkıyor. `results/runs` dosya fakat dizin değilse de kapalı hata. Klasör açıldıktan sonra kilit oluşturulmadan ikinci symlink denetimi yapılıyor.
3. Kod commit'i: `09379a3146290e200f3bcdcd311ec379dcece4a4`. Yeni `run_uvlo.py` Git blob SHA-1 **`f324db9e2e66909a9b79b1116a4b1765f782a682`**, SHA-256 **`676d41ef1b72e95771e34ed26f54e23ecdf803fcdd432ad0df3cdbaf099cd5f6`**. Yeni `test_locked_runner.py` Git blob SHA-1 **`02e68ca35fe830089b408cd9a39cdc26da81fc4a`**, SHA-256 **`c295fd8ffefe5fa19fee6005e4c697903ecc9e4abc2cccaa25478a5470646d32`**. GitHub'dan tekrar okunan blob SHA'ları yerelde test edilen dosyalarla **tam eşleşti**.
4. Yerel Python 3.13.5 ortamında yeni runner+test dosyası üzerinden tüm testler **11/11 PASS**. Yeni negatif testlerde dış klasörün yalnız sentinel içerdiği ve kilidin bırakılmadığı doğrulandı. Testte kullanılan ngspice ikilisi **sahte test stub'ı**; gerçek ngspice veya elektriksel kabul yok.
5. Protocol lock yeniden bağlandı: `PKG02-PROTOCOL-LOCK.json` yalnız runner blob kimliğini güncelledi ve test provenance notu eklendi. GitHub üzerinden **259/259 deck ve 25/25 kaynak girdi** blob SHA-1 eşleşmesi ayrıca tekrar doğrulandı. Önceki loglar, 259 vaka sınırları ve ölçüm politikaları değişmedi.

## Bu oturumda yerel test kapsamı

| Gerçek yürütülen test | Sonuç | Nitelik |
|---|---:|---|
| `pdu-pkg07/test_locked_runner.py` (GitHub blob ile eş) | **11/11 PASS** | 259 sentetik deck, sahte ngspice, izolasyon/abort/negatif |
| `pdu-pkg06/test_fixture_summary.py` (GitHub blob ile eş) | **6/6 PASS** | stdout summary parser |
| `pdu-pkg01/test_study_integrity.py` | **27/27 PASS** | Decimal/provenance yardımcı modülü |
| `pdu-pkg03/test_verifier_provenance.py` | **7/7 PASS** | **ayrılmış** provenance, tam verifier değil |
| `pdu-pkg05/test_pkg05_run_selection.py` | **9/9 PASS** | **ayrılmış** run-path helper, tam verifier değil |
| `pdu-pkg05b/test_pkg05_historical_readonly.py` | **8/8 PASS** | **ayrılmış** output helper, tam verifier değil |
| **Toplam** | **68/68 PASS** | Yerel birim/sentetik test, ürün kabulü değil |

Bu çalışmada tam `verify_uvlo.py` + güncel tüm `tests/test_uvlo_tur*.py` ve `test_locked_verifier.py` **aynı temiz Git checkout'ta çalıştırılamadı**. Container'ın `github.com` DNS erişimi yok, özel repo klonu yok ve `ngspice` kurulu değil. GitHub connector ile dosyaların bağımsız blob/HEAD kontrolü yapılabildi, ancak bu connector yerel test sürecini otomatik kurmuyor. Gerçek tam entegrasyon **AÇIK**, hiçbir PASS uydurulmadı.

## Değişmeyen karar ve açık kapılar

- WP2 tarihsel `tur5-6e150c8`/yeniden doğrulama: **161 PASS / 69 FAIL / 6 eksik**; bu turda yeni 259-deck kabul çalıştırılmadı.
- Eski 20×2 `num-study-tmax100n`: hash doğrulamalı Decimal yeniden analiz **6/20**, **6 farklı vakada 9 yöntem abort**; 50/25 ns yakınsama yok; O3 süreklilik açık.
- WP1 dört ESL koşusu eksik. M3 negatif lag (0…1.000 µs kapsayıcı, negatif tüm değerler FAIL), H1 12.0 V, H2 11.1605 V, M1 60 ms, M4 6 V değişmedi.
- Koşu boyunca tek yazar, temiz HEAD, korunan geçmiş çıktılar ve **gerçek ngspice** hâlâ kabul ön koşulu. PR yorumunu ön onay olmadan atma, CI'yi açma, main'e yazma, merge/üretim onayı verme: **YOK**.

**Sonraki bağımlılık (PKG-08):** `verify_uvlo.py` tam entegrasyonunu **birebir tam depo checkout'unda** çalıştır; güncellenen eski fikstürlerin gerçek FAIL sebeplerini düzelt; ardından kilitli koşu için hazır ortam varsa çalıştır. Çıktı izolasyonu regresyonu korunmalı.
