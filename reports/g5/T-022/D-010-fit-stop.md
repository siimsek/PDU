# T-022 — D-010 durdurma kanıtı (Q2 ve güney şerit)

**Durum: T-022 Blocked.** D-010 durdurma koşulu gerçek DRC ile tetiklendi: Q2 180° iken gate izi 10 mm'ye sığmıyor. `PDU.kicad_pcb` bu dalda değişmedi; güç yolu çizilmedi.

Kaynak: [`q2_fit_probe.py`](q2_fit_probe.py) → [`q2-fit-probe.json`](q2-fit-probe.json). 10.0.7, `pcb drc --severity-all --refill-zones --schematic-parity`, geçici kopyalarda. Koordinatlar D-006. Uzunluklar pad merkezinden pad merkezine iz merkez hattıdır. Bu bir yerleşim sığma denemesidir, bitmiş rota değildir; `unconnected_items` sayılmadı.

## Olgular (DRC)

| Durum | Eklenen | Uzunluk | DRC hatası | Parite |
|---|---|---:|---:|---:|
| Değişmemiş kart (Q2 0°) | — | — | 0 | 0 |
| Q2 180°, gate doğudan, x = 97,55 | 0,4 mm F.Cu | 11,033 mm | 3 (clearance, /VSAFE via) | 0 |
| Q2 180°, gate doğudan, x = 97,90 | 0,4 mm F.Cu | **11,562 mm** | 0 | 0 |
| Q2 90°, gate | 0,4 mm F.Cu | **5,469 mm** | 0 | 0 |
| D-010 güney şeridi 7,0 mm (y 25–32, x 60–96) | F.Cu | 36,0 mm | 6 (1 kısa devre `TP_VSAFE`, 5 maske köprüsü) | 0 |
| Güney şerit 5,5 mm (y 26,5–32) | F.Cu | 36,0 mm | 0 | 0 |
| Q2 90° adayı: gate + B.Cu 7,0 mm /VOUT + B.Cu 5,5 mm /VSAFE + 20 ek via | | gate 5,469 / /VOUT 46,8 / /VSAFE 23,5 mm | 0 | 0 |

## Neden 180° sığmıyor (HESAP, geometri KiCad'den)

- 180°'de gate padi [96.748, 56.11], source padleri [96.748, 52.3], [96.748, 53.57], [96.748, 54.84]: gate, source sütununun U6'dan uzak (kuzey) ucunda.
- Drain padi ile source sütunu arasındaki boşluk yaklaşık 0,56 mm; 0,4 mm iz ve iki yandaki açıklıklar sığmaz. İz source sütununun doğusundan dolaşmak zorunda.
- Source padlerindeki T-021 vialarına karşı `HV to logic clearance` kuralı (0,6 mm, `PDU.kicad_dru`) izi x = 97,90 hattına itiyor; x = 97,55'te 3 clearance hatası çıktı.
- D-010'un 9,33 mm tahmini drain padi ve 0,15 mm açıklıkla kuruluydu; gerçek kural ve source dolaşmasıyla DRC temiz ölçüm 11,562 mm. HANDOFF §3.4 sınırı 10 mm.

## 90° adayı (yalnız sığma kanıtı)

- 90°'de gate padi [95.9, 51.453], source padleri güneyde, drain kuzeyde.
- Denenen: drain padinde 9 + 8 = 17 via; source tarafında 3 + 12 = 15 via; /VOUT B.Cu Q2'den bankanın ortasına (x 57, y 44,2) kadar; /VSAFE B.Cu U3/U4 altına kadar. Bu, HANDOFF §3.3'teki "Q2 drain'i bankanın ortasına" koşuluyla da uyumludur; 7,0 mm güney şeridini gereksiz kılar.
- **Kanıtlanmayan:** source padlerinden via alanına F.Cu bağlantısı, L3 dökümlerinin yeni Q2 yönüne göre yeniden çizilmesi (T-021 /VSAFE cebi Q2 0° içindi), eFuse ve COUT bağlantıları, Kelvin uçları, akım/termal davranış.

## D-010'daki diğer ölçü notu

D-010'un 5×3, 0,75 mm adımlı drain dizisi mevcut 3×3, 1,2 mm adımlı T-021 dizisiyle aynı noktalara oturmuyor; pad merkezli yorumda merkez vialar üst üste biner (D-011). Dolayısıyla "9 + 6 = 15" olduğu gibi uygulanamaz. Bu denemede mevcut 9 via korunup araya 8 via eklendi.

## Karar gereği

T-022 kartı ve D-010, bu durumda netclass/DRC gevşetmeyi yasaklıyor ve yerleşim kararı istiyor. Q2 yönü THINKER kararıdır (D-011 bekleniyor).
