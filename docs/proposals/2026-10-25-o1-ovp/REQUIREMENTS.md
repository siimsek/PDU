# WP1 – Gereksinimler (O1 aşırı gerilim koruması)

Paket: `2026-10-25-o1-ovp` · Tarih: 2026-10-25 (Europe/Istanbul) · Kaynak repo: `siimsek/PDU` `wp/baseline-2026-10-24` @ `a1dbeeb` (2026-10-19 13:50 +03).
**Konnect bu ortamdan erişilemedi**; aşağıdaki gereksinimler repo içeriğinden (KiCad/netlist/BOM/doğrulama betikleri) ve görev tanımından alınmıştır. Konnect ile çapraz kontrol: *doğrulanamadı*.

| # | Gereksinim | Değer | Kaynak | Tür |
|---|---|---|---|---|
| R1 | Batarya | 6S LiPo, 20–26 V | görev tanımı; `simulation/` startup decks | Gereksinim |
| R2 | Bus gerilimi | 11 V nominal, ±%2 (10,78–11,22 V) | `simulation/verify_results.py` L79 (transient 10.78..11.22) | Değiştirilmeyen kriter |
| R3 | Sistem yükü | 7 A / 77 W | görev tanımı | Gereksinim |
| R4 | Kademe (stage) kapasitesi | 7,5 A / 82,5 W | görev tanımı; `bus-7p5a` deck | Gereksinim |
| R5 | **O1 giriş sınırı** | Portta **anlık en yüksek değer ≤ 12,0 V** | owner protokolü [pt5u]; `verify_results.py` L90–91 (`o1_peak<=12`) | Değiştirilmeyen kriter |
| R6 | O1 tanımı | T3 Gemstone O1, DC 5–12 V / 5 A | `hardware/bom.csv` L18 | Kaynak |
| R7 | S2E | Ayrı korumalı (U4 TPS259824); OVP sonrası S2E rayı da ≤ bus | `hardware/pdu-current-bom.csv` U4 | Kapsam |
| R8 | Motor/ESC | **Kapsam dışı** | görev tanımı | Kapsam |
| R9 | 0,45→4,5 A yük basamağı | bus 10,78–11,22 V | `verify_results.py` L79 | Değiştirilmeyen kriter |
| R10 | 7,5 A basamak penceresi | 10,78–11,22 V | WP3 için **tracking** (repo kriteri değil) | Tracking |
| R11 | Yanlış tetik yok | 11,1605 V + ripple (10 mV, 870 kHz) ve 11,21 V'ta FET açık kalmalı | WP1 tanımı; 11,1605 V = mevcut regülasyon üst değeri (önceki WP notu) | Kabul |
| R12 | Yükselme eğimleri | 0,07 / 0,17 / 0,23 V/µs rampalar | WP1 tanımı | Kabul |
| R13 | Buck high-side short | L 2,72 µH + 15,4 mΩ, 26 V'tan; RAW C 92,65 ve 165 µF; −40 °C / 100 mΩ ESR köşesi | WP1 tanımı | Kabul (100 mΩ = stres köşesi, ayrı raporlanır) |
| R14 | Cihaz sınırları | VDS ≤ 60 V (CSD18540Q5B), TLV3601 giriş ≤ 10 mA, VCC ≤ 5,5 V, U3/U4 IN ≤ 30 V (abs max) | ilgili veri sayfaları | Kabul |
| R15 | Baseline regresyonu | `simulation/pdu-efuse-ovp.ng.cir` değişmeden **FAIL** etmeli (~16,89 V) | `verify_results.py` L91 metni | Regresyon |

## Varsayımlar
- **V1 (DC/geçici belirsizliği):** O1 "DC 5–12 V" olarak tanımlı; geçici (transient) mutlak maksimum yayımlanmamış. Bu pakette en sıkı yorum uygulanmıştır: **anlık tepe ≤ 12,0 V**. Gevşetilmemiştir.
- **V2:** 12,0 V sınırı O1 portunda (eFuse U3 çıkışı, `O1_11V`) ölçülür; bus (VOUT) tepeleri ayrıca raporlanır.
- **A1 (G1 açığı):** TLV3601 VIO ±5 mV yalnızca VCM = VEE+0,3 V'ta garanti; bizim VCM ≈ 4,1 V. CMRR 80 dB yalnızca *tipik*. Bütçede 60 dB CMRR varsayımıyla pinde ±4,1 mV ek pay alınmıştır. Bu **garanti değildir** (TI teyidi veya tezgâh karakterizasyonu gerekir).
- **V3:** Bus setpoint'i (11,0 V / regülasyon üst değeri 11,1605 V) değiştirilmemiştir; düşürülmesi kullanıcı kararıdır (WP2).
