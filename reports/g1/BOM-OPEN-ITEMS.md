> **SUPERSEDED (G3, 2026-11-07) → reports/g2/BOM-OPEN.md.** Bu belge geçmiş kaydıdır; içerik değiştirilmedi.

# BOM doğrulama açıkları

- Satır işlendi: **73/73**.
- BOM MPN sütunu boş: **57** satır. Hiçbir MPN uydurulmadı; Value alanından kesin kimlik yalnız Q1 ve konektör family candidate olarak not edildi, sipariş kodu diye onaylanmadı.
- F1 ve yuva/footprint seçilmedi; short current, DC interrupt ve I²t koordinasyonu açık.
- L1/L2 candidate IHLP4040DZER6R8M01 found from Vishay official cross-reference; BOM approval, stock, hot DCR and land match remain open.
- J1/J2/J3 mating housing/contact/cable absent. 7.5 A target requires exact 18 AWG wire-to-board setup; wire-to-wire 18 AWG 7 A published maximum is below target.
- SMCJ33A/SS34 generic manufacturerless family; exact TVS pulse/thermal and diode-current roles open.
- RS1/RS2 exact shunt, power/TCR/tolerance missing; recommended selection screen ≥0.5 W, ≤1% and ≤100 ppm/K, subject to vendor qualification.
- CIN/CBIN/CEFOUT and other generic MLCCs have no voltage rating or manufacturer; CIN/CBIN on the protected VIN node need a ≥80 V candidate to satisfy 1.5×53.3 V assumed clamp screen. 10 µF port Ceff under 11 V DC bias is unknown.
- Current live inventory/lifecycle was not verifiable for any line; no stale cached quantity is presented as current.
- Exact datasheet verification for generic R/C and SS34 cannot be completed without exact manufacturer/MPN input. Ask for PDFs/approved vendor list rather than inferring family data.

Row detail: [`bom-verification.csv`](bom-verification.csv).
