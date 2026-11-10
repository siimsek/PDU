# T-006 — KiCad 10 ERC/netlist kanıtı (R-004 engelleyicisinin kapatılması)

R-004 (Codex, KOŞULLU): THINKER ortamında KiCad 9.0.2 var ve KiCad 10 şemasını açamıyor; ERC/netlist bağımsız üretilemedi. Kapatma: KiCad **10.0.7** ham çıktıları repoya eklendi; THINKER bu metin dosyalarını KiCad olmadan da ayrıştırıp doğrulayabilir.

| Dosya | Komut (`C:\Program Files\KiCad\10.0\bin\kicad-cli.exe`) | Çıkış | Sonuç |
|---|---|---|---|
| [kicad-cli-version.txt](kicad-cli-version.txt) | `version` | 0 | 10.0.7 |
| [erc.json](erc.json) | `sch erc --format json PDU.kicad_sch` | 0 | **0 ihlal** (baseline 0) |
| [netlist.net](netlist.net) | `sch export netlist --format kicadsexpr PDU.kicad_sch` | 0 | F1 yok; J1.1 = /ANODE; U5 1 VCAP→/VCAP, 2 GND→/GND, 3 EN→/ANODE, 4 CATHODE→/VIN, 5 GATE→/GATE, 6 ANODE→/ANODE (TI Tablo 5-1); D1 K→/VIN, A→/GND (D-007); Q1 S→/ANODE, G→/GATE, D→/VIN |
| [check-B1.txt](check-B1.txt) | `python analysis/check_consistency.py --schematic B1` | 0 | B1 16 ref, spec ile **fark 0** (footprint, MPN, pin→ağ) |

D-007 uygulandı: spec/BOM D1.K = /VIN, SPICE `DTVS 0 vin`; 5 SPICE ailesi yeniden koşuldu (`reports/g2/SIM-RESULTS.md`).
