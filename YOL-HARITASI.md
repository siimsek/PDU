# STM32 tabanlı dijital buck yol haritası

PDU, 20–26 V girişten 11 V / 7,5 A (82,5 W) sağlayacak, tek fazlı 100 kHz asenkron buck modülüdür. Nominal giriş 24,6 V. Çalışma zarfı direnç, sabit akım ve gerilim/akım çalışma sınırları tanımlanmış sabit güç yüklerini kapsar.

| Aşama | Durum | Geçiş ölçütü |
|---|---|---|
| Güç katı ve Git başlangıcı | Nominal ngspice karşılaştırması geçti | `6879e87` etiketi, şematik ve hesap tutarlı. Nominal çıktı ortalaması ±20 mV, ripple ±2 mV ve bobin uç değerleri ±50 mA içinde tarihî LTspice kaydını karşılar. |
| Model ve kontrol seçimi | Sürüyor | CCM küçük işaret analizi, DCM dahil anahtarlamalı A/B, çalışma köşelerinde ölçülebilir marj ve geçici rejim. |
| Sayısal etkiler ve korumalar | Bekliyor | ADC/PWM zaman planı, gecikme ve hata testleri, ayrı CBC / OVP eşiği ve gecikme kanıtı. |
| Firmware ve platform | Bekliyor | Aynı kontrol kaynakları host ve MCU derlemesinde kullanılır. İki CI çıktısı sayısal toleransla karşılaştırılır. |
| Fiziksel hazırlık | Bekliyor | Bağımsız koruma, kısa devreli S1 için enerji kesme yolu, algılama, sürücü, besleme, ısı ve prototip planı doğrulanır. |

Açık çevrim LTspice kanıtları [OPTIMIZASYON.md](buck/OPTIMIZASYON.md), güç elemanı adayları [PARCA-HEDEFLERI.md](buck/PARCA-HEDEFLERI.md) içinde. Bunlar güç katı referansına ait kayıtlardır. Yeni kontrol mimarisi için varsayımlar ve deneyler bu geliştirme dalında kaydedilir.
