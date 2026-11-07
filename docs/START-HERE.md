# START HERE — IDA PDU (6S LiPo → 11 V, 7.5 A)

**Hedef:** 20–26 V girişten 2 fazlı LM70880 buck ile 11 V ortak bara; 2× TPS259824L eFuse ile O1 ve S2E portları. Sert kriterler: O1 anlık ≤12.0 V, kararlı bara ≤11.1605 V, yük adımında bara ≥10.78 V, eFuse IN <30 V.

**Durum (G3, 2026-11-07):** devre tasarımı hesap + SPICE + parça seviyesinde tamam; **fiziksel ölçüm yok**. KiCad dosyaları henüz G2/G3 değişikliklerini içermiyor — sıradaki faz KiCad aktarımı. Kapı: [`reports/g3/PCB-READY.md`](../reports/g3/PCB-READY.md).

## Geçerli mimari (tek seçim)
Buck COUT (`/VOUT`) → **ortak bara seri ayırıcı** (CSD19531Q5A, LM74502H sürücü; TLV3601 + REF5025A + SN74LVC1G74 mandal; bağımsız kaba OV bölücüsü) → `/VSAFE` → U3/U4 IN. Yedek: G1 LTC7001 zinciri (gecikme garanti edilemez). Gerekçe: [`reports/g2/PROTECTION-DECISION.md`](../reports/g2/PROTECTION-DECISION.md).

## Doğruluk kaynakları (oku)
| Ne | Dosya |
|---|---|
| Parametre tek kaynağı (datasheet sayfalı) | `analysis/g2/params.py`, seçilen değerler `analysis/g2/design.py` |
| Tam sistem netlisti | `design/pdu_v2.cir` |
| BOM / şema özeti / açık MPN | `design/bom-v2.csv`, `design/pdu_v2_spec.yaml`, `reports/g2/BOM-OPEN.md` |
| KiCad'e yapılacak değişiklikler | `reports/g2/KICAD-CHANGE-LIST-FINAL.md` |
| PCB kuralları / tezgâh planı | `reports/g2/PCB-HANDOFF.md`, `reports/g2/BENCH-ACCEPTANCE.md` |
| Tasarım kuralları ve durumları | `reports/g2/DESIGN-RULES.md` |
| Denetim ve kapı | `reports/g3/AUDIT.md`, `reports/g3/PCB-READY.md` |
| Kullanıcı kararları | `reports/g3/USER-DECISIONS.md` |

## Komutlar
| Komut | Doğrular |
|---|---|
| `python -m pytest -q` | tüm hesap/kanıt testleri (G1 + G2) |
| `python analysis/run_all.py` | G2 hesapları + 5 SPICE ailesi + pytest → `reports/g2/VERIFY.md` (~5 dk) |
| `python analysis/run_all.py --skip-sim` | yalnız hesaplar + pytest |
| `"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe" sch erc / pcb drc` | baseline: `reports/g3/baseline/` |

ngspice: `PDU_NGSPICE` ortam değişkeni veya `F:\Spice64\bin\ngspice_con.exe` (Linux: PATH'teki `ngspice`).

## Açık kalemler (özet)
Fiziksel kabul (T0–T6), yığılmış tolerans + yük adımı köşeleri, LM70880 termali (ortam sıcaklığı), MPN'siz 43 BOM satırı (MLCC, F1, TVS, konnektör, buton), artık tek-nokta arızaları. Liste: `reports/g3/PCB-READY.md` §Fiziksel kabul.

## Okuma haritası
- **Okunacak:** bu dosya, `AGENTS.md`, yukarıdaki tablo.
- **Gerekmedikçe okuma:** `archive/` (taşınmış kanıt; `archive/INDEX.md`), `reports/g2/sim/` ve `reports/g1/sim/` (deck/log; özet `SIM-RESULTS.md`), `reports/g1/*.json`, SUPERSEDED başlıklı belgeler.
