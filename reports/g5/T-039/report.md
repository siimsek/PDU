# T-039 — TPS25982 dVdt ve kalkış hesabı

**Durum: Review. Şema, PCB, BOM ve model değişmedi.** Etiketler: DATASHEET / HESAP / VARSAYIM / AÇIK. Sonuç fiziksel kanıt değildir; ham sayı [results.json](results.json), üreten betik [calc_dvdt.py](calc_dvdt.py).

Kaynak: TI TPS25982 SLVSEI3D Rev. D (MAY 2026) https://www.ti.com/lit/ds/symlink/tps25982.pdf. Formül s.22 Eş. 3: `CdVdt[pF] = 4600 / SR[V/ms]`; s.22 Eş. 2: `SR[V/ms] = IINRUSH[mA] / COUT[µF]`. IdVdt 2 / 4,6 / 6,33 µA (s.10). dVdt kapasitörü kalkışta tipik VIN+4 V görür (s.37).

## Girdiler

- CDVDT1, CDVDT2: 1,0 nF, C1608C0G1H102J080AA (C0G, ±%5, BOM). C0G'de DC-bias ihmal edildi, VARSAYIM.
- Rampa yüksekliği: kararlı bara üst sınırı 11.1605 V.
- Çıkış kapasitesi: CEFOUT1/2 nominal 10 µF X7R 1206 25 V (BOM), Ceff **bilinmiyor**. Port dışı yük kapasitesi **AÇIK**. Deck `CPORT` 4 µF VARSAYIM.

## Sonuç

SR için HESAP `IdVdt/CdVdt`; Eş. 3 ile tipikte aynı (1 nF → 4,6 V/ms).

| Durum | SR (V/ms) | Rampa (ms) | Yük | Kalkış akımı (mA) | CV²/2 (mJ) |
|---|---:|---:|---|---:|---:|
| en hızlı (Imax, C-%5) | 6,663 | 1,675 | 4 µF (deck CPORT, VARSAYIM) | 26,7 | 0,249 |
| en hızlı (Imax, C-%5) | 6,663 | 1,675 | 10 µF (CEFOUT nominal; Ceff bilinmiyor) | 66,6 | 0,623 |
| en hızlı (Imax, C-%5) | 6,663 | 1,675 | 100 µF (örnek) | 666,3 | 6,228 |
| en hızlı (Imax, C-%5) | 6,663 | 1,675 | 470 µF (örnek) | 3131,7 | 29,271 |
| tipik | 4,600 | 2,426 | 4 µF (deck CPORT, VARSAYIM) | 18,4 | 0,249 |
| tipik | 4,600 | 2,426 | 10 µF (CEFOUT nominal; Ceff bilinmiyor) | 46,0 | 0,623 |
| tipik | 4,600 | 2,426 | 100 µF (örnek) | 460,0 | 6,228 |
| tipik | 4,600 | 2,426 | 470 µF (örnek) | 2162,0 | 29,271 |
| en yavaş (Imin, C+%5) | 1,905 | 5,859 | 4 µF (deck CPORT, VARSAYIM) | 7,6 | 0,249 |
| en yavaş (Imin, C+%5) | 1,905 | 5,859 | 10 µF (CEFOUT nominal; Ceff bilinmiyor) | 19,0 | 0,623 |
| en yavaş (Imin, C+%5) | 1,905 | 5,859 | 100 µF (örnek) | 190,5 | 6,228 |
| en yavaş (Imin, C+%5) | 1,905 | 5,859 | 470 µF (örnek) | 895,2 | 29,271 |

Hesap, IdVdt'in sabit olduğunu ve SR'nin yalnız CdVdt ile belirlendiğini varsayar. Fiziksel rampa FET sınırlarına ve yüke bağlıdır, **doğrulanamadı**.

- En hızlı SR'de kalkış akımının garanti ILIM alt sınırına ulaştığı C: O1 1085.1 µF, S2E 654.3 µF (HESAP). Dış yük kapasitesi bilinmeden kullanılamaz, AÇIK.
- CdVdt gerilimi: 11.1605+4 = 15.161 V, 50 V C0G içinde.
- U3/U4 IN < 30 V ve O1 ≤ 12,0 V kriteri bu hesapla kontrol edilmez: rampa kalkış davranışıdır, hata tepesi T-038/F aileleridir.
- Isı: FET'teki kalkış enerjisi CV²/2 ile mertebedir, güvenli çalışma alanı ve TJ **AÇIK**.
- `/DVDT_S2E` iz uzunluğu 70,1 mm (PR #70, birleşmemiş): 10 pF ek kapasite %1 etkidir (HESAP); gerçek pF ve kuplaj **doğrulanamadı**.

## Model kapsamı

`design/pdu_v2.cir` içinde dVdt ifadesi 0 kez geçiyor. `BEF1/BEF2` yalnız etkinleştirme, akım sınırı ve Ron içerir, çıkış rampası yoktur. Bu yüzden F aileleri CDVDT kalkışını temsil etmez.

Öneri (THINKER kararı): dış yük kapasitesi belirlenince ayrı dVdt alt devre kartı. Tezgâh: kalkışta VOUT eğimi ve giriş akımı ölçümü.
