# T-005a — Özel footprint doğrulaması (LM70880 RRX0029B, TPS25982 RGE0024M)

Tarih 2026-11-07. Komut: `python analysis/check_footprints.py` → [`check.json`](check.json) (exit 0). Testler: `analysis/test_check_footprints.py` (kaydırılmış pad ve eksik EP yakalanıyor). Footprint dosyaları **değişmedi** — düzeltme gerekmedi.

| Footprint | Kaynak çizim | Pad (tolerans 0,02 mm) | Çokgen/ayrık bakır | Exposed pad | Courtyard | Pin 1 | Sembol pinleri |
|---|---|---|---|---|---|---|---|
| `PDU:TPS25982_RGE0024M` | TI SLVSEI3D, RGE0024M 4223975/B s.56 | 24 çevre pad 0,575 × 0,24, aralık 0,5, sıra merkezleri ±1,9125 — **eşleşti** | — | 25 = IN (2,7 × 1,45 @ y −0,625), 26 = GND (2,7 × 0,85 @ y +0,925), ayrı numaralı — **eşleşti** | gövde 4 × 4 ve tüm bakırı kapsıyor | silk köşe işareti | 26 pin TI Tablo 5-1 (s.5–6) ile aynı |
| `PDU:LM70880_RRX0029B_RectLands` | TI SNVSBX7A, RRX0029B 4228757/D s.52 | 29 sinyal pad 0,6 × 0,25 (sol x −2,9, alt y +2,9, sağ x +2,9, üst y −2,9) — **eşleşti** | VIN (29) sınır kutusu (−3,2, −3,2)…(−0,625, −0,484); SW (22) (−0,125, −2,1)…(3,2, −0,14) — **eşleşti**; aynı ağdaki pinler (1, 2, 27–29 = VIN; 20–22 = SW) ortak bakır | 30 = PGND 3,125 × 1,584 @ (0,037, 1,308) — **eşleşti** | gövde 6 × 6 ve tüm bakırı kapsıyor | silk köşe işareti | 30 pin TI Tablo 5-1 (s.3–4) ile aynı |

Görsel kontrol: `kicad-cli fp export svg` → [`TPS25982_RGE0024M.svg`](TPS25982_RGE0024M.svg), [`LM70880_RRX0029B_RectLands.svg`](LM70880_RRX0029B_RectLands.svg). Şekiller TI "Example Board Layout" sayfalarıyla aynı (VIN çokgeni sol üst, SW çokgeni sağ, PGND pad'i alt orta; RGE'de iki ayrı EP).

## Kapsam dışı / açık
- **Stencil (paste) açıklıkları** TI "Example Stencil Design" sayfalarıyla (RGE s.57, RRX s.53) karşılaştırılmadı — montaj kabulü (üretici ile) kalır.
- Termal via dizisi footprint'te yok (TI not 5: isteğe bağlı) — PCB-HANDOFF termal bölümü yerleşimde ekler.
- `PDU.kicad_sym` içindeki TPS25982 sembol adı hâlâ `TPS259824ONRGET` (pinler L varyantıyla aynı); ad/MPN alanı T-011'de `TPS259824LNRGER` yapılacak.
- T-005b: Q1 TDSON-8, C5750 2220, J2 Molex 46015-0206 (stok 5566-02A ↔ Molex çizimi), F1 (U-006 kararına bağlı).

## T-005b ön bulgu (2026-11-07)
- `PDU:TDSON-8-1_Konnect` (Q1) açıklaması "KiCad TDSON-8-1 ile aynı 5 bakır pad" diyor, ama KiCad 10 stok `Package_SON:Infineon_PG-TDSON-8_6.15x5.15mm` ile **farklı**: pad 1–4 0,85 × 0,5 @ x −2,9 (stok 1,2 × 0,65 @ x −2,825); drain pad 5 tek parça 4,55 × 4,41 @ x 1,05 (stok 4,5 × 4,7 @ x 0,675 + 4 dış pad 1,0 × 0,7 @ x 2,925). Infineon resmi footprint'i yerel datasheet'te yok → **R-003** (THINKER) üretici belgesiyle karar verir; T-005b Blocked.
- C5750: yerel TDK teslim spesifikasyonundaki tablo (a 4,5 / b 8,0 / c 5,6 mm) güvenilirlik **test kartı** ölçüsüdür, önerilen land değildir; footprint'teki "gap 4,45, pad 1,30 × 4,50" TDK önerisiyle R-003'te doğrulanacak.
- J2 (Molex 46015-0206): stok Mini-Fit Jr 5566-02A dikey footprint'i ↔ Molex 460150206_sd.pdf karşılaştırması R-003'te.
