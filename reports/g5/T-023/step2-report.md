# T-023 Adım 2 — GND dönüşleri, INA296 Kelvin, gate dönüşü (D-012, R-019)

**Durum: T-023 InProgress; adım 3 ve 4 kaldı.** KiCad 10.0.7 (`--refill-zones --schematic-parity`): DRC hatası **0**, parite **0**, açık çift **199 → 116**, adım 1'e göre yeni açık ağ **0**. Uyarı: `{'warning:via_dangling': 6}`.

Kaynak: [`scripts/pcb_route_signals.py`](../../../scripts/pcb_route_signals.py) `--step2`, `--audit2`. Ham çıktı: [step2-audit.json](step2-audit.json), [step2-gnd-applied.json](step2-gnd-applied.json), [drc-step2.json](drc-step2.json). Netclass ve DRC kuralları değişmedi.

## GND ve L2

- Yeni GND via **71**, 71 grup; L2'ye bağlı olmayan GND padi **0**. Pad merkezi–via en uzak 2,66 mm.
- L2: **1** ada, dolu alan 9284,83 mm² (adım 1: 9287,11 mm²).
- **U12.7 (R-019):** Kendi viasına Kelvin kolu nedeniyle yer yok; U14.2 ile 0,25 mm F.Cu kısa bağla ortak via kullanır. Bu, U12 ve U14 yerel GND'sini birleştirir; dönüş akımı/SI **doğrulanamadı**.

## Kelvin (IN+ / IN−)

| Kol | Uçlar | Gerçek merkez hattı (mm, sınır 15) | Katman | SW pad / SW bakır (mm) | Aynı katman en yakın başka ağ izi (mm) | Rota altında L2 dolu |
|---|---|---:|---|---:|---:|---:|
| RS1-U11 IN+ (/ISNS1) | U11.8 → RS1.1 | 4,113 | F.Cu | 11,36 / 12,95 | 2,839 (`/VOUT`) | %86,0 |
| RS1-U11 IN- (/VOUT) | U11.1 → RS1.2 | 13,384 | B.Cu | 6,52 / 7,64 | 16,689 (`/ANODE`) | %89,7 |
| RS2-U12 IN+ (/ISNS2) | U12.8 → RS2.1 | 12,357 | F.Cu | 4,78 / 5,86 | 1,215 (`/VOUT`) | %94,4 |
| RS2-U12 IN- (/VOUT) | U12.1 → RS2.2 | 14,147 | B.Cu | 7,88 / 9,33 | 32,179 (`/ANODE`) | %91,2 |

- Dört kol da KiCad bağlantı denetiminde uçlarına bağlı ve ≤15 mm. SW bakırının altından geçmiyor.
- Kol tipi: yük akımı taşımayan zone tap; INA296 yanında IN− için 0,25 mm neck, avlu içinde.
- HV 0,6 mm: DRC kuralı değişmeden geçti.
- **Paralel değil:** IN+ F.Cu, IN− B.Cu ve iki kol farklı uzunlukta. RS padlerinin aralığı ile INA296'nın IN+/IN− pinlerinin karşı kenarlarda olması, kart üstünde yakın paralel çifti engelliyor. Kartın "paralel" koşulu bu haliyle **sağlanmadı**; karar THINKER'da.
- L2 oranı yüzde 100 değil: rota örneklerinin kalanı, yolun kendi vialarının ve komşu vialarının L2 anti-padlerine denk geliyor.

## Gate

- U6.6 → Q2.4: 5,469 mm (sınır 10,0 mm), değişmedi.
- R_GS kolu: 16,015 mm, 0,4 mm, F.Cu. R_GS, Q2'den yaklaşık 11 mm güneyde olduğu için HANDOFF §3.4'teki "bitişik" düzen sağlanmıyor; yerleşim değiştirilmedi, karar THINKER'da.
- **TP_ISO_GATE taşındı:** D-008 konumu kartın batısında, gate düğümünden yaklaşık 90 mm uzaktaydı. TP_SW1/2 için R-018'de seçilen ilkeyle (97,4; 44,6) konumuna alındı, 1,2 mm bağ. Bu taşıma R-019'da açıkça yazılı değildir; inceleme gerekir.

## Açık kalanlar (adım 3 ve 4)

Toplam 116 açık çift; en çok: `/P5V_PROT` 22, `/CLR_N` 5, `/EN_BUCK` 5, `/COMP` 4, `/ISO_OV` 4, `/OC_REF` 4, `/OVP_REF` 4, `/VOUT` 4.

Kelvin test padleri TP_ISNS1P, TP_ISNS1N, TP_ISNS2P, TP_ISNS2N kartın batısında kaldı; INA296 girişine uzun kol asmamak için bağlanmadı. TP_SW ve TP_ISO_GATE ile aynı karar gerekiyor.

## Doğrulanamayanlar

Dönüş akımı dağılımı ve SI; gerçek Kelvin ölçüm doğruluğu; üretici via onayı; 0,6/0,3 mm via (VARSAYIM, PCB-HANDOFF §7).
