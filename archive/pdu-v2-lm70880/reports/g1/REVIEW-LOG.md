# G1 inceleme kaydı (PR #2, 7 tur) — birleştirilmiş

Orijinal tur raporları [`archive/g1-evidence/reports/g1/`](../../archive/g1-evidence/reports/g1/) altında (git geçmişi korunur). Her bulgunun G2'deki tasarım karşılığı [`reports/g2/DESIGN-RULES.md`](../g2/DESIGN-RULES.md) kural numarasıyla verilir; güncel durum için [`docs/START-HERE.md`](../../docs/START-HERE.md).

| Tur (yorum) | Bulgu | G1 sonucu | G2 karşılığı | Kanıt (arşiv) |
|---|---|---|---|---|
| 6681813880 | OVP aileleri birleştirilemez (Family 1 ideal, Family 2 buck-short ayrı) | Family 1 TDELAY düzeltildi; Family 2 O1 18.8039 V **FAIL** korundu | R01/R02: tek netlistte kısa devre + koruma (G2 F1) | PR2-REVIEW-6681813880.md |
| 6681813880 | Yük adımı bara min 10.7109 V | **FAIL** korundu | R26: COUT 16×, COMP yeni → G2 F3 nominal min 10.81 V | aynı |
| 6681813880 | UVLO 180k 20 V restart sağlamaz | 174k önerildi | RUV1 174k (17.365–19.623 V) | aynı |
| 6681813880 | eFuse ILIM nominal toplam 7.4877 A < 7.5 A | **FAIL** | R17: 182/300 Ω garantili min 11.59 A | aynı |
| 6682187742 | Gerçek kapanma kenarı, Ceff/akım zarfı, MPN zinciri, fail-closed testler | MPN zinciri aday; kapanma garanti yok | R04/R14: maks gecikmeli sürücü (LM74502H) | PR2-REVIEW-6682187742-RESPONSE.md |
| 6683120653 | Ortak bara hatasında U3/U4 IN 40.709 V (>30 V abs) | **FAIL**; ortak ayırıcı önerildi | R01: VSAFE ≤11.915 V (SİM) | PR2-REVIEW-6683120653.md |
| 6692033623 | TLV3601 giriş clamp akımı (10.956 mA @ VCC=0), 5 V ray geri beslemesi | **FAIL** → bölücü büyütüldü | R06/R07: 6.29 mA, bleeder | PR2-REVIEW-6692033623.md |
| 6692825552 | Mandal VCC<1.65 V belirsiz; sürücü INP/kapı boşaltma eksik; eFuse OUT ≤ VIN+0.3 V; LDO termal | AÇIK | R08–R13, R16, R21 | PR2-REVIEW-6692825552.md |
| 6693550928 | Çift ray kaybında pasif 10 kΩ boşaltma 238.779 µs **FAIL**; OUT−IN 10.997 V | AÇIK | R12 (LM74502H aktif deşarj, tipik), R16 (D_REV; SİM 0.133 V) | PR2-REVIEW-6693550928.md |
| 6694409747 | TLV1701 yalnız tipik gecikme; LTC6752 ortak mod; LTC7001 bootstrap; pin tablosu | Karşılaştırıcı zinciri garanti edilemez | R04/R05/R25: TLV3601 maks + kaba OV yolu | PR2-REVIEW-6694409747.md |

Korunan G1 FAIL'leri (silinmedi): baseline O1 16.89 V; Family 2 O1 18.8039 V; Family 4 bara 10.7109 V; U3/U4 IN 40.709 V; ILIM 7.4877 A; WP1 4 ESL eksik + N-01; WP2 69 FAIL / 6 eksik.
