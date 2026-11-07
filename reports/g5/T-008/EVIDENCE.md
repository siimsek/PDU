# T-008 — şema bloğu B3 (COUT bankası 8 → 32) kanıtı

Düzenleme: `python scripts/sch_edit_b3.py` (B1+B2 uygulanmış main şeması üzerinde). KiCad 10.0.7.

| Kontrol | Komut | Sonuç |
|---|---|---|
| ERC | `kicad-cli sch erc --format json` → [erc.json](erc.json) | **0 ihlal** |
| Netlist | `kicad-cli sch export netlist --format kicadsexpr` → [netlist.net](netlist.net) | ham çıktı |
| Spec farkı | `python analysis/check_consistency.py --schematic B1 B2 B3` → [check-B1-B3.txt](check-B1-B3.txt) | B1 + B2 + B3 (COUT1–32) **fark 0** |
| Blok dışı | main netlistiyle karşılaştırma | pin→ağ değişikliği **0**; eklenen 24 ref (COUT9–COUT32) |

## Değişiklik
- COUT9–COUT32: COUT8 klonu, C5750X7S2A226M280KB 22 µF 100 V, `PDU:TDK_C5750_2220_Recommended`; pin 1 `VOUT`, pin 2 `GND` yerel etiketleri (COUT1–8 ile aynı ağlar).
- Yerleşim: sayfa üst ortası, 3 × 8 ızgara (x 171,45–260,35 mm, satırlar 27,94 / 43,18 / 58,42 mm; 1,27 mm ızgara), başlık ve notlarla çakışmıyor (SVG ile görsel kontrol).
- COUT1–8: footprint/MPN alanları spec'ten.
- RRAWBL (VRAW boşaltma direnci) B5 (koruma ayırıcı) bloğuna aittir; B3 kapsamında değil.

Not: şemadaki "AKIŞI: J1 -> F1 -> ..." açıklama metni F1'in kart dışına alınmasından önceki halidir; T-012 (antet/notlar) güncelleyecek.
