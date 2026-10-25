# WP2 2026-10-25-uvlo – Tezgâh test planı (YAPILMADI)

Bu testlerin **hiçbiri yapılmadı**. Simülasyon fiziksel doğrulamanın yerini tutmaz. Ekipman: programlanabilir DC kaynak (≥ 30 V / 10 A, programlanabilir iç direnç veya seri 0,25 Ω güç direnci), elektronik yük 7,5 A, ≥ 4 kanal osiloskop (VIN, EN_BUCK, G_OVP veya VGS, O1_11V), DMM 6½ hane, termal kabin (−40…+85 °C, mümkünse 125 °C) ve 6S LiPo (gerçek pil testi için).
Geçme ölçütleri REQUIREMENTS.md ile aynıdır. **O1 anlık tepe ≤ 12,0 V; normal bus ≤ 11,1605 V.** 11,22 V yalnızca OVP yanlış tetik uyarısıdır.

| No | Test | Yöntem | Geçme ölçütü |
|---|---|---|---|
| B-U1 | Eşik ölçümü | VIN 0 → 21 V ve 21 → 17 V, 10 mV/s rampa, yük yok. OUTA_UV'de V_r ve V_f ölçülür. Oda sıcaklığı, −40, +85 (+125) °C | V_r ≤ 19,978 V, V_f ≥ 18,023 V, H ≥ 1,433 V. Ölçülen ve bütçedeki nominal (19,72 / 18,26 V) arasındaki sapma raporlanır |
| B-U2 | 20 V'ta garanti açılış | EMF 20,00 V, seri 0,25 Ω, 7,5 A yük (soğuk başlangıç ve 10 tekrar) | Her seferinde başlar, kapanma olmaz, bus ≤ 11,1605 V |
| B-U3 | Motorboating | EMF'yi V_f + I·R civarında ±50 mV adımlarla tutun, 7,5 A, 0,25 / 0,30 / 0,45 Ω | ≤ 0,25 Ω'da tekrarlı açma-kapama olmaz. Daha yüksek R değerleri INFO olarak kaydedilir |
| B-U4 | Besleme yokken çıkışlar | VIN 0 → 8 V yavaş rampa (V5_OVP < 2,7 V bölgesi). OUTA_UV, OUTB_UV, EN_BUCK izlenir | EN_BUCK < 0,4 V; U21 durumu kaydedilir. TLV3202'nin VCC < 2,7 V davranışı tanımsızdır (V) |
| B-U5 | Aşırı deşarj kapanması | 7,5 A altında EMF 20 → 17 V, 1 V/s ve 10 V/s | VIN ≥ 18,0 V iken EN düşer. Kapanmadan sonra açma-kapama olmaz |
| B-U6 | Sıcak takma | 20,0 / 25,2 / 26,0 V'ta konnektörden takma (gerçek kablo) | VIN aşımı S_UV'yi 4,90 V altında tutar. O1 ≤ 12,0 V, bus ≤ 11,1605 V. EN, ≥ 60 ms sonra |
| B-U7 | Lehim kayması | REFD_UV, VREF_OVP ve RTU/RBU oranı reflow öncesi/sonrası (veya elle lehim) | REF35 kayması + direnç kayması bütçe paylarının (±%0,1 lehim) içinde kalır |
| B-U8 | Zamanlayıcı | Soğuk açılış: OUTA ↑ → EN ↑ gecikmesi, −40 / 25 / 85 °C | 77,8–255 ms bandı içinde, ≥ 60 ms |
| B-U9 | COMP windup / restart | RAW bankı dolu iken (ayar noktası üstü) kısa dip (300 µs, 1 ms, 20 ms) sonrası yeniden etkinleşme. COMP, RAW ve VOUT izlenir | Ölü buck süresi yok; RAW aşımı OVP eşiğinin altında; bus ≤ 11,1605 V (simülasyondaki model kenetlemesi doğrulanır) |
| B-U10 | TPS48000 yeniden kurma gecikmesi (P0-03) | U10 EN/UVLO düşüp tekrar kalktığında G_OVP gecikmesi ölçülür (TDRV_EN). 300 µs / 1 ms dip sonrasında FET ↑ ve EN_BUCK ↑ sırası | **FET, buck EN'den önce açık olmalı.** Değilse P0-03 riski gerçekleşmiştir → zamanlayıcı süresini (RTT/CTT) artırın veya kısmi boşalmayı engelleyin |
| B-U11 | Kısa dip sonrası bus | 300 µs 0 V dip, 7,5 A | VOUT tepe değeri kaydedilir (simülasyon 11,43 V, anormal rejim INFO). O1 ≤ 12,0 V zorunlu |
| B-U12 | Kahverengi düşüş (brown-out) | 19 V'a 50 ms ve 15 V'a 20 ms çökme | Kapanma/yeniden başlama temiz, O1 ≤ 12,0 V |
| B-U13 | OVP etkileşimi | WP1 BENCH-TEST testleri UVLO bloğu takılıyken tekrarlanır | WP1 ölçütleri değişmez (U13 ve U10 davranışı) |
| B-U15 | U22 EN kapısı ve artık kısa dip penceresi | 7,5 A, 0,25 Ω; 0 V dipler 50 / 100 / 150 / 200 / 250 / 300 / 500 µs (20 µs kenar). OUTA_UV, EN_BUCK, COMP, RAW, VGS izlenir. Ayrıca OUTA ↓ → EN_BUCK < 0,4 V gecikmesi | OUTA düşükken EN_BUCK < 0,4 V. Her dipte O1 ≤ 12,0 V. U22'nin tetiklemediği en uzun dip süresi ve RAW aşımı/OVP açması kaydedilir (simülasyon: R-DIP, RESULTS.md) |
| B-U14 | Gerçek 6S LiPo | 3,40 V/hücreden 3,0 V'a kadar 7,5 A deşarj | Kapanma ≥ 3,0 V/hücre, kapanma sonrası salınım yok |
