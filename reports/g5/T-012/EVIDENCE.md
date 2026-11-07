# T-012 — şema bloğu B7 (test noktaları, fixture, jumper, notlar, antet) kanıtı

Düzenleme: `python scripts/sch_edit_b7.py` (B1–B6 uygulanmış main şeması). KiCad 10.0.7.

| Kontrol | Komut | Sonuç |
|---|---|---|
| ERC | `kicad-cli sch erc --format json` → [erc.json](erc.json) | **0 ihlal** |
| Netlist | `kicad-cli sch export netlist` → [netlist.net](netlist.net) | ham çıktı |
| Spec farkı | `python analysis/check_consistency.py --schematic B1 … B7` → [check-B1-B7.txt](check-B1-B7.txt) | B1–B7 **fark 0** (180 ref) |
| BOM | `python -m analysis.g2.bom` | 187 satır; satın alınan 149 satırın tamamı MPN'li; 38 PCB-only satır (TP/FIX/JP) BOM-OPEN dışında |

## Eklenenler (decisions/D-008-test-points.md)
- 36 test padi (`Connector:TestPoint`, in_bom no): ray ve prob GND padleri 2,0 mm, sinyal padleri 1,0 mm.
- J_OVP_INJ_BUS (`Connector_Generic:Conn_01x02`, in_bom no): 1 = /VOUT, 2 = /GND. **D-008'den sapma:** footprint `..._Relief2x` yerine gerilme gidermesiz `Connector_Wire:SolderWire-6sqmm_1x02_P14mm_D3.5mm_OD7mm` (aynı 6 mm² pad geometrisi; Relief2x courtyard'ı 22,5 × 92,3 mm idi ve kart alanını 2076 mm² şişiriyordu).
- JP_EN_BUCK (`Jumper:SolderJumper_2_Open`, in_bom no): 1 = /EN_BUCK, 2 = /GND, normalde açık.
- Şema notları G5 tasarımına göre yeniden yazıldı (eski metinler kart üstü F1, "eFuse OVP 16,9 V", "O1 korunması tamamlanmadı" diyordu); antet: başlık, tarih, rev G5, üretici betikler.

Görsel: test padi grupları başlık/not metinleriyle çakışmayan iki şeride yerleştirildi (SVG ile kontrol).
