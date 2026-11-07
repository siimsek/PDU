# G2 — kullanıcıdan gereken karar ve belgeler

G1 [`USER-DECISIONS.md`](../g1/USER-DECISIONS.md) kararları cevaplanmadı; G2 aşağıdaki muhafazakâr varsayılanlarla ilerledi (VARSAYIM). Her satırda varsayım değişirse etkilenen sonuç yazılıdır.

## Kararlar (G2 varsayılanıyla ilerlendi)

| # | Karar / girdi | G2 varsayılanı | Değişirse ne değişir |
|---|---|---|---|
| 1 | O1 (T3 Gemstone O1) gerçek mutlak maksimum giriş gerilimi — **datasheet PDF** | 12.0 V sert sınır | Eşik penceresi, COUT sayısı (O1 bütçesi), karşılaştırıcı bölücüsü |
| 2 | 12.0 V şartı ölçüm payıyla mı (okunan tepe + belirsizlik ≤12.0 V)? | Evet (tutucu) | T5c kabul kriteri; 65 mV HESAP marjı belirsizlikten küçükse COUT artırımı |
| 3 | O1 hatasında S2E'nin de kapanması kabul mü? | Kabul (ortak ayırıcı) | Hayırsa yedek: port başına ayırıcı (zincir ×2) |
| 4 | Hata sonrası davranış | Mandallı; yalnız güç döngüsü / SW1 | Otomatik yeniden deneme istenirse mandal/CLR mantığı değişir |
| 5 | Ölçülmüş O1/S2E akımları (sürekli/kalkış/tepe) | ILIM zarfı; O1 yük zarfı 6.78 A | RILIM_O1 (182 Ω) ve O1 marjı 0.45 A; COUT/termal |
| 6 | Batarya iç direnci, kablo uzunluğu/kesiti, hücre kesim politikası | 20–200 mΩ tarama; kablo 0.5–1 µH | F1 kesme kapasitesi (≥1040 A), hot-plug VIN tepe (SİM 42.1 V), UVLO düşüş politikası |
| 7 | Tasarım ortam sıcaklığı ve muhafaza/hava akışı | 85 °C (G1) | **LM70880 Tj 137.7 °C → FAIL (125 °C taraması)**; ≤72 °C ortamda geçer |
| 8 | Statik tolerans + yük geçişinin aynı anda en kötü köşede olması kabul mü, yoksa üretimde bara ayarı (trim) mı? | İkisi birlikte değerlendirildi → SİM F3 yığılmış köşeler FAIL (alt: bara min, üst: bırakma tepe 11.35 V > trip_min) | Trim kabul edilirse statik pencere daralır ve yığılmış köşeler kapanabilir; aksi hâlde AÇIK |

## Erişilemeyen resmi datasheet'ler (PDF gerekli)

| Belge | Neden gerekli | Durum |
|---|---|---|
| Molex PS-43045-001 (Micro-Fit 3.0) + eş housing/crimp | J1–J3 akım derating, kablo kesiti | molex.com bağlantıyı reddetti |
| SMCJ33A (Vishay veya Littelfuse) | D1 VRWM/Vc/Ipp, clamp 53.3 V varsayımı | erişim yok (404/403) |
| DC sigorta + yuva (≥10 A, ≥53.3 VDC, ≥1040 A kesme) | F1 seçimi, I²t | Littelfuse 403/DNS |
| 100 V 1210 4.7 µF ve 25 V 0805 10 µF MLCC serisi (DC-bias eğrisiyle) | CIN, CEFOUT, küçük dekuplajlar | TDK/Murata 403 |
| ADI LTC7001 (yalnız yedek B için) | yedek zincir doğrulaması | analog.com bağlantı reddi |
| Reset butonu (ör. Omron B3U-1000P) | SW1 | bu turda okunmadı |
