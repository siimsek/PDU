# G4 B1 — N1 bobin doyumu / hata enerjisi kararı

Hesap: [`analysis/g2/n1.py`](../../analysis/g2/n1.py) → [`n1-results.json`](n1-results.json); SİM: F1/F5 ([`reports/g2/SIM-RESULTS.md`](../g2/SIM-RESULTS.md)). Etiketler: HESAP / DATASHEET / SİM / VARSAYIM / AÇIK.

## 1. Bulgu (G3 N1, G4'te doğrulandı)

Bir fazın üst anahtarı kısa devre olursa bobin VIN'i doğrudan baraya bağlar: di/dt = (VIN − V)/L(i). Eski tasarımda ayırıcı yalnız bara gerilimiyle tetikleniyordu; tetik ancak bara 11.76 V garanti eşiğine çıktığında geliyor; ayırıcı açıldığında faz akımı **60–151 A** (16 A üstü L tabanı 0.5…0.05, HESAP `rows[].voltage_trip_only.i_at_open_A`), yani bobinin datasheet eğrisinin bittiği 16 A'nın çok üstünde.

- **Bobin verisi:** Vishay IHLP-4040DZ 6.8 µH L(I) eğrisi (doc 34207 p.3, **tipik**) 16 A'da biter: 0 A 6.6 µH → 16 A ≈4.85 µH (%73.5). 16 A üstü **yayımlanmamış** → son eğim uzatılıp taban F'ye (0.5…0.05) kadar tarandı (VARSAYIM).
- **Eski tasarım (yalnız gerilim tetiği), 32× COUT:** O1 tepe HESAP 11.92 V (F 0.5) … **12.01 V (F 0.15) … 12.15 V (F 0.05) → FAIL**; SİM F1 "g3 design" 11.96 V (F 0.15). G3'te yazılan "L %40 → 12.019 V" doğrudur (16× COUT); kesişim referansı nominal 6.8 µH'nin ≈0.46 katıdır (alt ajan B).
- **Enerji dengesi:** ayırıcı açılınca bobin enerjisi ½·L(i)·i² (≈2–4 mJ) ve süren VIN beslemesi yalnız ham bara COUT'una gider; Q2 gövde diyodu VSAFE'i korur. Ham bara VIN + (VIN − V) mertebesine salınır (kayıpsız sınır ≈41 V). Doyumlu L ve 16× COUT ile kelepçesiz tepe SİM'de 53.1 V'a çıktı; **32× COUT ile F1/F5 ham bara tepe ≤35.8 V** (LM70880 VOUT/ISNS+ abs 60 V, DATASHEET p.5). Ayırıcı açıldıktan sonra arızalı faz akımı ≤138 A tepeye (SİM F1/F5 `il1_max_fault`) çıkıp VRAW ≈ VIN olunca söner; batarya akımı sürekli kalmaz (ham barada yük yok) → F1 bu senaryoda açmaz, kart zaten arızalıdır (üst anahtar ölü).

## 2. Seçenekler (aynı en kötü köşe: VIN 26 V, L −20 %, Ceff min, Rsrc 20 mΩ, yük yok)

| Seçenek | O1 tepe (HESAP/SİM) | U3/U4 IN | Ham bara | Basitlik / test | Sonuç |
|---|---|---|---|---|---|
| (a) Daha yüksek Isat'lı bobin | Tetik anındaki 32–47 A'yı kapsayan resmi L(I) eğrisi bulunan 6.8 µH parça bu oturumda yok; IHLP-4040 eğrisi 16 A'da biter | — | — | Kart alanı ↑, eğri yine tipik | **Seçilmedi** (veri yok) |
| (b) Giriş tarafı hızlı kesme (LM74700+Q1 yerine sırt sırta yük kesici) | Ayırıcıyla aynı anda kestiği için **O1 tepesini değiştirmez** | — | Ham barayı sınırlar | LM74800-Q1 datasheet'i erişilemedi (TI 404); mantık beslemesi yeniden düzenlenmeli | **Seçilmedi**; çıkış yolu olarak kayıtlı |
| (b′) Ham baraya TVS kelepçe | — | — | TVS2700 40 A sınırı, kelepçe sonrası akım 60–90 A → aşırı yük; SMCJ sınıfı yüksek akımda 60 V üstü kelepçe | — | **Reddedildi** (SİM'de takılma + enerji) |
| (c) **Faz aşırı akım tetiği** (her fazın RS'i → INA296A2 → TLV3601; 3 girişli AND ile bara OV karşılaştırıcısı → aynı mandal) | **HESAP ≤11.41 V** (tüm F, VIN 20/26, V0 alt/üst); yol B (yük üst sınırı, F 0.05) ≤11.35 V; **SİM F1 11.04–11.37 V, F5 48 köşe ≤11.07 V** | VSAFE ≤11.37 V | ≤35.8 V (32× COUT) | +2 INA296, +2 TLV3601, +1 LVC1G11, +2 direnç, +5 kondansatör; tezgâhta faz şöntüne akım enjeksiyonuyla test edilebilir | **SEÇİLDİ** |
| (d) (c) + 32× COUT (B4 ile birlikte geldi) | yukarıdaki SİM değerleri 32× ile | | ≤35.8 V | | Uygulandı |

**Neden (c):** tetik, bobin datasheet eğrisinin içinde (OC eşiği **12.97–13.60 A**, normal en yüksek tepe 8.97 A'nın 1.45 katı) gelir; açılma anında akım 18.6–23.4 A (HESAP; SİM `il1_at_open` ≤22.1 A) ve bara yükselmesi küçüktür. 16 A üstü L tabanı %5'e düşse bile O1 ≤11.41 V (HESAP). Ayrıca bağımsız ikinci tetik yolu olduğundan **hassas bölücü açık devre artık riski de kapandı** (SİM F5 residual: O1 11.20 V PASS).

**Koşul (AÇIK, tezgâh):** INA296 yerleşme süresi yalnız **tipik** 1 µs (DATASHEET); bütçede 1.5 µs (VARSAYIM). Duyarlılık (F 0.05, V0 11.16 V, VIN 20/26 V'un kötüsü; `ina_delay_sensitivity_floor0p05_v0high`): 1 µs → 11.39 V, 1.5 µs → 11.41 V, 2 µs → 11.44 V, 3 µs → 11.49 V, **4 µs → 11.56 V** — yani 4× tipik gecikmede bile ≤12.0 V. Gerilim tetiği (garantili gecikmeli) yedek olarak kalır.

## 3. Uygulanan değişiklikler (zincir)

- Netlist `design/pdu_v2.cir`: doğrusal olmayan L(i) (her iki faz), OC tetik yolu, D1 SMCJ33A datasheet eğrisi.
- BOM: U11/U12 INA296A2QDGKRQ1, U13/U14 TLV3601DCKR, U15 SN74LVC1G11DBVR, R_OCT 255 Ω / R_OCB 1.00 kΩ (TNPW 0.1 %), C_INA1/2, C_OCC1/2, C_AND.
- Parametreler: `OC_INA_*`, `LFLOOR_BEYOND_16A`, `LM70880_VOUT_ABS` (`analysis/g2/params.py`).
- SİM kriterleri: F1/F5 ham bara < 60 V; F1'e taban 0.05 ve yüksek setpoint koşuları, G3 tasarımı karşılaştırma koşusu.
- KICAD-CHANGE-LIST-FINAL, PCB-HANDOFF, BENCH-ACCEPTANCE, DESIGN-RULES güncellendi.

## 4. Kalan ölçüm

BENCH T5c (gerçek bobinle üst anahtar kısa devre emülasyonu), T5g (faz şöntüne akım darbesi ile OC eşiği 12.97–13.60 A ve gecikme), IHLP L(I) eğrisinin 16–40 A aralığında ölçümü veya Vishay'den istenmesi.
