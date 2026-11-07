# T-003 — Yerleşim alan bütçesi (FLOORPLAN)

Güncelleme 2026-11-07 (T-015 J2 dikey HCS; T-004 F1 kart dışı; R-009 Q2 TI land; T-012 D-008 test noktaları). Üretici: `python scripts/floorplan.py` → [`floorplan.json`](floorplan.json). Girdi: `design/footprint-map.csv` (180 PCB satırı: 142 parça + 38 D-008 test padi/fixture/jumper), footprint courtyard katmanları. Etiket: HESAP.

## Yöntem ve sınırlar
- Parça alanı = footprint'teki F.CrtYd/B.CrtYd çizimlerinin sınır kutusu (konnektörlerde kart dışına taşan kısım dahil → muhafazakâr).
- J_OVP_INJ_BUS: D-008'deki `..._Relief2x` varyantının courtyard'ı 90 mm kablo gerilme giderme yolunu içerdiği için (22,5 × 92,3 mm) aynı 6 mm² pad geometrisinin gerilme gidermesiz varyantı kullanıldı (22,5 × 8,0 mm).
- **Dahil olmayanlar:** iz/via/döküm alanı, Q1/Q2 ≥645 mm² bakır (iç katmanlara da yayılabilir), montaj delikleri, kenar boşluğu → doluluk **alt sınırdır**.

## Toplam ve gruplar

Toplam courtyard alanı **3817,7 mm²** (180 satır).

| Grup | Parça | Alan mm² | Pay |
|---|---:|---:|---:|
| COUT bankası (32× C5750) | 33 | 1567,8 | %41,1 |
| eFuse + çıkış konnektörleri | 24 | 584,6 | %15,3 |
| Test noktaları / fixture (D-008) | 38 | 382,2 | %10,0 |
| Giriş (J1, TVS, ters kutup, CIN) | 16 | 366,7 | %9,6 |
| OVP + OC mantık, REF, mandal, LDO | 36 | 311,6 | %8,2 |
| Buck faz 1 | 8 | 244,0 | %6,4 |
| Buck faz 2 | 8 | 244,0 | %6,4 |
| Ortak bara ayırıcı | 5 | 64,8 | %1,7 |
| Buck ortak kontrol (FB/COMP/UV/CFG) | 12 | 51,8 | %1,4 |

## Kart ölçüsü seçenekleri

| Seçenek | Alan mm² | Doluluk tek taraf | İki taraf |
|---|---:|---:|---:|
| current 101,6 x 76,2 | 7741,9 | %49,3 | %24,7 |
| PCB-HANDOFF estimate 120 x 85 | 10200,0 | %37,4 | %18,7 |
| 130 x 90 | 11700,0 | %32,6 | %16,3 |
| 140 x 100 | 14000,0 | %27,3 | %13,6 |

%55 sınırı için en küçük alan 6941 mm². Karar: **D-006 — 120 × 85 mm, bileşenler yalnız üst yüzde** (doluluk %37,4). Mevcut 101,6 × 76,2 mm kart %49,3 ile sınırın altında ama bakır/iz payı düşünüldüğünde sıkışık.

## Kritik gruplar
- COUT bankası (1568 mm²): 120 × 85 kartta iki faz arasında ~63 × 25 mm şerit (4 × 8).
- J1 + J2 + J3 kenar uzunluğu ≈ 35 mm; J_OVP_INJ_BUS (22,5 mm) kart kenarına yakın (PCB-HANDOFF §3.7).
- Test padleri (D-008) ilgili grupların yanına; prob GND padleri her grupta.
