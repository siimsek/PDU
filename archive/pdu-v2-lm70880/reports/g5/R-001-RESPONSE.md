# R-001 tur 1 — BUILDER yanıtı

İnceleme: [`reviews/R-001.md`](../../reviews/R-001.md) (Codex, karar RED, 3 engelleyici). Tur 2, D-003 ve D-004 sonuçlandıktan sonra açılır (WORKFLOW: en çok 2 tur).

| No | Bulgu (özet) | BUILDER değerlendirmesi | Kanıt | İşlem |
|---|---|---|---|---|
| 1 | LM70880 akım sınırı (maks 8,35 A) "normal tepe 8,97 A"nın altında | **Geçersiz — kök neden BUILDER'ın kart girdi tablosu.** 8,97 A normal çalışma tepesi değil, `ilim_peak_max_A`: akım sınırına girildiğinde (VCS-TH maks, RS min, CS gecikmesi boyunca eğim taşması) ulaşılabilecek en yüksek tepe. Normal en kötü tepe faz akımı **5,58 A** (VIN 26 V, L −%20, 7,5 A bara, faz başı 4,125 A ort. + 2,92 A p-p dalgalanma). İncelemenin kendi bulduğu en düşük sınır 6,60 A → normal çalışma sınırın 1,02 A altında; dahili sınır yalnız aşırı yükte devreye girer, harici OC eşiği (≥12,97 A) ondan sonra gelir — tasarlanan sıra budur. | `reports/g2/power-results.json` → `inductor.peak_A_pathA` 5,583 A, `ilim_peak_max_A` 8,974 A; `analysis/g2/power.py` (`inductor()`) | Kart girdi tablosu düzeltildi (`tasks/R-001.md`). Tur 2'de bu satırın yeniden kontrolü istenir. |
| 2 | J2'de iki kontağa eşit paylaşım garanti değil; 9,07 A tek kontakta 8,5 A'yı aşar | **Geçerli.** Paralel kontak paylaşımı Molex sayfasında garanti edilmiyor. TPS25982 ILIM tablosunda 182 Ω (7,23–9,07 A) ile 300 Ω (4,36–5,66 A) arasında garantili nokta yok; ara değer interpolasyonu garanti değildir. | Molex 43045-0400 ürün sayfası; TPS25982 p.9 (`params.py` `EF_ILIM_TABLE`) | **D-003** (THINKER karar notu): kontak başı ≥9,07 A konnektör seçenekleri veya O1 ILIM yeniden seçimi. |
| 3 | O1 ≤12,0 V, garantili maksimumu olmayan OC yolu zamanlamasına dayanıyor | **Geçerli.** INA296 yerleşmesi yalnız tipik; gerilim yolu tek başına L tabanı ≤0,15'te FAIL (HESAP 12,01–12,15 V). G4 bunu "koşullu" olarak kaydetmişti; inceleme koşulun kapatılmasını istiyor. | `reports/g4/n1-results.json` `rows[].voltage_trip_only` | **D-004** (THINKER karar notu): garantili gecikmeli algılama, COUT/L verisi veya tezgâh kabul sınırı seçenekleri. |

Engelleyici olmayan 3 madde Codex tarafından `tasks/backlog.md`'ye yazıldı (değişiklik yok).
