# T-038 — F5 eksik iki köşe

**Sonuç: AÇIK. İki köşe tam pencereyle tamamlanmadı; PASS yazılmadı.** Eski FAIL/AÇIK kayıtlar silinmedi. `design/pdu_v2.cir`, `analysis/g2/sim_runner.py`, şema, PCB ve BOM değişmedi.

## Köşeler ve eski koşu

`reports/g2/sim/f5/f5_vt11.487_td300ns_ctyp_r200m_l0.8` ve `f5_vt11.765_td300ns_ctyp_r200m_l0.8`. Parametre: VTRIP_EFF 11,4868 / 11,7650 V, TDLY 300 ns, COUT tipik (0,000659904 F), RSRC 0,2 Ω, LPH 5,44 µH, `.tran 2e-08 0.0003 0 2e-08`, fault 100 µs. Eski kayıt `reports/g2/sim-results.json`: çıkış -9 (900 s zaman aşımı), 0 ölçüm. Netlist SHA-256 öneki f6351423677407fb.

## Yeniden koşu

ngspice-47, aynı deck, ayrı klasör, her biri ayrı, 21600 s limit. 2026-11-09 12:19:31 ve 12:19:33 UTC'de başladı. Bu rapor yazılırken ikisi hâlâ çalışıyor, çıkış kodu yok, ölçüm yok: yaklaşık 2,6 saatte 9348 s CPU. Komşu köşeler (`reports/g2/sim/f5/*_ctyp_r20m_*`, `*_r200m_l1.2`) 0,6–0,8 s'de biter. Sonuç iddia edilmedi.

## Teşhis

Her köşe ayrı koşuldu ve kimlikli kaydedildi: `stall/<köşe>.stall.json` (deck ve netlist SHA-256, komut, süre, çıkış, ham dosya SHA-256), `stall/<köşe>.wave.csv` (1 µs seyreltilmiş dalga + son 300 nokta), [run_stall.py](run_stall.py). Ham dosya boyutu nedeniyle saklanmadı; SHA'sı kayıtlı. Simülatör: ngspice-47 : Circuit level simulation program. Her koşu 75 s sonra kesildi, tam pencere değildir.

| Köşe | Deck SHA | Çıkış | Nokta | t_son s | Son 3000 nokta adımı s | ens>0,5 geçişi | ens aralığı V |
|---|---|---|---:|---:|---|---:|---|
| vt11.487_ | `72736f77f27cba23…` | timeout | 62976 | 2.141142112e-04 | 8.1e-20 … 2.6e-17 | 0 | 0.500000044 … 0.500000046 |
| vt11.765_ | `d959cbae4d089df7…` | timeout | 62313 | 2.141142112e-04 | 8.1e-20 … 4.1e-16 | 0 | 0.500000042 … 0.500000045 |

**OLGU (iki köşe, ayrı ayrı):** Fault 100 µs'de başlar. Yaklaşık 113 µs'de `ens` düşer. `ven` kısa devre akımı azaldıkça yükselir ve 213,4–214,1 µs arasında 1,0 V'u yukarı geçer; `ens` aynı aralıkta 0,5 V'u yukarı geçer. Simülasyon bundan hemen sonra 214,114 µs'de ilerlemez. Kilitlenme penceresindeki kabul edilmiş noktalarda `ens>0,5`, `ven>1,0`, `ven<0,9`, `q` ve `fault1` için işaret değişimi **yoktur**.

**HİPOTEZ, kanıtlanmadı:** Yeniden etkinleşmede `V(ens)>0.5` keskin eşiği `BSS`, `BSW1`, `BSW2` ifadelerini değiştirir ve Newton iterasyonları yakınsamaz. Reddedilen adımlar ham çıktıda görünmez, bu yüzden salınım veya tek nedenli mekanizma gösterilemedi. Önceki sürümdeki "eşik sonsuz geçişe sıkışır" ifadesi kanıtsızdı ve geri alındı. T-053 bu hipotezi test eder.

## Eski koşuların denetimi

`Get-CimInstance Win32_Process` 15:36 UTC: iki `timeout.exe 21600 ... ngspice_con.exe -b -o <köşe>.log <köşe>.cir`, başlangıç 12:19:31 ve 12:19:33 UTC. Limit bu komutlardan doğrulandı; dolum zamanı yaklaşık 18:19 UTC. Çıkış kaydı henüz yok; sonuç AÇIK, simülasyon zamanları dışarıdan okunamadı.

**15:43 UTC güncellemesi (OLGU):** Uygulama iki arka plan görevini `killed` bildirdi (görev kimlikleri bxj1twmte, b692md2ps). Aynı dakikada `Win32_Process` iki `ngspice_con.exe` (PID 10296, 2336) ve bunların `timeout.exe` üstlerini hâlâ çalışır gösterdi. Çalışma klasöründe `.exit` veya `.end` dosyası yok, log dosyaları 12:19:31/33 UTC'den sonra değişmedi. Sarmalayıcı kabuk kapandığı için çıkış kodu artık kaydedilemez. Limit dolumu yine 18:19 UTC. Bu iki koşu için tam pencere, çıkış veya ölçüm kanıtı yoktur; sonuç **AÇIK** kalır.

## Tanı varyantı — resmi sonuç değil

[run_variant.py](run_variant.py) `V(ens)>0.5` karşılaştırmalarının önüne yalnız bu klasörde RC filtresi ekler. Sonuç [variant-results.json](variant-results.json).

| Köşe | τ µs | Çıkış | s | Ölçüm | o1 maks V | vsafe maks V | vraw maks V |
|---|---:|---:|---:|---:|---:|---:|---:|
| vt11.487_ | 0.2 | 0 | 0.7 | 12/12 | 10,924 | 10,925 | 21,107 |
| vt11.765_ | 0.2 | 0 | 0.7 | 12/12 | 10,924 | 10,925 | 21,107 |
| vt11.487_ | 1 | 0 | 0.75 | 12/12 | 10,924 | 10,925 | 21,107 |
| vt11.765_ | 1 | 0 | 0.71 | 12/12 | 10,924 | 10,925 | 21,107 |
| vt11.487_ | 5 | -9 | 600.01 | 0/12 | — | — | — |
| vt11.765_ | 5 | -9 | 600.02 | 0/12 | — | — | — |

0,2 ve 1 µs'de iki köşe tamamlanır, iki VTRIP aynı değerleri verir ve kriterler (o1 ≤12, vsafe <30, vraw <60) sağlanır. 5 µs'de zaman aşımı sürer. Yani yakınsama filtre değerine bağlıdır ve varyant model değişikliğidir. Bu sayılar F5 sonucu olarak **kullanılmamalıdır**.

## Kapsam dışı

Ortalama model anahtarlama, gerçek EN/UVLO komparatörü, parazitik ve ısıyı içermez. UVLO civarında gerçek VIN ve buck davranışı için tezgâh gerekir.

## Karar gerektiren

`ens` eşiğine gerekçeli histerezis ekleyen ana deck değişikliği ve 76 koşunun tekrarı ayrı THINKER kararıdır. Çalışan iki koşu 21600 s limitte kendiliğinden kesilecek; o güne kadar çıkış verirse rapor güncellenir.
