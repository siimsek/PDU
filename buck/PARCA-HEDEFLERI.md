# Parça Hedef Değerleri — Açık Çevrim Buck

**Tarih:** 11 Kasım 2026
**Sınıf:** analitik hesap + varsayım. Gerçek parça (MPN) seçimi **yapılmadı**; parçaları kullanıcı kendi bulur. Bu liste arama yaparken aranacak değerleri verir.

Çalışma noktası: Vin 20 / 22,2 / 26 V → 11 V / 7,5 A (82,5 W), fsw = 100 kHz.
Ana şematik ([ltspice/buck_guc_kati.asc](ltspice/buck_guc_kati.asc)) bu tablodaki "şematikteki değer" sütununu kullanır.

| Eleman | Şematikteki değer | Aranacak özellik (hedef) | Neden |
|---|---|---|---|
| **L1** bobin | 33 µH, DCR 15 mΩ | 33 µH ±%20 (yakın: 33–47 µH) · Isat ≥ 12 A · Irms (ısıl) ≥ 9 A · DCR ≤ 15 mΩ · ekranlı güç bobini | Tepe akım 8,7 A (L −%20, 26 V) + %30 pay; RMS 7,5 A |
| **CIN** (Cin1, Cin2) | 2 × 220 µF, ESR 20 mΩ/adet | toplam ≥ 440 µF · ≥ 35 V · ESR ≤ 20 mΩ/adet · ripple akımı ≥ 2,5 A RMS/adet · polimer veya düşük ESR elektrolitik | Toplam ripple akımı ≈ 3,8 A RMS; 26 V girişe gerilim payı |
| **COUT** | 330 µF, ESR 15 mΩ | 330 µF (yakın: 330–470 µF) · ≥ 25 V · ESR ≤ 15 mΩ · ripple akımı ≥ 1 A RMS | Ripple ≤ 55 mV p-p hedefi; ESR 19 mΩ üstünde hedef aşılır |
| **S1** anahtar (N-MOSFET) | ideal, Ron 10 mΩ (`SW_10m`) | VDS ≥ 40 V (tercihen 60 V) · ID ≥ 15 A · RDS(on) ≤ 10 mΩ | Gerilim 26 V + zil payı; RMS ≈ 5,6 A, tepe 8,7 A |
| **D1** Schottky diyot | ideal, Vf 0,5 V + 10 mΩ (`D_0V5`) | VR ≥ 40 V (tercihen 60 V) · IF(AV) ≥ 10 A · Vf ≤ 0,5 V @ 7,5 A | Ortalama akım ≈ 4,3 A (26 V'ta); ters gerilim 26 V |
| **Rload** yük | 1,467 Ω | 1,47 Ω, ≥ 100 W (direnç bankası veya elektronik yük) | 82,5 W sürekli ısı |

## Notlar

- Sayılar `python buck/hesap.py` çıktısıyla aynıdır.
- ESR, DCR, Ron ve Vf değerleri **hedef/varsayımdır**; bulunan parçanın veri sayfasındaki değer şematiğe yazılıp simülasyon tekrar koşulmalıdır.
- Bulunan parça hedefi tutmuyorsa değer şematikte değiştirilir; ripple ve akımlar yeniden kontrol edilir (ör. 47 µH bobin veya 470 µF çıkış kondansatörü kabul edilebilir yakın değerlerdir).
- MOSFET'in kapı sürücüsü bu aşamanın kapsamında değildir; şematikte anahtar ideal ve `PULSE` kaynağıyla sürülür.
- Sıfırdan sert kalkışta (soft-start yok) LTspice bu ideal modelde bobin akımı tepesini ≈ 35 A, çıkış aşımını ≈ 17,4 V gösterdi. Yukarıdaki Isat hedefi yalnız kararlı durumu kapsar; gerçek devrede kalkış ayrıca ele alınmalıdır.
- Açık çevrim: duty sabitken Vin veya yük değişirse çıkış 11 V'ta kalmaz. Hassas yük bağlanmaz.
