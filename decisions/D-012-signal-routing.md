# D-012 — T-023 sinyal yönlendirme planı

- **Kart:** tasks/D-012.md
- **Yazan:** Codex (THINKER)
- **Fiziksel iş gerekli mi:** Hayır
- **Durum:** Review

## Soru

T-022 sonrası açık KiCad bağlantıları, mevcut güç bakırı ve L2 GND dönüşünü koruyarak T-023’te hangi araç ve sırayla tamamlanmalı? Kelvin, gate ve HV sınırları tasks/T-023.md:27-37 ve PDU.kicad_dru:41-44 ile sabittir.

## Başlangıç komut çıktıları

git status -sb → ## main...origin/main.
git rev-parse HEAD → a05a8d7ce290119a387d70656140e4d6bf1d7564.
gh pr list --state open --json number,title,headRefName,baseRefName,isDraft,headRefOid →
[{"baseRefName":"main","headRefName":"wp/T-025-card","headRefOid":"9386c39c7e0160de1bffe48ab076231f5b46703a","isDraft":true,"number":61,"title":"Draft T-025: UTF-8 kalıcı düzeltmesi"}].

gh pr view 66 ve 68 komutları ikisini MERGED gösterdi; main HEAD ve tasks/T-023.md:7, HANDOFF.md:4-5 T-023 Ready bilgisini doğruladı. T-023’ün başlamadığı bilgisi açık PR listesi ve kart durumu ile uyumludur; yerel/harici yayımlanmamış çalışma bu yolla doğrulanamaz.

## Seçenekler

| Seçenek | Kapsam, tekrarlanabilirlik ve risk | Karar |
|---|---|---|
| A — D-009 bundled pcbnew, elle tanımlı koordinat/waypoint | 199 açık çift için tamamını elle yazmak yüksek düzenleme ve bakım yükü; sabit koordinatlar sürümlenebilir ve DRC/parite ile denetlenebilir. | Kritik, kısa ve fiziksel anlamı önemli ağlarda kullan. |
| B — D-009 pcbnew ile sınırlı betikli yönlendirici + açık waypoint | Aynı board/net/engel girdisinde sabit sıralama, grid ve maliyetle tekrarlanabilir; yanlış net, açıklık ve dönüş yolu riski her adayda gerçek KiCad DRC ile kontrol edilir. 199 çiftin geri kalanı için kapsamı nettir; rota sayısı/çalışma süresi denenmedi. | Seç. Kritik ağları otomatik yönlendiriciye koşulsuz bırakma. |
| C — D-009 değiştirip harici autorouter | DSN/SES round trip bu repoda doğrulanmadı (decisions/D-009-routing-tool.md seçenek C). Tüm ağları kapsama iddiası, net/zone kaybı ve parite riski sınanmadı. | Seçilmedi; araç değişikliği için ayrıca ölçülü karar gerekir. |

## Öneri

**KOŞULLU — B:** KiCad 10.0.7 bundled pcbnew kullan; Kelvin ve gate için açık, ölçülebilir waypoint’ler, diğer sinyaller için kapsamı sınırlandırılmış deterministik arama uygula. Her alt adımın aday kartında refill + DRC + schematic parity ve ağ bazında açık çift farkı kaydet. L2’yi GND düzlemi olarak koru; B.Cu baraları ve tap’leri sabit engel kabul et. Hiçbir netclass veya DRC açıklığını küçültme.

## Kanıt — kendi komutlarım ve ölçüler

KiCad CLI version → 10.0.7. pcb drc --format json --severity-all --refill-zones --schematic-parity → exit 0; 0 error, 6 via_dangling warning, 199 unconnected_items, 0 parity. IPC-2581 export → exit 0. İkisi de PDU.kicad_pcb @ a05a8d7’den, GUI kaydı olmadan üretildi.

### Açık çift sınıflaması

KiCad unconnected_items içindeki her çifti ağ adına ve /VOUT çiftinde uç adına göre yalnız bir sınıfa atadım. /VOUT üzerindeki INA/TP_ISNS çiftleri Kelvin, R_INJ/TP_FB_INJ çiftleri FB’dir. Bunlar **çift sayısıdır**, iz veya pad sayısı değildir.

| Sınıf | Çift | Ağ kuralı |
|---|---:|---|
| Kelvin | 8 | /ISNS1, /ISNS2 ve /VOUT’un Kelvin uç çiftleri |
| Gate | 3 | /GATE, /ISO_GATE |
| FB/COMP | 12 | /FB, /FB_INJ, /FB_TRIM, /COMP, /COMP_MID ve /VOUT FB uç çiftleri |
| OVP/OC mantık | 34 | /CLR_N, /ISO_EN, /ISO_OV, /OC_REF, /OC_SENSE1/2, /OC_TRIP1_N/2_N, /OVP_BUS_N, /OVP_Q, /OVP_REF, /OVP_SENSE, /OVP_TRIP_N |
| GND dönüş | 77 | /GND |
| Diğer | 65 | /P5V_PROT 22 çift dahil, yukarıdaki sınıflara atanmayan besleme, enable, PG, bootstrap ve yardımcı ağlar |
| Toplam | 199 | 8+3+12+34+77+65 |

**Karşılaştırma:** reports/g5/T-022/drc.json ve route-review.md:122-126, toplam 199 ve /GND 77 bildirir; kendi DRC’mle fark iki sayıda da 0 (%0). Kategori bölümü BUILDER tablosu değil, yukarıdaki atanmış sınıflamadır. 6 dangling via uyarısı başlangıç borcudur; T-023 her birini inceleyip yeni uyarı eklememeli, finalde durumunu açıkça göstermelidir.

### /GND pad ve via kararı

77 /GND çiftinin uç açıklamalarında **78 farklı pad tanımı** sayıldı (KiCad DRC JSON, item descriptions). Bazı çiftler iki pad arasında olduğundan 77 çift = 77 via değildir; aynı açıklama birden fazla çifte katılabilir. 78 uç, tek tek bağlantı denetimi için üst listedir; bir padin bitişik GND bakırı veya mevcut via ile bağlanması yeni via gerektirmeyebilir.

Öncelik kısa F.Cu GND izi + yakındaki 0,6/0,3 mm through via ile L2’ye yerel bağlantıdır. Yakın padler, analog/dijital dönüş davranışları uygunsa aynı yerel GND bakırı/via grubunu paylaşabilir. Mevcut via-in-pad korunabilir; yeni via-in-pad yalnız ayrı pad sığma/clearance ve filled/capped fab onayıyla seçilir (PCB-HANDOFF.md:60). 78 yeni via önerilmiyor: gerçek gerekli sayı, her padin mevcut bağlı bileşenine göre T-023 adayında KiCad bağlantı denetimiyle ölçülür; bugün **doğrulanamadı**. Yeni via antipadleri L2’yi bölmemeli.

### Katmanlar ve sığma

KiCad IPC-2581 exportundan L2/In1.Cu GND dolgusunun dış kontur sayısı 1, alanı 9287,11 mm²; B.Cu/L4 GND dış kontur sayısı 10’dur. T-022 route-review.md:116-122 aynı ada sayılarını verir; kendi L2 alan farkı 0’dır. B.Cu GND konturlarının dış poligon birleşimi 7632,06 mm², BUILDER dolu alan 7609,76 mm²’dir; benim ölçümüm iç kesikleri hesaba katmayan dış konturdur ve fark doğrudan hata karşılaştırması değildir.

B.Cu IPC exportunda /ANODE, /VIN, /VOUT, /VSAFE, /O1_11V ve /S2E_11V zone dış poligon birleşim alanları sırasıyla 46,89; 35,56; 78,10; 93,86; 76,92; 10,25 mm²; toplam 341,58 mm². Bunlar yalnız exporttaki zone konturlarıdır; geniş B.Cu track, pad, delik, kesik ve clearance alanlarını içermez. Bu yüzden toplam serbest sinyal yönlendirme alanı ve kesintisiz kanal genişliği **doğrulanamadı**. T-022’de /VOUT 7,0 mm ve /VSAFE 5,5 mm baralar var (scripts/pcb_route_power.py; route-review.md); iki yanda 0,6 mm HV açıklığı gereken sinyal için yalnız bu izlerin yasak enkesitleri sırasıyla en az 8,2 ve 6,7 mm’dir. Bu basit enkesit, köşeler/vialar/diğer nesneler çevresindeki gerçek yol kanıtı değildir.

L4 GND’nin 10 konturu nedeniyle L4 boyunca GND sürekliliği varsayma. F.Cu kritik kısa yerel bağlantılar, B.Cu yalnız güç bakırı ve HV açıklığı çevresindeki DRC temiz koridorlarda sinyal için kullanılır. L2 tek ada olduğu için referans ve yerel GND dönüşüdür; sinyal iziyle kesilmez. L3 güç zonları üzerinden sinyal geçişi varsayılmaz.

### Kelvin ve gate — ölçülen alt sınırlar

IPC-2581 F.Cu pad merkezlerinden Öklid uzaklıkları:

| Bağlantı | Merkezden merkeze düz uzaklık (mm) | 15 mm’ye aritmetik fark (mm) |
|---|---:|---:|
| RS1.1 → U11.8 | 4,9228 | 10,0772 |
| RS1.2 → U11.1 | 12,7188 | 2,2812 |
| RS2.1 → U12.8 | 8,2409 | 6,7591 |
| RS2.2 → U12.1 | 13,8288 | 1,1712 |

Kaynak: bu oturum KiCad IPC-2581 exportunda F.Cu Pad/PinRef konumları; kriter tasks/T-023.md:33. Bunlar düz merkez mesafesidir; RS pad iç kenarı, via, eğim, paralellik ve gerçek iz merkezi hesaba katılmadığı için ≤15 mm geçiş kanıtı değildir. Özellikle RS2’nin 1,1712 mm aritmetik payı yol aramadan yeterli sayılamaz. Her iki kutbu RS pad iç kenarından ayrı Kelvin koluyla çıkar, SW bakırı altından geçirme; her gerçek yolu ayrı ölç. Engel nedeniyle sığmazsa önce aynı kuralı koruyan katman/waypoint alternatifini ölç; yine sığmazsa INA296/RS yerleşim düzeltmesini açıkça bildir, sınırı değiştirme.

Q2.4–U6.6 pad merkezlerinin düz mesafesi 4,5166 mm (aynı IPC export). T-022 route-review.md gate centerline 5,469 mm bildirir; düz mesafe gerçek yol değildir. Mevcut gate yolunu koru, R_GS ve TP_ISO_GATE uçlarını tamamla; gate dönüş çevrimi ile seri elemanları ve Q2–U6 gerçek centerline’ı T-023’te ayrıca ölç. /ANODE, /VIN, /VOUT, /VSAFE ile mantık/analog arasındaki 0,6 mm açıklığı koru (PDU.kicad_dru:41-44; tasks/T-023.md:29).

## T-023 için dört alt adım

1. Başlangıç snapshot: 199 açık çift, 6 warning, parity 0 tabanını yeniden üret; 78 farklı GND pad açıklamasını UUID/ref/pin ve mevcut bağlı GND bakırı ile envanterle. Yerel GND via/kol adaylarını seç.
2. GND dönüşleri ve kritik Kelvin/gate: L2’yi bölmeden yerel GND bağlantıları, ardından RS1/RS2–INA296 çiftleri ve Q2/U6 gate dönüşü. Her Kelvin yolunun ayrı uzunluğu, SW’ye göre katmanı, GND dönüşü ve HV clearance’ı raporlanır.
3. FB/COMP/OVP/OC: F.Cu/B.Cu koridorlarını L2 referansı ve SW’den uzaklıkla yönlendir; besleme tap’leri ile karışıklığı net/pad bazında kontrol et.
4. Diğer enable, PG, bootstrap, besleme ve kalan sinyal uçlarını tamamla; ERC/netlist pin haritası, tüm KiCad açık çiftleri, 6 başlangıç uyarısının bireysel durumu ve son bağlantı envanteriyle kapat.

Her adımda candidate board’u zone refill ile KiCad 10.0.7 DRC ve schematic parity’den geçir; yeni short/error/izinsiz clearance yok, parity 0; önceki netlere kopma eklenmez. Başlangıçtaki açık çiftlerin aşama başı/sonu net bazında sayısını kaydet; sıfırlanmadığı ara aşamayı tamamlanmış kart sayma. Final tasks/T-023.md:36-37 kriterine göre tüm uçlar bağlanmalı. Uyuşmayan bağlantı/kural varsa dur ve fiziksel alternatif veya placement düzeltmesi için kanıt üret.

## Açık varsayımlar

- **VARSAYIM:** Deterministik sınırlı arama bu karttaki sinyal koridorlarını bulabilir; gerçek deneme yapılmadı.
- **VARSAYIM:** Fab 0,6/0,3 mm via, 1 oz stackup ve yeni via-in-pad için dolgulu/capped süreci kabul eder (PCB-HANDOFF.md:60).
- **VARSAYIM:** Mevcut L2 GND referansı yeni via antipadlerinden sonra da tek ada kalır; her aşamada refill ve bağlantı kontrolü gerekir.

## Doğrulanamayanlar

- B.Cu gerçek serbest alanı/kanal genişlikleri: tüm bakır ve clearance geometrisinin birleşimi ölçülmedi.
- Kelvin gerçek route centerline uzunlukları, paralellik, HV ve SW altından geçmeme: henüz sinyal rotası yok.
- 78 GND pad için gerçek yeni via sayısı; bireysel pad/zone bağlantıları ve paylaşılan dönüşler adayda hesaplanmalı.
- Gate dönüş alanı ve bağlantıları: R_GS ve TP açık.
- Harici autorouter round trip ve sınırlı arama başarısı: bu oturumda denenmedi.
