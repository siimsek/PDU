# PDU PR #1 — bağımsız çalışma/durum kaydı

Son kontrol: 2026-11-05 (Europe/Istanbul). Dal: `wp/baseline-2026-10-24`. PR: https://github.com/siimsek/PDU/pull/1 (draft). Ana inceleme: https://github.com/siimsek/PDU/pull/1#issuecomment-6666773349. Önceki yanıt: #issuecomment-6420218157.

## Değişmez çalışma kuralları

- Tek yazar: yalnız bu dalda, `main`/merge yok. PR yorumunu kullanıcıya Türkçe taslak sunmadan gönderme.
- KiCad kaynak üçlüsü, ana BOM, baseline sonuç/netlist ve `simulation/pdu-behavioral.lib` salt okunur; teklif kopyaları dışında model değişikliği yok.
- Kabul simülasyonu sırasında commit/girdi değişikliği yok; kesintide önce süreç ve logları incele, tekrar koşu başlatma.
- CI `proposal-ngspice` kapalı, açılmayacak. Yerel/sentetik test ile ngspice kabul koşusunu ayır.
- H1 O1 peak ≤12.0 V; H2 normal PRE/RUN/POST bus/O1 ≤11.1605 V; Vf≥18.0 V; M1≥60 ms (65 ms hedef); M3 0…1.000 µs kapsayıcı (negatif/NaN/Inf/eksik FAIL); M4 EN ↑ anında VGS≥6 V. R-DIP yalnız report-only.
- Yeni kabul koşusu yok; tarihsel sayılar mevcut dosyalara aittir. Fiziksel tezgâh ölçümü yok; WP1/WP2 açık, üretim/merge onayı yok.

## Son tamamlanan iş paketi: PKG-01 — test altyapısı ve provenance koruması

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

**PKG-02 / sabit sayısal protokol ve ön koşu denetimi:** İlk olarak uzak HEAD, bu kayıt, yeni süreç/çıktı durumu; sonra 259-deck vakalarını ve 20×2 Gear/Trap giriş listesini kaynak dosyaların hash'leriyle dondur. Yeni temiz bir çalışma kökü üzerinde `test_uvlo_tur6.py`, `test_doe_provenance.py`, `test_study_integrity.py` ve mevcut ilgili testleri doğrula; `--run-id` ile geçmiş kanıtı koru. Ancak **gerçek ngspice ve tüm girdiler mevcutsa** tek koşu başlat; değilse simülasyon sonucu uydurma. Model fiziksel güç akışı tasarımına/deck seçimine henüz geçme. Bütün açık FAIL ve abort'ları koru.
