# PDU PR #1 — bağımsız çalışma/durum kaydı

Son kontrol: 2026-11-05 (Europe/Istanbul). Dal: `wp/baseline-2026-10-24`. PR: https://github.com/siimsek/PDU/pull/1 (draft). Ana inceleme: https://github.com/siimsek/PDU/pull/1#issuecomment-6666773349. Önceki yanıt: #issuecomment-6420218157.

## Değişmez çalışma kuralları

- Tek yazar: yalnız bu dalda, `main`/merge yok. PR yorumunu kullanıcıya Türkçe taslak sunmadan gönderme.
- KiCad kaynak üçlüsü, ana BOM, baseline sonuç/netlist ve `simulation/pdu-behavioral.lib` salt okunur; teklif kopyaları dışında model değişikliği yok.
- Kabul simülasyonu sırasında commit/girdi değişikliği yok; kesintide önce süreç ve logları incele, tekrar koşu başlatma.
- CI `proposal-ngspice` kapalı, açılmayacak. Yerel/sentetik test ile ngspice kabul koşusunu ayır.
- H1 O1 peak ≤12.0 V; H2 normal PRE/RUN/POST bus/O1 ≤11.1605 V; Vf≥18.0 V; M1≥60 ms (65 ms hedef); M3 0…1.000 µs kapsayıcı (negatif/NaN/Inf/eksik FAIL); M4 EN ↑ anında VGS≥6 V. R-DIP yalnız report-only.
- Yeni kabul koşusu yok; tarihsel sayılar mevcut dosyalara aittir. Fiziksel tezgâh ölçümü yok; WP1/WP2 açık, üretim/merge onayı yok.

## Son uygulanan alt paket: PKG-05B — historical salt-okunur doğrulama (tam entegrasyon AÇIK)

- Başlangıç uzak HEAD: `646b914801883d916bb5461405bdaed195737c6f` (PR #1 draft; main değişmedi).
- Somut hata: `verify_uvlo.py --historical`, normal akışın sonunda `VERIFY_OUTPUT.write_text(...)` üzerinden repo tarafından izlenen `results/uvlo-verify.json` dosyasını yeniden yazıyordu. `--run-id` için ayrı klasör seçimi bundan farklıdır.
- Önce test: `test_pkg05_historical_readonly.py` eklendi (commit `b0dac61d`); yerel eski çıkarılmış modülde **8/8 beklenen ERROR** (eksik `write_verification` işlevi). Düzeltme: `verify_uvlo.py` `write_verification(mode, artifact)`; historical modunda **hiçbir çıktı dosyasına yazma yok** (özet stdout), yalnız doğrulanmış izole kabul modunda `open('x')` ile ilk kez yazma var; mevcut rapor/symlink üzerine yazılamaz. Kod commitleri: `18dec5f5`, newline düzeltmesi `7d864fbe`.
- **Bu turda gerçekten çalıştırılan yerel testler:** yeni artifact-helper 8/8 PASS; eski izole run-id seçici 9/9; PKG-01 integrity 27/27; PKG-03 sentetik runner 9/9 ve ayrılmış provenance 7/7. Toplam **60/60 yerel birim/sentetik PASS**. Yeni testin Github Git blob SHA-1'i **9e6126870eb4f998000f7486739f8a25123eadba** ile yerel test dosyası birebir aynı. **Tam `verify_uvlo.py` doğrudan import/CLI testleri çalıştırılamadı**: container'da tam özel depo klonu yok, GitHub ağına doğrudan DNS erişimi yok. Yeni helper'ın yerel kopyası tam verifier değil; 60/60 tam entegrasyon olarak ifade edilmeyecek.
- Kilit yenilendi: `PKG02-PROTOCOL-LOCK.json` içindeki verifier Git blob **e0e3d7270209f0aed58c938ed813745806a5fae2**; **25/25 kaynak girdisi ve 259/259 deck** GitHub kaynak blob eşleşmesi. Hiçbir eski ngspice logu, ana model/baseline/BOM veya KiCad dosyası değişmedi.
- **Açık entegrasyon sorunu:** `tests/test_uvlo_tur2.py` ve `tests/test_uvlo_gates.py` gibi tarihsel sentetik fikstürler `--run-id` ile eski `results/logs` şemasını ve eski `uvlo-verify.json` çıktısını bekliyor; `tests/test_uvlo_tur5.py` V53b tarihi modu JSON çıktısından okuyor. Bu test altyapısı güvenli izole koşu ve yeni historical stdout davranışına güncellenmeli; mevcut eski testlerin PASS olduğu **iddia edilmiyor**.
- **Yeni simülasyon yok**; WP2 gerçek tarihsel 161 PASS / 69 FAIL / 6 incomplete, önceki yeniden analiz 6/20; 9 yöntem abort ve O3 farkı açık. WP1 4 ESL eksik. CI kapalı, merge yok, fiziksel kabul yok.

## Önceki alt paket: PKG-05A — locked verifier fail-closed (tam entegrasyon açık)

- Kaynak HEAD `3963f5973490e45d4d3e99c425cd20249a8c0a15`. Rapor: `docs/proposals/2026-10-25-uvlo/PKG05-VERIFIER-SAFETY.md`.
- **Bulgu:** `verify_uvlo.py --run-id ID` mevcut olmayan izole dizin için sessizce eski `results/logs/` ve depodaki `uvlo-verify.json` hedeflerine düşüyordu. Bu yazma/kanıt bütünlüğü riski test-önce düzeltildi.
- Test commit'i `25c59f5a`; kod `53aeddff`; tam verifier CLI negatif testi `66c39e68`; kaynak kilidi `2c1dcffd`. Artık olmayan/eksik/symlink'li koşu dizini **exit 2 / LOCKED_RUN_PRECHECK**, eski dosyaya geçiş/yazım yok.
- **Çalışan yerel test:** yeni izole seçim işlevi **9/9**, PKG-01 integrity **27/27**, sahte ngspice locked runner **9/9**, çıkarılmış provenance **7/7** PASS. Bunlardan **hiçbiri tam `verify_uvlo.py` entegrasyon koşusu değildir**; repo içindeki `test_locked_verifier.py` 8 test ve yeni testin birebir GitHub dosyası henüz tam depoda çalıştırılamadı.
- GitHub statik: **25/25 girdi ve 259/259 deck kilit SHA-1 eşleşmesi**. Yeni ngspice simülasyonu / regresyon koşusu / fiziksel test yok. Tarihsel WP2 **161 PASS / 69 kabul FAIL / 6 eksik**; sayısal yeni yorum **6/20**, 9 abort açık; WP1 4 ESL açık.
- **Açık:** `--historical` varsayılan yazma hedefi tarihsel `uvlo-verify.json`; salt-okunur moda geçiş için ayrı negatif test/düzeltme. Tam verifier entegrasyon kapısı ve bütün ürün P0'ları açık. CI kapalı, main/merge yok.

## Önceki iş paketi: PKG-04 — SHA-256 kaynaklı 20×2 Decimal yeniden analiz (yeni simülasyon yok)

- Kaynak HEAD `db6237a955f4314bc91a4f274f91491b7de9b4e3`; rapor commit'i `80bd8cff5c22ecae7322da776e74b27254167733`. Rapor: `docs/proposals/2026-10-25-uvlo/PKG04-DECIMAL-REANALYSIS.md`.
- Eski `num-study-tmax100n` **40/40 ngspice log SHA-256**, **20/20 kaynak deck SHA-256**, ölçüm/metrik, `missing/no_event` bütünlük denetimi başarılı; hiçbir eski log/girdi/sonuç değiştirilmedi. Ham basılı ondalık ve `.meas` türü ile tam ondalık kapsayıcı karşılaştırma: **4/20 → 6/20** (yeniden analiz, yeni simülasyon değil).
- Yalnız `dip0v-10us-mbmin-tmin` ve `dip0v-100us-mbmin-tmin` için `EN_R1/EN_RLAST` farkı tam `1e-7 s` olduğundan eski float FAIL, Decimal **PASS**; `resolution-sensitive` olarak açık.
- **6 farklı vakada 9 gerçek yöntem abort'u**, diğer yöntem tolerans farkları ve O3 50 µs mbmin `POST_O1_AVG` Gear 2.769516 V / Trap 0.2660205 V (2.5034955 V) değişmedi. Sonuç **6 PASS / 14 NOT-PASS**; protokol kabulü yok.
- Yerel tekrar testleri: `test_study_integrity.py` **27/27**, sahte solver `test_locked_runner.py` **9/9**, ayrılmış provenance `test_verifier_provenance.py` **7/7** PASS. **Tam `verify_uvlo.py` entegrasyonu çalıştırılamadı**: özel repo klonu/gerçek ngspice erişimi yok. 259 Gear kabul ve 23/23 regresyonun yeni koşusu yok.
- Tarihsel UVLO 161 PASS/69 kabul FAIL/6 incomplete; WP1 4 ESL incomplete değişmedi. WP1/WP2 P0 bloklayıcıları, R-DIP politikası, fiziksel test ve üretim kapıları açık.

## Önceki iş paketi: PKG-03 — güvenli UVLO runner ve izole kanıt (yeni simülasyon yok)

- Değişiklikler: `run_uvlo.py` önce temiz HEAD, 259/259 kilitli kaynak blob ve 25 kritik girdi SHA-1, ngspice -v kontrolü; yalnız `--run-id` ile ayrı ve **üzerine yazılamayan** `results/runs/<ID>` dizini, atomik `.active-acceptance.lock` ve kesintide saklanan durum. Tam 259 Gear deck'e aynı `.tran ... 100n`; kaynak deck/baseline/ana BOM değişmiyor. Her aşamada kaynak/staged/log SHA-256; eksik/abort/dirty/interruption fail-closed.
- `verify_uvlo.py` eski `--historical` kaynaklarını korurken `--run-id` ile izole manifest/log/staged içeriğini denetler: `COMPLETE`, 259, 100n/Gear, runner+kilit SHA-256, kaynak/staged/çıktı SHA-256, staging dönüşümünün yalnız tmax ve include yoluyla sınırlı olması. Yeni `.gitignore` yalnız `results/runs/` çıktısını dışlar.
- Runner doğrulaması: `test_locked_runner.py` **9/9 PASS**, yerel sentetik Git fixture ve **sahte ngspice**; test dosyası ve runner GitHub blob SHA'sı test edilen yerel kopyalarıyla eşleşti. Testler: tüm 259 yapay deck, tarihsel log korunumu, tmax dönüşümü, aynı run-id ret, abort, yok ngspice, dirty/untracked, tamper, eksik deck, tek-yazar lock ve geçersiz ID.
- Doğrulayıcı provenance fonksiyonunun GitHub'dan alınan bölümüyle yerel sentetik fixture **7/7 PASS** (temiz, RUNNING, tamper staged/log, solver, eksik vaka, girdi değişikliği). Tam `verify_uvlo.py` koduyla depoya eklenen `test_locked_verifier.py` **henüz çalıştırılamadı**. Bu 7 sayısı tam dosyanın entegrasyon testi olarak sunulmamalı.
- Kod/test commitleri: `bdde5c53` (önce test), `79d158d2` (runner), `cc1543cd` (verifier), `d907f5aa` (lock update), `539295e8` (output ignore), `efc3eb21` (verifier negatif testleri). Manifest/durum commitleri Git geçmişindedir.
- **Önemli açık kapı:** gerçek özel depo klonu + ngspice çalıştırılabilir ortam bu oturumda yok. Gerçek 259 Gear/tmax100n koşusu, tam entegrasyon ve `provenance_consistent=true` henüz doğrulanmadı; 23/23 yeni regresyon tekrarı yok. Mevcut 161 PASS /69 FAIL /6 eksik ve 4/20 tanı tarihsel kaldı. Asıl WP1/WP2 P0 bloklayıcıları açık.

## Önceki iş paketi: PKG-02 — 259 + 20×2 protokol kilidi (yeni simülasyon yok)

- Kaynak HEAD: `1bb0b3a751828f444a54c20edd9155d116a2d985`; kilit commit'i: `1c06266751b276b9cc44a8b0b77f06c428284286`. Dosya: `docs/proposals/2026-10-25-uvlo/PKG02-PROTOCOL-LOCK.json`.
- 259/259 UVLO .cir deck, 259/259 test-case kaydı ve tarihsel `tur5-6e150c8` manifestindeki 259/259 isim **birebir aynı**; 25 ek kaynak/girdi dosyasının Git blob SHA-1'i ve 259 deck'in Git blob SHA-1'i sabitlendi. Git blob SHA-1, simülasyon logunun SHA-256'sı değildir.
- Sayısal 20 sabit vaka × Gear/Trap (40 yöntem koşusu/stage), tüm 20 deck'te tek `.tran`, tek `method=gear` ve 80 `.meas` **statik** doğrulandı. 100 ns → 50 ns → (önceden belirtilen gereksinim oluşursa) 25 ns aynı matris, tekdüze; time Decimal kapsayıcı 100 ns, voltage 5 mV, no-event/missing/abort fail-closed.
- GitHub connector ile kilidin güncel kod/deck girdilerine karşı 8/8 statik kontrolü PASS (kilit commit'i `1c062667` üzerinde); `test_study_integrity.py` yerel tekrar 27/27 PASS. `test_uvlo_tur6.py`, `test_doe_provenance.py` ve tam depo entegrasyonu çalıştırılamadı: erişilebilen ortamda özel depo klonu ve ngspice bulunmuyor.
- Mevcut `run_uvlo.py` eski `results/logs/*.log` ve `run-manifest.json` dosyalarını başlangıçta **siliyor** ve .tran tmax'i tekdüze 100 ns'ye indirmiyor. Bu iki koşul kapanmadan 259-deck çalıştırmak YASAK; tarihsel kayıtlar korunacak. Çalışan ngspice süreci bu container ortamında yok; kullanıcının PC'si erişilebilir değil.
- **Yeni 259, 20×2 veya WP1 13-deck koşusu yok.** Eski 161/69/6 ve 4/20 tarihsel; 23/23 regresyonun yeni koşusu yok. CI kapalı; main/PR draft ve sert kapılar değişmedi.

## Önceki iş paketi: PKG-01 — test altyapısı ve provenance koruması

- `simulation/proposals/study_integrity.py`: Decimal ile ham basılı .meas kıyaslama; tam 100 ns kapsayıcı PASS ve resolution-sensitive işareti; log SHA doğrulamalı tarihsel yeniden çözüm; tüm repoda başlangıç/bitiş HEAD + runner/helper hash + tracked/dirty denetimi; yalnız önceden bilinen, hash'i doğrulanmış **yeni ve izlenmeyen** çıktı loglarına izin.
- `simulation/proposals/2026-10-25-uvlo/num_study.py`: ham ölçümler korunur, eski ölçümler yalnız hash-doğrulanmış logdan yeniden okunur; float sınır kararına son; eski çalışma klasörü üzerine yazma yasağı, yeni `--run-id`; provenance true yalnız gerçek temiz koşuda.
- `simulation/proposals/2026-10-25-o1-ovp/doe-study/doe_study.py`: aynı çıktı/runner bütünlüğü ve immutability; yeni `--run-id` ile geçmiş DOE korunur.
- `simulation/proposals/test_study_integrity.py`: 27/27 sentetik sınır/negatif test **yerel container** ortamında PASS (GitHub'a yazılan test dosyasının blob SHA'sı yerel dosyayla eşleşti). Tam repo testi ve ngspice **çalıştırılmadı** (depo yerel olarak klonlanamıyor, ngspice mevcut değil); yeni `provenance_consistent=true` **kanıtlanmadı**.
- Kod commitleri: `fe55d866`, `e6ed06df`, `4f58ed51`, `e442a25e`. Bu kayıt ve manifest commitleri ayrıca Git geçmişindedir.
- Son tarihsel WP1: `wp1-rev3-tur6` / verify 1766 PASS, 0 kabul değer FAIL, 4 MISSING; 4 ESL açık. Son WP2: `tur5-6e150c8`, 259 deck ve 23/23 tarihsel regresyon; `reverify-t6-ebe56b2` = 161 PASS, 69 kabul FAIL, 6 MISSING (yeni simülasyon değil). 100 ns 20×2 tanı: `num-study-tmax100n` = 4/20; eski 100 ns sınır raporu float hassasiyeti yüzünden yanlıştır.

## İnceleme bulguları (asıl durum / kanıt / sonraki kapı)

| ID | Önem | Durum 2026-11-05 | Son kanıt / ilgili commit | Kapanış için |
|---|---|---|---|---|
| WP1-T13-01 | P0 | AÇIK | `imon-diag-t6`; 4 ESL abort | ε ve model tanısı → sabit A/B/C, 4 ESL + 154 |
| WP1-T13-02 | P2 | KOD DÜZELDİ / KOŞU AÇIK | `e442a25e`; eski DOE JSON provenance yok | temiz yeni A/B/C koşusunda start/end + log SHA |
| WP1-T13-03 | P0 | AÇIK | `doe-study-NUM-U3`: 12.41205/12.41832 V | bağımsız O1 comparator/latch/cutoff ve köşe testleri |
| WP1-T13-04 | P2 | BELGE KAPALI | `RESULTS.md`, 4 MISSING görünür | durum açık şekilde raporlanmalı |
| UVLO-T7-01 | P0 | AÇIK | `reverify-t6-ebe56b2`, 53 ilave negatif M3 | 259 Gear ve ham nedensel kenarlar |
| UVLO-T7-02 | P0 | DECIMAL KOD DÜZELDİ / SAYISAL AÇIK | `4f58ed51`; `num-study-tmax100n` 4/20 tarihsel | 20×2 sabit 100→50→25 ns, 0 abort; O3 sürekliliği |
| UVLO-T7-03 | P0 | AÇIK | `imon-diag-t6`, Bpath −10.417 A | yalnız teklif kopyasında ε/Bpath A/B |
| UVLO-T7-04 | P1 | KOD DÜZELDİ / KOŞU AÇIK | `4f58ed51`; eski JSON `false` | temiz yeni koşuda `true`, negatifte `false` |
| UVLO-T7-05 | P1 | KOŞULLU AÇIK | BUDGET §4d | gerçek BOM / tüm köşeler / 20 V açılış |
| UVLO-T7-06 | P2 | METRİK KAPALI / POLİTİKA AÇIK | R-DIP 179/184; O1 instant 184/184 PASS | report-only ve 5 ekran FAIL'i koru |
| UVLO-T7-07 | P1 | AÇIK | R_total 0.35/0.45 Ω FAIL | 0.25/0.30/0.35/0.45 Ω ortak kapsam |
| UVLO-T7-08 | P1 | AÇIK | mevcut noreset kapsamı yetersiz | 200/225/250/300 µs ve çift darbeler |
| UVLO-T7-09 | P1 | BOM EŞLEMESİ KAPALI / YETERLİLİK AÇIK | `7f6ea62`, `2bd1c9d` | MPN worst-case / pulse SOA / pin |
| UVLO-T7-10 | P0 | AÇIK | G28 davranışsal | gerçek kaynak-referanslı VGS-ready + fail-low |
| UVLO-T7-11 | P0 | AÇIK | U27 PRE#/CLR# eşzamanlı L riski | fiziksel CLR# maskeleme / garantili latch |

## Bir sonraki `devam` için tek iş

**PKG-06 / fixture uyumluluğu ve tam verifier kapısı:** GitHub HEAD/durum/proses kontrolü; eski `test_uvlo_tur2.py`, `test_uvlo_gates.py` ve V53b'nin izole `--run-id` / salt-okunur historical stdout ile uyumsuz beklentilerini önce failing testle gösterip sonra yalnız test fikstürlerinde düzelt. Ürün sınırını, regresyon beklenen FAIL'lerini veya doğrulayıcıyı testleri geçiriyor görünmek için gevşetme. Özel repo tam dosya ağacı ve ngspice varsa gerçek 8+9+mevcut testleri çalıştır; yoksa açıkça sınırlı doğrulama olarak kaydet. Tam entegre doğrulayıcı kanıtı olmadan yeni 259 Gear koşusunu kabul olarak duyurma. Sonrasında M3 ham nedensellik ve 20×2 yakınsama aynı sabit matrisle yürütülecek.
