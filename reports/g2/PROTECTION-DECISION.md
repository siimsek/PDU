# G2 koruma mimarisi kararı — ortak bara seri ayırıcı

G1 kapanış kararı (ortak bara seri ayırıcı, U3/U4 IN önünde) somutlaştırıldı. Hesaplar: [`analysis/g2/protection.py`](../../analysis/g2/protection.py) → [`protection-results.json`](protection-results.json); testler: [`analysis/g2/test_protection.py`](../../analysis/g2/test_protection.py). Etiketler: HESAP / DATASHEET(sayfa) / SİM / VARSAYIM / AÇIK. Bu belge **fiziksel kabul değildir**.

## 1. Uygulama seçenekleri

| Ölçüt | **A (SEÇİLDİ)**: TLV3601 + REF5025A + SN74LVC1G74 → **LM74502H OV pini** → 1× CSD19531Q5A; LM74502H OV pininde bağımsız kaba OV bölücüsü | **B (YEDEK)**: G1 zinciri TLV3601/TLV1701 + REF5025A + SN74LVC1G74 + LTC7001 + 2× CSD19536KTT + TPS7A1601 12 V + 2× MMBT3904 INP kenetleme | **C (ELENDİ)**: Yalnız LM74502H, OV pini doğrudan VRAW bölücüsünden (entegre OVP kontrolcülü tek zincir) |
|---|---|---|---|
| Tam MPN | TLV3601DCKR, REF5025AQDRQ1, SN74LVC1G74DCUR, **LM74502HDDFR**, **CSD19531Q5A**, TPS7A1650QDGNRQ1 | Aynı + LTC7001EMSE#PBF, CSD19536KTTT ×2, TPS7A1601QDGNRQ1, MMBT3904LT1G ×2 | LM74502HDDFR + FET |
| Eşik köşesi | **11.2649–11.5309 V** (HESAP; iki yol farkı 0.41 mV). Ref ±0.1 % + 8 ppm/K, R 0.1 %/15 ppm/K (TNPW 'X'; 10 ppm yalnız TNPU serisinde), Vos ±5 mV, hist. 1.5–5 mV, IB ±5 µA, ΔT 100 K | Aynı karşılaştırıcı/referans → benzer | OV eşiği 1.165–1.333 V (DATASHEET p.6): oran 1.144 > izinli pencere 12.0/11.25 = 1.067 → **sayısal olarak imkânsız** |
| Gecikme MAKS | 4.5 ns (TLV3601, 50 mV OD, VCM=VEE+0.3 V, p.7) + 6.4 ns (LVC1G74 PRE→Q, 5 V, −40…125 °C, p.7) + 36.4 ns (OV düğümü RC, HESAP) + **1.000 µs (LM74502H tOVP_OFF max, C_GS=4.7 nF, p.6)** = **1.047 µs** | LTC7001 70 ns max yalnız 1 nF yükte; 2×CSD19536 (Qg max 153 nC/adet) yükünde **garanti edilemez**. LTC7001 datasheet'i bu turda okunamadı (analog.com bağlantı reddi) → **doğrulanamadı** | 1 µs max var, ama eşik çözülemez |
| Gecikme koşulları | Karşılaştırıcı: datasheet VCM=0.3 V'ta test eder, bizde VCM≈2.53 V → **koşullu**. Sürücü: CSD19531Q5A Qg(13.9 V)≈63.1 nC vs test yükü 4.7 nF×13.9 V=65.3 nC (oran 0.97) → **koşullu, tezgâh ölçümüyle kabul** | **Garanti edilemez → yalnız tezgâh** | — |
| O1 tepe (HESAP, en kötü köşe) | **11.935 V** (16× COUT; marj 65 mV); **SİM F1 11.912 V, F5 48 köşe maks 11.912 V**; 12× COUT'ta 11.962 V; özgün 8× COUT'ta **12.006 V FAIL** | Gecikme sınırı yok → hesaplanamaz | — |
| U3/U4 IN tepe | VSAFE ≤11.935 V HESAP; SİM F1/F5 ≤11.915 V; korumasız referansta 33.0 V (FAIL korunur) | — | — |
| FET VDS / VGS | 100 V vs VRAW maks 53.3 V (TVS clamp VARSAYIMI) → 46.7 V pay; VGS ≤13.9 V (LM74502H VCAP max) < 20 V | 100 V | — |
| Kapanma enerjisi | ≤0.40 mJ (üçgen sınır 15 A × 53.3 V × 1 µs / 2) vs EAS 180 mJ → oran 0.0022. **SOA grafiği sayısal okunamadı → AÇIK** | SOA 100 µs'den kısa eğri yok → AÇIK | — |
| İletim kaybı | 7.5 A, RDS(on) 6.4 mΩ × 1.8 (sıcak VARSAYIM) → 0.65 W, Tj≈117 °C (85 °C ortam, RθJA 50 K/W) | 2 FET seri → 2× RDS | — |
| Ek aktif parça | 6 (CMP, REF, LAT, DRV, FET, LDO5) | 10 | 2 |
| Tezgâh testi | Tek enjeksiyon `J_OVP_INJ_BUS` → VRAW; ölçüm VSAFE, O1, S2E, GATE, PRE_n, Q. Kaba OV yolu, mantık rayı kesilerek ayrı denenebilir | Aynı + 12 V ray, INP kenetleme, bootstrap | Basit, ama eşik tutmaz |
| DESIGN-RULES | R01–R15 hepsi karşılanır (koşullu: R04, R12, R14, R15) | R14 karşılanamaz | R02/R03 karşılanamaz |

**Karar: A.** Gerekçe: (1) sürücü katında datasheet'te **maksimum** kapanma gecikmesi olan tek seçenek; (2) en az parça (12 V ray, bootstrap ve BJT kenetleme yok); (3) LM74502H OV pini 65 V'a kadar dayanıklı ve VS beslemeli olduğundan, mantık rayı yokken de çalışan bağımsız kaba OV yolu aynı pine eklenebiliyor; (4) bütün parçaların datasheet'i bu turda okundu (B'deki LTC7001 okunamadı).

**Yedek: B**, yalnız LM74502H'nin gerçek CSD19531Q5A yükünde tezgâhta ölçülen kapanma süresi 1 µs'yi aşarsa ve daha küçük Qg'li FET (ör. CSD19534Q5A, Qg max 22 nC, RDS max ~15.5 mΩ) iletim kaybı nedeniyle kabul edilemezse. B'nin gecikmesi "garanti edilemez" kategorisindedir ve yalnız tezgâh ölçümüyle kabul edilebilir.

## 2. Seçilen zincirin değerleri

| Ref (öneri) | Değer / MPN | İşlev | Kanıt |
|---|---|---|---|
| R_OVT / R_OVB | 8.25 kΩ / 2.32 kΩ, TNPW1206 0.1 % 15 ppm/K (TNPW12068K25BXEA / TNPW12062K32BXEA) | Hassas eşik bölücüsü, VRAW → U_CMP IN− | HESAP; Vishay doc 28758 parça numarası şeması |
| U_REF | REF5025AQDRQ1, 2.5 V | U_CMP IN+ | DATASHEET p.4 |
| U_CMP | TLV3601DCKR (SC70-5), VCC=+5V_PROT | Çıkış LOW = aşırı gerilim → PRE_n | DATASHEET p.7 |
| U_LAT | SN74LVC1G74DCUR; D=VCC, CLK=GND, PRE_n=U_CMP OUT, CLR_n=POR/PG/buton | Mandal; Q=H → ayırıcı KAPALI | DATASHEET p.4, p.7 |
| R_Q | 10.0 kΩ CRCW0603 1 % | Q → U_DRV OV | HESAP |
| R_OV2T / R_OV2B | 64.9 kΩ / 24.9 kΩ CRCW0603 1 % | Kaba OV: VRAW → U_DRV OV; trip **11.55–13.70 V** (iki yol farkı ≤2.5 mV) | HESAP |
| U_DRV | LM74502HDDFR; VS=VRAW, SRC=VSAFE, GATE=Q_ISO G, VCAP 0.1 µF | Kapı sürücüsü + şarj pompası | DATASHEET p.3–6 |
| R_EN1 / R_EN2 | 15.0 kΩ / 10.0 kΩ CRCW0603 1 % | +5V_PROT → U_DRV EN: açma ≤3.375 V, kapama 2.57–3.16 V | HESAP |
| Q_ISO | CSD19531Q5A (SON 5×6) | VRAW (drain) → VSAFE (source) | DATASHEET p.1–2 |
| R_GS | 100 kΩ CRCW0603 | G-S boşaltma (R13) | Tasarım |
| U_LDO5 | TPS7A1650QDGNRQ1, giriş VIN (Q1 sonrası) | +5V_PROT | DATASHEET; R21 |
| R_BL5 | 1.0 kΩ CRCW0805 | 5 V bleeder (clamp geri beslemesi, R07) | HESAP |
| R_CLR / C_CLR | 100 kΩ / 1 µF | POR: CLR_n ~120 ms LOW | HESAP |
| SW_RST | manuel reset butonu, CLR_n → GND | R11 | MPN AÇIK (BOM-OPEN) |

Hesap özetleri (HESAP, `protection-results.json`):

- Hassas eşik payı: trip_min 11.2649 V, 11.22 V transient bandının 44.9 mV üstünde (R03 hedefi 30 mV). Katkılar (V): ref 0.0205, oran 0.0445, offset 0.0228, hist. 0.0040, bias 0.0413.
- Karşılaştırıcı VCM trip anında 2.531 V (aralık −0.2…5.1 V). VRAW > 23.24 V'ta giriş aralık dışı → bu bölgede kaba OV (≤13.70 V) zaten kapıyı kapalı tutar (R05).
- Clamp akımı VCC=0, VRAW=53.3 V: 6.29 mA (yol A) / 6.47 mA (yol B, tolerans köşesi, 0 V clamp) < 10 mA (R06).
- LDO yokken 5 V ray geri beslemesi (1 kΩ bleeder): 26 V'ta 1.92 V, 40.709 V'ta 3.07 V, 53.3 V'ta 4.06 V. **Not:** 40.7 V ve üstünde ray 2.1 V POR ve 1.65 V mandal eşiğinin üstüne çıkar; bu durumda kaba OV yolu (VS beslemeli) kapıyı kapalı tutar; mantık durumu kredi edilmez (R07 kısmen; AÇIK not).
- Bölücü gücü: R_OVT 26 V sürekli 0.050 W, 53.3 V geçici 0.210 W → TNPW1206 (P70 0.25 W, doc 28758) sürekli %20, geçici %84 (geçici, süre sınırlı; R20 sürekli için sağlanır).
- Kapı eşdeğerliği oranı 0.97 (gerçek FET yükü ≤ test yükü), sınırda.

## 3. O1 tepe bütçesi (yüksek taraf kısa devre, tek faz)

Model: kısa devre olan fazın bobini (L, −20 % köşe) VIN'i doğrudan baraya bağlar; yük yok (en kötü); baraya Ceff_min (COUT min köşe + VSAFE kapasitörleri VARSAYIM) bağlı; ayırıcı garanti eşiğine (trip_max + 50 mV × k = 11.759 V) ulaşınca 1.047 µs sonra açılır.

| Yol | Yöntem | En kötü köşe (VIN 26 V, V0 10.8333 V, L 5.44 µH, Rsrc 20 mΩ, 16× COUT) |
|---|---|---|
| A | Kayıpsız LC kapalı form | 11.9345 V |
| B | RK4, seri direnç dahil | 11.9279 V |
| Fark | | 6.6 mV (A konservatif üst sınır) |
| SİM (F1 f1_worst, aynı köşe, tam sistem ortalama model) | ngspice | 11.912 V (A'dan 22 mV düşük) |

COUT sayısına duyarlılık: 8× → 12.006 V (FAIL), 12× → 11.962 V, 16× → 11.935 V, 18× → 11.924 V. **Seçim: 16× COUT** (Aşama 3/4'te yük adımı ile birlikte teyit).

Bu değişirse ne değişir: L toleransı, VIN maks, faz bobini, COUT Ceff ve sürücü gecikmesi tepe değerini doğrudan değiştirir; 50 mV overdrive kabulü 0.229 V'luk payı belirler.

## 4. Fail-safe tablosu (pin düzeyi)

| Olay | U_CMP OUT | U_LAT PRE_n / CLR_n / Q | U_DRV OV / EN | GATE / Q_ISO | VSAFE, U3/U4 | Kanıt |
|---|---|---|---|---|---|---|
| Soğuk açılış, VIN ↑, +5V_PROT <2.1 V | VCC<POR → LOW (DATASHEET p.7) | PRE_n=L; Q belirsiz (VCC<1.65 V) | EN ray <2.57 V → kapalı | VRAW yok (buck henüz başlamadı), G-S 100 kΩ → KAPALI | 0 V | DATASHEET+HESAP |
| +5V_PROT geçerli, POR süresi | normal: HIGH | CLR_n=L (RC) → Q=L; hata varsa PRE_n=L → Q=H (set-dominant) | EN açık; OV=Q·oran | Buck VRAW yükselince kapı açılır | VSAFE=VRAW | DATASHEET |
| Normal | HIGH | PRE_n=H, CLR_n=H, Q=L | OV ≈ VRAW/… <1.165 V | AÇIK | ≈11 V | — |
| VRAW > hassas eşik | LOW (≤4.5 ns koşullu) | PRE_n=L → Q=H (≤6.4 ns) | OV ≥2.78 V (min) | ≤1 µs kapalı (koşullu) | VSAFE ≤11.94 V (HESAP), 11.91 V (SİM) | HESAP |
| Hata sürer, VRAW > 23.2 V | giriş aralık dışı, çıkış kredi edilmez | Q=H tutulur (yalnız CLR temizler) | Kaba OV de aktif (VRAW>13.70 V) | KAPALI | Yük boşalır | HESAP |
| Hata kalkar | HIGH | Q=H kalır | OV yüksek | KAPALI | — | R11 |
| Manuel reset, hata yok | HIGH | CLR_n=L → Q=L | OV düşer | AÇILIR (tOVP_ON 5–10 µs) | yeniden enerji | DATASHEET p.6 |
| Manuel reset, hata sürüyor | LOW | PRE_n=L ve CLR_n=L → Q=H | yüksek | KAPALI | — | DATASHEET fonksiyon tablosu |
| +5V_PROT kaybı (LDO arızası), VIN ve VRAW var | POR altı LOW | mandal belirsiz | **EN < 1.027 V → kapı kapanır** (ray 2.57–3.16 V); kaba OV aktif | EN iç deşarjı (RDSON 0.4–2 Ω); tUVLO_OFF yalnız tipik 2 µs → **koşullu** | VSAFE düşer; U3/U4 UVLO | DATASHEET p.5–6 |
| VRAW kaybı (buck durur) | — | — | VS < POR → sürücü kapalı | Kapı yükü R_GS üzerinden; FET zaten akım taşımaz | VSAFE ≤ VRAW + gövde diyotu | DATASHEET |
| VIN kaybı (batarya çıkar) | ray düşer | — | EN düşer | KAPALI | eFuse OUT > IN riski → D_REV + VSAFE bleeder (R16) | HESAP; Aile 4 |
| Referans kaybı (U_REF çıkışı 0) | IN+=0 < IN− → LOW | PRE_n=L → Q=H | yüksek | KAPALI (güvenli yönde) | — | Mantık |
| R_OVB açık devre | IN− → VRAW (clamp) → LOW | trip | — | KAPALI (güvenli) | — | Mantık |
| **R_OVT açık devre** | IN−=0 → HIGH, hassas yol kör | — | Kaba OV tek koruma: 11.55–13.70 V | VSAFE SİM 13.94 V (F5 artık-risk koşusu) | U3/U4 korunur; **O1 ≤12 V garantisi yok** | **Artık risk, AÇIK** (tezgâhta periyodik eşik testi) |
| R_OV2T açık | — | — | Kaba yol kör; hassas yol çalışır | — | — | Tek arıza: koruma devam eder |
| Q_ISO kısa devre (D-S) | trip | Q=H | — | Kapı kapalı ama FET iletken → **koruma yok** | **AÇIK**: tek nokta arızası; ikinci seri FET yedek B ile değerlendirilebilir | AÇIK |

## 5. SİM özeti

F1: 3/3 korumalı koşu PASS (O1 ≤11.91 V), korumasız referans FAIL (O1 19.57 V, VSAFE 33.0 V). F5: 48/48 köşe PASS, O1 11.505–11.912 V; hassas yol açık artık riski O1 13.94 V (FAIL, beklenen). Ayrıntı [`SIM-RESULTS.md`](SIM-RESULTS.md).

## 6. Kapanmayanlar

- Karşılaştırıcı gecikmesi VCM≈2.5 V'ta ve düşük overdrive'da garanti değil; sürücü 1 µs yalnız 4.7 nF toplu yükte garanti → **tezgâhta gerçek kapanma süresi ölçümü şart** (BENCH T5).
- SOA (µs ölçeği) grafikten okunamadı; enerji oranı küçük ama fiziksel kabul AÇIK.
- TVS clamp 53.3 V varsayımı (datasheet doğrulanamadı).
- R_OVT açık devre ve Q_ISO kısa devre tek-nokta arızaları (artık risk).
