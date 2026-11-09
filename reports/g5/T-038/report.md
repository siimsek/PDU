# T-038 — F5 eksik iki köşe

**Sonuç: AÇIK. İki köşe tam pencereyle tamamlanmadı; PASS yazılmadı.** Eski FAIL/AÇIK kayıtlar silinmedi. `design/pdu_v2.cir`, `analysis/g2/sim_runner.py`, şema, PCB ve BOM değişmedi.

## Köşeler ve eski koşu

`reports/g2/sim/f5/f5_vt11.487_td300ns_ctyp_r200m_l0.8` ve `f5_vt11.765_td300ns_ctyp_r200m_l0.8`. Parametre: VTRIP_EFF 11,4868 / 11,7650 V, TDLY 300 ns, COUT tipik (0,000659904 F), RSRC 0,2 Ω, LPH 5,44 µH, `.tran 2e-08 0.0003 0 2e-08`, fault 100 µs. Eski kayıt `reports/g2/sim-results.json`: çıkış -9 (900 s zaman aşımı), 0 ölçüm. Netlist SHA-256 öneki f6351423677407fb.

## Yeniden koşu

ngspice-47, aynı deck, ayrı klasör, her biri ayrı, 21600 s limit. 2026-11-09 12:19:31 ve 12:19:33 UTC'de başladı. Bu rapor yazılırken ikisi hâlâ çalışıyor, çıkış kodu yok, ölçüm yok: yaklaşık 2,6 saatte 9348 s CPU. Komşu köşeler (`reports/g2/sim/f5/*_ctyp_r20m_*`, `*_r200m_l1.2`) 0,6–0,8 s'de biter. Bu koşular tamamlanmayacak gibi görünüyor; bitene kadar sonuç iddia edilmedi.

## Teşhis

Aynı deck 75 s ham veriye yazdırıldı: [stall-evidence.json](stall-evidence.json). Simülasyon 2.141142112e-04 s'de duruyor; son 3000 noktada adım 8.13e-20–2.56e-17 s. Bu noktada Q=1 ve kontrol düğümü ~0, yani ayırıcı açılmış. `ens` 0,500000 V, `ven` 1,0015 V.

Neden (HESAP/gözlem): faz 1 kısa devresinde VIN yaklaşık 18,43 V'a düşüyor; `ven` VEN_R = 1,0 V eşiğinin üzerinde kalıyor, `BENS` düğümü `V(ens)>0.5` keskin eşiğine ulaştırıyor. Bu eşik `BSS`, `BSW1`, `BSW2` ifadelerinde histerezissizdir; faz 2 durum değiştirince VIN ve ven de değişir ve çözücü sonsuz küçük adımlarda sıkışır. Bu ortalama modelin sayısal kusurudur.

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
