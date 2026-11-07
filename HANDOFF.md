# HANDOFF — devam notu (her oturum sonunda üzerine yazılır; geçmiş git'te)

- **Tarih:** 2026-11-07
- **Dal / son commit:** wp/T-001 → main (T-001 birleştirildi)
- **Aktif kart:** — (Ready: R-001, D-001, D-002 → Codex; T-002, T-003 → Claude Code)

## Yapılanlar
- W0 + röle modu main'de (PR #4).
- T-001: baseline yeniden üretildi (pytest 110, run_all 12/12, ERC 0, DRC 228/197/73) → reports/g5/baseline/BASELINE.md; bom.py CSV'leri LF yazıyor (+ test).

## Sonraki adım
Codex: R-001 (prompt kullanıcıda). Claude Code: T-002 (şema düzenleme aracı kararı), sonra T-003 (FLOORPLAN).

## Engeller
- Yok.

## Kullanıcıdan bekleyenler
- U-001 tezgâh ölçümü (fiziksel; ne zaman mümkünse).
- **Birleştirme yetkisi: VERİLDİ (2026-11-07, kullanıcı: "Yetki veriyorum").** Kapsam: BUILDER, kabul kriterleri + pytest + check_workflow geçen PR'ları birleştirir; KiCad dosyası veya tasarım değeri değiştiren PR'da birleştirmeden önce tek satır onay sorar (WORKFLOW röle kuralı 6).

## Okuma gerektirmeyen notlar
- Baseline: reports/g5/baseline/ (G4 ile aynı sayılar).
- R-001, D-001, D-002 birbirinden ve BUILDER kartlarından bağımsız (yazma yolları ayrık).
