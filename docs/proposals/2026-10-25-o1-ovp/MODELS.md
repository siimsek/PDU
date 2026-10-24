# WP1 – Model sınıflandırması

Hiçbir üretici (vendor) modeli pakete/zip'e **eklenmemiştir**; yalnız yol + sha256 ile referans verilir. TI modelleri TI lisansı (yeniden dağıtım kısıtlı) altındadır → *dağıtılmaz*.

| Model | Dosya | sha256 | Sınıf | Sürüm/Kaynak | Lisans | Bu pakette kullanım |
|---|---|---|---|---|---|---|
| O1OVP_TLV3601 | `simulation/proposals/2026-10-25-o1-ovp/pdu-o1ovp-behavioral.lib` | `62d862b4166c0348775510a72612f627d2157896d031922164fdb8bffe86588b` (tüm lib) | **Davranışsal** (ideal eşik + histerezis + gecikme, ESD diyotları) | 2026-10-25, bu paket | Repo ile aynı (öneri) | Tüm decks |
| O1OVP_REF35 | aynı lib | 〃 | **İdeal** kaynak (VREF parametresi, köşe değerleri) | 〃 | 〃 | 〃 |
| O1OVP_LDO | aynı lib | 〃 | **Davranışsal**, yalnız kaynak; akım sınırı 150 mA (gerçek TPS7A1650 100 mA – yük < 15 mA olduğundan etkisiz, not) | 〃 | 〃 | 〃 |
| O1OVP_TPS48000 | aynı lib | 〃 | **Davranışsal** (TDON/TDOFF/TDOV iletim hattı gecikmeleri, IPU/IPD, BST UVLO, CP off; INP lojik eşiği 1,35/1,45 V – veri sayfası 0,8/2 V sınırları içinde) | 〃 | 〃 | 〃 |
| O1OVP_NFET | aynı lib | 〃 | **Davranışsal** anahtar (RON, VTH, CGS, CDS 1,24 nF tipikten türetildi; çığ/avalanche **modellenmedi**) | 〃 | 〃 | 〃 |
| Baseline buck/eFuse | `simulation/pdu-behavioral.lib`, `pdu-protection.inc`, `pdu-circuit.inc` | `9fa5c122…74c0`/`0846d2f6…8a5f`/`e167560c…a826` (tam değerler `o1ovp-results.json` → `baseline_sha256`) | **Davranışsal** (repo baseline, değiştirilmedi) | repo `a1dbeeb` | Repo | Include ile |
| Indüktör | `simulation/pdu-inductor-ng.lib` / `-lt.lib` | `5be12648…7480` / `f93036cc…09eb` | Davranışsal (repo) | repo | Repo | Include ile |
| TI TLV3601 PSpice | `/workspace/ds/models/SBOMBZ3.zip` | `93b68e5230d3cfacc95a4aefea6c7eb4cfb7c7047fd452bd4f5566c2ceb57e7e` | Üretici (PSpice) | TI SBOMBZ3 | TI – yeniden dağıtılamaz | **Kullanılmadı** (yalnız referans) |
| TI TLV3601 TINA | `/workspace/ds/models/SNOM713.zip` | `a146f84f1a876baf288b0a4139a46c6211d9b1a9aee172d66085623df799a75b` | Üretici (TINA) | TI SNOM713 | TI | Kullanılmadı |
| TI TPS48000-Q1 PSpice | `/workspace/ds/models/SLUM909.zip` | `befcaabf40be13e5a1f35b8e29d04d063fa9e0014f9e9c1cd6078d312efa164a` | Üretici (PSpice, şifreli olabilir) | TI SLUM909 | TI | Kullanılmadı |
| TI CSD18540Q5B PSpice | `/workspace/ds/models/SLPM129.zip` | `a336ce2682ceca5845584dc7c9469e7c640dbed0e68d66c36923e997a2be8b88` | Üretici | TI SLPM129 | TI | Kullanılmadı |
| TI CSD18540Q5B TINA | `/workspace/ds/models/SLPM227.zip` | `a120f5f27eb74641ee455840f4409ae843a04f81ba72689b3e1a176c538db1e4` | Üretici | TI SLPM227 | TI | Kullanılmadı |

**Sim ≠ silikon:** Tüm sonuçlar davranışsal/ideal modellere dayanır. Parazitik endüktans, PCB yerleşimi, FET çığ davranışı ve gerçek TPS48000 kapı sürüş dalga formu modellenmemiştir.
