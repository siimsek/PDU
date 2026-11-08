# HANDOFF — devam notu (her oturum sonunda üzerine yazılır; geçmiş git'te)

- **Tarih:** 2026-11-08
- **Dal / son commit:** wp/T-020 (taslak PR; **birleştirilmedi** — R-015 bekliyor)
- **Aktif kart:** T-020 (Review — ayrıntılı yerleşim). T-021…T-024 Draft; T-019 bekliyor.

## Yapılanlar
- T-020 (dal): `scripts/pcb_place.py`; DRC ihlal/uyarı 0, parite 0, 402 unconnected (iz yok); CIN U1/U2 kenarında, RS–INA296 ≤9,5 mm. Sınırlar: reports/g5/T-020/placement-review.md.
- R-014 (#56) ONAY: yerel KiCad 10.0.7 ile ERC 0, 180 ref, 422 pin, 0 fark, parite 0. D-009: bundled pcbnew API; gerçek bağlantı, refill ve parite T-020…T-024 aday kartında doğrulanacak.
- T-018: START-HERE G5'e, VERIFY.md T-014 koşusuna (F5 47/49 + iki eksik isim) eşitlendi; KICAD-CHANGE-LIST'e T-013. sim-results.json zaten doğruydu, değişmedi.
- R-002 (#53) Tur 2 ONAY, 0 engelleyici; T-014 (#52) Done. Koşullar korundu: F5 47/49, belge eşitleme. THINKER'ın kendi KiCad 10 koşusu doğrulanamadı (KiCad 9.0.2); onay BUILDER ham çıktıları + bağımsız karşılaştırmayla.
- R-002 tur 1 (PR #53, 1 engelleyici: Codex'te KiCad 9.0.2): 5a2985c üzerinde KiCad 10.0.7 ile ERC 0 + netlist, R-002 karşılaştırıcısı 0 fark (reports/g5/T-014/R-002-tur2/). LDSTRT/ITIMER gerekçesi AÇIK.
- T-013 (#49) + R-012 (#50) + R-013 (#51) main'de. T-014: 9 maddeden 8 GEÇTİ, 1 KALDI (belge: START-HERE, VERIFY.md eski). run_all exit 0, F5 47/49 (bilinen 2 köşe AÇIK).
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
Codex: R-015. ONAY → Claude Code: T-020 birleştir → T-021 (L2/L3 dökümleri, refill + parite aday kartta).

## Engeller
Yok (yönlendirmeye). Açık koşullar: F5 iki köşe tam pencere AÇIK (kısaltılmış pencerede O1 10,92 V); 26 spec dışı düğüm; izli dosyalarda yerel yol (backlog).

## Kullanıcıdan bekleyenler (yalnız fiziksel, engellemez)
- U-001, U-007 tezgâh ölçümleri (kart üretilince).
- **Birleştirme yetkisi: VERİLDİ (2026-11-07).** KiCad/tasarım PR'ı için THINKER onayı yeterli (WORKFLOW kural 6).

## Okuma gerektirmeyen notlar
- KiCad GUI açıksa şemayı/PCB'yi GUI'den kaydetmeyin; şema `scripts/sch_edit_b*.py`, PCB `scripts/pcb_setup.py` + `pcb_rules.py` ile yeniden üretilir.
