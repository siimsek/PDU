# G3 ilerleme kaydı

Dal `wp/g3-pcb-ready` (taban `wp/g2-circuit-design` @ `6b2b16b`). `*.kicad_*` değiştirilmez. Context sıfırlanırsa son bölümden devam.

## A1–A4 (2026-11-07)
- `git fetch --all`; ağaçta yalnız G2 hata ayıklama klasörü `reports/g2/sim/dbg/` (izlenmeyen, G2 üretimi) vardı → repo dışına (oturum scratchpad) taşındı, silinmedi.
- G2 commit'leri 9e2918e…6b2b16b (Aşama 1–6), çıktı dosyalarının hepsi mevcut.
- Ortam: Python 3.14.5; kicad-cli 10.0.7 (`C:\Program Files\KiCad\10.0\bin`, PATH'te değil); ngspice-47 `F:\Spice64\bin\ngspice_con.exe`.
- Baseline: ERC 0 ihlal; DRC 228 uyarı (silk_over_copper 199, silk_overlap 21, lib_footprint_mismatch 5, silk_edge_clearance 3) + 197 bağlantısız + 73 şema paritesi uyarısı (Description/MPN alan farkı); boş MPN 57/73. Kayıt: ERC 0/0, DRC 197/301 → bağlantısız eşleşti, uyarı 301→228 (KiCad 10.0.7 kural seti farkı; ayrıntı AUDIT).
- ngspice baseline O1: Windows-47 16.890 V = Linux-44.2 kaydı 16.89 V (fark 0).
- pytest 91 passed (2.5 s); `analysis/run_all.py` 7/7 adım exit 0 (4 m 12 s). Yeniden koşuda 68 koşunun ölçümleri ve deck/girdi hash'leri birebir aynı; loglar yalnız süre/bellek satırında farklı → geri alındı.
