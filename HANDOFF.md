# HANDOFF — devam notu (her oturum sonunda üzerine yazılır; geçmiş git'te)

- **Tarih:** 2026-11-07
- **Dal / son commit:** wp/workflow-setup (W0 + röle modu; taslak PR siimsek/PDU#4, base main)
- **Aktif kart:** — (THINKER: R-001, D-001, D-002 Ready; BUILDER: T-001 Ready, W0 birleşince)

## Yapılanlar
- W0: kart tabanlı düzen (docs/WORKFLOW.md, AGENTS.md = THINKER, CLAUDE.md = BUILDER), tasks/ reviews/ decisions/.
- **Röle modu** (kullanıcı isteği): kullanıcı yalnız prompt taşır; her oturum `SONRAKİ PROMPT` bloğuyla biter; dosyalar GitHub dal/PR'larından akar.
- G5 KiCad fazı kartlara bölündü (tasks/queue.md, 19 kart); U-002/U-003/U-004 ajan kartlarına devredildi (D-002, D-001, R-002).

## Sonraki adım
Codex: R-001 / D-001 / D-002 (taban dal `wp/workflow-setup` — W0 main'e girene kadar). Claude Code: W0 birleşince `wp/T-001`.

## Engeller
- W0 PR'ı (#4) birleşmeden BUILDER kartları main'den başlayamaz.

## Kullanıcıdan bekleyenler
- U-001 tezgâh ölçümü (fiziksel; ne zaman mümkünse).
- **Birleştirme yetkisi: VERİLDİ (2026-11-07, kullanıcı: "Yetki veriyorum").** Kapsam: BUILDER, kabul kriterleri + pytest + check_workflow geçen PR'ları birleştirir; KiCad dosyası veya tasarım değeri değiştiren PR'da birleştirmeden önce tek satır onay sorar (WORKFLOW röle kuralı 6).

## Okuma gerektirmeyen notlar
- Baseline (G4): pytest 109 (W0 dahil); run_all exit 0; ERC 0; DRC 228 / 197 / 73.
- `design/*.csv` CRLF yazımı T-001'de düzeltilecek (içerik aynı).
