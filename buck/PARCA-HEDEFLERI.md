# Parça Hedef Değerleri — Açık Çevrim Buck

**Tarih:** 11 Kasım 2026
**Sınıf:** analitik hesap + LTspice (ideal elemanlar) + varsayım. Gerçek parça (MPN) seçimi **yapılmadı**; parçaları kullanıcı kendi bulur. Bu liste arama yaparken aranacak değerleri verir. Gerekçe ve test sonuçları: [OPTIMIZASYON.md](OPTIMIZASYON.md).

Çalışma noktası: Vin 20 / 22,2 / **24,6** / 25,2 / 26 V → 11 V / 7,5 A (82,5 W), fsw = 100 kHz.
Ana şematik ([ltspice/buck_guc_kati.asc](ltspice/buck_guc_kati.asc)) bu tablodaki "şematikteki değer" sütununu kullanır.

| Eleman | Şematikteki değer | Aranacak özellik (hedef) | Neden |
|---|---|---|---|
| **L1** bobin | 33 µH, DCR 15 mΩ | 33 µH ±%20 · Isat ≥ 12 A · Irms (ısıl) ≥ 9 A · DCR ≤ 15 mΩ · ekranlı güç bobini | Tepe akım 8,74 A (L −%20, 26 V) + %30 pay; RMS 7,5 A; ripple %25 (24,6 V) |
| **CIN** (Cin1, Cin2) | 2 × 220 µF, ESR 20 mΩ/adet | toplam ≥ 440 µF · ≥ 35 V · ESR ≤ 20 mΩ/adet · ripple akımı ≥ 2,5 A RMS/adet · polimer veya düşük ESR elektrolitik | Toplam ripple akımı 3,8 A RMS; giriş ripple'ı ≈ 125 mV t-t; 26 V girişe gerilim payı |
| **COUT** | 680 µF, ESR 25 mΩ | 680 µF ±%20 (2 × 330 µF olabilir) · ≥ 25 V · **toplam ESR 20–30 mΩ** (alt sınır da var) · ripple akımı ≥ 1 A RMS | Sabit güç yüküyle LC sönümü ve yük adımı tepkisi; ESR 20 mΩ altına inerse sönüm payı azalır, 30 mΩ üstünde ripple artar (köşede 80 mV t-t) |
| **S1** anahtar (N-MOSFET) | ideal, Ron 10 mΩ (`Ron=10m`) | VDS ≥ 40 V (tercihen 60 V) · ID ≥ 15 A · RDS(on) ≤ 10 mΩ | Gerilim 26 V + zil payı; RMS 5,7 A (20 V), tepe 8,7 A |
| **D1** Schottky diyot | ideal, Vf 0,5 V + 10 mΩ (`Vf=0.5 Ron=10m`) | VR ≥ 40 V (tercihen 60 V) · IF(AV) ≥ 10 A · Vf ≤ 0,5 V @ 7,5 A | Ortalama akım 4,2 A (26 V); iletim kaybının üçte ikisi (2,3 W) diyottadır |
| **Rload** yük | 1,467 Ω | 1,47 Ω, ≥ 100 W (direnç bankası veya elektronik yük) | 82,5 W sürekli ısı |

## Notlar

- Sayılar `python buck/hesap.py` (analitik) ve `python buck/dogrula.py secilen` (LTspice) çıktılarıyla aynıdır.
- ESR, DCR, Ron ve Vf değerleri **hedef/varsayımdır**; bulunan parçanın veri sayfasındaki değer şematiğe ve `hesap.py` / `dogrula.py` sabitlerine yazılıp yeniden koşulmalıdır.
- COUT için çok düşük ESR'li (≈ 5–10 mΩ) polimer kondansatör tek başına **hedefi tutmaz**: ripple küçülür ama LC sönümü zayıflar. Böyle bir parça seçilirse kapasite artırılmalı ve `dogrula.py` yeniden koşulmalıdır.
- Isat hedefi yalnız kararlı durumu kapsar. Soft-start olmadan sert kalkışta LTspice bu ideal modelde bobin akımı tepesini ≈ 46 A, çıkış aşımını ≈ 17 V gösterir; 5 ms'lik duty rampasıyla aynı devre 10 A / 11,3 V'ta kalır. Kalkış kontrol aşamasında çözülmelidir, bobin seçimiyle değil.
- MOSFET'in kapı sürücüsü bu aşamanın kapsamında değildir; şematikte anahtar ideal ve `PULSE` kaynağıyla sürülür. Anahtarlama ve çekirdek kayıpları modelde yoktur.
- Açık çevrim: duty sabitken Vin veya yük değişirse çıkış 11 V'ta kalmaz. Gerçek O1 / S2E bağlanmaz.
