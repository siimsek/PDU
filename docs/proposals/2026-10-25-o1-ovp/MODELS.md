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
| RAW bankı (rev2: COUT1–8 + COUT21–28) | `pdu-circuit-o1ovp.inc` (16 × `{2.2e-05*CBIAS}`); kısa-devre decklerinde `Craw {CRAW}` + `Resr {ESR}` | `input_sha256` (o1ovp-results.json) | **İdeal** C + seri ESR (DC-bias/sıcaklık/yaşlanma köşe parametresiyle: CRAW 185,3 µF / 483 µF; CBIAS 0,5 / 1,372) | bu paket | Repo | Tüm decks |
| TDK C5750X7S2A226M280KB SPICE | https://product.tdk.com/system/files/dam/tvcl/capacitor/ceramic/mlcc/spice_p/commercial_midvoltage/c5750/c5750x7s2a226m280kb_p.mod | – (bu kutuda indirilmedi) | Üretici (frekans/bias modeli) | TDK | TDK kullanım koşulları – dağıtılmaz | **Kullanılmadı**; 20,622 µF @ 11 V değeri `hardware/COUT-qualification.md` kaynaklı |
| Indüktör | `simulation/pdu-inductor-ng.lib` / `-lt.lib` | `5be12648…7480` / `f93036cc…09eb` | Davranışsal (repo) | repo | Repo | Include ile |
| TI TLV3601 PSpice | `/workspace/ds/models/SBOMBZ3.zip` | `93b68e5230d3cfacc95a4aefea6c7eb4cfb7c7047fd452bd4f5566c2ceb57e7e` | Üretici (PSpice) | TI SBOMBZ3 | TI – yeniden dağıtılamaz | **Kullanılmadı** (yalnız referans) |
| TI TLV3601 TINA | `/workspace/ds/models/SNOM713.zip` | `a146f84f1a876baf288b0a4139a46c6211d9b1a9aee172d66085623df799a75b` | Üretici (TINA) | TI SNOM713 | TI | Kullanılmadı |
| TI TPS48000-Q1 PSpice | `/workspace/ds/models/SLUM909.zip` | `befcaabf40be13e5a1f35b8e29d04d063fa9e0014f9e9c1cd6078d312efa164a` | Üretici (PSpice; okunabilir – kapı deşarjı PD = 2 Ω **tipik** eşdeğer) | TI SLUM909 | TI | Kullanılmadı; yalnız P0-3 tipik karşılaştırma notu |
| TI CSD18540Q5B PSpice | `/workspace/ds/models/SLPM129.zip` | `a336ce2682ceca5845584dc7c9469e7c640dbed0e68d66c36923e997a2be8b88` | Üretici | TI SLPM129 | TI | **ngspice-44.2'de fiziksel olmayan sonuç** (rev1 denemesi) → kullanılmadı; PSpice'ta değerlendirme WP2 |
| TI CSD18540Q5B TINA | `/workspace/ds/models/SLPM227.zip` | `a120f5f27eb74641ee455840f4409ae843a04f81ba72689b3e1a176c538db1e4` | Üretici | TI SLPM227 | TI | Kullanılmadı |
| TI TPS259824O (U3/U4 eFuse) PSpice Transient | `/workspace/ds/models/SLVMD37/` (zip) ; lib `tps259824onrge_trans.lib` | zip `8697208e8f8a7a0a15a51975efc0329813c01fb7e3ea72d9e1775a9ae8fd70f1`; lib `e0a6016a6de96077eddc70f3a475bcf5ffbb30e1903ff7dad246769b4a841b88` | Üretici – **Cadence şifreli ($CDNENCSTART)** | TI SLVMD37, "Final 1.30", 24APR2019; sıcaklık bağımlılığı modellenmemiş (model notu) | TI – dağıtılamaz | **ngspice'ta çalıştırılamaz** → P0-4 karşılaştırması PSpice veya tezgâh (B13) gerektirir. Diğer TPS25982 modelleri: SLVMD20–23, 36, 38A, 39 (indirilmedi) |

**Sim ≠ silikon:** Tüm sonuçlar davranışsal/ideal modellere dayanır. Parazitik endüktans, PCB yerleşimi, FET çığ davranışı ve gerçek TPS48000 kapı sürüş dalga formu modellenmemiştir.

## rev2 ekleri
- **eFuse (U3/U4) modeli:** Paket ve baseline, repo'daki **davranışsal** eFuse'u (RON 2,7 mΩ tipik, geçiş anahtarı) kullanır. Gerçek TPS259824O'nun OVP'si VOVP(R) **16,32 V min** (SLVSEI3D) olduğundan O1'i 12 V'ta korumaz; tOVP yalnız tipik (5 µs). O1 ≤ 12 V iddiası **RAW tepe değerine** dayanır: rezistif geçiş elemanı + kapasitif/rezistif yük ile O1(t) ≤ max RAW (negatif olmayan dürtü yanıtlı RC ağı – Ç sınıfı çıkarım). Yerleşim endüktansı/çınlama modellenmedi → tezgâh B13.
- **LTspice bulut ortamında çalıştırılmadı.** Tüm koşular ngspice-44.2 (`/usr/bin/ngspice`, Debian 13) ile.
- **Bağımlılıklar:** python3 (yalnız standart kütüphane) + ngspice. CI'da `ubuntu-latest` apt ngspice sürümü farklı olabilir (sürüm farkı → sayısal küçük farklar; doğrulayıcı aynı kriterleri uygular).
- **C bankı modeli (P1-1):** kısa devre decklerinde `Craw {CRAW}` + `Resr {ESR}` (+ ESL köşesinde `Lesl 2n`, **V** varsayım). Değerler: 185,3 µF (ürün min.), 176 µF (CBIAS 0,5 kart deckleri), **165 µF (dürüst min.)**, 483 µF (maks.), 92,65 µF (rev1 bilgi). ESR 1 / 12,5 mΩ (+100 mΩ stres).
