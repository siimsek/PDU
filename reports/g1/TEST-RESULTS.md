# G1 test kaydı

| Tarih | Komut | Sonuç | Kapsam |
|---|---|---|---|
| 2026-11-06 | `python -m pytest -q` | **exit 0; 7 passed** | G1 analiz testleri (`analysis/test_pdu_calc.py`) |
| 2026-11-06 | `python analysis\run_g1_simulations.py family1_ovp` | **exit 0; 1 family completed, model criterion PASS** | TDELAY kullanımını düzelten Family 1 tekrar koşusu; 11.9741 V ideal model, 12.0 V marjı 25.9 mV. High-side-short adayı veya fiziksel kabul değildir. Önceki deck/log saklandı. |
| 2026-11-06 | `python analysis\run_g1_simulations.py --metadata-only` | **exit 0; 0 ngspice runs** | Beş ailenin kapsam ve PASS/FAIL yorum metaverisi eşitlendi; ölçüm değerleri değiştirilmedi. |
| 2026-11-06 | `python analysis\verify_pr2_review.py` | **exit 0; 8/8 checks passed** | Review bulguları için kaydedilmiş deck/log ve rapor kapsam kontrolü; SPICE koşusu veya elektriksel PASS değildir. |
| 2026-11-06 | `python -m pytest -q` | **exit 0; 10 passed** | Güncel tam suite: 7 hesap + 3 PR #2 kanıt kapsamı testi. |

Testler ripple/tepe akımı iki-yol hesabını, FB/UVLO köşelerini, çift-yol farklarını, koruma açıklarını, güncel 2L/4L yönlendirme zarfını ve PR #2 yorumundaki kanıt kapsamı/FAIL korumasını denetler. İki-yol sayısal fark testi aynı modeldeki hesap çapraz kontrolüdür; bağımsız fiziksel model geçerliliği raporda sıfırdır. Test geçişi elektriksel veya fiziksel donanım kabulü değildir.

| 2026-11-06 | `python analysis/ovp_component_analysis.py` | **exit 0** | MPN-köşe, Ceff ekranı ve datasheet koşullu gecikme hesap JSON/Markdown çıktıları üretildi. Ceff kapalı-formu aynı eşitsizliğin sayısal bisection'ı ile çapraz kontrol edildi; fiziksel kanıt değildir. |
| 2026-11-06 | `python analysis/run_ovp_component_checks.py` | **exit 0; 3/3 targeted SPICE cases completed** | Family 1 seri akım kapanma ölçümü ve Family 2 high-side-short + aday OVP, 10 µF/7 A ile 4 µF/yüksüz köşeleri. Family 2/4 tarihsel FAIL sonuçları korunuyor; tüm OVP koşuları behavioral modeldir. |
| 2026-11-06 | `python -m pytest -q` | **exit 0; 14 passed** | 7 hesap + 3 PR #2 evidence scope + 4 OVP component/timing/case evidence testleri. Bu sonuç elektriksel veya fiziksel kabul değildir. |
| 2026-11-06 | `PDU_NGSPICE=F:\Spice64\bin\ngspice_con.exe python analysis/shared_bus_fault.py` | **exit 0; 4/4 cases completed** | Eski ortak-bara overload süresi, ortak ayırıcı steady/startup hassasiyetleri ve TPS1686x alternatifi; sayısal sonuçlar `shared-bus-ovp-results.json` ve sim loglarında. Behavioral model; fiziksel kabul değildir. |
| 2026-11-06 | `python -m pytest -q analysis/test_shared_bus_fault.py` | **exit 0; 8 passed** | Ortak bara hesapları, yük ayrımı, input split topology ve eşik-feasibility kontrolü. Elektriksel kabul değildir. |
| 2026-11-06 | `python -m pytest -q` | **exit 0; 22 passed** | Güncel tam suite: 14 önceki + 8 ortak-bara kontrolleri. Elektriksel veya fiziksel kabul değildir. |
