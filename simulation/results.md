# LTspice ortalama Buck modeli — sonuç özeti

- Araç: LTspice 26.1.1, Windows batch mode
- Tarih: 2026-10-14
- Girdi: `buck-average.cir`
- Model: ideal kontrollü ortalama Buck; L=6.8 µH, C=132 µF, seri L direnci=10 mΩ, çıkış ESR=3 mΩ; PI benzeri davranışsal duty kontrolü.
- Koşul: Vin 20/22.2/25.2/26 V parametre süpürmesi; yük 5 ms'de 0.75 A'dan 7.5 A'a çıkar; ölçüm penceresi 12–15 ms.

| Vin | Vout ort. | Vout min | Vout maks. | Endüktör akımı maks. | Endüktör akımı min |
|---:|---:|---:|---:|---:|---:|
| 20.0 V | 11.00009 V | 10.98386 V | 11.01665 V | 7.62911 A | 7.36686 A |
| 22.2 V | 10.99996 V | 10.98711 V | 11.01249 V | 7.60697 A | 7.39632 A |
| 25.2 V | 11.00003 V | 10.99170 V | 11.00857 V | 7.57214 A | 7.42551 A |
| 26.0 V | 11.00002 V | 10.99599 V | 11.00415 V | 7.53767 A | 7.46353 A |

Bu sayılar yalnızca ideal ortalama modelin çıktısıdır. Model gerçek anahtarlama akım ripple'ını çözmez; akım aralığı, gerçek endüktör ripple hesabının yerine geçmez. LM70880 silikonu, akım limiti, kararlılık, EMI, kayıp ve sıcaklık hakkında kanıt oluşturmaz. Fiziksel test ve üretici modeliyle analiz gerekir.
