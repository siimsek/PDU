# Ön-düzeltme koşusu (C3, U22 EN kapısı YOK) — kanıt arşivi

- Koşu: `run_uvlo.py -j 7`, başlangıç 2026-10-25 09:52 (Europe/Istanbul, TSİ), git HEAD b6b4b10 (çalışma ağacı kirli: yalnız izlenmeyen results/).
- `verify_uvlo.py` (o zamanki sürüm) çıkış kodu **1**: 52 durumdan 45 PASS, kabul FAIL = `dip0v-300us-mbmin-tmin`.
- `seq-ref-nodelay-typ` "reproduced" görünüyordu ama log'da `Timestep too small ... run simulation(s) aborted` var:
  bu geçerli kanıt değildi; verifier cb1df5e ile sıkılaştırıldı ve deste değiştirildi.
- Tam log seti burada tutulmadı (yalnız iki ilgili log); diğer log'ların SHA-256 değerleri `uvlo-verify.json` içinde.
- Bu dosyalar sonuç DEĞİŞTİRİLMEDEN arşivlendi; güncel sonuçlar üst klasörde.
