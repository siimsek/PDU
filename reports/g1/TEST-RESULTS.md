# G1 test kaydı

| Tarih | Komut | Sonuç | Kapsam |
|---|---|---|---|
| 2026-11-06 | `python -m pytest -q` | **exit 0; 7 passed** | G1 analiz testleri (`analysis/test_pdu_calc.py`) |
| 2026-11-06 | `python analysis\run_g1_simulations.py family1_ovp` | **exit 0; 1 family completed, model criterion PASS** | TDELAY kullanımını düzelten Family 1 tekrar koşusu; 11.9741 V ideal model, 12.0 V marjı 25.9 mV. High-side-short adayı veya fiziksel kabul değildir. Önceki deck/log saklandı. |
| 2026-11-06 | `python analysis\run_g1_simulations.py --metadata-only` | **exit 0; 0 ngspice runs** | Beş ailenin kapsam ve PASS/FAIL yorum metaverisi eşitlendi; ölçüm değerleri değiştirilmedi. |
| 2026-11-06 | `python analysis\verify_pr2_review.py` | **exit 0; 8/8 checks passed** | Review bulguları için kaydedilmiş deck/log ve rapor kapsam kontrolü; SPICE koşusu veya elektriksel PASS değildir. |
| 2026-11-06 | `python -m pytest -q` | **exit 0; 10 passed** | Güncel tam suite: 7 hesap + 3 PR #2 kanıt kapsamı testi. |

Testler ripple/tepe akımı iki-yol hesabını, FB/UVLO köşelerini, çift-yol farklarını, koruma açıklarını, güncel 2L/4L yönlendirme zarfını ve PR #2 yorumundaki kanıt kapsamı/FAIL korumasını denetler. İki-yol sayısal fark testi aynı modeldeki hesap çapraz kontrolüdür; bağımsız fiziksel model geçerliliği raporda sıfırdır. Test geçişi elektriksel veya fiziksel donanım kabulü değildir.
