# T-041 — U5/U6 VCAP ve kapı kalkış kapsamı

**Durum: Review. Şema, PCB ve model değişmedi.** Sayılar [results.json](results.json), üreten betik [calc_vcap.py](calc_vcap.py). Tipik değer garanti sayılmadı; tablo tipik ve uç değerleri ayrı verir.

## Girdiler

- U5: CVCAP 100 nF, C1608X7R1H104K080AA, VCAP–ANODE. U6: C_ISO_VCAP 100 nF, aynı MPN, VCAP–VS (BOM). Tolerans ±%10 (K); X7R DC-bias eğrisi okunmadı, **AÇIK**.
- Şarj pompası kaynak akımı 162 / 300 / 600 µA, VCAP farkı 7 V'ta (LM74700-Q1 SNOSD17G s.7, LM74502H SNOSDE5A s.5).
- Her iki belge C(VCAP) = 0,1 µF koşulunda karakterize eder (s.6–7, s.5–6). Veri sayfasında ayrı minimum C değeri okunmadı, **AÇIK**.
- Mutlak sınır: GATE ve VCAP pin farkı 15 V (s.5, s.4).

## Kapı sürücü etkinleşme gecikmesi

Formül: `T = 75 µs + C × V(VCAP_UVLOR) / 300 µA`, belgede tipik akımla verilir. Uç sütunlar aynı formüle sınır akım ve tolerans koyan HESAP'tır, üretici garantisi değildir.

| Ref | Kaynak | UVLO min/tip/maks V | Hızlı (ms) | Tipik (ms) | Yavaş (ms) |
|---|---|---:|---:|---:|---:|
| U5 (LM74700-Q1) | SNOSD17G, s,13 Eş,1 | 5,8 / 6,6 / 7,7 | 0,945 | 2,275 | 5,303 |
| U6 (LM74502H) | SNOSDE5A, s,11 Eş,1 | 5,7 / 6,5 / 7,5 | 0,930 | 2,242 | 5,168 |

## Kapı yükü ve VCAP düşümü (HESAP, ΔV = Qg / C)

| Ref | FET | Kaynak | Qg tip/maks nC | ΔV tipik (V) | ΔV maks, Cmin (V) |
|---|---|---|---:|---:|---:|
| U5 | Q1 BSC160N10NS3 G | Infineon Rev, 2,4 s,3 | 19 / 25 | 0,190 | 0,278 |
| U6 | Q2 CSD19531Q5A | SLPS406B s,1 tipik, params,py s,3 maks | 37 / 48 | 0,370 | 0,533 |

VCC–UVLO histerezisi ve pompanın gate şarjı sırasındaki katkısı dahil değil. UVLO düşüşüne yakınlık için ayrıntılı dinamik **AÇIK**.

## Model kapsamı

`design/pdu_v2.cir` içinde U5 ayrı eleman değil, `BQ1` ideal diyot (Q1 gate düğümü yok). U6 için `BCTL/CCTL/RCTL` yalnız `TDLY` gecikmeli kontrol üretir. VCAP düğümü, UVLO gecikmesi, EN/UVLO girişi, SRC/VS ve Qg yükü yoktur. Bu yüzden F aileleri giriş kalkışında kapı gecikmesini temsil etmez.

PCB: `/VCAP` yolu 28,76 mm (PR #70, birleşmemiş). Sayısal ihlal değil; gürültü ve etkisi **doğrulanamadı**.

Öneri (THINKER kararı): gerekirse VCAP/gate alt devre kartı. Tezgâh: VCAP şarj süresi, Q1/Q2 VGS rampası.
