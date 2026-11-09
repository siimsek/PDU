# T-052 — İzole U5/U6 VCAP ve kapı yükü deneyi

**Durum: Review. Ana deck, F5 kanıtı, şema, PCB ve BOM değişmedi.** Etiket SİM; TI modeli veya fiziksel kanıt değildir. Şarj pompası sabit akımlı kaynak, 75 µs veri sayfası gecikmesi sonradan eklendi. Kapı yükü Cg = Qg_maks / Vdur eşdeğer kapasitesidir. Sonuç [results.json](results.json), deck'ler `U*.cir`.

Girdiler: LM74700-Q1 SNOSD17G s.7 ve s.13; LM74502H SNOSDE5A s.5–6 ve s.11; Qg maks Q1 25 nC (Infineon Rev. 2.4 s.3), Q2 48 nC (SLPS406B, params.py). Akım 162/300/600 µA veri sayfasında VCAP farkı 7 V koşulundadır.

| Ref | Durum | I µA | C nF | UVLOR V | exit | El t ms | SİM t ms | Hata % | El ΔV V | SİM ΔV V |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| U5 | hızlı | 600 | 90,0 | 5,8 | 0 | 0,945 | 0,945 | 0,0 | 0,2778 | 0,2717 |
| U5 | tipik | 300 | 100,0 | 6,6 | 0 | 2,275 | 2,275 | 0,001 | 0,25 | 0,2447 |
| U5 | yavaş | 162 | 110,0 | 7,7 | 0 | 5,3034 | 5,3035 | 0,002 | 0,2273 | 0,2222 |
| U6 | hızlı | 600 | 90,0 | 5,7 | 0 | 0,93 | 0,93 | 0,0 | 0,5333 | 0,5111 |
| U6 | tipik | 300 | 100,0 | 6,5 | 0 | 2,2417 | 2,2417 | 0,001 | 0,48 | 0,4616 |
| U6 | yavaş | 162 | 110,0 | 7,5 | 0 | 5,1676 | 5,1677 | 0,002 | 0,4364 | 0,4205 |

Fark: SİM kapasiteye yük paylaşımıyla düşüm verir, el hesabı `Qg/C` yaklaşıklığıdır. Tipik ve sınır satırları ayrıdır; uç akımlar garanti zaman değildir.

AÇIK: X7R DC-bias, VCAP'e bağlı akımın 7 V dışı değeri, gerçek kapı eğrisi, pompanın kapı şarjı sırasındaki katkısı, F5 ile etkileşim. Tezgâh gerekir.
