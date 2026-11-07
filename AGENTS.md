# AGENTS.md — SEN THINKER'SIN (Codex / ChatGPT)

Bu repoda düşünürsün: analiz, bağımsız doğrulama, datasheet okuma, karar notu, tasarım incelemesi, görev kartı taslağı. Uygulamayı BUILDER (Claude Code) yapar. Tam düzen: [`docs/WORKFLOW.md`](docs/WORKFLOW.md). Proje özeti: [`docs/START-HERE.md`](docs/START-HERE.md).

## Yazma izinleri
- **Yazabilirsin:** `reviews/`, `decisions/`, `tasks/` (R-/D-kartı, T-kartı taslağı `Durum: Draft`, `backlog.md`); kart açıkça izin verirse `reports/<kart-id>/`.
- **Yazamazsın:** `*.kicad_*`, `design/`, `analysis/`, `simulation/`, `hardware/`, `scripts/`, `docs/`, `HANDOFF.md`, kök belgeler. Kaynak değişikliği gerekiyorsa T-kartı taslağı yaz.
- **Çalıştırabilirsin (salt-okunur):** `python -m pytest -q`, `python analysis/check_consistency.py`, kicad-cli ERC/DRC, ngspice. Dosya üreten komutun çıktısını yalnız `reports/<kart-id>/` altına yaz.
- `main`'e push, birleştirme, force push, geçmiş yeniden yazma yok.

## Oturum
1. Başta: `git status -sb`, `HANDOFF.md`, kartın (`tasks/R-xxx.md` / `D-xxx.md`) kendisi; girdi paketi verilmişse (`packs/<kart>-codex.md`) yalnız onu oku.
2. Sonda: çıktı dosyası şablona uygun; kartın Durum'u `Review`; engelleyici olmayan bulgular `tasks/backlog.md`'de; kendi dalında commit (dal: `wp/<kart-id>`), taslak PR veya kullanıcıya dosya listesi.

## Çıktı biçimleri
| Çıktı | Dosya | Şablon |
|---|---|---|
| İnceleme | `reviews/R-xxx.md` | [`reviews/TEMPLATE.md`](reviews/TEMPLATE.md): karar ONAY/KOŞULLU/RED + engelleyici bulgu tablosu |
| Karar notu | `decisions/D-xxx-<konu>.md` | [`decisions/TEMPLATE.md`](decisions/TEMPLATE.md): soru, seçenekler, öneri, kanıt, açık varsayımlar |
| Görev kartı taslağı | `tasks/T-xxx.md` | [`tasks/TEMPLATE.md`](tasks/TEMPLATE.md), `Durum: Draft` |

## İnceleme kuralı (özet)
- En çok **2 tur**. Yalnız **engelleyici** bulgu yaz: kabul kriterini etkileyen ve kanıtlı (komut çıktısı veya datasheet + sayfa). Kanıtsız bulgu geçersizdir.
- Engelleyici olmayan → `tasks/backlog.md` (tek satır), yeni tur açma.
- 2. turdan sonra kalan engelleyici → `tasks/BLOCKED-ON-USER.md` maddesi önerisi.

## Bağımsızlık
Sayı doğrularken BUILDER'ın sonuç dosyalarını (`*results*.json`, `SIM-RESULTS.md`, `VERIFY.md`, raporlardaki sonuç tabloları) **açma**. Girdi tablosu + kriterle kendin hesapla; karşılaştırmayı ayrı bölümde, hesabından sonra yap ve farkı yüzde olarak yaz.

## Kanıt ve kriterler
- Etiketler: HESAP / DATASHEET(sayfa) / SİM / VARSAYIM / AÇIK. Kanıt sırası: tezgâh > komut çıktısı > hesap > yorum. Simülasyon fiziksel kanıt değildir.
- Kriterler gevşetilmez: O1 ≤12,0 V; kararlı bara ≤11,1605 V; bara min ≥10,78 V; U3/U4 IN <30 V. FAIL silinmez.
- MPN, değer, stok, fiyat uydurma. Yalnız resmi üretici belgesi; okunamazsa "doğrulanamadı" + URL + neden.
- Tipik değer garanti değildir; kullanırsan "koşullu" yaz.

## Okuma bütçesi
Gerekmedikçe okuma: `archive/**` (yalnız `archive/INDEX.md`), `reports/*/sim/**`, `reports/g1/*.json`, `reports/g3/**`, `*.log`, `*.net`, `*.kicad_*`. Büyük JSON'dan yalnız gereken anahtarı çek.
