# Çalışma düzeni (W0) — üç rol, kart tabanlı, limit-dostu

Kalıcı bağlam repodadır: oturum = kısa prompt + [`HANDOFF.md`](../HANDOFF.md) + bir görev kartı (`tasks/`). Eski düzen: [`archive/docs-legacy/AI-WORKFLOW.md`](../archive/docs-legacy/AI-WORKFLOW.md) (SUPERSEDED).

## Roller ve yazma izinleri

| Rol | Kim | Yapar | Yazabilir | Yazamaz |
|---|---|---|---|---|
| **BUILDER** | Claude Code (Opus/Sonnet/Haiku) | T-kartını uygular: KiCad, betik, SPICE, BOM, test, belge; commit, push, taslak PR | kartın "İzinli yazma yolları"; her zaman `HANDOFF.md`, `tasks/queue.md`, kendi kartının Durum alanı | kart dışı yollar; `main`; `reviews/`, `decisions/` içeriği |
| **THINKER** | Codex (CLI/App/Web), ChatGPT (Web/Work) | analiz, bağımsız doğrulama, datasheet okuma, R-/D-kartı, T-kartı taslağı | `reviews/`, `decisions/`, `tasks/` (kart taslağı, backlog); kart izin verirse `reports/<id>/` | `*.kicad_*`, `design/`, `analysis/`, `simulation/`, `hardware/`, `scripts/` |
| **CHECKER** | Claude (sohbet) | prompt/kart yazar, kontrol paketini denetler | repoya yazmaz (kullanıcı aktarır) | — |
| **KULLANICI** | proje sahibi | karar, tezgâh ölçümü, birleştirme, kritik onay | her şey | — |

THINKER salt-okunur komut çalıştırabilir (pytest, kicad-cli ERC/DRC, ngspice); dosya üretiyorsa `reports/<id>/` altına. `python scripts/check_workflow.py` izin matrisi dışı değişikliği uyarır.

## Görev yaşam döngüsü

`Draft → Ready → InProgress → Review → Done` (veya `Blocked`). Kart türleri: `T-xxx` (BUILDER uygulama), `R-xxx` (THINKER inceleme), `D-xxx` (THINKER karar notu), `U-xxx` (kullanıcı; [`tasks/BLOCKED-ON-USER.md`](../tasks/BLOCKED-ON-USER.md)). Sıra: [`tasks/queue.md`](../tasks/queue.md). Biten kart `tasks/done/`'a `git mv`.

- Kart tek başına yeterlidir: hedef, minimum girdiler, izinli yollar, ölçülebilir ve komutlu kabul kriteri, durdurma koşulu. Şablon: [`tasks/TEMPLATE.md`](../tasks/TEMPLATE.md).
- Boyut **S ≤ ~30 dk**, **M ≤ ~90 dk**; **L yasak** → böl.
- Eksik karar/girdi: BUILDER tahmin etmez; kartı `Blocked` yapar, nedenini yazar, `BLOCKED-ON-USER.md`'ye madde ekler, durur.

## İnceleme kuralı (en çok 2 tur)

1. Çıktı = karar (**ONAY / KOŞULLU / RED**) + yalnız **ENGELLEYİCİ** bulgular: kabul kriterini etkileyen ve kanıtlı (komut çıktısı veya datasheet sayfası). Kanıtsız bulgu geçersizdir.
2. Engelleyici olmayan bulgu [`tasks/backlog.md`](../tasks/backlog.md)'ye gider, yeni tur açmaz.
3. İkinci turdan sonra kalan engelleyici → kullanıcı kararı (`BLOCKED-ON-USER.md`). Şablon: [`reviews/TEMPLATE.md`](../reviews/TEMPLATE.md).

## Bağımsızlık kuralı

Sayı doğrulayan THINKER, BUILDER'ın sonucunu görmez: yalnız girdi tablosu + kriter alır, kendi hesaplar, sonra karşılaştırılır. `scripts/make_pack.py --for codex|chatgpt` sonuç dosyalarını varsayılan olarak çıkarır (`--include-results` yalnız karşılaştırma turunda).

## Kanıt ve kriterler (değişmez)

Kanıt sırası: tezgâh ölçümü > komut çıktısı/log > hesap > yorum. Etiketler HESAP / DATASHEET(sayfa) / SİM / VARSAYIM / AÇIK; simülasyon fiziksel kanıt değildir. FAIL silinmez, kriter gevşetilmez: O1 ≤12,0 V; kararlı bara ≤11,1605 V; bara min ≥10,78 V; U3/U4 IN <30 V. MPN/değer/stok uydurulmaz; okunamayan belge → "doğrulanamadı". Tipik değer garanti gibi kullanılmaz. Aynı araç hatası 2 denemede aşılmazsa dur, "kanıt yok" yaz. Raporlardaki sayılar JSON/hesap çıktısından gelir.

## Dal, commit, PR

- Dal `wp/<kart-id>` (ör. `wp/T-001`); ardışık küçük kartlar kartta yazıyorsa aynı dalı paylaşabilir. Taslak PR, base `main`.
- `main`'e doğrudan push, force push, rebase/reset, uzak dal silme, `--admin` yok. Birleştirmeyi kullanıcı yapar veya kart açıkça yetkilendirir.
- Kanıt silme yok: temizlik = `git mv archive/...` + `archive/INDEX.md` + `archive/MANIFEST-SHA256.txt`.
- KiCad dosyası yalnız kart izin veriyorsa: blok öncesi commit, blok sonrası ERC + tutarlılık; bozulursa geri al. Gizli anahtar/kişisel yol sızdırma yok.

## Oturum ritüeli

- **Açılış:** `git status -sb` → `docs/START-HERE.md` → `HANDOFF.md` → aktif kart. Kirli ağaçta sahipliği kontrol et; kullanıcı dosyasına dokunma.
- **Kilometre taşı:** commit + `HANDOFF.md` güncelle (oturum kesilirse sonraki oturum buradan devam eder).
- **Kapanış:** kabul kriteri komutları, kart Durum + `queue.md`, `HANDOFF.md` üzerine yaz (≤40 satır), `python scripts/check_workflow.py`, commit + push.

## Limit yönetimi ve model rehberi

Claude 5 saatlik pencere: kartı bitiremeyeceksen bir sonraki kilometre taşında dur, HANDOFF'a tek satırlık "sonraki adım" komutu yaz. Giriş paketi (START-HERE + CLAUDE/AGENTS + HANDOFF + kart) ≤ ~6k token; `archive/`, `reports/*/sim/` gerekmedikçe okunmaz.

| İş | Model |
|---|---|
| Mimari karar, zor hata ayıklama | Opus |
| Uygulama, betik, ERC döngüsü, belge | Sonnet |
| Toplu/mekanik (yeniden adlandırma, tablo üretimi) | Haiku |

## Oturum prompt şablonları

**BUILDER (Claude Code):**
```
CLAUDE.md ve docs/START-HERE.md'yi oku, HANDOFF.md'den devam et, aktif kart tasks/T-xxx.md'yi uygula.
Kart dışına çıkma; eksik karar varsa kartı Blocked yap ve dur.
Her kilometre taşında commit + HANDOFF. Bitince kısa rapor: kabul kriterleri, komut çıkışları, açıklar.
```

**THINKER inceleme (Codex/ChatGPT):**
```
AGENTS.md'yi oku. Girdi: packs/R-xxx-codex.md (yoksa: python scripts/make_pack.py --task R-xxx --for codex).
Sonuçları görmeden bağımsız doğrula; reviews/R-xxx.md'yi reviews/TEMPLATE.md ile yaz:
karar (ONAY/KOŞULLU/RED) + yalnız engelleyici, kanıtlı bulgular; diğerleri tasks/backlog.md.
```

**THINKER karar notu:**
```
AGENTS.md'yi oku. Girdi: packs/D-xxx-chatgpt.md. Soru kartta.
decisions/D-xxx-*.md'yi decisions/TEMPLATE.md ile yaz: seçenekler tablosu, öneri, kanıt (resmi belge + sayfa),
açık varsayımlar, kullanıcı kararı gerekli mi. Okunamayan değer uydurma: "doğrulanamadı" yaz.
```

**CHECKER (Claude sohbetine yapıştır):**
```
Aşağıdaki kontrol paketi IDA PDU reposundan (python scripts/make_pack.py --task <ID> --for checker).
Bu pakette tutarsızlık, aşırı iddia (kanıtsız PASS, tipik değeri garanti sayma), atlanmış kabul kriteri ara.
En çok 10 madde; her madde için paketteki satırı göster. Yeni iş önerme.
<paketi buraya yapıştır>
```
