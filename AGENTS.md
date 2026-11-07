# AGENTS.md — bu depoda çalışan ajanlar için kurallar

Önce [`docs/START-HERE.md`](docs/START-HERE.md) dosyasını oku (≤1 sayfa). Repo dili Türkçe; kod yorumları İngilizce olabilir.

## Okuma bütçesi
- Giriş paketi: `docs/START-HERE.md`, bu dosya, ilgili `reports/g2/*.md` başlığı.
- **Gerekmedikçe okuma:** `archive/**` (yalnız `archive/INDEX.md` yeter), `reports/g2/sim/**`, `reports/g1/sim/**`, `reports/g1/*.json`, `hardware/_datasheets/`, `*.log`, `*.net`, `*.kicad_*`.
- Büyük JSON'u tümden okuma; `python -c` ile ilgili anahtarı çek.

## Kanıt kuralları
- Etiketler: **HESAP** / **DATASHEET(sayfa)** / **SİM** / **VARSAYIM** / **AÇIK**. Simülasyon fiziksel kanıt değildir.
- Kriterler gevşetilmez: O1 ≤12.0 V; kararlı bara ≤11.1605 V; yük adımında bara ≥10.78 V; U3/U4 IN <30 V.
- FAIL silinmez; tamamlanmayan koşu PASS sayılmaz; eski deck/log `-attemptN` veya `archive/` altında kalır.
- MPN, stok, fiyat, datasheet değeri **uydurma**. Okunamayan belge → "doğrulanamadı" + `reports/g3/USER-DECISIONS.md`.
- Her yeni hesap iki bağımsız yolla, farkı raporlu, pytest'li (`analysis/g2/test_*.py` örnek).
- Tipik değer garanti gibi kullanılmaz; kullanılıyorsa "koşullu" yazılır.
- Aynı araç hatası 2 denemede aşılmazsa dur, "kanıt yok" yaz, sonraki kaleme geç.

## Yasaklar / kullanıcıya bırakılanlar
- `*.kicad_*` dosyalarını değiştirme, taşıma (KiCad fazı ayrı). `git diff --name-only a1dbeeb..HEAD | grep -i kicad` boş kalmalı (belge adları hariç `\.kicad_`).
- force push, rebase/reset ile geçmiş yeniden yazma, `main`'e doğrudan push/merge, uzak dal silme, PR merge/kapatma yok.
- Kanıt silme yok: temizlik = `git mv archive/...` + `archive/INDEX.md` + `archive/MANIFEST-SHA256.txt`.
- `archive/g1-tooling/generate_g1_reports.py` çalıştırılmaz (G1 raporlarının üzerine eski içerik yazar).
- Gizli anahtar ve kişisel yol sızdırma.

## Dosya düzeni
- `analysis/g2/` — G2 hesap/sim kodu (params → design → protection/power/loop/routing/bom/sim_runner).
- `analysis/*.py` — G1 araçları (testleri hâlâ koşar; veri `reports/g1/`).
- `design/` — netlist, BOM, şema özeti. `reports/g1|g2|g3/` — aşama raporları. `archive/` — taşınmış kanıt.
- `simulation/` — yalnız G1 baseline O1 regresyon deck'i ve `pdu_calc` girdileri (14 dosya).

## Çalışma akışı
1. `git status -sb`; kirliyse sahipliğini kontrol et.
2. Değişiklikten sonra `python -m pytest -q`; hesap/sim değiştiyse `python analysis/run_all.py`.
3. Aşama sonunda ilgili `reports/gN/PROGRESS.md` güncelle, commit et (dal: aşamanın `wp/...` dalı).
4. Commit mesajı sonunda istenen attribution satırı.
