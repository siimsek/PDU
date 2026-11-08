# Çalışma düzeni (W0) — röle modu, kart tabanlı, limit-dostu

Kalıcı bağlam repodadır: oturum = kısa prompt + [`HANDOFF.md`](../HANDOFF.md) + bir görev kartı (`tasks/`). Eski düzen: [`archive/docs-legacy/AI-WORKFLOW.md`](../archive/docs-legacy/AI-WORKFLOW.md) (SUPERSEDED).

## Röle modu (varsayılan): kullanıcı yalnız prompt taşır

Kullanıcı dosya yüklemez, komut çalıştırmaz, kart yazmaz; yalnız bir ajanın verdiği prompt'u diğerine yapıştırır.

```
Claude Code ──(SONRAKİ PROMPT → Codex)──▶ kullanıcı ──▶ Codex
     ▲                                                    │
     └──────── kullanıcı ◀──(SONRAKİ PROMPT → Claude Code)┘
```

1. **Her oturum bir prompt ile biter.** Son mesajın sonunda tek bir kod bloğu: başlık `SONRAKİ PROMPT → Codex` veya `SONRAKİ PROMPT → Claude Code`. Prompt kendi kendine yeterlidir (repo, dal, kart, ne yapılacak, nereye yazılacak, bitince ne döndürülecek) ve ≤ 15 satırdır.
2. **Dosya alışverişi yalnız GitHub üzerinden** (`siimsek/PDU`): her ajan kendi dalına (`wp/<kart-id>`) push eder ve taslak PR açar; diğer ajan dalı/PR'ı oradan okur. Datasheet ve resmi belgeleri ajan kendisi indirir (resmi üretici sitesi); erişemezse "doğrulanamadı" yazar, kullanıcıdan dosya istemez.
3. **Codex push/PR açamıyorsa** (ör. Codex Web oturumu): çıktı dosyalarının tam içeriğini son mesajda `DOSYA: <yol>` başlıklı kod bloklarıyla verir; Claude Code bu içeriği `wp/<kart-id>` dalına commit edip PR açar. Kullanıcıya düğme/komut işi bırakılmaz.
4. **Paket:** Codex `python scripts/make_pack.py --task <ID> --for codex` komutunu kendi ortamında çalıştırır (paket git'e girmez).
5. **Kullanıcıya soru sorulmaz** (kullanıcı kararı, 2026-11-07). Tasarım/mimari kararı gerekirse BUILDER onu bir THINKER D-kartı olarak yazar ve `SONRAKİ PROMPT → Codex` ile sorar; THINKER önerisi karar olarak uygulanır. Belge erişimi gerekiyorsa da THINKER dener. Kullanıcıya yalnız **fiziksel** işler kalır (tezgâh ölçümü, kart/yük elde etme); bunlar `tasks/BLOCKED-ON-USER.md`'de durur ve tasarım akışını engellemez.
6. **Birleştirme:** BUILDER kabul kriterleri + `check_workflow.py` + pytest geçen PR'ları birleştirir (yetki 2026-11-07). KiCad dosyası veya tasarım değeri değiştiren PR için kullanıcı onayı yerine **THINKER onayı** yeterlidir: dayandığı D-kartı kararı veya bir R-kartı ONAY/KOŞULLU sonucu. Bunlardan biri yoksa BUILDER önce R-kartı açar ve prompt'la sorar.

## Roller ve yazma izinleri

| Rol | Kim | Yapar | Yazabilir | Yazamaz |
|---|---|---|---|---|
| **BUILDER** | Claude Code (Opus/Sonnet/Haiku) | T-kartını uygular: KiCad, betik, SPICE, BOM, test, belge; commit, push, taslak PR | kartın "İzinli yazma yolları"; her zaman `HANDOFF.md`, `tasks/queue.md`, kendi kartının Durum alanı | kart dışı yollar; `main`; `reviews/`, `decisions/` içeriği |
| **THINKER** | Codex (CLI/App/Web), ChatGPT (Web/Work) | analiz, bağımsız doğrulama, datasheet okuma, R-/D-kartı, T-kartı taslağı | `reviews/`, `decisions/`, `tasks/` (kart taslağı, backlog); kart izin verirse `reports/<id>/` | `*.kicad_*`, `design/`, `analysis/`, `simulation/`, `hardware/`, `scripts/` |
| **CHECKER** (isteğe bağlı) | Claude (sohbet) | ara kontrol: `make_pack --for checker` paketi | repoya yazmaz | — |
| **KULLANICI** | proje sahibi | prompt taşır; karar cevabı, tezgâh ölçümü, birleştirme yetkisi | — | — |

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

Ajanlar bu şablonları doldurup **SONRAKİ PROMPT** bloğu olarak verir; kullanıcı aynen yapıştırır.

**→ Codex (THINKER, inceleme/karar):**
```
GitHub siimsek/PDU reposunda THINKER'sın. AGENTS.md'yi oku (dal: <taban dal>).
Kart: tasks/<ID>.md. Paket: python scripts/make_pack.py --task <ID> --for codex (kendi ortamında).
BUILDER sonuçlarını kendi hesabın bitmeden açma. Çıktı: <reviews/R-xxx.md | decisions/D-xxx-*.md> şablonla.
wp/<ID> dalına push et, taslak PR aç (base: main). Push edemiyorsan dosyaları "DOSYA: <yol>" bloklarıyla ver.
Sonunda "SONRAKİ PROMPT → Claude Code" bloğu yaz: PR/dal adı, karar, engelleyici bulgu sayısı, Claude'un yapacağı iş.
```

**→ Claude Code (BUILDER):**
```
CLAUDE.md, docs/START-HERE.md ve HANDOFF.md'yi oku. <Codex PR #n / dal wp/<ID>> çıktısını GitHub'dan al.
Aktif kart: tasks/<ID>.md. Kabul kriterlerini sağla; her kilometre taşında commit + HANDOFF; taslak PR.
Sonunda "SONRAKİ PROMPT → Codex" bloğu yaz (veya kullanıcıya tek soru).
```

## Metin kodlaması
Depodaki her metin dosyası BOM'suz UTF-8'dir; Türkçe karakterler okuma, yazma, alt süreç ve üretilen çıktı boyunca korunur. Her araç UTF-8 ile okur ve yazar (ayrıntı `AGENTS.md`, `CLAUDE.md`). `scripts/check_workflow.py` geçersiz UTF-8, BOM, bozuk karakter dizileri ve kelime içi soru imini hata sayar; `archive/`, `design/`, KiCad dosyaları, `.net` çıktıları ve ikili dosyalar kapsam dışıdır. Yanlış alarm yalnız URL sorgu ayıracıdır (`reports/R-003/land-data.md`, `decisions/D-001-F1.md`).
