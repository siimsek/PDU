# D-010 — T-022 güç yolu topolojisi

- **Kart:** tasks/D-010.md
- **Yazan:** Codex (THINKER), 2026-11-08
- **Fiziksel iş gerekli mi:** Hayır

## Soru

T-022, /VOUT ve /VSAFE için L3 dökümüne tek başına güvenmeden 7,5 A BUS_POWER yolunu nasıl kurmalı; 32 COUT bağlantısını, Q2 çıkışlarını, akım ölçüm uçlarını ve VIN–CIN–PGND dönüşünü mevcut karta nasıl sığdırmalı? Ölçütler Handoff genişlik/via hedefleri, gerçek pad açıklıkları, ≤10 mm U6–Q2 kapı sınırı, L2 GND sürekliliği ve gevşetilmemiş KiCad DRC/paritedir.

## Seçenekler

| Seçenek | Ölçü | Kriter | Risk |
|---|---|---|---|
| A — Yalnız L3 /VOUT ve /VSAFE | L3 en dar kesiti 6,0 mm; BUS_POWER iç katman alt sınırı 18,364 mm | Hayır | L3, hesaplanan genişliğin %32,7’si; analiz dolgu üzerinde varsayımsal uç via’ları kullanıyor, gerçek yol değil. |
| B — 5,5 mm izi COUT pad sıraları arasından geçirmek | Farklı ağ komşu pad kenar aralığı 1,040 mm; satırlar arası pad boşluğu 1,940 mm | Hayır | Her iki açıklık da 5,5 mm iz için yetersiz. |
| C — Q2’den bankaya düz dış katman bus’ı | Q2 /VOUT padinin batı kenarı x=121,5225 mm; COUT bankasının doğu pad kenarı x=118,625 mm; aralık 2,8975 mm | Hayır | Doğrudan koridor 5,5 mm’ye de sığmıyor. |
| D — Q2’yi 180° çevirip B.Cu dış bus’ları ve güney COUT beslemesi kullanmak | /VOUT 7,0 mm, /VSAFE 5,5 mm; bus’lar arası bakır kenar açıklığı 0,75 mm; güney F.Cu şeridi ile alt COUT pad kenarı arası 0,285 mm | Geometrik ön yerleşim evet; yönlendirme DRC’si bekliyor | Seçilen topoloji. Gate izi, zone bağlantıları, via sığması ve DRC T-022’de gerçek kart üzerinde doğrulanmalı. |

## Öneri

**KOŞULLU — Seçenek D ile T-022 başlayabilir.** Q2’yi 180° çevir; /VOUT’u Q2 drain via’larından B.Cu üzerinden güneye, 7,0 mm F.Cu dağıtım şeridine ve L3’e en az iki 15-via besleme dizisiyle ver. /VSAFE için Q2 source via’larından ayrı 5,5 mm B.Cu omurga kur. Her iki ağın 15-via hedefini tamamla. Q2–U6 gerçek gate izi 10 mm’yi aşarsa veya strict DRC’de yollar sığmazsa yerleşim düzeltmesine dön; netclass/DRC’yi gevşetme.

## Kanıt

- İlk çalışma ağacı: git status -sb → ## main...origin/main, temiz.
- git rev-parse HEAD → 6712c9e40c430afee9728826f2c36bf1e55c8761.
- Başlangıçtaki gh pr view çıktısı → no pull requests found for branch "main" (çıkış kodu 1). gh pr list --head wp/D-010 --state all → boş; dal/PR henüz yoktu.
- kicad-cli version → 10.0.7.
- Salt okunur kaynak çıkarımı: kicad-cli pcb export ipc2581 --output <geçici IPC-2581 dosyası> PDU.kicad_pcb → çıkış kodu 0. Tüm koordinat ve pad ölçü hesapları KiCad’in bu dışa aktarımından, kaynak PCB PDU.kicad_pcb @ 6712c9e üzerinden yapıldı; PCB dosyasına yazılmadı.
- Bu karar sırasında DRC, refill ve parite çalıştırılmadı. Bu bir tamamlanmış rota kabulü değildir. T-022 için KiCad 10.0.7 refill + schematic parity, ayrıca boş kart DRC zorunlu kapıdır.

## Olgular ve bağımsız hesaplar

### Güç hedefleri

reports/g2/PCB-HANDOFF.md:18-30 ve reports/g2/routing-g2.json hedefleri:

| Ağ / sınıf | Dış katman genişliği | Via hedefi | T-022 önerilen katman ve yöntem |
|---|---:|---:|---|
| /VIN, /ANODE — INPUT_POWER | 3,3 mm | 9 | F.Cu ana giriş yolu; gerektiğinde B.Cu geçişi. U1/U2 CIN girişine kısa F.Cu kolları. |
| /VOUT, /VSAFE — BUS_POWER | en az 5,5 mm | en az 15 | /VOUT: Q2 çıkışında B.Cu, bankanın güneyinde 7,0 mm F.Cu şerit ve L3 dağıtımı. /VSAFE: Q2’den ayrı B.Cu 5,5 mm bus, CEFIN uçları. |
| /O1_11V — O1_PORT | 5,3 mm | 19 | F.Cu, konektöre kesintisiz ana yol; katman geçişi gerekiyorsa B.Cu ve via sayısı raporu. |
| /S2E_11V — S2E_PORT | 3,3 mm | 12 | F.Cu ana yol; gerekirse B.Cu geçişi ve raporlanmış via sayısı. |
| /SW_PHx, /ISNSx — PHASE_POWER | 2,6 mm, kısa | 12 | SW: F.Cu’da en kısa anahtarlama çevrimi. ISNS güç segmenti: şönt yolunda 2,6 mm hedef; INA296 girişleri ayrı Kelvin kolları. 12 via hedefinin ağ başına uygulanışı ve SW bakır alanının EMI etkisi route raporunda gerekçelendirilmeli; geniş SW dolgusu varsayılan çözüm değildir. |

Via hedefleri PCB-HANDOFF.md:22-30’daki hesap/varsayımlardır: her via için 0,5 A kabulü, 0,3 mm delik, 20 µm varil kaplaması; üretici kaplama ve termal onayı AÇIK. Genişlikler 1 oz dış bakır hesabına bağlıdır; 1 oz tüm katman üretim onayı Handoff §7’de AÇIK. Bunlar DRC kuralını değiştirme gerekçesi değildir.

### COUT, Q2 çıkışları ve fiziksel sığma

**HESAP — KiCad IPC-2581 geometrisi:** COUT1–32’de 32 adet pin1 /VOUT ve pin2 /GND pad’i vardır; her pad 1,30 × 4,50 mm. Boyutlar RECT_1 pad dikdörtgenlerinin bounding box farkıdır. Komşu farklı ağ padlerinin en küçük kenar aralığı 1,040 mm: COUT5 pin1 ve COUT4 pin2 merkezleri arası 2,340 mm; yarım pad genişlikleri toplamı 1,300 mm; boşluk = 2,340−1,300 = 1,040 mm. Ardışık satırların pad açıklığı 1,940 mm. Dolayısıyla 5,5 mm iz pad aralarından geçirilemez. Önermedeki 32 kapasitör ve 1,3 × 4,5 mm ölçüsü doğrulandı; boşluk 1 mm’ye yakın, fakat bağımsız ölçüm 1,040 mm’dir.

Q2 mevcut drain padinin batı kenarı ile bankanın en doğu pad kenarı arasındaki 2,8975 mm doğrudan aralık da 5,5 mm yolu almıyor. Bu ölçüde kenarlar IPC-2581 pad konturlarının min/max x koordinatlarıdır; nokta/merkez mesafesi değildir. Güney çevresinden dolaşma gerekir.

**/VOUT topolojisi:**
- 32 COUT pin1 padini L3 /VOUT’a via-in-pad ile bağla. COUT pin2 GND’lerini yerel L2 dönüşlerine bağla.
- Q2 drain pad 5’te via dizisini 9’dan 15’e tamamla: 5×3 dizi, via merkez adımı 0,75 mm, land 0,60 mm; dış zarf 3,60 × 2,10 mm. Pad 4,295 × 4,510 mm olduğundan merkezli dizide kalan kenar payları yatay 0,3475 mm, dikey 1,205 mm. Mevcut 9 via + 6 ilave = 15.
- Q2’den B.Cu’da 7,0 mm /VOUT bus’ı güneye indir; bankanın altından 7,0 mm F.Cu dağıtım şeridine bağla. En az iki ayrı 5×3 via dizisini L3 /VOUT’a yerleştir; böylece akım L3’e yalnız Q2 yanındaki 6 mm raster boğazından girmeye zorlanmaz. Her dizi başına 15 via, BUS_POWER 15-via hedefini karşılayan planlama hedefidir.
- Güney şerit merkezi y=−86,5 mm, genişliği 7,0 mm alınırsa üst kenarı −83,0 mm’dir. En güney COUT pad kenarı −82,715 mm olduğundan açıklık 0,285 mm olur. Bu, Handoff DFM varsayımındaki 0,15 mm açıklığın üstündedir; kalan marj yalnız 0,135 mm’dir. Pad çevresindeki gerçek zone, via ve DRC geometrisiyle doğrulanmalı.
- 5×3 dağıtım dizisi için örnek via merkezleri x=90,00…93,00 mm (0,75 mm adım), y=−86,15…−84,65 mm (0,75 mm adım): via land zarfı 3,60 × 2,10 mm’dir. Bu yalnız geometrik adaydır; KiCad zone sınırı/clearance ve DRC geçişi değildir.

**/VSAFE ve Q2 yönü:**
- Q2 source pin1–3 padleri 0,75 × 0,66 mm; mevcut source vias 3, drain vias 9’dur. Önermedeki 0,75 × 0,66 ve 9/3/15 sayıları doğrulandı. Bir adet 0,60 mm via land pad içinde yalnız 0,075 mm ve 0,030 mm kenar payı bırakır; ilave via’ları küçük pad içine sığdırma. Via-in-pad üretim onayı da yoktur.
- /VSAFE B.Cu bus merkezi x=129,5 mm, genişlik 5,5 mm (kenarlar 126,75–132,25 mm). Q2 180° sonrası source via sütunu x=126,7475 mm; via land bus’la yaklaşık 0,30 mm bindir, bilerek aynı net bağlantısı kurar. /VOUT merkezi x=122,5 mm, genişlik 7,0 mm (kenarlar 119,0–126,0); source via landinin en batı kenarı x=126,4475 mm ile /VOUT bakırı arasında 0,4475 mm açıklık kalır. İki bus bakır kenarı arasında 0,75 mm olur.
- Q2 source bus’ına 4×3 diziyle 12 ilave 0,6/0,3 mm via ekle; üç mevcut source via ile toplam 15. 0,75 mm adımda dizi zarfı 2,85 × 2,10 mm’dir; bus ölçülerine sığdığı geometrik olarak hesaplanır. Dizi konumu zone, keepout, DRC ve gerçek bağlantıyla T-022’de sınanmalı.
- 180° dönüş sonrası U6 pad6 ile Q2 gate pad4 merkezleri arası 9,132 mm. Drain padı ve 0,15 mm açıklık etrafındaki tahmini kısa poliline 9,33 mm; 10 mm sınırına tahmini pay 0,67 mm. Bu bir merkez/engel hesabıdır, gerçek iz değildir. Q2 dönüşü önerilir: iki geniş bus’ı ayırır; R-016’daki “önceden çevirmek gerekmiyor” sonucu rotasız ve 5,5 mm bus’lar seçilmeden verilmişti. T-022 gerçek gate izini ölçerek ≤10 mm’yi kanıtlamalı; geçmezse yön/yerleşimi tekrar ele almalı.

### /VSAFE ve /VOUT L3 sınırları

reports/g5/T-021/q2-path.json ve zones-review.md:53-78: L3 raster boğazı 6,0 mm, BUS_POWER iç katman alt sınırı 18,364 mm, Q2 /VOUT vias 9, /VSAFE vias 3, hedef 15; en uzun varsayımsal COUT raster yolu 75,3 mm. Bağımsız incelemedeki 5,8 mm kesit, kaynak pad merkezleri hizasındaki gerçek dolgu dilimi; q2-path 6,0 mm raster/clearance ölçüsüyle aynı metrik değil. 5,8 mm, 6,0 mm ve 18,364 mm’nin hepsi 5,5 mm dış katman hedefinden farklı ölçülerdir. T-021 analizi gerçek iz değildir ve uç via’ları varsayar. Önermedeki 6,0 mm, 18,36 mm ve 9/3/15 doğrulandı. Tasarlanan dış bus’lar L3 boğazını tek geçiş yolu olmaktan çıkarır; L3 dağıtımı ve akım paylaşımı yine DRC/elektrik/termal kanıt ister.

### C düzeni CIN dönüşü ve sıcak döngü

IPC-2581 pad merkezleri ve mevcut GND via merkezlerinden HESAP: U1 doğu/uzak CIN3/4 GND merkezleri (84,55;−43,175) ve (88,10;−43,175), en yakın L2 GND via merkezlerine uzaklık yaklaşık 7,226 mm; U2 doğu/uzak CIN7/8 GND merkezleri (58,95;−102,825) ve (55,40;−102,825), en yakın via’ya yaklaşık 9,868 mm. Merkez uzaklığı, döngü uzunluğu değildir. Her dört uzak GND padine bir L2 GND via’yı pad merkezinden ≤1,0 mm uzağa koy; mümkün değilse pad içinde via ancak filled/capped üretim onayıyla. Via ve anti-pad’lerin L2 GND’yi kesme etkisi DRC/refill sonrasında incelenmeli.

VIN–CIN–PGND döngü alanı rotadan önce sayısallaştırılamaz. T-022 sonrası her buck için ayrı ayrı: U VIN padinden CIN VIN’e gerçek F.Cu iz/arc merkez hattını çıkar; PGND akım dönüşünün gerçek L2 via’larını ve çözümlenmiş dönüş akımı merkez çizgisini belirle; dönüş yolunu aynı XY düzlemine izdüşürüp ileri ve dönüş yoluyla kapalı poligon oluştur; alanı shoelace formülüyle mm² hesapla. Akım çözümü yoksa “geometrik yaklaşık” diye etiketle; pad merkezleri veya L2 zone sınırları döngü alanı yerine kullanılmamalı. VIN–CIN–PGND prompt konusu ölçüm yöntemiyle yanıtlandı; mevcut kart için gerçek döngü alanı doğrulanamadı.

### Ölçüm uçları, Kelvin ve ağ tap’leri

Handoff §3 ve tasks/backlog.md:17 güç ölçüm uçlarının sınıf min genişlikleriyle çakıştığını bildiriyor. Öncelik: ölçüm padini aynı ağın güç zone’una kısa, dar bir kol ile bağla; geniş BUS_POWER izini pad’e boğazlatma. INA296 sense padleri şöntün iki terminalinden ayrı Kelvin kollarıyla alınmalı; yük akımı sense kolundan geçmemeli. U11 pin8 /ISNS1 ve RS1 pin1 aynı ağ; U11 pin1 ve RS1 pin2 /VOUT. U12/RS2 eşleşmesi aynıdır (net bağlantısı şema/PCB net tablosuyla T-022 raporunda yeniden doğrulansın). Uç izi için 0,25 mm yalnız başlangıç hedefidir ve HANDOFF §2 ANALOG min’ine dayanır; iz kısa (≤15 mm) ve ana akım izinden ayrık tutulmalı. KiCad zone-tap bağlantısı mevcut DRC’yi geçmezse ölçüm ucunu/zone bağlantı yerini düzelt; netclass, genel DRC veya geniş kapsamlı muafiyetle çözme. Net/obje UUID’sine özel istisna ancak T-022 kabul kriterine uygun, dar ve kanıtlı gerekçe ile raporlanabilir.

## Kaynaklar

- HANDOFF.md §§1–4, §7 — stackup, güç yolu/akım varsayımları, CIN yerleşimi ve DFM.
- reports/g2/PCB-HANDOFF.md:18-30, 32-48, 60 — netclass genişlik/via hedefleri, güç akışı ve DFM varsayımları.
- reports/g2/routing-g2.json — seçilmiş sınıf hedefleri ve hesap girdileri.
- tasks/T-022.md — T-022 kabul kriterleri ve stop koşulu.
- reports/g5/T-021/q2-path.json, reports/g5/T-021/zones-review.md:53-86 — raster analizinin sınırları, L3 boğazı/via sayıları, east CIN dönüşü devri.
- reviews/R-016.md:73-92 — önceki Q2 yön kararının varsayımsal sınırları ve gate merkez mesafeleri.
- tasks/backlog.md:17 — ölçüm uçları sorunu.
- PDU.kicad_pcb @ 6712c9e, KiCad IPC-2581 export — component/refdes, pad number, nets, pad geometry, zone polygon and coordinates used by independent calculations.

## Açık varsayımlar

- 1 oz all-layer copper, via barrel plating and filled/capped via-in-pad manufacturer approval.
- Via bank effective current sharing and inner-layer thermal behavior.
- B.Cu bus and south F.Cu stripe clearances remain valid after KiCad zone refill and via-in-pad insertion.
- Two or more distributed via banks spread current acceptably into L3.
- A short 0.25 mm Kelvin spur of at most 15 mm preserves measurement accuracy and passes the analog design rules.
- DRC will accept 0.285 mm southern clearance after via-in-pad pads and zone refill.
- Gate route bends and width can fit under 10 mm actual centerline length.

## Doğrulanamayanlar

- Real KiCad track and zone connectivity, refill, clearance, empty-board DRC and schematic parity; there is no route yet.
- Actual route performance, 7.5 A rise, 50 mV drop, loop area, Kelvin behavior and DRC/parity as stated above.
- Production viability of via-in-pad and exact stackup.
