# G1 test kaydı

| Tarih | Komut | Sonuç | Kapsam |
|---|---|---|---|
| 2026-11-06 | `python -m pytest -q` | **exit 0; 7 passed** | G1 analiz testleri (`analysis/test_pdu_calc.py`) |

Testler ripple/tepe akımı iki-yol hesabını, FB/UVLO köşelerini, çift-yol farklarını, koruma açıklarını ve güncel 2L/4L yönlendirme zarfını denetler. Test geçişi elektriksel veya fiziksel donanım kabulü değildir.
