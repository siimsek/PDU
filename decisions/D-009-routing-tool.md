# D-009 — PCB yönlendirme aracı

- **Kart:** tasks/D-009.md
- **Yazan:** Codex (THINKER), 2026-11-08
- **Fiziksel iş gerekli mi:** Hayır

## Soru
G5 yönlendirme ve zone işleri için hangi araç, KiCad 10.0.7 tasarımını denetlenebilir biçimde değiştirmeli? Kriterler: tekrarlanabilirlik, net/parite/DRC kanıtı, geri alınabilirlik ve repodaki mevcut iş akışıyla uyum.

## Seçenekler
| Seçenek | Temel değerler (etiketli) | Kriteri sağlıyor mu | Risk | Kanıt (belge + sayfa) |
|---|---|---|---|---|
| **A — KiCad'in paketli Python'ıyla pcbnew API betikleri** | Mevcut `scripts/pcb_setup.py` `pcbnew` kullanıyor; kullanım örneği KiCad 10.0 bundled Python'ı sabitliyor. `scripts/pcb_rules.py` API'nin stackup'a erişemediğini açıkça belirtiyor ve yalnız bu metaveri için S-expression yazıyor. `scripts/pcb_drc.py` KiCad CLI ile DRC/parite üretiyor. (REPO KANITI) | **Evet, önerilen.** Kart ve zones/tracks tek sürümlü KiCad API'siyle düzenlenebilir; kontrol aynı KiCad 10.0.7 CLI ile tekrarlanabilir. | pcbnew binding'leri yalnız KiCad'in paketli Python'ında bulunabilir; her milestone'da kopya PCB, hash, import smoke-test ve rollback gerekir. API'nin sunmadığı metaveri ayrı, dar S-expression yardımcı koduyla işlenir. | Repo: `scripts/pcb_setup.py` docstring; `scripts/pcb_rules.py` stackup notu; `scripts/pcb_drc.py` DRC gate. |
| **B — Konnect + açık KiCad GUI** | Main'de Konnect bağımlılığı, config'i veya doğrulanmış KiCad 10.0.7 akışı bulunmadı. Bu entegrasyonun davranışı bu incelemede **doğrulanamadı**. | Karar ölçütlerinde repo kanıtı yok; ana düzenleme yolu olarak seçilmedi. | GUI/plugin sürüm uyumu, değişiklik provenansı ve tekrarlanabilir DRC akışı kanıtlanmamış. | `scripts/` ve `docs/WORKFLOW.md` incelemesi; ürün davranışı için kaynak kullanılmadı. |
| **C — Başka harici autorouter / DSN aktarımı** | Main'de bu akışın üretim ve import betiği yok. | Seçilmedi; mevcut iş akışına göre ek aktarım/doğrulama adımı gerektirir. | KiCad'e dönüşte ağ/zone/track paritesi ve DRC sapması riski, bu repoda testli değil. | Main'deki T-013 script akışı; harici araç uyumluluğu **doğrulanamadı**. |

## Öneri
**A'yı seç: KiCad 10.0.7'nin bundled Python pcbnew API'si ile sürümlenmiş betikler.** Zone, track ve via değişiklikleri bu betiklerden gelsin; API'nin sağlamadığı özelliklere yalnız dar kapsamlı mevcut S-expression yaklaşımı uygulansın. Her milestone'da kopya dosyada düzenle, hash/diff al, CLI DRC/parite çalıştır. GUI açılırsa salt görüntü/inceleme için kullanılsın ve GUI'den kaydedilmesin. Üçüncü taraf AI yönlendirme bağımlılığı eklenmesin.

## Kanıt
- Repo `scripts/pcb_setup.py`: KiCad 10.0 bundled Python komutunu açıkça örnekliyor ve `import pcbnew as P` kullanıyor.
- Repo `scripts/pcb_rules.py`: board stackup binding'in Python API'de olmadığı, bu yüzden mevcut kural betiğinin S-expression kullandığı belirtilmiş.
- Repo `scripts/pcb_drc.py`: `kicad-cli` ve rapor JSON'larıyla DRC/parite denetliyor.
- `HANDOFF.md`: KiCad GUI açıksa PCB'yi kaydetmeme uyarısı.
- Proje kullanıcı talimatı: PCB'yi doğrudan KiCad API ile geliştirme tercihi.

## Açık varsayımlar
- **VARSAYIM:** KiCad 10.0.7 dağıtımındaki bundled Python'da `pcbnew` binding'i çalıştırılabilir ve route/zone nesneleri bu iş için yeterli. T-020'de sürüm ve import smoke-test yapılır; başarısızsa başka araca sessizce geçmek yerine engel raporlanır.
- **VARSAYIM:** KiCad GUI yalnız görsel review için kullanılır; tüm kaydedilen değişiklikler betiklerden gelir.

## Doğrulanamayanlar
- Konnect'in KiCad 10.0.7 ile uyumlu yetenekleri / DRC integrasyonu — resmi repo dokümanı bu task girdilerinde yok, entegrasyon bu PR'da denenmedi.
