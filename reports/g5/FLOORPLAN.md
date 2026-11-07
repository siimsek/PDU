# T-003 — Yerleşim alan bütçesi (FLOORPLAN)

Güncelleme 2026-11-07 (T-015: J2 dikey Mini-Fit Plus HCS; T-004: F1 kart dışı; T-010/R-009: Q2 TI CSD19531Q5A land). Üretici: `python scripts/floorplan.py` → [`floorplan.json`](floorplan.json). Girdi: `design/footprint-map.csv` (142 PCB satırı), footprint dosyalarının courtyard katmanı (KiCad 10 stok kütüphanesi + `hardware/lib/PDU.pretty`). Etiket: HESAP.

## Yöntem ve sınırlar
- Parça alanı = footprint dosyasındaki F.CrtYd/B.CrtYd çizimlerinin sınır kutusu (konnektörlerde kart dışına taşan kısım dahil → muhafazakâr).
- Footprint'siz PCB parçası kalmadı (F1 kart dışına taşındı).
- **Dahil olmayanlar:** iz/via/döküm alanı, Q1/Q2 için PCB-HANDOFF'un istediği ≥645 mm² bakır (iç katmanlara da yayılabilir), test noktaları, montaj delikleri, konnektör kenar boşluğu. Bu yüzden doluluk **alt sınırdır**.

## Toplam ve gruplar

Toplam courtyard alanı **3435,4 mm²** (142 parça).

| Grup (PCB-HANDOFF §3) | Parça | Alan mm² | Pay |
|---|---:|---:|---:|
| COUT bankası (32× C5750 + RRAWBL) | 33 | 1567,8 | %45,6 |
| eFuse + çıkış konnektörleri (U3/U4, J2, J3, D_REV, TVS) | 24 | 584,7 | %17,0 |
| Giriş (J1, D1, Q1/U5, CIN) | 16 | 366,7 | %10,7 |
| OVP + OC mantık, REF, mandal, LDO | 36 | 311,6 | %9,1 |
| Buck faz 1 / faz 2 | 8 + 8 | 244,0 + 244,0 | %14,2 |
| Ortak bara ayırıcı (Q2, U6) | 5 | 64,8 | %1,9 |
| Buck ortak kontrol (FB/COMP/UV/CFG) | 12 | 51,8 | %1,5 |

En büyük tekil parçalar: L1/L2 137,2 mm², J2 76,8 mm² (dikey HCS), D1/D2/D3/D_REV (SMC) 65,7 mm², U1/U2 53,3 mm², C5750 48,7 mm² × 32.

## Kart ölçüsü seçenekleri

| Seçenek | Alan mm² | Doluluk tek taraf | İki taraf | Değerlendirme |
|---|---:|---:|---:|---|
| Mevcut 101,6 × 76,2 | 7741,9 | **%44,4** | %22,2 | %55 sınırının altında, ama doluluk alt sınır; 32× C5750 bankası + Q1/Q2 bakırı + 5,5 mm bara izleriyle tek tarafta sıkışık. |
| **120 × 85 (PCB-HANDOFF tahmini)** | 10200 | **%33,7** | %16,8 | **Öneri:** tüm güç parçaları üst yüzde, COUT bankası iki fazın arasında simetrik, mantık grubu SW düğümlerinden ≥10 mm uzak. |
| 130 × 90 | 11700 | %29,4 | %14,7 | Rahat; termal yayılım için fazla bakır. |
| 140 × 100 | 14000 | %24,5 | %12,3 | Gereksiz büyük. |

%55 sınırı için gereken en küçük alan 6246 mm² — mevcut kart bunu sağlıyor. Öneri **120 × 85 mm** (yedek: mevcut 101,6 × 76,2 mm, COUT bankasının bir kısmı alt yüzde). Kart ölçüsü T-013'te THINKER kararıyla (D-kartı) sabitlenir; kullanıcıya soru sorulmaz.

## Kritik gruplar sığıyor mu
- COUT bankası (1568 mm²): 120 × 85 kartta iki faz arasında ~63 × 25 mm'lik şerit (4 sıra × 8 courtyard) yeterli; mevcut kartta aynı şerit kartın %20'sini kaplar.
- Giriş ve çıkış konnektörleri karşı kenarlarda (PCB-HANDOFF §6): J1 + J2 + J3 kenar uzunluğu ≈ 35 mm, her iki ölçüde sığar.
- Buck faz grupları (her biri 244 mm²) sıcak döngü için kompakt kalmalı; alan sorunu yok.
