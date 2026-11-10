# IDA PDU

6S LiPo kaynağından ortak 11 V güç barası üretip T3 Gemstone O1 ve SLAMTEC RPLIDAR S2E'yi ayrı korumalı çıkışlardan beslemek için geliştirilen iki fazlı güç dağıtım kartı.

**Durum (G4, 2026-11-07):** devre tasarımı hesap + SPICE + parça seviyesinde kapandı; **fiziksel ölçüm yok, üretime hazır değil.** KiCad şema/PCB dosyaları hâlâ G1 öncesi tasarımı gösterir; G2–G4 değişiklikleri [`reports/g2/KICAD-CHANGE-LIST-FINAL.md`](reports/g2/KICAD-CHANGE-LIST-FINAL.md) ile KiCad fazında işlenecek.

## Buradan devam et

1. [START HERE](docs/START-HERE.md) — hedef, mimari, doğruluk kaynakları, komutlar (1 sayfa)
2. [Ajan kuralları](AGENTS.md)
3. [PCB-HAZIR kapısı v2](reports/g4/PCB-READY-v2.md) ve [kullanıcı kararları](reports/g4/USER-DECISIONS.md)

## Doğrulama

```bash
python -m pytest -q
python analysis/run_all.py
```

Son koşu özeti: [`reports/g2/VERIFY.md`](reports/g2/VERIFY.md); SPICE sonuçları: [`reports/g2/SIM-RESULTS.md`](reports/g2/SIM-RESULTS.md) (davranışsal ortalama model, fiziksel kanıt değil).

## Mevcut KiCad dosyaları (G1 öncesi tasarım)

[KiCad 10 projesi](PDU.kicad_pro), [şema](PDU.kicad_sch), [PCB](PDU.kicad_pcb), [projeye özel kütüphane](hardware/lib). Bu dosyalardaki eski değerler (ör. TPS259824O, RFB2 10.2k, 8× COUT) bilinçli olarak değiştirilmedi. Eski durum belgeleri (`docs/PROJECT-STATE.md`, `docs/design.md`, `hardware/*.md`) SUPERSEDED başlığıyla geçmiş kaydıdır.

## KiCad düzenleme kuralı

KiCad şema/PCB dosyaları yalnız `scripts/kicad_sexpr.py` (kayıpsız S-ifade; dokunulmayan metin baytça korunur) ile ve her bloktan sonra kicad-cli ERC + netlist tutarlılığıyla düzenlenir. Eski "yalnız Konnect MCP" kuralı, MCP sunucusu ve açık KiCad GUI gerektirdiği için kaldırıldı (gerekçe ve yuvarlak-gezi kanıtı: [`reports/g5/TOOLING.md`](reports/g5/TOOLING.md)). Kilit dosyaları silinmez.

Kaynak depo: [siimsek/PDU](https://github.com/siimsek/PDU).
