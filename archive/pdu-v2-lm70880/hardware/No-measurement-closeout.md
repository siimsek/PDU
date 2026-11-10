> **SUPERSEDED (G4, 2026-11-07) → docs/START-HERE.md.** 2026-10-19 anlık görüntüsünün geçmiş kaydıdır; içerik değiştirilmedi.

# Ölçüm gerektirmeyen tamamlamalar — 19 Ekim 2026

## Uygulanan değişiklikler

- RFB1: Panasonic ERA3AEB134V130k; RFB2: ERA3AEB1022V10.2k. Kesin MPN/tolerans/TCR/datasheet bilgileri Konnect ile işlendi. İki direnç0.1%,25ppm/K,0603,0.1W. Nominal oran değişmedi.
- RIMON1 ve RIMON2: ERA3AEB8060V806ohm. Şema ve PCB güncellendi. Dönüşüm0.198276V/A; yayımlanmış kazanç/sıcaklık aralığındaki15A üst değerlendirmesi3.07165V.301/604ohm ILIM ayarı değişmedi; O1'e5A yük atanmadı. S2E'nin3A altındaki doğruluk sınırı ve75°C üzerindeki eksik kazanç garantisi açık.
- COUT1–8: TDK C5750X7S2A226M280KB22uF100V X7S2220. Üretici dosyaları, şifreli modeli değiştirmeden AC koşusu, geometrik pin/pad kabulü, deneme kartı render/canlı geri okuma tamamlandı.100V seçimi tanımlı53.3V varsayılan zarfın üzerindedir; gerçek arıza darbesi/enerjisi onayı değildir.
- Yeni özel ayak izi `PDU:TDK_C5750_2220_Recommended`. Eski1210 ayak izlerini değiştirmek Konnect'in doğrudan sync aracı tarafından reddedildi. Kartta iz olmadığı doğrulandı; yalnız sekiz eski COUT örneği MCP ile kaldırıldı ve şemadan doğru pin/net eşliğiyle yeni örnekler eklendi. Yerleşimden sonra iki REN/COUT courtyard çakışması bulundu ve REN1/REN2 sağa1.27mm alınarak kapatıldı.72 footprint, F1 hâlâ atanmamış.
- COUTbankları x125.73mm'de; y60.96,68.58,78.74,86.36,93.98,100.33,110.49,118.11mm. Bu ilk yerleşimdir; gerçek yüksek frekanslı döngü/EMI/termal kabulü değildir. Şemadaki sembol/tel/etiket konumları bu değişikliklerde taşınmadı.
- Kütüphane refresh'i yeni sekiz COUT mismatch uyarısını giderdi. Son PCB DRC197 hata (tamamı bağlantısız öğe),301 uyarı. Bakır kısa devresi/clearance/courtyard hatası yok; iz sayısı0.
- Son PCB kaydı eski açık-proje önbelleğinden sınıfları geri yazdığı için9 netclass/46 tam ağ ataması Konnect üzerinden tekrar uygulandı ve okundu. Sonraki GUI kaydı aynı riski taşır; temiz kapatmadan sonra `.konnect/ApplyRoutingRules.py` kapalı-proje tekrar uygulama yoludur. Router ek menü listesi açık kartta uygulanmış sayılmaz.

## Tekrarlanabilir doğrulama

- Yeni ortak netlist:73 fiziksel parça,257 pin,46 ağ. Önceki tamamlanmış şemaya göre bütün pin-net üyelikleri/referanslar aynı. Yalnız iki RIMON değeri ve sekiz COUT footprinti değişti; MPΝ/rating bilgileri eklendi.
- Her küçük şema değişiminden sonra short_count0, ERC0 hata/0 uyarı.218 tel korunuyor. Yeni PNG/PDF `PDU_schematic_finished.*` dosyalarında.
- `python simulation/run_all.py`:24 senaryo, iki motor,48 koşu tamamlandı:512 kontrol geçti,2 O1 kontrolü başarısız. Sonuç netlist SHA256 ile eşleştirildi. Önceki tekrarın120s araç zaman aşımı sonrası aynı fiziksel devre/ölçütler300s süreç sınırıyla yeniden çalıştırıldı. Nominal IMON ölçüm kontrolleri ve165uF/257.66uF COUT hassasiyetleri eklendi. Güncel sayısal sonuç `simulation/verification-results.json`; O1 başarısızlığı için çıkış kodu1 korunur.
- `python simulation/check_static_corners.py`: gerçek BOM/MPN/gerilim alanlarıyla statik FB/IMON/UVLO/rating hesabı. FB statik köşesi10.8333–11.1605V; UVLO20.3318V üst kalkış köşesi ve bilinmeyen EN sızıntısı nedeniyle20V yeniden başlama kabulü hâlâ başarısızdır.
- Ayrı LTC4365 koruma adayı sekiz senaryoda çalıştırıldı. Soğuk/yüksek ESR senaryosu yaklaşık12.4055V tepe verdiği için ana şemaya aktarılmadı. Bu adayın kaydı COUT gerilim yükseltmesinden önceki25V taramasını korur; ana COUT artık100V'dur. Aday MOSFETleri yaklaşık modeldir; SOA/enerji testi sayılmaz.
- Üreticinin tam kapasitör modeli11V25°C'de164.9775uF/banka ve400kHz'de1.9204mOhm/parça verir. Ortak LT/ng davranış devresi bu modelin eşdeğeri değildir: CBIAS ile ideal kapasite hassasiyetleri taranır. İki motorun eşliği gerçek buck iç döngüsünü doğrulamaz.

## Açık kalanlar ve nedenleri

- BOM aktarımındaki yedi `?` referans farkı ham CSV korunarak düzeltildi: `simulation/canonical_bom.py` yalnız tam netlist ref/değer/footprint eşliğinde düzeltme yapar.73 yayınlanan satır doğrulandı; upstream KiCad export davranışı düzeltilmiş sayılmaz.57 MPN alanı hâlâ boş; satın alma BOM'u tamamlanmış değildir. Bu eksiklerin bir bölümü ölçüm gerektirmeden parça seçimiyle tamamlanabilir; tüm kalan işlerin ölçüm beklediği iddia edilmez.

- O1 girişinin12V sınırı hâlâ sağlanmıyor; ana devredeki16.9V eFuse OVP'si iki motorda yaklaşık16.89V tepe veriyor. Yeni aday da bütün taramaları geçmedi. Bu, fiziksel ölçüm beklediği için kapatılmış bir madde değil; mimari/tolerans/tepki süresi çalışması hâlâ gerekiyor.
- F1 kesin DC sigorta/yuva seçimi için batarya/kablo olası kısa devre akımı ve I²t koordinasyonu eksik. MPN/footprint uydurulmadı.
- UVLO batarya politikası ve garantili EN sızıntısı eksik;20V kalkış garantisi verilmedi. RC/CHF değerleri model testinden geçmiş olsa da üretici denklemleriyle gerçek loop/phase-margin tasarımı ve sonraki fiziksel doğrulama açık.
- PCB yönlendirme, termal-via/stencil incelemesi, mekanik/konnektör doğrulaması, gerçek yük/başlangıç akımları, TVS/fuse enerji koordinasyonu, termal/EMI kabulü tamamlanmadı.301 DRC uyarısı gizlenmedi; mevcut MCP referans/değer metin konumlarını veya Description alanını düzeltemiyor.

Ölçüm yapılmadı, CUA kullanılmadı, KiCad kaynağı metin olarak değiştirilmedi. Commit/push yok. Bu kayıt bütün işlerin veya üretim kabulünün tamamlandığı anlamına gelmez.

Kanıt: `.konnect/diagnostics/no-measurement-final-parity.json`, `cout-hv-main-drc.json`, `restore-profile-after-save-results.json`, `simulation/verification-results.json`, `simulation/static-corner-results.json`, `hardware/COUT-qualification.md`, `hardware/validation/c5750/physical-acceptance.md`.
