# T-007 — şema bloğu B2 (buck çekirdeği) kanıtı

Düzenleme: `python scripts/sch_edit_b2.py` (kayıpsız S-ifade; B1 uygulanmış main şeması üzerinde). KiCad 10.0.7.

| Kontrol | Komut | Sonuç |
|---|---|---|
| ERC | `kicad-cli sch erc --format json` → [erc.json](erc.json) | **0 ihlal** (baseline 0) |
| Netlist | `kicad-cli sch export netlist --format kicadsexpr` → [netlist.net](netlist.net) | ham çıktı (THINKER KiCad'siz ayrıştırabilir) |
| Spec farkı | `python analysis/check_consistency.py --schematic B1 B2` → [check-B1-B2.txt](check-B1-B2.txt) | B1 16 + B2 28 ref, **fark 0** (footprint, MPN, sayısal değer, pin→ağ) |
| Blok dışı | main netlisti ile karşılaştırma (B1/B2 dışı tüm ref'ler) | pin→ağ değişikliği **0**; eklenen ref: R_INJ, R_TRIM |

## Şema değişiklikleri
- U1/U2 pin 6 BIAS: `VOUT` etiketi → `GND` (LM70880 p.13, G4 B3).
- RBOOT–CBOOT seri düğümü `CBOOT_R1/2` olarak adlandırıldı.
- **R_INJ** (0 Ω, CRCW06030000Z0EA) /VOUT ↔ RFB1.1 arasına; yeni ağ `/FB_INJ` (FRA enjeksiyonu, BENCH T3).
- **R_TRIM** (442 Ω, TNPW0603442RBXEA) RFB2.2 ↔ mevcut GND teli arasına; yeni ağ `/FB_TRIM` (kart başı trim, B4/T1b).
- Değerler: RCOMP 33,2k, CCOMP 10n, CHF 22p, RFB2 9,76k (+ tüm B2 footprint/MPN alanları spec'ten).

## Spec düzeltmeleri (şema zaten doğruydu; datasheet kanıtlı)
- **U2 FB → /GND**: FPWM çift faz modunda ikincil cihazın FB'si AGND'ye (LM70880-Q1 SNVSBX7A p.19). G2 spec'i `/FB` yazıyordu.
- **RBOOT seri**: "1 Ω in series with the bootstrap capacitor" (p.4). G2 spec'i RBOOT ve CBOOT'u paralel (ikisi de /CBOOT–/SW4) yazıyordu.
- **SW4 ayrı ağ** (`/SW4_PHk`, p.3: SW4 içten SW1–3'e bağlı, PCB'de ayrıca yönlendirilmez).

TP_FB_INJ_A/B test noktaları T-012 (B7) kapsamında.

## R-006 düzeltmesi
RFB2 (ve klonlanan R_INJ/R_TRIM) üzerindeki önceki parçanın (Panasonic ERA3AEB1022V / ERA3AEB134V) Datasheet, Specification, TCR, Tolerance, Manufacturer alanları silindi; MPN/Value spec'ten. `check_consistency.py --schematic` Manufacturer alanını BOM üreticisiyle karşılaştırıyor (RFB1, RIMON1/2 Panasonic = BOM). ERC 0, B1+B2 fark 0 (yeniden üretildi).
