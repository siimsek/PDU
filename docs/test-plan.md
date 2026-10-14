# Prototip test planı

## Donanım

- Akım sınırlı 0–30 V DC kaynak, 20/22.2/26 V.
- 100 W, 0–10 A electronic load veya uygun direnç bankası.
- Diferansiyel prob/osiloskop; giriş transientine uygun ölçüm.
- Akım probu veya Kelvin shunt, termokupl/IR camera, DMM/data logger.

## Sıra

1. Görsel, polarite, kısa devre kontrolü; akım limitli ilk açılış.
2. Yüksüz 20/22.2/26 V: çıkış ayarı, startup, PG ve input current.
3. 0.5 A basamaklarla 7.5 A hedefe kadar Vout/ripple/sıcak nokta.
4. 0.75→7.5 A ve geri load step; overshoot, undershoot, recovery.
5. Her eFuse kolunda kısa devre/limit/latch; diğer port yüklüyken fault.
6. Cihaz başına 20 aç/kapa; 11 V ve 20 V girişte başlangıç akımı; sonra eşzamanlı başlatma.
7. En düşük batarya ve ağır yazılım yükünde termal denge.
8. ESC ile giriş transient genlik/süre/enerji kaydı; TVS/fuse/reverse guard gözden geçir.
9. Ethernet UDP akışını load step ve güç geçişlerinde izle.
10. Her satıra pass/fail, setup fotoğrafı, board ID, kalibrasyon ve ham veri ekle.

## Durdurma ölçütü

Anormal ses/ısı/koku, akım limiti, cihaz minimum gerilim altı, component rating aşımı, beklenmeyen latch/reset veya kontrolsüz transientte testi durdur. Düzeneği ve ölçüm bandwidth'ini kaydet.
