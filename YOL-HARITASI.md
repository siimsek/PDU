# STM32 tabanlı dijital buck yol haritası

PDU, 20–26 V girişten 11 V / 7,5 A (82,5 W) sağlayacak, tek fazlı 100 kHz asenkron buck modülüdür. Nominal giriş 24,6 V. Hedef yükler direnç, sabit akım ve gerilim/akım çalışma sınırları tanımlanmış sabit güç yükleridir.

| Aşama | Durum ve geçiş ölçütü |
|---|---|
| Güç katı ve temiz başlangıç | `6879e87` güç dalı ve etiketiyle eşleşiyor. Yerel `main` bu sürüme getirildi, `e22f92b` eski `main` yedeklendi. Uzak `main` işlemi kullanıcı onayını bekliyor. Şematik ve açık çevrim LTspice dosyaları korundu. ngspice nominal gerilim farkı 0,5 mV, ripple farkı yaklaşık 0,02 mV. |
| Kontrol seçimi | 180 doğrusal CCM noktası, beş anahtarlamalı aday ve aynı C kontrol çekirdeği. Type III + Vin feedforward ve büyük sinyal akım desteği ilk aday. En düşük gerilim çevrimi faz/kazanç marjı 49,2° / 7,29 dB, kesim frekansı 3,36 kHz. Hesap kapısı 40° / 6 dB. |
| Anahtarlamalı elektriksel kapı | CachyOS’ta 90 zarf koşusu, ilave kalkış matrisi, 48 örnekli 10–55 mΩ Cout ESR tasarım zarfı ve iki ayrı zamanlama/şönt koşusu. Zarf test sınırları geçici 9–11,75 V, kararlı ortalama 11 V ±%1, PWM ripple ≤165 mV t-t, tepe akım ≤10,65 A ve arıza kilidi yok. Bu değerler prototip doğrulama hedefidir. |
| Geniş sıcaklık/ESR stresi | ESR 120 mΩ’a kadar birleşik örneklerde 48 koşudan 14'ü sınırı aştı. `--strict-stress` bu koşulları başarısızlık olarak döndürür. 55 mΩ işletim üst hedefi, düşük L ile yüksek ESR birleşiminin ripple etkisini sınırlar. Cout adayının soğuk ve yaşlanmış ESR, akım ve gerilim anması laboratuvarda kapatılmalı. |
| Koruma | Simülasyonda kısa devre CBC ölçütü ≤0,65 µs ve <11 A, kalıcı arıza PWM kilidi ≤2,2 ms. Kayıp ADC, rayda ADC, takılı gerilim okuması, UVLO, kapanma ve ön gerilimli yeniden başlama koşuları var. S1 kısa devresinde ikili analog tetik ve seri kesici adayının gecikme şartları belirlendi. |
| Firmware ve platform | STM32G474 ELF/BIN ve vektör tablosu CachyOS’ta Arm GNU 14.3.Rel1 ile doğrulandı. Emniyetli varsayılan imaj ve güçsüz osiloskop imajı derlendi. [GitHub Actions](https://github.com/siimsek/PDU/actions) Windows Server 2025 x64 ve Ubuntu koşuları için. Windows 11 masaüstü ve tezgâh ayrı aşamalar. |
| Prototip kapısı | Bekliyor. Harici kilit, iki analog eşik, ayırıcı/klemp, driver, kaynak koruması, doğrulanmış ESR ve fiziksel ısı/EMI. ADC yerleşme süresi, ADC→PWM WCET, gate kesme zamanı ve hata durumunda yük düğümü osiloskopla ölçülecek. Ön gerilim, boşta bootstrap ve 82,5 W CPL power-good sırası ölçülecek. |

Tarihî açık çevrim ölçütleri [OPTIMIZASYON.md](buck/OPTIMIZASYON.md) ve güç elemanı adayları [PARCA-HEDEFLERI.md](buck/PARCA-HEDEFLERI.md) içinde. Yeni yöntem, sınırlar, pinler ve üretici kaynakları [TASARIM.md](control/TASARIM.md) içinde. Testler ve üretilebilen dosyalar için [README](README.md).
