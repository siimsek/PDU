# G3 — G2 çıktısının bağımsız denetimi

Kapsam: dal `wp/g2-circuit-design` @ `6b2b16b` (Aşama 1–6). Yöntem: (1) çalışma ortamı ve baseline, (2) 10 kritik sayının ayrı betikle yeniden türetilmesi ([`rederive.py`](rederive.py) → [`rederive-results.json`](rederive-results.json); yöntemler farklı: Monte Carlo köşe, Euler entegrasyonu, ayrı Ridley kodu), (3) 14 datasheet atfının sayfa sayfa PDF'te aranması, (4) SPICE koşu bütünlüğü, (5) G2 sonuçları verilmeden yalnız kod/rapor okuyan bağımsız alt ajan incelemesi. Not: (2)'yi G2'yi yazan aynı ajan yaptı; kısmi bağımsızlıktır. Bağımsız gözlük (5) ayrı bağlamda çalıştı.

Durumlar: **DOĞRULANDI** / **FARK** / **DÜZELTİLDİ** / **AÇIK**.

## 1. Ortam ve baseline

| Madde | G2/repo kaydı | Bağımsız sonuç | Durum |
|---|---|---|---|
| G2 Aşama 1–6 dosyaları | PROGRESS "tamam" | Commit 9e2918e…6b2b16b; `design/pdu_v2.cir`, 5 aile, `bom-v2.csv`, `pdu_v2_spec.yaml`, KICAD-CHANGE-LIST-FINAL, PCB-HANDOFF, BENCH, run_all, VERIFY, BOM-OPEN mevcut | DOĞRULANDI |
| Araçlar | — | Python 3.14.5; kicad-cli 10.0.7 (`C:\Program Files\KiCad\10.0\bin`, PATH dışı); ngspice-47 | DOĞRULANDI |
| ERC | 0/0 | 0 ihlal ([baseline/erc.json](baseline/erc.json)) | DOĞRULANDI |
| DRC | 197 bağlantısız / 301 uyarı | 197 bağlantısız; **228 uyarı** (silk 223, lib_footprint_mismatch 5) + 73 şema paritesi uyarısı (Description/MPN alanı) ([baseline/drc.json](baseline/drc.json)) | FARK — KiCad 10.0.7 kural seti/yok sayılan kontroller; bağlantısız sayısı aynı |
| Boş MPN (mevcut şema BOM) | 57 | 57/73 | DOĞRULANDI |
| ngspice baseline O1 | Linux-44.2: 16.89 V | Windows-47: 16.890 V ([baseline/o1-efuse-ovp-windows.log](baseline/o1-efuse-ovp-windows.log)) | DOĞRULANDI (fark 0) |
| pytest / run_all | 91 passed / 7 adım exit 0 | 91 passed; run_all 7/7 exit 0; 68 koşunun ölçüm ve deck/girdi hash'leri birebir | DOĞRULANDI |

## 2. Kritik 10 sayı (bağımsız yeniden türetme)

| # | Madde | G2 iddiası | Bağımsız sonuç | Fark | Durum |
|---|---|---|---|---|---|
| 1 | Koruma eşiği + gecikme → O1 tepe (HESAP) | 11.9345 V (eşik 11.2649–11.5309, 1.047 µs) | 11.9283 V (Euler, seri R dahil; eşik MC birebir) | 0.05 % | DOĞRULANDI → G3'te referans sürüklenmesi 165 K ile **11.941 V** (DÜZELTİLDİ) |
| 2 | U3/U4 IN tepe | ≤11.935 V | aynı düğüm 11.928 V | 0.06 % | DOĞRULANDI |
| 3 | ILIM garantili-min toplam | 11.59 A | 7.23 + 4.36 = 11.59 A | 0 | DOĞRULANDI (varyant hatası ayrı: E1) |
| 4 | RUV1 174k yükselen köşe | 17.365–19.623 V | 17.3647–19.6229 V | 0 | DOĞRULANDI |
| 5 | Bobin Isat marjı | ilim tepe 8.974 A, marj 4.53 A | 8.974 A, 4.526 A | 0 | DOĞRULANDI (75 ns tipik → koşullu) |
| 6 | F1 hata akımı / kesme | 1040 A | 26/(0.025) = 1040 A | 0 | DOĞRULANDI |
| 7 | PM / GM köşeleri | 66.86° / 11.65 dB | 66.90° / 11.58 dB | 0.06 % / 0.6 % | DOĞRULANDI |
| 8 | Yük adımı bara min | SİM 10.81 V | 1. derece 10.799 V | 0.1 % | DOĞRULANDI |
| 9 | Kayıp bütçesi | 8.97 W | 8.97 W | 0 | DOĞRULANDI (aynı %92 VARSAYIMI; bağımsız fiziksel yol yok) |
| 10 | Tam sistem SİM O1 tepe | 11.912 V | analitik 11.928 V; G3 yeniden koşu 11.920 V | 0.1 % | DOĞRULANDI |

## 3. Datasheet sayfa atıfları (14 örnek)

10 doğru (LM70880 VFB p.7, gm p.7, VEN p.6, VCS p.8, Eq.7 p.16; TPS25982 ILIM p.9; LM74502H tOVP p.6; TLV3601 tPD p.7; LVC1G74 p.7; TPS7A16 PG p.6). **4 sayfa numarası yanlış (değerler doğru, uydurma yok) → DÜZELTİLDİ:** TPS25982 abs-max p.6→**p.7**; REF5025A doğruluk p.4→**p.5**; CSD19531Q5A RDS/Ciss/Qg p.2→**p.3**; TPS25982 dV/dt Eq.3 p.21→**p.22** (VIN+4 V notu p.37).

## 4. Bağımsız alt ajan bulguları (13 hata + 9 şüpheli iddia)

| ID | Bulgu (özet) | Doğrulama | Durum |
|---|---|---|---|
| E1 | BOM TPS259824**O** = circuit breaker; model aktif sınırlayıcı | TPS25982 p.4 tablosu: O=Circuit Breaker, L=Active Current Limiter | **DÜZELTİLDİ** → TPS259824LNRGER (BOM, KICAD listesi); F4 ILIM max ile yeniden koşuldu |
| E2 | LM70880 BIAS `/VOUT`'ta (abs 32 V); hata SİM'de VRAW 33 V | Netlist pin 6 `/VOUT`; datasheet BIAS 32 V | **DÜZELTİLDİ** → BIAS `/VSAFE` (≤11.94 V); F1/F5'e VRAW <60 V (VOUT/ISNS+) kriteri |
| E3 | Eğim kompanzasyonu oranı ters | Se/Sn = L/L_sc | **DÜZELTİLDİ** 0.86 / 0.69 (≥0.5); test düzeltildi |
| E4 | "432 köşe" | 3·3·3·2·2·2 = 216 | **DÜZELTİLDİ** |
| E5 | LOOP'ta eski trip_min | | **DÜZELTİLDİ** |
| E6 | COUT9–16 gerekçesi "8×: 2.5 mV marj" | 8× → 12.006 V FAIL | **DÜZELTİLDİ** |
| E7 | Kaba OV "≤12.77 V" | JSON 11.58–13.74 V, SİM 13.98 V | **DÜZELTİLDİ** |
| E8 | R08 ray eşikleri | açılma 2.90–3.375, kapanma 2.57–3.16 V | **DÜZELTİLDİ** |
| E9 | BENCH T6b "≤2.5 mV" | SİM 0.133 V | **DÜZELTİLDİ** |
| E10 | Kaba–hassas aralık <30 mV | 21.6 mV | **DÜZELTİLDİ** → 60.4k/19.6k, aralık 44 mV; test eklendi |
| E11 | SİM kriterleri trip_min'e göre; mandal geç eşikte (görmüyor); kararlı üst sınır yok | | **DÜZELTİLDİ** → 11.22 V bandı, F3'te mandal trip_min'de, `vraw_end ≤11.1605 V`; yığılmış üst köşe artık mandalı set ediyor (FAIL) |
| E12 | FRA R_INJ yüksek empedans tarafında | | **DÜZELTİLDİ** → `/VOUT`–RFB1 üstü |
| E13 | D_REV derating 0.05 V | ters 11.94 V | **DÜZELTİLDİ** (%30); sıcak kaçak AÇIK |
| D1 | R02 "Evet" aşırı | koşul dışı gecikmeler, parazitik payı yok | **DÜZELTİLDİ** → "Koşullu" |
| D2 | Yük adımı yığılmış köşeler FAIL ama devam ediliyor; marj 25 mV; tek VIN | | KISMEN: VIN 20/26 + L köşeleri eklendi (PASS, min 10.802 V); yığılmış köşeler **AÇIK** (USER-DECISIONS #3) |
| D3 | Tipik değerler sınır gibi (75 ns, POR 2.1 V, IdVdt, Isat, OVLO, sim sabitleri) | | KISMEN: raporlarda "tipik/koşullu" işaretlendi; sim_runner'daki eFuse sabitleri params dışında → AÇIK (düşük) |
| D4 | Referans sürüklenmesi 100 K | kutu yöntemi 165 K | **DÜZELTİLDİ** (O1 marjı 65→59 mV) |
| D5 | Direnç derating 70 °C'de | | **DÜZELTİLDİ** (85 °C, ×0.82); R_OVT geçici 0.21 W darbe kapasitesi AÇIK; U5/U6/U10 %82–89 BOM-OPEN'da işaretli |
| D6 | "faz ~60 A" kanıtsız | | **DÜZELTİLDİ** → `il1_max_fault` ölçümü: F1 61–63 A, F5 ≤86 A |
| D7 | Kapanma enerjisi anlamsız | ideal anahtar, EAS çığ değeri | **DÜZELTİLDİ** → iddia kaldırıldı, AÇIK |
| D8 | gm maks VARSAYIM en kötü köşeyi belirliyor | | AÇIK (tezgâh FRA) |
| D9 | UVLO düşüş eşiği tipik | | AÇIK (kullanıcı politikası) |

## 5. G3'te ortaya çıkan yeni bulgu

| ID | Bulgu | Sonuç | Durum |
|---|---|---|---|
| N1 | Yüksek taraf kısasında arızalı faz akımı 61–86 A (Isat tipik 13.5 A); model sabit L | Duyarlılık: L_eff/L 0.5 → 11.990 V, **0.4 → 12.019 V FAIL** | **AÇIK** — L(I) eğrisi veya tezgâh ölçümü; alternatif yüksek Isat bobin / COUT artırımı |
| N2 | G2 commit'inde 2 hata ayıklama dalga dökümü (40 MB) | rapor sayısına kaynak değil | DÜZELTİLDİ (git rm, geçmişte duruyor) |
| N3 | sim-results.json eski koşu adlarını tutuyordu (F5 97 koşu) | | DÜZELTİLDİ (yalnız güncel vakalar; test eklendi) |

## 6. DESIGN-RULES ve SPICE bütünlüğü

- 30 kuralın her "sağlandı" satırı bir kanıt dosyasına bağlı (JSON/SİM/BOM/KICAD listesi); kanıtsız "Evet" bulunmadı. R02, R08, R14 "koşullu"; R18 "Hayır" (AÇIK).
- 70 koşunun hepsi tamamlandı; tamamlanmayan PASS yok; deck SHA256'ları dosyalarla eşleşiyor; kriter tablosu `sim_runner.py` ile birebir ve G3 kriterleriyle yeniden üretildi ([SIM-RESULTS](../g2/SIM-RESULTS.md)).

**Sayılar:** doğrulanan 10/10 kritik sayı + 10/14 sayfa; düzeltilen 4 sayfa + 13 hata + 6 şüpheli iddia + 2 G3 bulgusu; AÇIK 5 (N1, D2 yığılmış köşeler, D3 kalan sabitler, D8, D9) + G2'den devreden fiziksel kabul kalemleri.
