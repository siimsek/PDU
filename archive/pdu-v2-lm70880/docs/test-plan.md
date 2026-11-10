> **SUPERSEDED (G3, 2026-11-07) → reports/g2/BENCH-ACCEPTANCE.md.** Bu belge geçmiş kaydıdır; içerik değiştirilmedi.

# Prototip test planı

## Güncel kabul bağlamı

Bu test planı, [PROJECT-STATE](PROJECT-STATE.md) ve [REVIEW-CHECKLIST](REVIEW-CHECKLIST.md) ile okunur.48 simülasyon koşusu512 geçen/2 O1 başarısız kontrol verdi. Gerçek yük, koruma, döngü, termal ve EMI testleri yapılmış sayılmaz. Repo checkpoint'i yeni elektriksel kabul değildir.

## Donanım

- Akım sınırlı 0–30 V DC kaynak, 20/22.2/26 V.
- 100 W, 0–10 A electronic load veya uygun direnç bankası.
- Diferansiyel prob/osiloskop; giriş transientine uygun ölçüm.
- Akım probu veya Kelvin shunt, termokupl/IR camera, DMM/data logger.

## Sıra

1. Görsel, polarite, kısa devre kontrolü; akım limitli ilk açılış.
2. Yüksüz 20/22.2/26 V: çıkış ayarı, startup, PG ve input current.
3. 0.5 A basamaklarla 7 A gereksinime kadar Vout/ripple/sıcaklık; ardından yalnızca 7 A termal ve koruma koşulları geçerse 7.5 A tasarım kapasitesi kontrolü.
4. 0.75→7 A ve geri load step; overshoot, undershoot, recovery. İki faz akım paylaşımını ve her fazın peak akımını ayrı probla kaydet.
5. Her eFuse kolunda kısa devre/limit/latch; diğer port yüklüyken fault.
6. O1 ve S2E gerçek yük profilleri kaydedildikten sonra uygun eFuse ayarlarını belirle; otomatik olarak 5 A seçme. Mevcut 301 Ω / 604 Ω dirençleri yaklaşık 4.96 A / 2.53 A nominal eşik verir. Cihaz başına 20 aç/kapa; 11 V çıkış ve 20 V girişte başlatma akımını, sonra eşzamanlı başlatmayı kaydet. Erken eFuse açarsa testte limiti yükseltme, önce dalga şeklini kaydet.
7. En düşük batarya ve ağır yazılım yükünde 7 A'da termal denge; iki faz sıcaklığı ve akım paylaşımı eşiklerini kaydet.
8. ESC ile giriş transient genlik/süre/enerji kaydı; TVS/fuse/reverse guard gözden geçir.
9. Ethernet UDP akışını load step ve güç geçişlerinde izle.
10. Her satıra pass/fail, setup fotoğrafı, board ID, kalibrasyon ve ham veri ekle.

## Durdurma ölçütü

Anormal ses/ısı/koku, akım limiti, cihaz minimum gerilim altı, component rating aşımı, beklenmeyen latch/reset veya kontrolsüz transientte testi durdur. Düzeneği ve ölçüm bandwidth'ini kaydet.
