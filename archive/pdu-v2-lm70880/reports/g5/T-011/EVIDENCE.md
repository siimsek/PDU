# T-011 — şema bloğu B6 (eFuse'lar ve çıkış portları) kanıtı

Düzenleme: `python scripts/sch_edit_b6.py` (B1–B5 uygulanmış main şeması üzerinde). KiCad 10.0.7.

| Kontrol | Komut | Sonuç |
|---|---|---|
| ERC | `kicad-cli sch erc --format json` → [erc.json](erc.json) | **0 ihlal** (PWR_FLAG #FLG05 /VSAFE'e eklenmeden önce 1: U3/U4 IN güç pinleri sürülmüyordu) |
| Netlist | `kicad-cli sch export netlist` → [netlist.net](netlist.net) | ham çıktı |
| Spec farkı | `python analysis/check_consistency.py --schematic B1 B2 B3 B4 B5 B6` → [check-B1-B6.txt](check-B1-B6.txt) | B1–B6 **fark 0** |
| Tam şema | spec'teki tüm PCB ref'leri (142) ↔ şema | şemada eksik 0, spec'te olmayan 0, **tam fark 0** |
| Blok dışı | main netlistiyle karşılaştırma | pin→ağ değişikliği **0**; eklenen D_REV1, D_REV2 |

## Değişiklikler
- U3/U4 IN düğümleri (IN pinleri + CEFIN1/2) ve REN1 üst ucu: `VOUT` → `VSAFE` etiketi (ortak bara ayırıcı çıkışı).
- D_REV1/D_REV2 (SS34-E3/57T, D_SMC): A = O1_11V / S2E_11V, K = VSAFE (ters yol, R16).
- RILIM1 182 Ω, RILIM2 300 Ω; CEFOUT1/2 1206 (C3216X7R1E106K160AB); D2/D3 D_SMC (SS34); J2 Molex 46015-0206 footprint; U3/U4 MPN/Value TPS259824LNRGER; REN2 değer "10k"; tüm B6 MPN alanları; eski parça meta alanları temizlendi.
- PWR_FLAG #FLG05 /VSAFE üzerinde.
- Spec: RPG1/RPG2 pin sırası şemadaki çizime uyduruldu (direnç, elektriksel fark yok).

Kalan: T-012 (test noktaları, J_OVP_INJ_BUS / JP_EN_BUCK, notlar ve antet — şemadaki "J1 -> F1" metni, pasif yazı yerleşimi).

## R-010 düzeltmesi
Kanonik Value kuralı: şemadaki her sembolün Value'su spec değeriyle aynı (`scripts/sch_values.py`; D1, U1, U2, U3, U4, U5, Q1, D2, D3, J1, J2, J3 eşitlendi). `check_consistency.py --schematic` tüm Value dizgelerini karşılaştırıyor → B1–B6 fark 0; ERC 0 (yeniden üretildi).
