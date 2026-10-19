# IDA PDU

6S LiPo kaynağından ortak11 V güç barası üretip T3 Gemstone O1 ve SLAMTEC RPLIDAR S2E'yi ayrı korumalı çıkışlardan beslemek için geliştirilen iki fazlı güç dağıtım kartı.

**19 Ekim2026: prototip tasarım; üretime hazır değil.** O1 aşırı gerilim kabulü başarısız, PCB henüz yönlendirilmedi, sigorta ve satın alma BOM'u tamamlanmadı.

## Buradan devam et

1. [Amaç, yapılanlar ve kaldığımız yer](docs/PROJECT-STATE.md)
2. [Kesin kalan işler ve özel hazırlanan parçaların kontrolü](docs/REVIEW-CHECKLIST.md)
3. [Repo düzeni, kurulum ve yeniden çalıştırma](docs/REPOSITORY.md)
4. [Değişiklik özeti](docs/CHANGELOG.md)

## Ana proje ve güncel çıktılar

- [KiCad10 projesi](PDU.kicad_pro), [ana elektrik şeması](PDU.kicad_sch), [ilk PCB yerleşimi](PDU.kicad_pcb)
- Şema [PNG](PDU_schematic_finished.png) / [PDF](PDU_schematic_finished.pdf); PCB [PNG](hardware/PDU_blocks_placed.png)
- [Netlistle doğrulanmış parça dökümü](hardware/pdu-current-bom.csv); [mühendislik seçim notları](hardware/bom.csv)
- [Projeye özel semboller ve ayak izleri](hardware/lib)

## Son kaydedilmiş doğrulama

- Şema:77 sembol,73 fiziksel parça,46 ağ,257 pin,218 tel; kısa devre0, ERC0 hata/0 uyarı.
- PCB:72 footprint; F1 atanmamış; iz sayısı0. DRC197 bağlantısız öğe hatası ve301 uyarı.
- Ortak LTspice/ngspice modeli:24 senaryo ×2 motor =48 koşu;512 kontrol geçti,2 O1 aşırı gerilim kontrolü başarısız.
- O1 için esas alınan12 V üst sınıra karşı yaklaşık16,89 V tepe görülüyor. ERC0 ve simülatör eşliği bu hatayı kapatmıyor.
- Ortak IC modelleri yaklaşık davranış modelleridir; gerçek kararlılık, SOA, termal veya üretim onayı değildir.

Kanıt: [bağımsız denetim](hardware/no-measurement-final-audit.md), [sayısal sonuçlar](simulation/verification-results.json), [uygulanan düzeltmeler](hardware/No-measurement-closeout.md).

## Tasarım sınırları

Hedef11 V/7 A/77 W; güç katı kapasite hedefi7,5 A. Gerçek yük/açılış akımları ölçülmedi.301/604 Ω dirençlerin nominal kesme ayarları ölçülmüş yük veya garantili akım tavanı değildir; O1'e5 A tüketim atanmadı. Motor/ESC beslemek kapsam dışındadır.

Kararlar [tasarım notlarında](docs/design.md), yönlendirme sınıfları ve hesap sınırları [teslim kaydında](docs/SON-TESLIM.md).

## Çalışma kuralları

- KiCad kaynak değişiklikleri yalnız Konnect MCP üzerinden yapılır; kaynaklar metin olarak düzenlenmez. Kilit dosyaları silinmez.
- Şemada1,27 mm ızgara korunur; sembol ve bağlı etiket aynı miktarda taşınır. Küçük değişikliklerden sonra kısa devre/ERC denetlenir.
- Üretici modelleri yerel tutulur; kaynaklar ve edinme adımları [repo rehberinde](docs/REPOSITORY.md).
- [Arşiv](docs/archive/README.md), [eski işlevsel blok şeması](hardware/functional-blocks.kicad_sch) ve [eski buck modeli](simulation/buck-average.cir) güncel ana devrenin yerine kullanılmaz.

Kaynak depo: [siimsek/PDU](https://github.com/siimsek/PDU).
