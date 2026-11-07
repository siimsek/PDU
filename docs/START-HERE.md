# START HERE — IDA PDU (6S LiPo → 11 V, 7.5 A)

**Önce bunu oku → [`HANDOFF.md`](../HANDOFF.md) → aktif kart (`tasks/`, sıra [`tasks/queue.md`](../tasks/queue.md)).** Rolün: Claude Code = BUILDER ([`CLAUDE.md`](../CLAUDE.md)); Codex/ChatGPT = THINKER ([`AGENTS.md`](../AGENTS.md)); Claude sohbet = CHECKER; karar/ölçüm/birleştirme = kullanıcı. Düzen: [`WORKFLOW.md`](WORKFLOW.md).

**Hedef:** 20–26 V girişten 2 fazlı LM70880 buck ile 11 V ortak bara; 2× TPS259824L eFuse ile O1 ve S2E portları. Sert kriterler: O1 anlık ≤12,0 V, kararlı bara ≤11,1605 V, yük adımında bara ≥10,78 V, eFuse IN <30 V.

**Durum (G4 → main, 2026-11-07):** devre tasarımı hesap + SPICE + parça seviyesinde kapandı; kapı **PCB-HAZIR (koşullu)** ([`PCB-READY-v2.md`](../reports/g4/PCB-READY-v2.md)). Fiziksel ölçüm yok. KiCad dosyaları G2–G4 değişikliklerini henüz içermiyor — **sıradaki faz KiCad (G5)**, kartlar T-001…T-014.

## Geçerli mimari
Buck COUT (32×, `/VOUT`) → ortak bara seri ayırıcı (CSD19531Q5A + LM74502H; SN74LVC1G74 mandal) → `/VSAFE` → U3/U4. Mandalı üç tetik kurar (SN74LVC1G11): hassas bara OV (TLV3601 + REF5025A) ve faz 1/2 aşırı akım (INA296A2 + TLV3601, 12,97–13,60 A). Kaba OV bölücüsü LM74502H OV pininde. VOUT kart başı trim (R_TRIM). Gerekçe: [`PROTECTION-DECISION.md`](../reports/g2/PROTECTION-DECISION.md) §0.

## Dizin haritası
| Yol | Ne | Kim yazar |
|---|---|---|
| `HANDOFF.md` | tek, yuvarlanan devam notu | BUILDER |
| `tasks/` | kartlar T/R/D, `queue.md`, `backlog.md`, `BLOCKED-ON-USER.md`, `done/` | BUILDER (T), THINKER (R/D/taslak) |
| `reviews/`, `decisions/` | inceleme ve karar notları | THINKER |
| `scripts/` | `make_pack.py` (oturum paketi → `packs/`), `check_workflow.py` | BUILDER |
| `analysis/g2/` | parametre tek kaynağı `params.py`, seçimler `design.py`, hesap/sim | BUILDER |
| `design/` | netlist `pdu_v2.cir`, `bom-v2.csv`, `pdu_v2_spec.yaml`, `footprint-map.csv` | BUILDER |
| `reports/g2/` | KICAD-CHANGE-LIST-FINAL, PCB-HANDOFF, BENCH-ACCEPTANCE, DESIGN-RULES, SIM-RESULTS | BUILDER |
| `reports/g4/` | AUDIT2, N1-DECISION, PCB-READY-v2, USER-DECISIONS | (geçmiş G4) |
| `archive/` | taşınmış kanıt; yalnız `archive/INDEX.md` oku | — |

## Komutlar
| Komut | Doğrular |
|---|---|
| `python -m pytest -q` | tüm testler |
| `python analysis/run_all.py` | hesaplar + 5 SPICE ailesi + tutarlılık + iş akışı + pytest → `reports/g2/VERIFY.md` (~6 dk) |
| `python analysis/check_consistency.py` | spec ↔ BOM ↔ SPICE |
| `python scripts/check_workflow.py` | kart alanları, kuyruk, HANDOFF tazeliği, satır sınırları, bağlantılar |
| `python scripts/make_pack.py --task <ID> --for codex` | THINKER girdi paketi (sonuçsuz) |
| `"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe" sch erc / pcb drc` | baseline `reports/g4/baseline/` (ERC 0; DRC 228/197/73) |

ngspice: `PDU_NGSPICE` veya `F:\Spice64\bin\ngspice_con.exe`.

## Gerekmedikçe okuma
`archive/**`, `reports/*/sim/**`, `reports/g1/*.json`, `reports/g3/**`, SUPERSEDED başlıklı belgeler, `*.log`, `*.net`, `*.kicad_*`.
