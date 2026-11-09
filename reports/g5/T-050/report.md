# T-050 — LM70880 VCC 8 V düzeltmesi ve BIAS kaybı çift sayım denetimi

**Durum: Review. Şema, PCB, BOM değişmedi.** Değişen kod: `analysis/g2/power.py` (`VCC_ADJUSTABLE = 8.0`), test: `analysis/g2/test_power.py`. Sayılar [results.json](results.json). Üretilmiş `reports/g2/power-results.json` bu kartın yazma yolu dışında olduğundan yeniden üretilmedi.

Kaynak: TI LM70880-Q1 SNVSBX7A s.12 (ayarlı çıkışta VCC 8 V), s.13 (BIAS kullanılmıyorsa AGND).

## Çift sayım denetimi

`power.py` IC kaybını `p_in − p_out − dış kayıplar` olarak `ETA_ASSUMED = 0,92`'den türetir, sonra BIAS kaybını **ekler**. Veri sayfası verim eğrisi (Şekil 8-20, s.40) BIAS bağlantısını belirtmez; s.38 şeması "Tie to VOUT, External Bias, or GND" der. Bu yüzden eğri koşulu **AÇIK** ve çift sayım kanıtlanamadı. Düzeltme yapılmadı, üç olasılık aşağıda.

| Senaryo | Ek W | IC kaybı W | Tj 85 °C EVM | Tj 85 °C JEDEC | Ta maks EVM, Tj 125 °C |
|---|---:|---:|---:|---:|---:|
| A kod (5 V, eski) | 0,172 | 3,004 | 140,9 | 185,6 | 69,1 |
| B ek toplam, 8 V (yeni kod) | 0,142 | 2,974 | 140,3 | 184,6 | 69,7 |
| C eğri BIAS=VOUT ise artımlı (VIN-VOUT)×I, VOUT=11 V | 0,112 | 2,944 | 139,8 | 183,6 | 70,2 |
| D eğri BIAS=GND ise çift sayım, ek 0 | 0,000 | 2,832 | 137,7 | 179,9 | 72,3 |

- IVCC 10 mA **VARSAYIM**, gerçek değer okunamadı. RθJA değerleri s.6'dır; s.6 bunların tasarım için kullanılmamasını söyler.
- 85 °C tarama FAIL korunur (`reports/g2/USER-DECISIONS.md:17`): tabloda dört senaryonun hepsinde Tj 125 °C üzerindedir, FAIL silinmedi.
- BIAS=VOUT seçeneği için hata anında VOUT/BIAS sınırı T-040'ta AÇIK.
