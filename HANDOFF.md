# HANDOFF — devam notu (her oturum sonunda üzerine yazılır; geçmiş git'te)

- **Tarih:** 2026-11-07
- **Dal / son commit:** wp/T-013 (PR #49 taslak; R-012 tur 2 KOŞULLU → yay uzunluğu düzeltildi; bağımsız doğrulama R-013 bekliyor — **birleştirme yok**)
- **Aktif kart:** T-013 (Review). PCB kuruldu: 120 × 85, 4 katman, 180 ayak izi, parite 0, boş kart DRC 0 (reports/g5/PCB-SETUP.md).

## Yapılanlar
- R-012 tur 2 (1 engelleyici): `neck_audit` yayda gerçek yay uzunluğu (start/mid/end); prob E/F yayları + testler. Doğrulama kartı tasks/R-013.md (queue: yalnız R-013 satırı — check_workflow kapısı için).
- R-012 tur 1 (2 engelleyici) düzeltildi: CIN1–4/5–8 U1/U2 VIN–PGND kenarında (5,6–16,4 mm); darboğaz DRU kuralı ince adımlı padli ayak izleriyle sınırlı + `pcb_drc.py` uzunluk denetimi (≤1,5 mm), `pcb_neck_probe.py` kanıtı.
- T-012 (#47) main'de (R-011 ONAY). T-013 (dal): `pcb_setup.py` (pcbnew) + `pcb_rules.py` + `pcb_drc.py`; netclass routing-g2'ye eşitlendi; kaba bölge yerleşimi; iz yok.
- T-011 (#44) main'de (R-010: kanonik Value kuralı). T-012 (dal): D-008 test padleri + J_OVP_INJ_BUS + JP_EN_BUCK (BOM dışı), notlar/antet; ERC 0, B1–B7 fark 0.
- T-010 + T-009 (#42) main'de (R-009: Q2 TI land footprint). T-011 (dal): B6 tamam; şemadaki 142 PCB parçasının tamamı spec ile birebir, ERC 0.
- T-017 (#40) main'de. T-010 + T-009 (dal): B5 30 + B4 12 parça `sch_place.py` ile (etiket-pin); ERC 0; B1–B5 fark 0; blok dışı 0. Q2 footprint TI land'den özel (R-009).
- T-008 (#38) main'de (R-007 ONAY). B5 bloğu şemada yok → T-009 öncesi T-010; stokta olmayan 5 sembol T-017 ile üretildi (make_symbols.py; datasheet sayfaları görsel okundu).
- T-007 (#33) main'de; R-006 kapandı. R-005 (#37): BIL düzgünleştirmesi etkisiz (geri alındı); kısaltılmış pencere O1 10,92 V; `scripts/pre_merge.py` kapısı.
- T-007 (dal): `scripts/sch_edit_b2.py` — BIAS → GND, CBOOT_R düğümü, R_INJ (/VOUT–/FB_INJ), R_TRIM (/FB_TRIM–GND), RCOMP 33,2k / CCOMP 10n / CHF 22p / RFB2 9,76k + B2 MPN/footprint. ERC 0; B1+B2 fark 0; blok dışı değişiklik 0 (reports/g5/T-007/EVIDENCE.md).
- Spec düzeltmeleri (datasheet kanıtlı, şema doğruydu): U2 FB → GND (p.19), RBOOT seri (p.4), SW4 ayrı ağ.

## Sonraki adım
Codex: R-013 (yay uzunluğu düzeltmesinin bağımsız doğrulaması, dal wp/R-013). ONAY → Claude Code: #50 + R-013 PR + #49 birleştir, queue eşitle (R-012/R-013) → T-014 KICAD-READY.

## Engeller
F5 iki köşe: kısaltılmış pencere kanıtı var (O1 10,92 V), tam pencere AÇIK (backlog).

## Kullanıcıdan bekleyenler (yalnız fiziksel, engellemez)
- U-001, U-007 tezgâh ölçümleri (kart üretilince).
- **Birleştirme yetkisi: VERİLDİ (2026-11-07).** KiCad/tasarım PR'ı için THINKER onayı yeterli (WORKFLOW kural 6).

## Okuma gerektirmeyen notlar
- KiCad GUI açıksa şemayı/PCB'yi GUI'den kaydetmeyin; şema `scripts/sch_edit_b*.py`, PCB `scripts/pcb_setup.py` + `pcb_rules.py` ile yeniden üretilir.
