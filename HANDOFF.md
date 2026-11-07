# HANDOFF — devam notu (her oturum sonunda üzerine yazılır; geçmiş git'te)

- **Tarih:** 2026-11-07
- **Dal / son commit:** wp/T-003 → main
- **Aktif kart:** — (Ready: D-001, D-002, D-003, D-004 → Codex; T-005a → Claude Code)

## Yapılanlar
- R-001 tur 1 (Codex, RED): bulgu 1 kart girdi hatası (düzeltildi), 2 → D-003 (J2), 3 → D-004 (O1 zamanlama); yanıt reports/g5/R-001-RESPONSE.md. R-001 tur 2 bu kararlardan sonra.
- T-002: düzenleme aracı = scripts/kicad_sexpr.py (kayıpsız; 7/7 baytça aynı, ERC/netlist yuvarlak-gezi aynı). Konnect MCP erişilemez (GUI gerekir).
- T-003: courtyard toplamı 3759,9 mm²; mevcut kart %48,6 (tek taraf, alt sınır), 120 × 85 mm %36,9 → öneri 120 × 85 (reports/g5/FLOORPLAN.md).

## Sonraki adım
Codex: D-004, D-003, D-001, D-002 (paralel olabilir). Claude Code: T-005a (özel footprint doğrulama, `analysis/check_footprints.py`).

## Engeller
- R-001 tur 2 → D-003 + D-004 kararları ve uygulanması. T-013 → kart ölçüsü onayı (öneri 120 × 85).

## Kullanıcıdan bekleyenler
- U-001 tezgâh ölçümü (fiziksel; ne zaman mümkünse).
- **Birleştirme yetkisi: VERİLDİ (2026-11-07, kullanıcı: "Yetki veriyorum").** Kapsam: BUILDER, kabul kriterleri + pytest + check_workflow geçen PR'ları birleştirir; KiCad dosyası veya tasarım değeri değiştiren PR'da birleştirmeden önce tek satır onay sorar (WORKFLOW röle kuralı 6).

## Okuma gerektirmeyen notlar
- Baseline: reports/g5/baseline/ (pytest 116 dahil W0/T-002/T-003 testleri; ERC 0; DRC 228/197/73).
- D-kartları birbirinden bağımsız; yazma yolları ayrık (decisions/D-00x-*.md).
