# HANDOFF — devam notu (her oturum sonunda üzerine yazılır; geçmiş git'te)

- **Tarih:** 2026-11-07
- **Dal / son commit:** wp/T-012 (taslak PR; **birleştirilmedi** — R-011 bekliyor)
- **Aktif kart:** T-012 (Review). Şema bitti (B1–B7, 180 ref spec ile birebir, ERC 0). Sıradaki: T-013 PCB kurulumu (D-006: 120 × 85, 4 katman).

## Yapılanlar
- T-011 (#44) main'de (R-010: kanonik Value kuralı). T-012 (dal): D-008 test padleri + J_OVP_INJ_BUS + JP_EN_BUCK (BOM dışı), notlar/antet; ERC 0, B1–B7 fark 0.
- T-010 + T-009 (#42) main'de (R-009: Q2 TI land footprint). T-011 (dal): B6 tamam; şemadaki 142 PCB parçasının tamamı spec ile birebir, ERC 0.
- T-017 (#40) main'de. T-010 + T-009 (dal): B5 30 + B4 12 parça `sch_place.py` ile (etiket-pin); ERC 0; B1–B5 fark 0; blok dışı 0. Q2 footprint TI land'den özel (R-009).
- T-008 (#38) main'de (R-007 ONAY). B5 bloğu şemada yok → T-009 öncesi T-010; stokta olmayan 5 sembol T-017 ile üretildi (make_symbols.py; datasheet sayfaları görsel okundu).
- T-007 (#33) main'de; R-006 kapandı. R-005 (#37): BIL düzgünleştirmesi etkisiz (geri alındı); kısaltılmış pencere O1 10,92 V; `scripts/pre_merge.py` kapısı.
- T-008 (dal): COUT9–32 eklendi; ERC 0, B1–B3 fark 0 (reports/g5/T-008/EVIDENCE.md).
- R-005 (#31, #32): sim_runner timeout 900 s; F5 yeniden: aynı 2 köşe 3. kez tamamlanmadı → kanıt yok (AÇIK). Log'da yalnız başlangıç OP; adım çöküşü şüphesi → R-005 tur 2.
- T-007 (dal): `scripts/sch_edit_b2.py` — BIAS → GND, CBOOT_R düğümü, R_INJ (/VOUT–/FB_INJ), R_TRIM (/FB_TRIM–GND), RCOMP 33,2k / CCOMP 10n / CHF 22p / RFB2 9,76k + B2 MPN/footprint. ERC 0; B1+B2 fark 0; blok dışı değişiklik 0 (reports/g5/T-007/EVIDENCE.md).
- Spec düzeltmeleri (datasheet kanıtlı, şema doğruydu): U2 FB → GND (p.19), RBOOT seri (p.4), SW4 ayrı ağ.

## Sonraki adım
Codex: R-011. Sonra Claude Code: T-012 birleştir → T-013 (PCB: dış hat 120 × 85, 4 katman stackup, netclass + .kicad_dru, netlist aktarımı; yönlendirme yok).

## Engeller
F5 iki köşe: kısaltılmış pencere kanıtı var (O1 10,92 V), tam pencere AÇIK (backlog).

## Kullanıcıdan bekleyenler (yalnız fiziksel, engellemez)
- U-001, U-007 tezgâh ölçümleri (kart üretilince).
- **Birleştirme yetkisi: VERİLDİ (2026-11-07).** KiCad/tasarım PR'ı için THINKER onayı yeterli (WORKFLOW kural 6).

## Okuma gerektirmeyen notlar
- KiCad GUI açıksa şemayı GUI'den kaydetmeyin; düzenlemeler `scripts/sch_edit_b*.py` ile yeniden üretilebilir.
