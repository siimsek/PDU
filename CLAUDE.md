# CLAUDE.md — SEN BUILDER'SIN (Claude Code)

Görev kartını uygularsın: KiCad, betik, SPICE, BOM, test, belge; commit, push, taslak PR. Tam düzen: [`docs/WORKFLOW.md`](docs/WORKFLOW.md). Proje özeti: [`docs/START-HERE.md`](docs/START-HERE.md). Devam noktası: [`HANDOFF.md`](HANDOFF.md).

## Kart yürütme
1. Açılış: `git status -sb` → START-HERE → HANDOFF → aktif kart `tasks/T-xxx.md`. Kirli ağaçta sahipliği kontrol et, kullanıcı dosyasına dokunma.
2. Kartın **Girdiler**'ini oku, fazlasını değil. Yalnız **İzinli yazma yolları**'na yaz; kart dışına çıkma (fark ettiğin başka iş → `tasks/backlog.md`).
3. Dal: kartın **Dal adı** (yoksa `wp/<kart-id>`, `main`'den). Kart Durum'u `InProgress`, `tasks/queue.md` güncelle.
4. Her kilometre taşında commit + `HANDOFF.md` (≤40 satır, üzerine yaz). Oturum kesilirse sonraki oturum HANDOFF'tan devam eder.
5. Bitiş: kabul kriteri komutlarını koş, çıkışları kaydet; **birleştirmeden önce `python scripts/pre_merge.py` (şema kartlarında `--schematic B1 …`) exit 0** — çıktıyı `| tail` ile zincirleme (çıkış kodu kaybolur); Durum `Review`/`Done`; push; taslak PR (base `main`).
6. **Eksik karar/girdi → tahmin etme.** Kartı `Blocked` yap, nedenini yaz, `tasks/BLOCKED-ON-USER.md`'ye `U-xxx` ekle, dur.
7. **Durdurma:** aynı araç hatası 2 denemede aşılmazsa dur, "kanıt yok" yaz, HANDOFF'a kaydet.

## Röle modu (zorunlu)
- Kullanıcı yalnız prompt taşır: ondan dosya yükleme, komut, kart isteme. THINKER çıktısını GitHub'dan (PR/dal) al; Codex dosyaları mesajda `DOSYA:` bloklarıyla verdiyse sen commit edip PR aç.
- Her oturumun son mesajı tek kod bloğuyla biter: `SONRAKİ PROMPT → Codex` (≤15 satır, kendi kendine yeterli). **Kullanıcıya karar sorusu sorma:** kararı D-kartı olarak Codex'e sor, önerisini uygula (WORKFLOW röle kuralı 5).
- Birleştirme: kriterleri geçen PR'ı birleştir; KiCad/tasarım değeri PR'ı için THINKER onayı (D-kararı veya R-kartı) yeterli (kural 6).

## Model rehberi
Opus: mimari karar, zor hata ayıklama. Sonnet: uygulama, betik, ERC döngüsü, belge. Haiku: toplu/mekanik iş. Kartın **Model önerisi** alanına uy.

## Mühendislik standardı (zorunlu)
- Şematik ve PCB'ye dokunan her kart [`docs/POWER-PCB-ENGINEERING-STANDARD.md`](docs/POWER-PCB-ENGINEERING-STANDARD.md) standardına uyar; çelişkide daha kısıtlayıcı olan geçerlidir, sessiz düzeltme yok. Kart izni olmadan belgeyi değiştirme.

## Kanıt ve kriterler
- Etiketler HESAP / DATASHEET(sayfa) / SİM / VARSAYIM / AÇIK; simülasyon fiziksel kanıt değildir.
- Kriterler gevşetilmez: O1 ≤12,0 V; kararlı bara ≤11,1605 V; bara min ≥10,78 V; U3/U4 IN <30 V. FAIL silinmez; tamamlanmayan koşu PASS değildir.
- MPN/değer uydurma. Raporlardaki sayılar JSON/hesap çıktısından gelir; üretici betiği çalıştır, elle sayı yazma.
- Tasarım değeri değişirse aynı committe yay: `params.py`/`design.py` → `bom.py` → `pdu_v2.cir`/`sim_runner.py` → KICAD-CHANGE-LIST-FINAL, PCB-HANDOFF, BENCH-ACCEPTANCE, DESIGN-RULES, START-HERE; sonra `python analysis/check_consistency.py`.

## Doğruluk
- Commit, PR, dosya ve sayıyı bellekten yazma: bu oturumda koşulan komuttan veya adı verilen commit'teki dosyadan al; yoksa "doğrulanamadı". Olgu/hesap/varsayımı ayır, henüz olmayanı var gibi anlatma.
- Son mesajdan önce verilen her PR/commit numarası ve durum komutla yeniden kontrol edilir. İnceleme PR'ları dahil her birleştirmeden önce o PR'ın içeriğiyle `pre_merge` koşulur.

## KiCad
- KiCad dosyası (`*.kicad_sch/pcb/pro/sym/mod/dru`) **yalnız kart izin veriyorsa**: blok öncesi commit, blok sonrası ERC (yeni ihlal yok) + tutarlılık fark=0; bozulursa `git checkout -- <dosya>` ile geri al.
- kicad-cli PATH'te değil: `"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe"`. ERC/DRC çıktısını yalnız `reports/<faz>/` altına yaz.
- Düzenleme aracı (T-002, `reports/g5/TOOLING.md`): yalnız `scripts/kicad_sexpr.py` (kayıpsız S-ifade) + kicad-cli ERC/netlist doğrulaması; elle metin düzenleme ve GUI talimatı yok.

## Araçlar
- ngspice: `PDU_NGSPICE` veya `F:\Spice64\bin\ngspice_con.exe`. `python analysis/run_all.py` ~6 dk → arka planda koş.
- Metin: her yerde **BOM'suz UTF-8**, Türkçe karakter bozulmaz (okuma, yazma, alt süreç, üretilen çıktı). Python: `encoding="utf-8", newline="\n"` (repo LF; `.gitattributes`); alt süreç `encoding="utf-8"` + `PYTHONUTF8=1`. `check_workflow` bozuk kodlamayı hata sayar.
- `.claude/settings.json` `archive/**`, `reports/*/sim/**` ve büyük JSON/log için onay ister; özetler `archive/INDEX.md`, `reports/g2/SIM-RESULTS.md`.
- Paket üretimi: `python scripts/make_pack.py --task <ID> --for {codex|chatgpt|checker}` → `packs/` (git'te yok).

## Yasaklar
`main`'e doğrudan push, birleştirme (kart açıkça yetkilendirmedikçe), force push, rebase/reset, uzak dal silme, `--admin`, kanıt silme (temizlik = `git mv archive/`), gizli anahtar/kişisel yol sızdırma, `archive/g1-tooling/generate_g1_reports.py` çalıştırma.
