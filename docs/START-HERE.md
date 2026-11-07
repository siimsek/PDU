# START HERE — IDA PDU (6S LiPo → 11 V, 7.5 A)

**Hedef:** 20–26 V girişten 2 fazlı LM70880 buck ile 11 V ortak bara; 2× TPS259824L eFuse ile O1 ve S2E portları. Sert kriterler: O1 anlık ≤12.0 V, kararlı bara ≤11.1605 V, yük adımında bara ≥10.78 V, eFuse IN <30 V.

**Durum (G4, 2026-11-07):** devre tasarımı hesap + SPICE + parça seviyesinde kapandı (BOM 146/147 MPN; tek açık F1). **Fiziksel ölçüm yok.** KiCad dosyaları henüz G2–G4 değişikliklerini içermiyor — sıradaki faz KiCad aktarımı. Kapı: [`reports/g4/PCB-READY-v2.md`](../reports/g4/PCB-READY-v2.md).

## Geçerli mimari (tek seçim)
Buck COUT (32×, `/VOUT`) → **ortak bara seri ayırıcı** (CSD19531Q5A, LM74502H; mandal SN74LVC1G74) → `/VSAFE` → U3/U4 IN. Mandalı üç tetik kurar (SN74LVC1G11): hassas bara OV (TLV3601 + REF5025A), **faz 1 ve faz 2 aşırı akım** (INA296A2 + TLV3601, 12.97–13.60 A). Bağımsız kaba OV bölücüsü LM74502H OV pininde. VOUT kart başı trim (R_TRIM). Gerekçe: [`PROTECTION-DECISION.md`](../reports/g2/PROTECTION-DECISION.md) §0, [`N1-DECISION.md`](../reports/g4/N1-DECISION.md).

## Doğruluk kaynakları
| Ne | Dosya |
|---|---|
| Parametre tek kaynağı (datasheet sayfalı) / seçilen değerler | `analysis/g2/params.py` / `analysis/g2/design.py` |
| Tam sistem netlisti | `design/pdu_v2.cir` |
| BOM / şema özeti / footprint haritası | `design/bom-v2.csv`, `design/pdu_v2_spec.yaml`, `design/footprint-map.csv` |
| KiCad'e yapılacak değişiklikler | `reports/g2/KICAD-CHANGE-LIST-FINAL.md` (G4 bölümü önce) |
| PCB kuralları / tezgâh planı / kurallar | `reports/g2/PCB-HANDOFF.md`, `BENCH-ACCEPTANCE.md`, `DESIGN-RULES.md` |
| Denetim, kapı, kullanıcı kararları | `reports/g4/AUDIT2.md`, `reports/g4/PCB-READY-v2.md`, `reports/g4/USER-DECISIONS.md` |

## Komutlar
| Komut | Doğrular |
|---|---|
| `python -m pytest -q` | tüm hesap/kanıt testleri (G1 + G2 + G4) |
| `python analysis/run_all.py` | hesaplar + N1/B4/B5 + 5 SPICE ailesi + tutarlılık + pytest → `reports/g2/VERIFY.md` (~5 dk) |
| `python analysis/run_all.py --skip-sim` | yalnız hesaplar + pytest |
| `python analysis/check_consistency.py` | spec ↔ BOM ↔ SPICE parametreleri |
| `"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe" sch erc / pcb drc` | baseline: `reports/g4/baseline/` |

ngspice: `PDU_NGSPICE` ortam değişkeni veya `F:\Spice64\bin\ngspice_con.exe` (Linux: PATH'teki `ngspice`).

## Açık kalemler (özet)
Fiziksel kabul (T-1, T0–T6; özellikle T1b trim, T5c, T5g), F1 MPN/kesme kapasitesi, INA296 gecikmesi (yalnız tipik), L(I) >16 A, EA gm maks, UVLO düşüş eşiği, Q_ISO D-S kısası (tek nokta). Liste: `reports/g4/PCB-READY-v2.md`.

## Okuma haritası
- **Okunacak:** bu dosya, `AGENTS.md`, yukarıdaki tablo.
- **Gerekmedikçe okuma:** `archive/` (`archive/INDEX.md` yeter), `reports/g*/sim/` (özet `SIM-RESULTS.md`), `reports/g1/*.json`, `reports/g3/` (G3 geçmişi), SUPERSEDED başlıklı belgeler.
