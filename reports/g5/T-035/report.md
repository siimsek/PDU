# T-035 — U15 şema sembolü pin adları

**Durum: Review.** Yalnız `PDU.kicad_sch` içindeki `74xGxx:74LVC1G11` kütüphane sembolünde pin 1, 3, 4, 6 adları boştan A, B, Y, C'ye alındı (TI SN74LVC1G11 SCES487I s.3, DBV). Sembolü yalnız U15 kullanıyor. PCB, ağ, değer ve MPN değişmedi. Düzenleme `kicad_sexpr` ile yapıldı: [apply_names.py](apply_names.py).

KiCad 10.0.7 kanıtı, [verify.json](verify.json):

| Kontrol | Sonuç |
|---|---|
| Şema satır farkı | 4 satır (`git diff --numstat`: 4 ekleme, 4 silme) |
| Netlist pin–ağ çifti | 488 → 488, fark 0 |
| Netlist `pinfunction` farkı | Yalnız U15.1/3/4/6 |
| ERC | Önce 0, sonra 0 ihlal ([erc-before.json](erc-before.json), [erc-after.json](erc-after.json)) |
| PCB parite | `pcb drc --schematic-parity` 0 |

Şema okunabilirliği iyileşti; ağ davranışı değişmedi. Simülasyon veya tezgâh kapsamı yoktur.
