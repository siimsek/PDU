# D-009 — PCB yönlendirme aracı kararı

- **Kart:** tasks/D-009.md
- **Yazan:** Codex (THINKER), 2026-11-08
- **Fiziksel iş gerekli mi:** Hayır
- **Durum:** Review (`tasks/D-009.md` zaten Review)

## Soru
G5 yönlendirme ve zone işleri için hangi araç KiCad 10.0.7 tasarımını tekrarlanabilir ve denetlenebilir biçimde değiştirmeli? Kriterler: repo iş akışına entegrasyon, net/parite/DRC kanıtı, geri alınabilirlik ve GUI kaydına bağımlı olmamak.

## Seçenekler
| Seçenek | Temel değerler (etiketli) | Kriteri sağlıyor mu | Risk | Kanıt |
|---|---|---|---|---|
| **A — KiCad 10.0.7 bundled Python `pcbnew` API betikleri** | Repo'daki `scripts/pcb_setup.py` zaten `pcbnew` kullanıyor. Yerel KiCad 10.0.7 testinde `PDU.kicad_pcb` yüklendi; `PCB_TRACK` ve `ZONE` nesneleri oluşturulup bellekte board'a eklendi (track 0→1, zone 4→5). | **Evet; önerilen.** Gerçek KiCad kurulumunda API importu, board yükleme ve track/zone ekleme çalıştı. CLI parity gate aynı 10.0.7 kurulumunda 0 parity verdi. | Smoke testi bağlı track geometrisini, net atamasını veya zone refill sonucunu kanıtlamaz; bunlar T-020…T-024 kabul kriterlerinde gerçek aday board üzerinde CLI DRC/refill ile doğrulanmalı. API yalnız KiCad'in bundled Python ortamında kullanılabilir. | Yerel komut çıktısı ve `reports/R-014/verification-summary.json`; repo `scripts/pcb_setup.py`, `scripts/pcb_drc.py`. |
| **B — Konnect + açık KiCad GUI** | Bu repoda doğrulanmış Konnect KiCad 10.0.7 routing/DRC akışı yok. | Ana düzenleme yolu olarak kanıtlanmadı; seçilmedi. | GUI oturumuna bağımlılık, kaydetme/provenans riski ve tekrarlanabilir CLI kanıtı eksik. | Bu doğrulama sırasında Konnect routing entegrasyonu denenmedi; davranışı **doğrulanamadı**. |
| **C — Harici autorouter / DSN aktarımı** | Repoda bu tasarıma ait sınanmış export/import yolu yok. | Seçilmedi. | KiCad'e dönüşte track/net/zone ve parity farkı riski; ek araca bağımlılık. | Bu repo ve yerel denemede entegrasyon **doğrulanamadı**. |

## Öneri
**A'yı seç: KiCad 10.0.7 bundled Python `pcbnew` API'siyle sürümlenmiş betikler.** Bu kurulumda API board, track ve zone nesneleri üzerinde çalıştı; aynı sürüm CLI'si ERC, netlist ve PCB-schematic parity kontrolünü üretti. T-020…T-024 bu sürümü sabitlemeli, sessiz araç değişimini yasaklamalı ve her rota/zone kilometre taşında gerçek aday board'u CLI DRC/refill ile doğrulamalı.

## Kanıt
- Yerel `kicad-cli version`: **10.0.7**.
- Yerel komut: KiCad'in bundled `python.exe` ile `import pcbnew as p`; `p.GetBuildVersion()` **10.0.7** verdi. `p.LoadBoard('PDU.kicad_pcb')` başarılı oldu.
- In-memory API denemesi: `PCB_TRACK(board)` oluşturulup `board.Add(track)` yapıldı; track sayısı 0'dan 1'e çıktı. `ZONE(board)` oluşturulup `board.Add(zone)` yapıldı; zone sayısı 4'ten 5'e çıktı. **Board kaydedilmedi** (`saved: false`).
- Aynı KiCad CLI ile taze ERC: 0 ihlal; taze netlist R-002 karşılaştırıcısında 180 referans, 422 pin anahtarı, 0 fark; `pcb drc --schematic-parity`: parity 0. Ayrıntı: `reports/R-014/verification-summary.json`, ham çıktılar `reports/R-014/`.
- Repo akışı: `scripts/pcb_setup.py` bundled Python `pcbnew` ile PCB kuruyor; `scripts/pcb_rules.py` API'nin sağlamadığı stackup metaverisini dar S-expression adımıyla yazıyor; `scripts/pcb_drc.py` CLI DRC/parity gate'ini çalıştırıyor.
- `HANDOFF.md`: KiCad GUI açıksa PCB GUI'den kaydedilmez.

## T-020…T-024 uygulama kuralı
1. KiCad CLI ve bundled Python sürümünün ikisi de 10.0.7 değilse dur; `Blocked` gerekçesini raporla. Başka araca sessizce geçme.
2. Her kilometre taşı öncesi temiz git checkpoint'i al. Script, board'u deterministik üretmeli/düzenlemeli; aday sonucu CLI ile incelemeden GUI'den kaydetme.
3. Rota/zone aşamasında `pcb drc --schematic-parity` çalıştır; parity 0 ve kabul kriterinde izin verilenler dışındaki error 0 olmalı. Zone refill ve iz bağlantısı gerçek aday board'da sınanmalı. `reports/<T-kartı>/` altında özet ve gerekli ham kanıtı bırak.
4. CLI gate başarısızsa değişikliği kabul etme; git checkpoint'ine dön ve bulguyu raporla.
5. GUI yalnız görüntü/inceleme içindir; kaydedilen değişikliklerin kaynağı sürümlenmiş betiklerdir.

## Açık varsayımlar
- **VARSAYIM:** In-memory track/zone API nesneleri üretmek ve board'a eklemek, gerçek net bağlantılı rota ve doldurulmuş zone için yeterli API yüzeyinin varlığına işaret eder; gerçek bağlantı, refill ve clearance davranışı T-020…T-024'ün aday-board gate'lerinde doğrulanacaktır.
- **VARSAYIM:** KiCad 10.0.7 bundled Python kurulumu BUILDER ortamında da bulunacak; her kart başında sürüm/import testi yapılacaktır.

## Doğrulanamayanlar
- Konnect'in KiCad 10.0.7 routing/DRC entegrasyonu — yerel denemede kullanılmadı; repo içinde doğrulanmış akış bulunamadı.
- Harici autorouter/DSN round-trip — yerel denemede kullanılmadı; bu repo için uyumluluk kanıtı bulunamadı.
