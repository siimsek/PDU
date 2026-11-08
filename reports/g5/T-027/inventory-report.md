# T-027 — Şematik referans ve pin kapsam envanteri

**Durum: Review.** Envanter tasarımı değiştirmez. Kaynak commit `90cff8bb7e4e0b0373a5e39ab01847637c98557e`; KiCad 10.0.7. Karşılaştırılan ikinci kart: `40e0a7bed18f7297445f11df8741501eedac88a8` (T-023 dalı).

Komut (depo kökünden): `python scripts/sch_inventory.py --alt-pcb <git-rev>`. Girdi: `kicad-cli sch export netlist --format kicadsexpr` ([netlist.net](netlist.net)), `design/bom-v2.csv`, `design/footprint-map.csv`, `design/pdu_v2_spec.yaml`, `PDU.kicad_pcb`, `design/pdu_v2.cir`. Defterler: [ledger-references.csv](ledger-references.csv), [ledger-pins.csv](ledger-pins.csv), özet [inventory-summary.json](inventory-summary.json).

## Sayılar

| Ölçüm | Değer | Kaynak |
|---|---:|---|
| Şema referansı | 180 | netlist `comp` |
| Şema pini | 488 | netlist `node` |
| Sembol UUID | 180 | netlist `tstamps`; çok birimli referans yok |
| Kayıtsız referans / pin | 0 / 0 | defter karşılaştırması |
| Kart padiyle eşleşen pin | 488 / 488 | `PDU.kicad_pcb` pad ağları |
| T-023 kartına göre pad ağı farkı | 0 | `40e0a7b` |
| Kasıtlı NC pin | 13 | pin tipi `no_connect` |
| BOM satırı | 187 | `bom-v2.csv` |
| Kart ayak izi | 184 | `PDU.kicad_pcb` |

| Sınıf | Referans |
|---|---:|
| elektriksel parça | 140 |
| DNP | 2 |
| test/injection (BOM dışı, D-008) | 38 |

## Sayı farklarının nedeni

- **187 BOM satırı, 180 şema referansı:** BOM'da olup şemada olmayan 7 satırın tümü `CABLE` (kart dışı): CT1, CT2, F1, P1, P2, P3, XF1. Şemada olup BOM'da olmayanlar 38 test/enjeksiyon referansı (D-008).
- **184 kart ayak izi:** H1, H2, H3, H4 montaj delikleri, şemada yok.
- **488 pin ile önceki 422 anahtar:** 422 spec pin anahtarı + 26 spec dışı düğüm + 40 test/enjeksiyon pini = 488.

## Uyuşmazlıklar

| Referans | Değer | Neden |
|---|---|---|
| C_LDO_DELAY | 10n | DNP farkı: şema False, BOM True |
| C_REF_NR | 1u | DNP farkı: şema False, BOM True |

Her iki parça `design/bom-v2.csv` içinde `dnp=True`, şemada `dnp no`. Kart kapsamı tasarımı değiştirmez; hangisinin doğru olduğu **doğrulanamadı**. Karar THINKER'da (D-kartı gerekir). Şemada DNP olmadığı için üretim çıktısında yerleşebilir.

## SPICE eşlemesi

| Durum | Referans |
|---|---:|
| SPICE'ta ad eşleşmesi yok: doğrulanamadı | 165 |
| SPICE elemanı (ad eşit) | 10 |
| SPICE metninde geçiyor, eleman adı değil: doğrulanamadı | 5 |

SPICE dosyası şema referanslarıyla aynı adları kullanmıyor; yalnız ad eşitliğine dayanılabildi. Geri kalanı model eşlemesi kanıtlanmadığı için **doğrulanamadı** kaldı, başarı sayılmadı. Eşleme tablosu T-028/T-029 için girdi eksiğidir.

## Sınırlar

- Pin adı ve tipi şema sembolünden gelir; üretici datasheet'iyle pin-pin denetimi T-028 kapsamındadır.
- `EŞLEŞTİ`, pin ağı ile kart pad ağının aynı olduğu anlamına gelir; elektriksel doğruluk değildir.
