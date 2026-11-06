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
| 2 Koruma mimarisi | tamam (COUT sayısı Aşama 4'te) | `PROTECTION-DECISION.md` |
| 3 Güç katı hesabı | tamam | `POWER-STAGE.md` |
| 4 Döngü kararlılığı | bkz. aşağı | `LOOP-STABILITY.md` |
| 5 Tam sistem SPICE | bkz. aşağı | `SIM-RESULTS.md`, `design/pdu_v2.cir` |
| 6 BOM + PCB devri | bkz. aşağı | `design/bom-v2.csv`, `PCB-HANDOFF.md`, `VERIFY.md` |

## Kararlar günlüğü

- K1 (Aşama 2 girdisi): Varsayılanlar — O1 ≤12.0 V sert; O1 hatasında S2E birlikte kapanır; hata sonrası mandallı, yalnız güç döngüsü/manuel reset; ILIM zarfı (O1+S2E garantili-min ≥7.5 A); batarya+kablo direnci 20–200 mΩ taraması.

- K2 (Aşama 2): Seçim A = TLV3601DCKR + REF5025AQDRQ1 + SN74LVC1G74DCUR → LM74502HDDFR OV pini → CSD19531Q5A; kaba OV bölücüsü 64.9k/24.9k aynı OV pinine. Yedek B = G1 LTC7001 zinciri (gecikme garanti edilemez). C (yalnız LM74502H OV) eşik penceresi nedeniyle elendi. Hassas bölücü 8.25k/2.32k TNPW1206 0.1 % 10 ppm/K → trip 11.2737–11.5219 V. O1 bütçesi 16× COUT ile 11.926 V.

- K3 (Aşama 3): COUT 16× C5750 (Aşama 4'te teyit), RILIM 182/300 Ω (garantili-min toplam 11.59 A), RUV1 174k TNPW 0.1 % (17.365–19.623 V), RS WSL25127L500FEA, L IHLP4040DZER6R8M01. LM70880 Tj 85 °C ortamda 137.7 °C (VARSAYIM %92 verim) → AÇIK. F1/TVS/CIN/konnektör MPN AÇIK (datasheet erişimi yok).

## Açık işler

(her aşama sonunda güncellenir)
