# T-040 — LM70880 BIAS kayıp ve seçenek analizi

**Durum: Review. Şema, PCB ve değer değişmedi.** Karar THINKER'ındır. Sayılar [results.json](results.json), üreten betik [calc_bias.py](calc_bias.py).

Kaynak: TI LM70880-Q1 SNVSBX7A (JUNE 2024) https://www.ti.com/lit/ds/symlink/lm70880-q1.pdf.

## Veri sayfası

- s.12: "12V fixed output or an adjustable output" için VCC **8 V**; BIAS VOUT'a veya 10–30 V kaynağa bağlanabilir.
- s.13: BIAS kullanılmıyorsa AGND'ye; BIAS > 9,1 V (tipik) iken VCC regülatör girişi VIN'den BIAS'a geçer. BIAS 32 V'u aşamaz (s.13, s.5). Harici kaynakta VIN her koşulda BIAS'tan büyük olmalı.
- s.3/CBOOT: VCC = 8 V seçilirse bootstrap'a 1 Ω seri direnç. BOM: RBOOT1 1, CBOOT1 47n, CVCC1 4.7u.

## Bulgu: `power.py` VCC değeri

`analysis/g2/power.py:173` kaybı `(VIN − 5 V) × 10 mA` ile alır. Ayarlı çıkışta veri sayfası VCC'yi 8 V verir. Kod kaybı fazla hesaplıyor; yönü güvenli tarafta, değer yanlış. 10 mA IVCC kaynaklı değildir, **VARSAYIM**. Gerçek IVCC (kapı yükü × fsw dahil) veri sayfası tablosundan okunamadı, **AÇIK**.

## Karşılaştırma (HESAP, IVCC varsayımlarıyla)

P = (VBesleme − VCC) × IVCC. BIAS=VOUT için VOUT = 11.0 V VARSAYIM. ΔTj = P × RθJA (s.6 değerleri; tasarım kullanımı için s.6 uyarısı geçerli).

| VIN | IVCC mA | AGND, VCC 8 V (W) | Kod 5 V (W) | BIAS=VOUT (W) | Kazanç (W) | ΔTj EVM (°C) | ΔTj JEDEC (°C) |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 20,0 | 5 | 0,060 | 0,075 | 0,015 | 0,045 | 0,84 | 1,51 |
| 20,0 | 10 | 0,120 | 0,150 | 0,030 | 0,090 | 1,67 | 3,01 |
| 20,0 | 20 | 0,240 | 0,300 | 0,060 | 0,180 | 3,35 | 6,03 |
| 22,2 | 5 | 0,071 | 0,086 | 0,015 | 0,056 | 1,04 | 1,88 |
| 22,2 | 10 | 0,142 | 0,172 | 0,030 | 0,112 | 2,08 | 3,75 |
| 22,2 | 20 | 0,284 | 0,344 | 0,060 | 0,224 | 4,17 | 7,50 |
| 26,0 | 5 | 0,090 | 0,105 | 0,015 | 0,075 | 1,40 | 2,51 |
| 26,0 | 10 | 0,180 | 0,210 | 0,030 | 0,150 | 2,79 | 5,02 |
| 26,0 | 20 | 0,360 | 0,420 | 0,060 | 0,300 | 5,58 | 10,05 |

Kayıplar akım varsayımına bağlıdır, ölçüm veya garanti değildir.

## Seçenekler

| Seçenek | Kalkış | Sınır | Durum |
|---|---|---|---|
| A: BIAS=AGND (mevcut) | VCC VIN'den, s.13'e uygun | BIAS mutlak riski yok | Geçerli; kayıp hesabı düzeltilmeli |
| B: BIAS=VOUT | Çıkış yükselene kadar VIN'den; BIAS>9,1 V geçişi | VOUT hatada BIAS'ı da yükseltir. SİM VRAW tepe: F1 34.76 V (f1_worst), F5 29.13 V (f5_vt11.487_td1048ns_cmin_r20m_l1.2; 47/49, iki köşe T-038'de). F1 değeri 32 V mutlak sınırı aşıyor | **Mevcut hata senaryosunda sığmıyor**, kelepçe gerektirir; AÇIK |
| C: Harici 10–30 V | Kartta uygun kaynak yok | VIN > BIAS her koşulda | AÇIK |

Isı sonucu: kazanç ΔTj tabloda; karar için gerçek IVCC ve kart RθJA gerekir. Tasarım değişikliği gerekirse ayrı THINKER kararı. SİM fiziksel kanıt değildir; tezgâh: VCC gerilimi, U1/U2 sıcaklığı.
