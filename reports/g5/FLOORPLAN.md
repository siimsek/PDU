# T-003 — Yerleşim alan bütçesi (FLOORPLAN)

Tarih 2026-11-07. Üretici: `python scripts/floorplan.py` → [`floorplan.json`](floorplan.json). Girdi: `design/footprint-map.csv` (143 PCB satırı), footprint dosyalarının courtyard katmanı (KiCad 10 stok kütüphanesi + `hardware/lib/PDU.pretty`). Etiket: HESAP; F1 satırı VARSAYIM.

## Yöntem ve sınırlar
- Parça alanı = footprint dosyasındaki F.CrtYd/B.CrtYd çizimlerinin sınır kutusu (yatay konnektörlerde kart dışına taşan kısım dahil → muhafazakâr).
- F1'in footprint'i yok: 25 × 10 mm = 250 mm² (VARSAYIM, 5×20 mm sigorta klipsi sınıfı; D-001/T-004 sonrası güncellenir).
- **Dahil olmayanlar:** iz/via/döküm alanı, Q1/Q2 için PCB-HANDOFF'un istediği ≥645 mm² bakır (iç katmanlara da yayılabilir), test noktaları, montaj delikleri, konnektör kenar boşluğu. Bu yüzden doluluk **alt sınırdır**.

## Toplam ve gruplar

Toplam courtyard alanı **3759,9 mm²** (143 parça).

| Grup (PCB-HANDOFF §3) | Parça | Alan mm² | Pay |
|---|---:|---:|---:|
| COUT bankası (32× C5750 + RRAWBL) | 33 | 1567,8 | %41,7 |
| eFuse + çıkış konnektörleri (U3/U4, J2, J3, D_REV, TVS) | 24 | 660,4 | %17,6 |
| Giriş (J1, F1, D1, Q1/U5, CIN) | 17 | 616,7 | %16,4 |
| OVP + OC mantık, REF, mandal, LDO | 36 | 311,6 | %8,3 |
| Buck faz 1 / faz 2 | 8 + 8 | 244,0 + 244,0 | %13,0 |
| Ortak bara ayırıcı (Q2, U6) | 5 | 63,6 | %1,7 |
| Buck ortak kontrol (FB/COMP/UV/CFG) | 12 | 51,8 | %1,4 |

En büyük tekil parçalar: J2 152,6 mm², L1/L2 137,2 mm², D1/D2/D3/D_REV (SMC) 65,7 mm², U1/U2 53,3 mm², C5750 48,7 mm² × 32.

## Kart ölçüsü seçenekleri

| Seçenek | Alan mm² | Doluluk tek taraf | İki taraf | Değerlendirme |
|---|---:|---:|---:|---|
| Mevcut 101,6 × 76,2 | 7741,9 | **%48,6** | %24,3 | Kart sınırı %55'in altında, ama doluluk alt sınır; 32× C5750 bankası + Q1/Q2 bakırı + 5,5 mm bara izleriyle tek tarafta sıkışık. Mümkün: COUT bankasının bir kısmı alt yüzde. |
| **120 × 85 (PCB-HANDOFF tahmini)** | 10200 | **%36,9** | %18,4 | **Öneri:** tüm güç parçaları üst yüzde, COUT bankası iki fazın arasında simetrik, mantık grubu SW düğümlerinden ≥10 mm uzak. |
| 130 × 90 | 11700 | %32,1 | %16,1 | Rahat; termal yayılım için fazla bakır. |
| 140 × 100 | 14000 | %26,9 | %13,4 | Gereksiz büyük. |

%55 sınırı için gereken en küçük alan 6836 mm² — mevcut kart bunu sağlıyor, bu yüzden kart kuralı gereği kullanıcı karar maddesi **açılmadı**. T-013 (PCB kurulumu) kart ölçüsünü yine de kullanıcı onayıyla sabitler; öneri **120 × 85 mm**, yedek mevcut 101,6 × 76,2 mm (COUT bankasının bir kısmı alt yüzde).

## Kritik gruplar sığıyor mu
- COUT bankası (1568 mm²): 120 × 85 kartta iki faz arasında ~63 × 25 mm'lik şerit (4 sıra × 8 courtyard) yeterli; mevcut kartta aynı şerit kartın %20'sini kaplar.
- Giriş ve çıkış konnektörleri karşı kenarlarda (PCB-HANDOFF §6): J1 + J2 + J3 kenar uzunluğu ≈ 35 mm, her iki ölçüde sığar.
- Buck faz grupları (her biri 244 mm²) sıcak döngü için kompakt kalmalı; alan sorunu yok.
