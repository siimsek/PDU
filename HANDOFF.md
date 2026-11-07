# HANDOFF — devam notu (her oturum sonunda üzerine yazılır; geçmiş git'te)

- **Tarih:** 2026-11-07
- **Dal / son commit:** wp/workflow-setup (W0 iş akışı kurulumu; taslak PR, base main)
- **Aktif kart:** — (W0 kurulumu; sıradaki: T-001)

## Yapılanlar
- W0: üç rollü düzen (docs/WORKFLOW.md, AGENTS.md = THINKER, CLAUDE.md = BUILDER), tasks/ reviews/ decisions/ yapısı.
- G5 KiCad fazı 18 karta bölündü (tasks/queue.md); kullanıcı maddeleri U-001…U-005.
- scripts/make_pack.py, scripts/check_workflow.py (+ testler); run_all'a iş akışı kontrolü eklendi.

## Sonraki adım
`git switch main && git pull --ff-only && git switch -c wp/T-001` → tasks/T-001.md (W0 PR birleştikten sonra).

## Engeller
- W0 PR'ı birleşmeden T-001 main'den başlayamaz (U-005).

## Kullanıcıdan bekleyenler
U-001 T-1 akım ölçümü, U-002 T3 Gemstone O1 spec, U-003 F1 belgesi, U-005 PR birleştirme (tasks/BLOCKED-ON-USER.md).

## Okuma gerektirmeyen notlar
- Baseline (G4): pytest 98 + W0 testleri; run_all exit 0; ERC 0; DRC 228 / 197 / 73.
- R-001 ve D-001 T-001 ile paralel yürütülebilir (THINKER; yazma yolları ayrık).
- `design/*.csv` CRLF yazımı T-001'de düzeltilecek (içerik aynı).
