# G2 ilerleme kaydı

Dal: `wp/g2-circuit-design` (taban `wp/g1-ai-analysis` @ `77c98dd`, G1 kapanış commit'i push edildi). `*.kicad_*` dosyalarına dokunulmaz. `analysis/generate_g1_reports.py` çalıştırılmaz.

Context sıfırlanırsa: bu dosyadaki son aşamanın "açık işler" listesinden devam et. Tüm hesap/sim tek komutla: `python analysis/run_all.py` (Aşama 6'da eklenir).

## Aşama 0 — kurulum (2026-11-07)

- `git status -sb`: temiz. `git pull --ff-only`: güncel. G1 `77c98dd` → `origin/wp/g1-ai-analysis` push edildi (force yok).
- `python -m pytest -q`: **63 passed** (başlangıç).
- ngspice: `F:\Spice64\bin\ngspice_con.exe` (ngspice-47). `PDU_NGSPICE` env yoksa bu yol kullanılır.
- Datasheet erişimi: TI ve Vishay PDF'leri indirildi ve `pdftotext` ile okundu. **ADI (analog.com) ve Molex sunucuları bağlantıyı reddetti** → LTC7001, LTC4368, Molex PS-43045 bu turda **doğrulanamadı** (USER-DECISIONS'a eklendi).

## Aşama durumları

| Aşama | Durum | Ana çıktı |
|---|---|---|
| 1 Tasarım kural kataloğu | tamam | `DESIGN-RULES.md` |
| 2 Koruma mimarisi | bkz. aşağı | `PROTECTION-DECISION.md` |
| 3 Güç katı hesabı | bkz. aşağı | `POWER-STAGE.md` |
| 4 Döngü kararlılığı | bkz. aşağı | `LOOP-STABILITY.md` |
| 5 Tam sistem SPICE | bkz. aşağı | `SIM-RESULTS.md`, `design/pdu_v2.cir` |
| 6 BOM + PCB devri | bkz. aşağı | `design/bom-v2.csv`, `PCB-HANDOFF.md`, `VERIFY.md` |

## Kararlar günlüğü

- K1 (Aşama 2 girdisi): Varsayılanlar — O1 ≤12.0 V sert; O1 hatasında S2E birlikte kapanır; hata sonrası mandallı, yalnız güç döngüsü/manuel reset; ILIM zarfı (O1+S2E garantili-min ≥7.5 A); batarya+kablo direnci 20–200 mΩ taraması.

## Açık işler

(her aşama sonunda güncellenir)
