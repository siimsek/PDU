# T-051 — İzole dVdt alt devresi ve T-039 karşılaştırması

**Durum: Review. Ana deck, F5 kanıtı, şema, PCB ve BOM değişmedi.** Etiket SİM; bu üretici modeli değildir ve fiziksel kanıt değildir. Devre: `IdVdt` akımı CdVdt'yi doldurur, çıkış V(dvdt)'yi akım sınırıyla izler. Girdi değerleri T-039 ve TI SLVSEI3D s.10, s.22 Eş.3'tür. Sonuç [results.json](results.json), deck'ler `run*.cir`.

| Durum | CL µF | ILIM A | exit | El SR V/ms | SİM SR V/ms | Hata % | El akım A | SİM tepe A |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| hızlı | 4 | 8,13 | 0 | 6,6632 | 6,6632 | 0,0 | 0,0267 | 0,0267 |
| hızlı | 10 | 8,13 | 0 | 6,6632 | 6,6632 | 0,0 | 0,0666 | 0,0666 |
| hızlı | 100 | 8,13 | 0 | 6,6632 | 6,6632 | 0,0 | 0,6663 | 0,6663 |
| hızlı | 470 | 8,13 | 0 | 6,6632 | 6,6607 | -0,037 | 3,1317 | 3,1317 |
| tipik | 4 | 8,13 | 0 | 4,6 | 4,6 | -0,0 | 0,0184 | 0,0184 |
| tipik | 10 | 8,13 | 0 | 4,6 | 4,6 | -0,0 | 0,046 | 0,046 |
| tipik | 100 | 8,13 | 0 | 4,6 | 4,6 | -0,0 | 0,46 | 0,46 |
| tipik | 470 | 8,13 | 0 | 4,6 | 4,5998 | -0,005 | 2,162 | 2,162 |
| yavaş | 4 | 8,13 | 0 | 1,9048 | 1,9048 | -0,0 | 0,0076 | 0,0076 |
| yavaş | 10 | 8,13 | 0 | 1,9048 | 1,9048 | -0,0 | 0,019 | 0,0191 |
| yavaş | 100 | 8,13 | 0 | 1,9048 | 1,9048 | -0,0 | 0,1905 | 0,1905 |
| yavaş | 470 | 8,13 | 0 | 1,9048 | 1,9048 | -0,0 | 0,8952 | 0,8952 |
| hızlı | 1000 | 4,36 | 0 | 6,6632 | 4,36 | -34,566 | 6,6632 | 4,36 |

Son satırda el hesabı ILIM'i yok sayar; SİM akımı ILIM'e kilitler ve SR düşer. Diğer satırlarda fark yalnız izleme kazancı ve sayısal adımdan gelir.

AÇIK: CEFOUT Ceff, dış yük, IdVdt sıcaklık değişimi, TI iç rampa gerçek davranışı, kalkış ısısı. F5 sonuçları bu modelle doğrulanmış sayılmaz.
