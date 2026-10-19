# Şematik okunurluk ve doğrulama — 2026-10-19

> Tarihsel kozmetik düzenleme kaydı: bu işlemden sonra RIMON806 Ω ve COUT100 V atamaları yapıldı. Güncel değer/footprint durumu `docs/PROJECT-STATE.md` ve `hardware/no-measurement-final-audit.md` içindedir; aşağıdaki “değerler aynı” ifadesi yalnız bu kozmetik geçişi karşılaştırır.

Ana dosya: `PDU.kicad_sch`. Bütün KiCad kaynak değişiklikleri Konnect MCP üzerinden yapıldı. Ana şematik kilidi başlangıçta ve yazma partilerinden önce yoktu; kilit silinmedi. PCB veya proje ayarı bu çalışmanın şematik alt görevi tarafından değiştirilmedi.

## Uygulanan değişiklikler

- 20 dikey direncin referans/değer alanları sembol gövdesinden çıkarıldı ve yatay okunur çiftler yapıldı: RT1, RCFG1, RFB1, RFB2, RCOMP, RSYNC, RT2, RCFG2, RILIM1, RIMON1, RILIM2, RIMON2, RUV1, RUV2, REN1, REN2, RPG1, RPG2, RPG1B, RPG2B. RSYNC yazıları komşu CHF koluyla çakışmasın diye sol yana alındı.
- Q1'in uzun MPN yazısı dikey baskıdan yatay metne çevrildi. U5'in referans/değeri GND yazısından ayrıldı. D1 referansı çerçeveye yalnız 0.22 mm yaklaşan eski konumdan sola alındı; SMCJ33A değeri yatay ve telden ayrık yazıldı. Toplam 23 bileşenin yalnızca görünen alan yerleşimleri değişti.
- Çerçeve altında kalan iki eski dipnot ve bunları düzeltmeye çalışan eski REV2 notu kaldırıldı. Çelişkili 100k/82.5k PG açıklaması artık yok; güncel oran tek açıklamada 100k/18k.
- Üstte J1 → F1 → U5/Q1 → VIN → ortak iki faz → VOUT → iki eFuse/konnektör güç akışı anlatıldı. İki fazın ortak EN/COMP/VOUT ve SYNC bağlantısı açıklandı. Mevcut altı blok başlığı korundu.
- O1'in 5–12 V girişi ile mevcut 16.9 V OVP uyumsuzluğu kırmızı notla görünür yapıldı; O1 bağlanmadan önce koruma revizyonu ve test gerektiği yazıldı. 5 A'nın ölçülmüş yük akımı olmadığı ve 301 ohm RILIM1'in nominal ~4.96 A kesme eşiği olduğu açıklandı.
- 20 V yeniden başlatma garantisinin bulunmadığı, UVLO tolerans/politika kararının açık olduğu, F1 MPN/footprint seçiminin yapılmadığı ve prototip LM70880 footprintlerinin üretim kabulünden geçmediği yazıldı.
- RFB1/RFB2'ye nominal değerler değişmeden gizli seçim şartları eklendi: Tolerance=0.1%, TCR=<=25 ppm/K, Specification=Required selection; verify procurement MPN before assembly. Bunlar satın alınmış parça/MPN doğrulaması değildir. Öncesinde iki dirençte de MPN alanı yoktu; MPN uydurulmadı.

## Korunan elektriksel yapı

Hiçbir sembol, pin, tel, etiket veya bağlantı taşınmadı/eklenmedi/silinmedi. Bileşen değerleri, referansları, footprintleri, net isimleri aynıdır. Eski kısa ve kısa devresiz teller korundu. Koruma mimarisi değiştirilmedi. F1 footprint/MPN boş kaldı; O1 yük akımı 5 A olarak ayarlanmadı.

`power-ics-assigned.net` ile yeni `schematic-finished.net` semantik karşılaştırması: 73 fiziksel bileşenin referans/değer/footprint/kütüphane alanları eşit; 46 netin her birindeki 257 referans-pin üyeliği aynı. Şematikte dört PWR_FLAG dahil 77 sembol var.

## Son kontroller

- short_count: **0**. ERC: **0 hata / 0 uyarı**.
- Örtüşen sembol/aynı noktadaki çelişkili etiket: **0**, 77/77 gövde geometrisi çözüldü. Bu otomatik kontrol serbest metin kapsamıyor; PNG ve kritik Q1/U5/kompanzasyon alanları ayrıca gözle incelendi.
- Açık pin: **0**; orphan: **0**; boşta tel ucu: **0**.
- **218 tel / 86 etiket**; tamamı önceki geometriyle aynı. Teller yatay/dikey; sembol/etiket/tel uçları 1.27 mm ızgarada. Şematik çizgi kalınlığı gerçek PCB akım kapasitesini belirlemez.
- Görsel: `../PDU_schematic_finished.png` (4096×2896); PDF: `../PDU_schematic_finished.pdf`; SVG: `schematic-finish/PDU.svg`.
- A2 antet sınırı dışa aktarılmış SVG'de x474.0044..582.0044, y375.989..407.989 mm. D1 gövde/pin sağ sınırı 471.17 mm (2.83 mm açıklık), GND teli 469.9 mm (4.10 mm açıklık). D1/Q1/U5 referans ve değerlerinin gerçek stroke-path sınırları 0.15 mm ek payla kontrol edildi; antet/çerçeve çakışması yok. Kanıt: `../.konnect/diagnostics/schematic-titleblock-clearance.json`.
- Makine kanıtları: `../.konnect/diagnostics/schematic-finish-checks.json`, `schematic-finish-geometry.json`, `schematic-finish-parity.json`. Netlist karşılaştırma aracı `compare_schematic_finish.py` sadece dışa aktarılmış `.net` dosyalarını okur.

## Kalan somut işler

O1 OVP revizyonu ve yeniden test; F1 gerçek parça/ayak izi seçimi; 20 V yeniden başlatma için tolerans/sızıntı bütçesi ve UVLO politika kararı; kesin 0.1%/25 ppm direnç MPN seçim ve satın alma doğrulaması; akım/termal/SOA/kararlılık ölçümleri ve üretim footprint onayı. Mevcut sıfır ERC sonucu bunların geçtiği anlamına gelmez. PCB iz yönlendirmesi ve üretim onayı bu şematik düzenleme alt görevinin dışındadır.
