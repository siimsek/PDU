# G5 — KiCad-HAZIR kapısı (T-014)

Tarih 2026-11-07. main @ `3cedd08` (PR #49–#51 sonrası), KiCad 10.0.7. Etiketler: HESAP / DATASHEET / SİM / VARSAYIM / AÇIK. Simülasyon fiziksel kanıt değildir. Biçim: [`reports/g4/PCB-READY-v2.md`](../g4/PCB-READY-v2.md).

## Sonuç: **PCB-YÖNLENDİRMEYE-HAZIR (koşullu)**

Elektriksel ve KiCad maddeleri geçti. Şema 180 ref ile spec'e birebir, ERC 0. Kart 120 × 85 mm, 4 katman; 180 ayak izi ve parite 0; kurallar yüklü boş kart DRC'si 0 hata; kural dosyası routing-g2 ile aynı. run_all exit 0; SPICE'ta F5'in bilinen iki köşesi tamamlanmadı (AÇIK, backlog). Tek KALDI maddesi belge (madde 8): START-HERE durum satırı G4'te kaldı ve main'deki `reports/g2/VERIFY.md` eski F5 sayısını (49/49) gösteriyor. Bu kart bu dosyalara yazamaz; düzeltme ayrı küçük bir kartla yapılmalı. Yönlendirmeyi engellemez.

| # | Madde | Komut | Çıkış özeti | Sonuç |
|---|---|---|---|---|
| 1 | pytest | `python -m pytest -q` | 133 passed in 10.10s | **GEÇTİ** |
| 2 | run_all | `python analysis/run_all.py` → [VERIFY-run_all.md](T-014/VERIFY-run_all.md), [sim-summary.json](T-014/sim-summary.json) | exit 0; 12/12 adım exit 0; süre 37m27.254s. SPICE: F1 7/7 tamam, 6 PASS; F2 4/4 tamam, 4 PASS; F3 13/13 tamam, 11 PASS; F4 3/3 tamam, 2 PASS; F5 47/49 tamam, 47 PASS. F5'in 2 koşusu tamamlanmadı (her biri 900 s zaman aşımı → süre): `run_all` içindeki pytest `test_sim_bom.py` eksik kümenin tam olarak bilinen AÇIK iki köşe olduğunu doğruladı (`KNOWN_INCOMPLETE`). F1/F3/F4 FAIL'leri beklenen referans/trimsiz/D_REV'siz koşular | **GEÇTİ (koşullu: F5 2 köşe AÇIK)** |
| 3 | ERC | `kicad-cli sch erc --format json --severity-all` → [erc.json](T-014/erc.json) | 0 ihlal | **GEÇTİ** |
| 4 | Şema ↔ spec | `check_consistency.py --schematic B1…B7` → [check-B1-B7.txt](T-014/check-B1-B7.txt); `check_consistency.py` | {"blocks": ["B1", "B2", "B3", "B4", "B5", "B6", "B7"], "pass": true, "n_errors": 0}; düz: {"pass": true, "n_errors": 0} | **GEÇTİ** |
| 5 | Footprint | `python analysis/check_footprints.py` → [check_footprints.txt](T-014/check_footprints.txt) | exit 0; 6 PASS, 0 FAIL | **GEÇTİ** |
| 6 | DRC kuralları + boş kart | şema ayak izleri çıkarılmış kopya + PDU.kicad_pro/.kicad_dru → `kicad-cli pcb drc` → [drc-empty.json](T-014/drc-empty.json); `pcb_rules.py --check` | boş kart 0 öğe; kural ↔ routing-g2 {"pass": true, "errors": []} | **GEÇTİ** |
| 6b | Yerleşimli kart (bilgi) | `kicad-cli pcb drc --schematic-parity` → [drc-placed.json](T-014/drc-placed.json); darboğaz denetimi | parite 0; hatalar {'error:unconnected_items': 402} (iz yok, beklenen); uyarı 413 silkscreen; neck violations: 0 | **GEÇTİ (bilgi)** |
| 7 | KiCad dosya kapsamı | `git diff --name-only 219a2c1..HEAD` (G5 tabanı) ve `main..HEAD` | G5'te değişen: `PDU.kicad_dru`, `PDU.kicad_pcb`, `PDU.kicad_pro`, `PDU.kicad_sch`, `hardware/lib/PDU.kicad_sym`, `hardware/lib/PDU.pretty/TI_CSD19531Q5A_Q5A.kicad_mod`; main..HEAD: boş (kapı dalı KiCad dosyası değiştirmiyor) | **GEÇTİ** |
| 8 | Belgeler güncel | `grep -c T-013/T-012` START-HERE, KICAD-CHANGE-LIST-FINAL, HANDOFF | docs/START-HERE.md T-013:0 T-012:0; reports/g2/KICAD-CHANGE-LIST-FINAL.md T-013:0 T-012:1; HANDOFF.md T-013:2 T-012:2. HANDOFF güncel; KICAD-CHANGE-LIST şema değişikliklerinde T-012'ye kadar güncel (PCB kurulumu PCB-SETUP.md'de, liste atıf vermiyor); **START-HERE durum satırı G4'te kalmış** ("KiCad dosyaları G2–G4 değişikliklerini henüz içermiyor"); main'deki `reports/g2/VERIFY.md` F5 için D-007 öncesi "49/49" gösteriyor, bu koşu 47/49 | **KALDI (belge)** |
| 9 | İş akışı | `python scripts/check_workflow.py` | check_workflow: 0 hata, 1 uyarı (reports/g2 geri alındıktan sonra) | **GEÇTİ** |

### run_all adımları

| Adım | Çıkış | Süre (s) |
|---|---:|---:|
| protection (Stage 2) | 0 | 0.8 |
| power stage / ILIM / UVLO / input (Stage 3) | 0 | 0.2 |
| loop analytic + ngspice AC (Stage 4) | 0 | 6.2 |
| N1 phase-OC trip / L(i) (G4 B1) | 0 | 4.6 |
| stacked tolerance + trim (G4 B4) | 0 | 0.1 |
| gm / UVLO open assumptions (G4 B5) | 0 | 1.3 |
| routing inputs (Stage 6) | 0 | 0.1 |
| BOM v2 / spec / footprint map (Stage 6, G4 C) | 0 | 0.1 |
| spec <-> BOM <-> SPICE consistency (G4 C3) | 0 | 0.1 |
| full-system ngspice families F1-F5 (Stage 5) | 0 | 2222.3 |
| workflow check (W0) | 0 | 0.2 |
| pytest (all) | 0 | 11.4 |

## Koşullar (yönlendirmeyi engellemez; tasarım kabulünü veya üretimi etkiler)

1. **Belge (madde 8):**
   - START-HERE durum satırı G5'e (şema tamam, PCB kurulu, sıradaki yönlendirme) güncellenmeli.
   - `reports/g2/VERIFY.md` ve `sim-results.json` güncel koşuyla yeniden yazılmalı (F5 47/49, bu karttaki VERIFY-run_all.md). Bu kart `reports/g2/` yoluna yazamadığı için run_all'un yeniden yazdığı dosyalar geri alındı.
   - KICAD-CHANGE-LIST-FINAL'e T-013 PCB kurulumu atfı (netclass adları O1_PORT/S2E_PORT, PCB-SETUP.md) eklenebilir.
2. **Fiziksel ölçüm yok:** U-001 ve U-007 tezgâh ölçümleri ile BENCH-ACCEPTANCE T-1, T1b, T5c, T5g kart üretilince yapılacak.
3. **SİM AÇIK:** F5'in iki köşesi tam pencerede tamamlanmadı (kısaltılmış pencerede O1 10,92 V; backlog).
4. **VARSAYIM / AÇIK (PCB):** stackup (prepreg 0,2 / çekirdek 1,04, 1 oz tüm katmanlar) üretici DFM onayı bekliyor. Montaj delikleri ve keep-out muhafaza bilinmediği için varsayım. Paket içi pad 0,15 mm DFM varsayımı.
5. **Yönlendirme kartına devredilen işler:**
   - kaba yerleşimden ayrıntılı yerleşime geçiş (sıcak döngü, RS Kelvin, GATE ≤10 mm, INA296 ≤15 mm),
   - 413 silkscreen uyarısı,
   - güç ağı ölçüm uçlarının sınıf min kuralına takılması (backlog: net-tie veya gerekçeli muafiyet),
   - Q1/Q2 ≥645 mm² bakır, LM70880 EP via dizisi, L2/L3 dökümleri.

## Kanıt dosyaları

`reports/g5/T-014/`: erc.json, netlist.net, check-B1-B7.txt, check_footprints.txt, drc-empty.json, drc-placed.json. T-013 kurulum kanıtı: [`PCB-SETUP.md`](PCB-SETUP.md).

Not: run_all `reports/g2/VERIFY.md`, `reports/g2/sim-results.json` ve `reports/g2/sim/**` dosyalarını yeniden yazar. Bu kartın izinli yolu olmadığı için `git checkout -- reports/g2` ile geri alındı. Koşunun özeti `T-014/VERIFY-run_all.md` ve `T-014/sim-summary.json` dosyalarında.
