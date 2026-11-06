# G2 Aşama 3 — güç katı, ILIM/IMON, UVLO ve giriş koruması

Hesap: [`analysis/g2/power.py`](../../analysis/g2/power.py) → [`power-results.json`](power-results.json); testler [`test_power.py`](../../analysis/g2/test_power.py). Her satırda iki yol (A analitik / B sayısal veya bağımsız formül) ve fark verilir. Etiketler: HESAP / DATASHEET / VARSAYIM / AÇIK.

## 1. Bobin L1/L2 — Vishay IHLP4040DZER6R8M01

Kaynak: Vishay doc 34509 p.1 (6.8 µH ±20 %, DCR max 23.3 mΩ, Isat typ 13.5 A, ısı akımı typ 8 A). Köşe: VIN 26 V, L −20 % (5.44 µH), fsw 400 kHz, faz payı +10 % (VARSAYIM).

| Büyüklük | Yol A | Yol B | Fark | Sınır / marj |
|---|---:|---:|---:|---|
| Ripple p-p | 2.916 A | — | — | — |
| Faz tepe akımı (7.5 A toplam) | 5.5832 A | 5.5831 A (sayısal üçgen) | 0.1 mA | Isat typ 13.5 A |
| Faz Irms | 4.2100 A | 4.2100 A | <1 µA | Iheat typ 8 A → 3.79 A marj |
| Akım sınırında tepe (VCS max 62 mV / RS min, soğuk + 75 ns gecikme aşımı, 53.3 V) | 8.974 A | — | — | Isat'a 4.53 A marj |
| OCP min ortalama toplam | 10.19 A | — | — | >7.5 A kapasite |
| Eğim kompanzasyonu Se/Sn (Eq.7, p.16) | 1.16 (L nom), 1.45 (L min) | — | — | ≥0.5 kararlılık için |

Isat/Iheat **tipik** değerdir; çekirdek kaybı Vishay hesaplayıcısı olmadan hesaplanamadı (0.15 W/adet VARSAYIM) → AÇIK.

## 2. Şönt RS1/RS2 — Vishay WSL25127L500FEA

7.5 mΩ, %1, 1 W (P70), bileşen TCR ±75 ppm/K (doc 30100 p.1–2). Kayıp 0.134 W/adet → %13 (≤%50 ✓). Tam yükte sense gerilimi 30.9 mV (eşik 50–62 mV). Kelvin bağlantı pad iç kenarından ayrı iz (LM70880 p.16).

## 3. Kapasitörler

| Grup | Değer | Hesap | Durum |
|---|---|---|---|
| COUT | **16× TDK C5750X7S2A226M280KB** (8 mevcut + 8 yeni COUT9–16) | Ceff min/typ/max 185.3 / 330.0 / 515.3 µF (G1 TDK modeli + tolerans/ısı/%10 yaşlanma); ESR 0.12 mΩ; gerilim kullanım oranı 11 V/100 V = %11 (≥%50 marj ✓, DC-bias Ceff'e dahil) | DATASHEET+HESAP |
| COUT ripple akımı (2 faz iptali) | 0.7777 A p-p (A) / 0.7777 A (B), fark 0.05 mA | ΔV ≈ 0.75 mV p-p | HESAP |
| CIN | 8× 4.7 µF 1210 (mevcut değer) | Irms 1.125 A (A, ripple hariç) / 1.197 A (B, ripple dahil), fark 72 mA (yol farkı modelden); VIN taramasında en kötü 1.353 A; kapasitör başına ~0.15 A | **MPN ve DC-bias doğrulanamadı** (TDK/Murata 403) → BOM-OPEN; Ceff %50 VARSAYIM |

## 4. Kayıp bütçesi ve sıcaklık

Toplam verim **%92 VARSAYIM** (LM70880 datasheet'inde RDS(on)/anahtarlama kaybı tablosu yok; yalnız tipik verim eğrisi). 82.5 W çıkışta dönüştürücü kaybı 7.17 W.

| Kalem | Kayıp (W) | Kaynak |
|---|---:|---|
| 2× bobin DCR (40 K ısınma) | 0.947 | HESAP |
| 2× bobin çekirdeği | 0.30 | VARSAYIM |
| 2× şönt | 0.263 | HESAP |
| 2× LM70880 (kalan) | 2× 2.83 | VARSAYIM'dan türetilmiş |
| Q1 (BSC160N10NS3G, 4.48 A, sıcak) | 0.579 | HESAP |
| Q_ISO (CSD19531Q5A) | 0.648 | HESAP |
| eFuse O1 / S2E | 0.235 / 0.001 | DATASHEET RON 3.2 mΩ ×1.5 |
| LDO5 | 0.336 | HESAP |
| **Kart toplamı** | **8.97** | |

**LM70880 Tj** (85 °C ortam VARSAYIMI): JEDEC θJA 33.5 K/W → 179.9 °C; EVM θJA 18.6 K/W → 137.7 °C. **125 °C taramasını aşar (FAIL, VARSAYIM bağımlı).** Tj ≤125 °C için izinli ortam: EVM kartında ≤72 °C, JEDEC kartında ≤30 °C. Kart ortalama ısınması ~58 K (doğal taşınım 10 W/m²K VARSAYIM). → Ortam sıcaklığı kullanıcı girdisi (USER-DECISIONS) ve tezgâh termal ölçümü (BENCH T4) şart. Verim varsayımı değişirse IC kaybı ve Tj doğrudan değişir.

## 5. eFuse ILIM / IMON / EN / dV/dt

| Büyüklük | Değer | Kanıt |
|---|---|---|
| RILIM_O1 | **182 Ω** → 7.23 / 8.13 / 9.07 A (min/typ/max, TJ −40…125 °C) | DATASHEET TPS25982 p.9 tablo noktası |
| RILIM_S2E | **300 Ω** → 4.36 / 4.98 / 5.66 A | DATASHEET p.9 tablo noktası |
| Garantili-min toplam | **11.59 A ≥ 7.5 A ✓** (eski 301/604 Ω nominal 7.4877 A FAIL korunur) | HESAP |
| Tipik toplam: tablo (A) / K/R uydurma (B) | 13.11 / 13.19 A | HESAP (B yalnız çapraz kontrol) |
| O1 marjı | 7.23 A − 6.78 A yük zarfı (VARSAYIM: 7 A − S2E 0.22 A) = 0.45 A | VARSAYIM |
| S2E marjı | 4.36 A − 1.5 A kalkış = 2.86 A | DATASHEET (S2E p.12, G1) |
| Maks toplam | 14.73 A > buck OCP min 10.19 A → iki port aynı anda sınırdaysa buck hiccup'a girer (koruma hiyerarşisi) | HESAP |
| IMON maks gerilim | 806 Ω × 253.4 µA/A × 9.07 A = 1.85 V | HESAP |
| eFuse EN açma (VSAFE) | 8.82–9.24 V (64.9k/10k) | HESAP |
| dV/dt | CdVdt 1 nF → 4.6 V/ms (Eq.3, p.21); 100 µF yükte 0.46 A ani akım | DATASHEET |

O1 için ILIM 182 Ω seçimi, ölçülmemiş yük zarfına dayanır. O1 sürekli akımı ≤6.78 A değilse seçim değişir (USER-DECISIONS).

## 6. UVLO — RUV1 174 kΩ / RUV2 10 kΩ (TNPW 0.1 %, 25 ppm/K)

| | Yol A (köşe sayımı) | Yol B (aralık) | Fark |
|---|---|---|---|
| Yükselen eşik, 174k | **17.365–19.623 V** | 17.364–19.622 V | 0.4 mV |
| Yükselen eşik, eski 180k | 17.931–20.263 V (**20 V restart FAIL korunur**) | 17.930–20.263 V | 0.4 mV |

- Girdiler: VEN-TH 0.95–1.05 V (DATASHEET p.6), EN kaçağı maks yayımlanmamış → 1 µA tarama (VARSAYIM; 174k'da +0.174 V dahil), ΔT 100 K.
- Hücre başına açma 2.894–3.270 V/hücre (6S).
- Düşüş eşiği: histerezis 0.1 V yalnız tipik → düşüş ~16.56 V (2.76 V/hücre) **tipik**; garanti aralığı AÇIK.
- Dip/çift darbe davranışı: LM70880 EN histerezisi (%10) ve iç soft-start (1.9–4.4 ms) dışında ek kontrol önerilmez; batarya koruması bu UVLO'ya bırakılmaz (hücre kesim politikası kullanıcı girdisi). Çok IC'li UVLO yalnız batarya üretici kesimi ≥3.3 V/hücre isterse gerekir.

## 7. Giriş koruma

| Kalem | Hesap | Durum |
|---|---|---|
| Kaynak kısa devre akımı (26 V, R_src 20–200 mΩ + 5 mΩ) | 1040 / 473 / 248 / 127 A | VARSAYIM taraması |
| F1 gereksinimi | Anma ≥5.98 A (giriş 4.48 A / 0.75) → 10 A sınıfı; DC gerilim ≥53.3 V; kesme kapasitesi ≥1040 A (20 mΩ köşesi) | **MPN AÇIK**: sigorta üretici datasheet'lerine erişilemedi (Littelfuse 403/DNS) |
| TVS D1 | SMCJ33A ailesi: VRWM 33 V (26 V'a 7 V marj), Vc 53.3 V | Datasheet doğrulanamadı → VARSAYIM |
| Q1 BSC160N10NS3G | VDS 100 V (clamp'a 46.7 V marj), iletim 0.58 W | DATASHEET (repo PDF) |
| LM74700-Q1 | ANODE abs ±65 V → clamp'a 11.7 V marj; ters polarite bloke | DATASHEET p.5 |
| Hot-plug | CIN enerjisi 0.32 mJ (Ceff %50 VARSAYIM) kaynak direncinde harcanır; Q1 SOA grafiği sayısal okunamadı | AÇIK |
| Konnektör J1/J2/J3 | 4.48 / 7.0 / 1.5 A | Molex PS okunamadı → AÇIK (G1 kaydı: W-W 7 A, W-B 8.5 A @18 AWG) |
