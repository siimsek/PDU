# Kütüphane kaynakları ve üçüncü taraf bildirimleri

KiCad topluluğunun standart sembol/footprint verileri projede kullanılıyor. Özellikle `TDSON-8-1_Konnect` uyarlaması stock `Package_TO_SOT_SMD:TDSON-8-1` bakır/paste geometrisini koruyup mask temsilini değiştirmiştir; değişiklik pin/pad kabul kaydında açıklanır.

KiCad'den alınan/uyarlanan kütüphane verileri upstream **CC-BY-SA4.0 ve KiCad elektronik tasarım istisnası** koşullarıyla korunur. Upstream bildirim `LICENSE-KiCad.md`, lisans metni `CC-BY-SA-4.0.txt` içindedir. Bu bildirim tüm PDU proje kodu/dokümantasyonu için yeni bir lisans atamaz.

Kaynaklar:

- https://gitlab.com/kicad/libraries/kicad-footprints
- https://gitlab.com/kicad/libraries/kicad-symbols
- https://www.kicad.org/libraries/license/

Diğer özel footprint/symbol tasarımlarının üretici geometrisi ve yapılan yaklaşım açıklamaları `hardware/validation/` kabul kayıtlarında bulunur. Bunlar üretici CAD'i olarak sunulmaz.

TDK üretici modellerinin izinsiz yeniden dağıtım kısıtı nedeniyle modeller ve indirilen üçüncü taraf dosyalar Git dışında yerelde tutulur. Resmî edinme kaynakları `docs/REPOSITORY.md` ve `hardware/COUT-qualification.md` içindedir. Repo içinde bulunan sayısal sonuçlar/model benchleri bu dosyaların kendisini içermez.
