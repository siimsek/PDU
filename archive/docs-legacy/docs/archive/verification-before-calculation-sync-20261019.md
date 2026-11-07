# IDA PDU — Tasarım Doğrulama Durumu

> Güncel checkpoint: [PROJECT-STATE](PROJECT-STATE.md), [bağımsız denetim](../hardware/no-measurement-final-audit.md). Son kayıt short0/ERC0/0; PCB197 unrouted/301 uyarı;48 koşu512 geçen/2 O1 başarısız. Aşağıdaki önceki aktarım/299-uyarı kayıtları tarihsel kanıttır. Kaynak/sonuç eşliği tamamlandı; üretim kabulü yok.

## Son şema ve ağ kuralları teslimi

`PDU_schematic_finished.png/.pdf` güncel.23 component alanı ve sayfa açıklamaları düzenlendi;73 fiziksel parça/257 pin/46 net üyeliği korundu. Short0/ERC0/0/açıkpin0/örtüşme0;218 tel/86 etiket korunur.46 ağ için9 netclass kaydedildi ve geri okundu. Hesap35µm nominal/31.5µm paylı kalınlığa dayanır;2oz yalnız opsiyonel yükseltmedir. Kanıt `.konnect/diagnostics/netclass-evidence.json`; tüm kalan karar ve kabul ölçütleri `docs/SON-TESLIM.md` içindedir. Eski tarihli kayıtlar aşağıda geçmiş kanıt olarak tutulur.

## Son PCB kaydı — 2026-10-19

Kullanıcı U1–U4'ün doğrulanmış footprint atamalarına izin verdi.72 footprint aktarıldı ve işlevsel bloklara taşındı; F1 bekliyor.72 parçanın977 bakır pad nesnesi/255 mantıksal pini netlerle eşleşiyor. Kısa devre0, ERC0/0. DRC197 unrouted ve299 uyarı; bakır kısa devresi, clearance ihlali, eksik sınır veya courtyard çakışması yok. Yerleşim skoru100 yalnız araç ölçütlerini karşılıyor; elektrik/termal üretim onayı değildir. O1 OVP ve bakır kalınlığı uyuşmazlığı açık. Güncel kayıt: `hardware/PCB-layout-status.md`; aşağıdaki68-parça ve önceki tarihli kayıtlar geçmiş durumu gösterir.

## 2026-10-19 güncellemesi

MCP/API düzeltildi. Q1'in uyumlu footprint seçimi deneme kartında doğrulandı; şema elektriksel bağlantıları ve değerleri korunarak 68 footprint ana PCB'ye ilk aktarım olarak kaydedildi. U1–U4 ve F1 footprint alanları boş. Şema kısa devre 0, ERC 0 hata/0 uyarı. PCB henüz sınır ve iz içermiyor: DRC 103 hata/77 uyarı; O1 aşırı gerilim kabulü de hâlâ başarısız. Ayrıntı ve kanıt: `hardware/PCB-transfer-status.md`. Aşağıdaki 2026-10-18 kayıtları geçmiş durumu gösterir.

**Tarih:** 2026-10-18 • **Sonuç:** Elektrik şeması düzeltildi, ERC 0 hata/0 uyarı. İki motor ortak devreyi çalıştırdı; O1 aşırı gerilim testi başarısız. PCB onayı yok.

| ID | Kontrol | Hedef/ölçüt | Mevcut kanıt | Durum |
|---|---|---|---|---|
| V-01 | O1 giriş ratingi | Kullanılan kart sürümü için resmi sınırlar | T3 güncel güç bağlantısı belgesi ve hardware GitHub deposu 5–12 V/5 A diyor; gerçek tüketim ölçülmedi | RESMÎ RATING UYUMLU; YÜK ÖLÇÜMÜ AÇIK |
| V-02 | O1 akım profili | Start/steady/peak | Ölçüm yok | AÇIK |
| V-03 | S2E girişi | 9–28 V; 12 V start typical 1.2 A, datasheet üst 1.5 A; work upper 0.22 A | SLAMTEC S2E v1.8 datasheet | KATALOG DOĞRULANDI; 11 V START AÇIK |
| V-04 | Buck seçimi | VIN aralığı ve 7 A sürekli/7.5 A kapasite | 2× LM70880-Q1 şemada 180° interleaved bağlı; RT 49.9 kΩ, CONFIG 54.9 kΩ / 90.9 kΩ | ŞEMA KURULU; TERMAL VE ÜRETİCİ MAKROMODELİ AÇIK |
| V-05 | Çıkış gerilimi | 11.0 V ±2% hedef | Bölücü hesabı 10.996 V. Ortalama model 7.5 A'da 10.996 V verdi. Tezgah ölçümü yok | HESAP VE ORTALAMA MODEL; ÖLÇÜM AÇIK |
| V-06 | Toplam bütçe | 11 V × 7 A = 77 W; 7.5 A güç katı/branch kapasitesi | İki fazda 7.5 A toplam 3.75 A/faz. O1 4.96 A + S2E 2.53 A nominal eFuse; O1 resmî DC ratingi 5–12 V/5 A; gerçek yük ölçülmedi | TASARIM KAPASİTESİ; O1 VARSAYIMI AÇIK |
| V-07 | Verim | Her giriş/yük koşulunda ölç | IDA PDU verim ölçümü yok | AÇIK |
| V-08 | Ripple/transient | Cihaz uçlarında bara ±2% | Güncel iki fazlı ideal PWM: 20 V'ta faz ripple 1.647 A, 26 V'ta 2.141 A. 0.45→4.5 A yük adımı yaklaşık 10.804–10.996 V. 2 ns/1 ns yakınsaması denetlendi | DAVRANIŞSAL MODEL; O1 OVP BAŞARISIZ; KART ÖLÇÜMÜ AÇIK |
| V-09 | Surge/reverse | Ölçülen ESC transientinde hasar yok | Şemada SMCJ33A korumalı VIN'de, LM74700 + BSC160N10NS3G sigortadan sonra. Surge enerjisi yok | DEVRE KURULU; ENERJİ KOORDİNASYONU KRİTİK AÇIK |
| V-10 | Branch eFuse | Trip profiles and thermal rise acceptable | TPS259824ONRGET şemada. 301 Ω / 604 Ω, EN 64.9 kΩ/10 kΩ, PG 100 kΩ/18 kΩ, IMON 2.61 kΩ/4.99 kΩ, dVdt 1.0 nF | HESAPLAR ŞEMADA; SICAKLIK VE ZAMANLAMA AÇIK |
| V-11 | Termal | Worst-case sıcaklık limitlerinde marj | PCB ve ölçüm yok | AÇIK |
| V-12 | KiCad ERC/DRC | Kritik çözülmemiş hata 0 | 2026-10-18 Konnect ERC: 0 hata, 0 uyarı. 77 sembol, 39 yerel ağ, kısa devre 0, bağlı olmayan pin 0. PCB bu şemadan üretilmedi; önceki kayıtlı DRC'de Edge.Cuts yoktu | ŞEMA ERC TEMİZ; PCB VE ÖZEL FOOTPRINT AÇIK |
| V-13 | LTspice/ngspice | Tekrarlanabilir ortak devre, açık model kapsamı | 20 senaryo ×2 motor; export edilen devreden aynı pin ve değerler. Sonuç sayıları simulation/verification-results.json içinde. O1 aşırı gerilim kabulü başarısız | TAMAMLANMADI; SİLİKON VE TERMAL KANIT YOK |
| V-14 | BOM/bütçe | Yerel toplam ve onaylı bütçe | TPS259824ONRGET ve Micro-Fit 43045/43025/43030 parçaları için Türkiye stok/fiyat snapshot'ı alındı; LM70880, pasif, koruma, PCB/assembly/kablo toplamı açık | KISMİ TEDARİK GÖRÜLDÜ; TOPLAM AÇIK |
| V-15 | Kaynak deposu | Private GitHub `main`, yerel temel commit ile eşleşiyor | Yerel `HEAD` ve `origin/main` = `40c853bc`; teknik doküman/BOM değişiklikleri ve korunmuş, izlenmeyen KiCad/datasheet/history dosyaları var; commit/push yapılmadı | TEMEL COMMIT EŞLEŞİYOR; ÇALIŞMA AĞACI KİRLİ; GÖNDERİM YOK |

## Ölçüm formu

| Tarih | Kart sürümü | Vin | O1 mode | S2E mode | Iin | Iport1 | Iport2 | Vbus min/max | ripple | T hottest | Sonuç |
|---|---|---:|---|---|---:|---:|---:|---:|---:|---:|---|
| — | — | — | — | — | — | — | — | — | — | — | Ölçülmedi |

## Geçme koşulları

1. 20 V girişte 7 A eşzamanlı yük altında cihaz girişleri üretici sınırında ve bara 11.0 V ±2% steady-state olmalı; 7.5 A kapasite ayrı termal/koruma kontrolünden geçmeli.
2. Kalkış/load step sırasında cihaz girişleri min rating altına düşmez; eFuse erken açmaz; tepe değerler absolute maximum altındadır.
3. Surge waveform/süre/enerji kaydedilir; TVS, fuse, reverse protection ve U1 pinindeki clamp koordine edilir.
4. Termal denge sonunda bileşen derating ve kablo/konnektör sınırları korunur.
5. ERC/DRC kapanır; BOM MPN'leri eşleşir; Gerber üretici kontrolünden geçer.

Bu koşullar fiziksel prototipte gösterilmedi. Katalog sınırları ürünün güvenli çalıştığını kanıtlamaz.
