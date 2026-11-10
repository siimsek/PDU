# G4 — G3 çıktısının bağımsız denetimi (AUDIT2)

Kapsam: `wp/g3-pcb-ready` @ `2421cb7`. G3 raporuna güvenilmedi; ölçümler yeniden yapıldı.

## 1. Senkron, test, baseline

| Madde | G3 kaydı | G4 sonucu | Durum |
|---|---|---|---|
| Çalışma ağacı / dal | temiz | temiz; `wp/g4-closure` dalı `2421cb7`'den | DOĞRULANDI |
| Ortam | — | Python 3.14.5; kicad-cli 10.0.7 `C:\Program Files\KiCad\10.0\bin` (PATH dışı); ngspice-47 `F:\Spice64\bin\ngspice_con.exe` | DOĞRULANDI |
| pytest / run_all | 95 / 7 adım exit 0 | 95 passed; run_all 7/7 exit 0 (70 koşu) | DOĞRULANDI |
| Arşiv manifesti | 880 dosya | `sha256sum -c` geçti | DOĞRULANDI |
| ERC | 0 | 0 ([baseline/erc.json](baseline/erc.json)) | DOĞRULANDI |
| DRC | 197 bağlantısız / 228 uyarı / 73 parite | aynı ([baseline/drc.json](baseline/drc.json)) | DOĞRULANDI |
| **DRC 301 ↔ 228+73 farkı** | "KiCad sürümü farkı" | **Fark yok:** eski kayıt (docs/PROJECT-STATE) 301 = 199 silk_over_copper + 72 alan eşliği + 21 silk_overlap + 5 lib eşliği + 3 silk_edge + 1 eksik F1. KiCad 10 JSON'u şema paritesini (72 alan + 1 eksik F1 = 73) ayrı listeler; kurallar aynı, toplam 301. | DÜZELTİLDİ (G3 açıklaması yanlıştı) |
| 73 parite uyarısının nedeni | — | 72 `footprint_symbol_field_mismatch` (PCB'de Description/MPN alanı boş, şemada dolu) + 1 `missing_footprint` (F1'in footprint'i yok) | DOĞRULANDI |

## 2. Alt ajan A — bağımsız yeniden türetme

Alt ajana yalnız [`datasheet-inputs.md`](datasheet-inputs.md) verildi (sonuç dosyası yok, repo kodu okunmadı).

| # | Büyüklük | G3 | Alt ajan A | Fark | Durum |
|---|---|---|---|---|---|
| 1 | Eşik min/maks | 11.2590 / 11.5368 V | 11.259 / 11.537 V | 0 | DOĞRULANDI |
| 1 | Garantili gecikme | 1.048 µs | 1.011 µs (OV-RC'yi 1 µs içinde saydı) | %3.5 | FARK — kök neden: OV düğümü RC'si (≈37 ns) ayrı sayılmadı; G3 değeri tutucu |
| 1/10 | O1 tepe (gerilim tetiği, doğrusal L) | 11.941 V HESAP / 11.920 V SİM | 11.93 / 11.917 V | ≤%0.2 | DOĞRULANDI |
| 2 | U3/U4 IN tepe | ≤11.94 V | 11.92 V | %0.2 | DOĞRULANDI |
| 3 | ILIM garantili-min toplam | 11.59 A | 11.59 A | 0 | DOĞRULANDI |
| 4 | RUV1 yükselen | 17.365–19.623 V | 17.37–19.62 V | 0 | DOĞRULANDI |
| 5 | Akım sınırında tepe / Isat marjı | 8.974 A / 4.53 A | 8.97 A / 4.53 A | 0 | DOĞRULANDI |
| 5 | Açılışta faz akımı | (G3 N1: "61–86 A") | 31–32 A | — | **DÜZELTİLDİ**: 61–86 A açılış SONRASI tepe; açılıştaki akım ≈32 A (alt ajan B de doğruladı) |
| 6 | F1 kısa devre akımı | 1040 A | 1040 A | 0 | DOĞRULANDI |
| 7 | PM / GM | 66.9° / 11.7 dB | 66.8° / 11.6 dB | %0.2 / %0.9 | DOĞRULANDI |
| 8 | Yük adımı bara min | 10.80 V (nominal SİM) | 10.71 V (statik alt köşe + 1. derece) | %0.8 | FARK — kök neden: alt ajan statik alt köşeden başladı (yığılmış köşe); G3 nominal setpoint. Yığılmış köşenin FAIL olduğu G3'te de kayıtlı → B4 ile çözüldü |
| 9 | Kayıp | 8.97 W | 7.21 W | %20 | FARK — kök neden: kapsam (Q1, eFuse, LDO dahil değil; sıcak RDS katsayısı 1.6 vs 1.8). Aynı kapsamda fark <%2 |
| 2 (not) | Ham bara salınımı | — | 35–41 V | — | Yeni bilgi → B1'de değerlendirildi |

## 3. Alt ajan B — G3'te değişen üç iddia

| İddia | Sonuç | Kanıt | G4 işlemi |
|---|---|---|---|
| eFuse TPS259824O → L | **DOĞRULANDI** | TPS25982 p.4: O = circuit breaker, L = aktif sınırlayıcı; "4" = 16.9 V OVLO (p.8: 16.32/16.9/17.31 V); ILIM tablosu p.9 varyanttan bağımsız; RGE0024M aynı (p.55–57); TPS259824LNRGER Active (p.50); retry iki varyantta aynı (p.30, p.32) | Kabul. Not: L, termal kapanmaya kadar ILIM'de kalır → (VSAFE−VOUT)×ILIM kaybı; mandal EN veya güç döngüsüyle temizlenir (fail-safe tablosuna eklendi). Makara ONRGET (250) → LNRGER (3000) |
| LM70880 BIAS → /VSAFE | **KISMEN** | BIAS abs 32 V, önerilen ≤30 V (p.5); harici 10–30 V izinli (p.3); **p.13: VIN her koşulda harici BIAS'tan büyük olmalı** → giriş çöküşünde VSAFE ~11 V kalırken VIN düşebilir | **DÜZELTİLDİ: BIAS → AGND** (p.13 "kullanılmıyorsa AGND"); VCC iç LDO'dan (VIN) beslenir, IC kaybı +~0.17 W/IC (VARSAYIM 10 mA × 17 V). Kaynak atfı p.4 → p.3 düzeltildi |
| N1 bobin doyumu | **DOĞRULANDI** (çerçeve kısmen yanıltıcı) | Duyarlılık sayıları yeniden üretildi; referans nominal 6.8 µH; kesişim ≈0.46×; ham bara tepesi L'den çok VIN'e bağlı | B1 çözümü: faz aşırı akım tetiği ([N1-DECISION.md](N1-DECISION.md)) |

## 4. Özet

Doğrulanan: 10 kritik sayının 7'si fark <%1; 3 fark kök nedeniyle açıklandı (kapsam/köşe tanımı). Düzeltilen: DRC fark açıklaması, N1 akım ifadesi, BIAS bağlantısı, BIAS sayfa atfı. Açık: INA296 gecikmesi (tipik), L(I) >16 A, F1 kesme kapasitesi belgesi.
