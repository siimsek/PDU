# D-011 — Q2 yönü ve /VOUT bankaya bağlantı

- **Kart:** tasks/D-011.md
- **Yazan:** Codex (THINKER), 2026-11-08
- **Fiziksel iş gerekli mi:** Hayır

## Soru

T-022’de D-010’un 180° Q2 ve güney /VOUT şeridi önerisi DRC ile durduktan sonra, hangi Q2 yönü ve çıkış topolojisi BUS_POWER 5,5 mm / 15 via hedefini, HANDOFF bankanın ortasına besleme niyetini ve ≤10 mm gate yolunu netclass veya DRC gevşetmeden karşılar? Seçim ayrıca mevcut Q2 via-in-pad alanlarını, L3 zone geometrisini ve T-022 izinlerini kapsamalıdır.

## Seçenekler

| Seçenek | Ölçülen kanıt | Kriter | Risk / değerlendirme |
|---|---|---|---|
| A — Q2 180°, U6 yerinde | DRC temiz gate yolu 11,562 mm; sınır 10 mm. | Hayır | 1,562 mm yol azaltımı gerekir. U6 taşıma denenmedi. |
| B — Q2 180°, U6’yi taşı | Mevcut sabit U6 ile gate 11,562 mm. U6 taşıma koordinatı/DRC denemesi yok. | Doğrulanamadı | Ek bileşen/zone/decoupling etkileşimi bilinmiyor; 90° çalışan deneme varken seçilmedi. |
| C — Q2 90°, iki ayrı B.Cu bara ve bankanın ortasındaki COUT via-in-pad ucu | Gate 5,469 mm; /VOUT B.Cu 7,0 mm, bank orta waypoint’ine 46,8 mm; COUT20 pin1 via-in-pad ucuna devam eden aday 50,154 mm; /VSAFE B.Cu 5,5 mm ve 23,5 mm. Q2 yanında 20 ilave via: 8 drain + 12 source. | Sığma kapısından koşullu geçer | Probe hatasız DRC/parite verse de kaynak L3 zone’u bu yönde via alanını kaplamaz; uyarılar ve bitmemiş uçlar çözülmeli. Önerilen. |
| D — Q2 180°, güney F.Cu şeridi | 7,0 mm şerit 1 kısa devre + 5 maske köprüsü; 5,5 mm örnek şerit 0 DRC hatası. | 7,0 mm hayır; 5,5 mm yalnız tekil deneme | 180° gate yine 11,562 mm. Güney şerit HANDOFF §3.3’teki orta-bankaya besleme niyetinin yerine kabul edilmedi. |

## Öneri

**KOŞULLU — Q2’yi 90° döndür ve Seçenek C ile T-022’ye devam et.** U6’yi taşımadan gate izi 5,469 mm’dir. /VOUT’u 7,0 mm B.Cu ile COUT bankasının orta bölgesindeki bir /VOUT via-in-pad ucuna bağla; 32 COUT pin1 via-in-pad noktasını L3’e dağıt. /VSAFE’te mevcut üç kaynak via-in-pad’i koru, 12 ek via’yı yeni Q2 yönünde L3 /VSAFE’ye bağlanan yerleşime koy. T-022 kartı bu Q2/zone değişikliğini açıkça izinli kılmalı. DRC hatasız geçici deneme bitmiş route veya tamamlanmış bağlantı kanıtı değildir; zone refill, dangling/unconnected temizliği, eFuse/COUT/Kelvin bağlantıları ve üretim onayı kapanmadan T-022 tamamlanmış sayılmaz.

## Kanıt

### Başlangıç provenansı ve istenen komut çıktıları

Ayrı klon C:\work\PDU-D011-20261108 içindeki başlangıç durumu:

- git status -sb → ## main...origin/main, temiz.
- git rev-parse HEAD çıktısı: 0864afe384603f8244ca0459e1f8e52275adea79.
- gh pr view 66 --repo siimsek/PDU çıktısı:

> title: T-022: D-010 durdurma kanıtı (Q2 yönü kararı bekliyor)
> state: DRAFT
> author: siimsek (Muhammed Ali Şimşek)
> labels:
> assignees:
> reviewers:
> projects:
> milestone:
> number: 66
> url: https://github.com/siimsek/PDU/pull/66
> additions: 496
> deletions: 8
> auto-merge: disabled
> --
> T-022 durduruldu: D-010'un durdurma koşulu gerçek DRC ile tetiklendi. Güç yolu çizilmedi, PDU.kicad_pcb değişmedi.
>
> Q2 180°: DRC temiz en kısa gate izi 11,562 mm (sınır 10 mm).
> D-010 güney şeridi 7,0 mm: TP_VSAFE ile kısa devre + 5 maske köprüsü. 5,5 mm şerit temiz.
> Q2 90° adayı: gate 5,469 mm, iki B.Cu bara ve 20 ek via ile 0 DRC hatası, parite 0. Yalnız sığma kanıtıdır, bitmiş rota değildir.
>
> Kanıt: reports/g5/T-022/D-010-fit-stop.md, q2-fit-probe.json. Q2 yönü için THINKER kararı (D-011) bekleniyor. Birleştirilmeyecek; T-022 aynı dalda sürecek.

- gh pr view --json çıktısı PR #66 açık taslak, base main @ 0864afe384603f8244ca0459e1f8e52275adea79, head wp/T-022 @ 0df40883fb982f3137ab2d50117740745defcb2e, URL https://github.com/siimsek/PDU/pull/66.
- PR farkında PDU.kicad_pcb değişikliği yoktu; kartın değişmediği iddiası git diff origin/main...HEAD -- PDU.kicad_pcb ile de doğrulandı.
- Yerel kicad-cli version → 10.0.7. PDU.kicad_pcb’den salt-okunur IPC-2581 dışa aktarımı çıkış kodu 0 verdi; board XML geçici dizine yazıldı, kaynak PCB değişmedi.
- Probe, KiCad 10.0.7 bundled Python ile ayrı geçici board kopyalarında yeniden çalıştırıldı. Kaynak probe ayrıca her senaryoda pcb drc --severity-all --refill-zones --schematic-parity çağırıyor. Çıktıdaki hata ve parity sayıları BUILDER JSON’ıyla senaryo senaryo eşleşti.
- Bu karar dalı için rapor/sonuç dosyası üretilmedi; geçici deneme dosyaları çalışma alanı dışındaydı.

### Bağımsız geometri ve hesaplar

Koordinatlar KiCad 10.0.7 IPC-2581 exportundaki Q2/U6 component ve pin Pad konumlarından hesaplandı. D-006 koordinat dönüşümü probe kodundaki kp/d6 formülüyle aynıdır (reports/g5/T-022/q2_fit_probe.py:27-37); ölçülen kart PDU.kicad_pcb @ 0df4088’dir.

| Ölçü | Bağımsız sonuç | Kaynak / hesap |
|---|---:|---|
| U6 pin6 merkezi | (93,7325; 47,4900) mm D-006 | IPC-2581 Pad/PinRef ve U6 Component Location |
| Q2 anchor | (93,9950; 54,2050) mm D-006 | IPC-2581 Q2 Component Location |
| Q2 pin4 gate merkezi, 0° | (91,2425; 52,3000) mm | IPC-2581 pin4 Pad; center distance to U6 pin6 = 5,416 mm |
| Q2 pin4, 90° | (95,9000; 51,4525) mm | Rigid transform of pin4 about Q2 anchor; center distance to U6 pin6 = 4,517 mm |
| Q2 pin4, 180° | (96,7475; 56,1100) mm | Same transform; center distance to U6 pin6 = 9,132 mm |

Merkez uzaklıkları iz uzunluğu değildir. Probe’nin route waypoints’lerinden bağımsız Euclidean centerline toplamları:
- 90° gate: 1,067 + 1,599 + 2,803 = 5,469 mm.
- 180° gate, clear route x=97,90: 1,067 + 5,108 + 4,170 + 1,217 = 11,562 mm.
- 180° x=97,55 denemesi 11,033 mm; daha kısa rota source-via çevresinde üç clearance hatası verdi.
- 90° B.Cu bus waypoints: /VOUT 8,0 + 11,3 + 27,5 = 46,8 mm; /VSAFE 6,5 + 7,5 + 9,5 = 23,5 mm. Bunlar probe centerline uzunluklarıdır, kapasitör/eFuse uç bağlantısı tamamlanmış uzunluk değildir.
- Q2 180°’de 10 mm kriterine göre gereken minimum yol kısalması 11,562−10 = 1,562 mm’dir. U6’yi taşımanın ne kadar hareket gerektireceği veya diğer parçalarla sığması **doğrulanamadı**.

COUT component merkezlerinin IPC-2581 konum ortalaması (56,785; 44,195) mm D-006’dır. Probe bank waypoint’i (57,0; 44,2) bu ortalamadan 0,215 mm uzaktadır. En yakın orta-banka /VOUT pad ucu COUT20 pin1 (57,955; 47,415) mm; banka merkezine 3,426 mm’dir. Probe yolunu bu pin1 ucuna 7,0 mm B.Cu ile uzatan geçici DRC denemesinde toplam /VOUT centerline 50,154 mm oldu.

### Via sayısı ve pad sığması

- IPC-2581 In2.Cu /VOUT via padleri mevcut Q2 drain üzerinde 3×3, 1,2 mm adımlı dokuz via; /VSAFE source padlerinde üç via gösteriyor. Bu sayılar reports/g5/T-021/zones-review.md:38, 76 ile aynı.
- 90° probe sekiz drain via’sını ve 12 source via’sını açık koordinat listeleriyle ekliyor (reports/g5/T-022/q2_fit_probe.py:81-83, 94-99). Toplam 20 yeni via; Q2 drain 9+8=17, source 3+12=15. Test edilen sekiz drain via merkezi ile döndürülmüş mevcut 3×3 grup arasındaki en küçük merkez uzaklığı 0,8485 mm’dir; via land çapı 0,60 mm olduğundan bu iki grup fiziksel olarak üst üste binmiyor.
- D-010 karar notu:57, pin5 merkezli 5×3 dizinin adımını 0,75 mm olarak verir. Eski 3×3 grubun merkez via’sı pin5 merkezindedir; pad merkezli 5×3’ün orta via’sı da aynı noktaya düşer. Böyle yorumlandığında merkez uzaklığı 0 mm, yani çakışır. D-010 bir 5×3 XY listesi vermediği için başka offset yerleşimin çakışmadığı **doğrulanamadı**. PR #66 fit raporu:34’teki “noktalar aynı değil” gerekçesi fiziksel via-land çakışmasını kanıtlamaz ve merkez noktasında mevcut geometriyle çelişir. Bu nedenle “9+6=15” uygulaması reddedildi; DRC denemesinde ayrı 8 via eklenerek 17 drain via kullanıldı.
- Source pad RECT ölçüsü IPC-2581’den 0,75×0,66 mm; mevcut via land 0,60 mm. Merkezli tek via’nın kenar payı yatay 0,075 mm, dikey 0,030 mm’dir. 90° probe mevcut source via-in-pad’leri Q2 ile döndürüp aynı B.Cu /VSAFE baraya bağlayınca hata üretmedi. PDU.kicad_dru:41-42 diğer ağlara karşı HV track/zone açıklığını 0,6 mm belirtiyor; bu kural değiştirilmedi.
- Karar: üç mevcut source via-in-pad’i koru; 12 ek source transfer via’sını aynı-net B.Cu baraya bağla ve L3 /VSAFE bağlantısını yeniden çizilmiş zone ile çöz. Pad dışına F.Cu fanout, 0,6 mm HV açıklığıyla denenmedi. Via-in-pad üretici filled/capped onayı Handoff §7’de varsayım olarak kalıyor.

### Probe sonuçlarının karşılaştırması

Bağımsız geometrik hesaplardan sonra reports/g5/T-022/q2-fit-probe.json ile karşılaştırıldı ve probe KiCad 10.0.7 ile ayrıca çalıştırıldı:

| Senaryo | Yeniden çalıştırılan sonuç | Değerlendirme |
|---|---|---|
| 0 deg unchanged baseline | No tracks; 0 DRC errors; parity 0 | Matches; baseline only. |
| Q2 180 deg gate x=97.55 | 11.033 mm; 3 clearance errors; parity 0 | Matches; shorter candidate has clearance errors. |
| 180° gate x=97,90 | 11,562 mm; 0 hata; parity 0 | Prompt ve PR raporuyla eşleşti; 10 mm sınırını aşar. |
| 90° gate | 5,469 mm; 0 hata; parity 0 | Eşleşti; ölçülen route sınırın 4,531 mm altındadır. |
| 7,0 mm güney F.Cu şeridi | 6 hata: TP_VSAFE kısa devresi + 5 solder-mask bridge | Eşleşti; seçilmedi. |
| 5,5 mm güney F.Cu şeridi | 0 hata; parity 0 | Eşleşti; tekil şerit denemesi, 180° gate sorununu çözmez. |
| 90° gate + B.Cu 7,0 /VOUT + B.Cu 5,5 /VSAFE + 20 via | 0 hata; parity 0; /VOUT 46,8 mm, /VSAFE 23,5 mm | Eşleşti; bitmiş bağlantı değil. |

“Hata 0” bu probe’larda “uyarı yok” anlamına gelmiyor. 90° bus senaryosunda KiCad uyarıları: 12 via_dangling, 2 track_dangling, 1 isolated_copper, 38 lib_footprint_issues. Probe açıklaması unconnected_items’ın beklenen olduğunu ve sayılmadığını söyler (q2_fit_probe.py:1-5, 117-124). Dolayısıyla parity 0 ve error 0, akım yolunun uçtan uca bağlı olduğunu kanıtlamaz.

### Orta-banka via alanı ve seçilen topoloji

- HESAP: 32 COUT’un center-location ortalaması üzerinden 5×3 via dizisi denendi: x=55,5…58,5 mm, y=43,45…44,95 mm D-006; via land 0,6 mm, pitch 0,75 mm. Bu diziyi tam bank waypoint’inde /VOUT geçişi olarak ekleyen geçici KiCad DRC denemesi 12 hata verdi: COUT2 ve COUT27 /GND padleriyle 4 kısa devre, 4 hole-clearance ve 4 solder-mask bridge. Bu koordinatta 15’li via bankı kullanılamaz.
- HESAP + geçici KiCad DRC: 32 COUT pin1 padinin her birine 0,6 mm /VOUT via-in-pad ekleyip B.Cu yolunu COUT20 pin1’e bağlama denemesinde 0 hata, parity 0 çıktı. Uyarılar yine 12 via_dangling, 1 track_dangling, 1 isolated_copper ve 38 lib_footprint_issues olarak kaldı; gerçek CEFIN uç bağlantısı yoktu. Öneri, bank ortasına 15’li array yerleştirmek değil, bank ortasına yakın COUT20 /VOUT via-in-pad noktasını ana B.Cu besleme ucu yapmaktır. 32 kapasitör via-in-pad üretim onayı gerektirir.
- T-021 L3_VOUT polygonunda COUT20 pin1 ucu ve önerilen COUT pad noktaları bulunuyor. Test edilen Q2 90° drain via noktalarının 15/17’sinin merkezi mevcut /VOUT polygonu içinde; iki probe via merkezi dışında kalıyor. Bu 2 nokta yer değiştirilmeli veya yerel zone sınırı dikkatlice düzenlenmeli; tüm L3-VOUT katmanını yeniden tasarlama zorunluluğu bu ölçümle kanıtlanmadı.
- T-021 L3_VSAFE polygonunda 90° source padleri + probe’un 12 ek source via merkezinin 0/15’i bulunuyor. Yani eski Q2 0° cebi bu via düzenine L3 bağlantısı vermiyor. Probe’da görülen 12 via dangling uyarısı bununla tutarlıdır. T-022, local L3_VSAFE bölgesini 90° çıkışlarına göre yeniden çizip doğu/eFuse dökümüne kesintisiz bağlamalı veya via grubunu başka gerçek, clearance’ı kanıtlanmış bölgeye taşımalıdır.
- Ek denemede 12 /VSAFE via’yı (107,0…109,25; 40,75…42,25) mm D-006 alanda U4 yakınında, 15 /VOUT via’yı bank merkezinde yerleştirme 38 DRC hatası verdi (8 clearance, 6 shorting, 17 hole_clearance, 7 solder_mask_bridge; toplam hata adedi üst üste binen issue kayıtlarını da sayar). Bu yalnız bu denenen eFuse array konumunu reddeder; tüm eFuse alanının imkânsız olduğunu kanıtlamaz.

### D-010’un kalan geçerliliği

- **Geçerli:** BUS_POWER dış iz hedefi en az 5,5 mm ve via hesabı en az 15; 7,5 A ve 0,5 A/via varsayımı HESAP/VARSAYIM niteliğindedir (reports/g2/PCB-HANDOFF.md:22-30). Netclass veya DRC gevşetilmez. 32 COUT pin1’in L3 /VOUT’a bağlantısı, COUT GND dönüşü, doğu CIN yerel L2 dönüşleri, gerçek VIN–CIN–PGND loop-area ölçümü, Kelvin ayrımı ve tüm T-022 DRC/parite kapıları geçerlidir.
- **Geçersiz:** Q2 180° yönü (gate 11,562 mm), güney 7,0 mm F.Cu şerit (TP_VSAFE kısa devresi) ve D-010’un güney şerit topolojisi.
- **Düzeltilmesi gereken:** D-010’daki 5×3 / “9+6” Q2 drain hesabı, mevcut 3×3 pad-merkez via’sıyla örtüşüyor; testte kullanılan 8 ayrı drain via düzeni ve toplam 17 daha iyi kanıta sahiptir. 15’li via dizisi tam COUT bank merkezine konamaz; DRC denemesi pad ihlali verdi.

### T-022 kartı için gereken metin

tasks/T-022.md izinli yollarında PDU.kicad_pcb zaten var; fakat zone üretim betiği ve Q2 yerleşim değişikliği açık yazılmamış. Kart kapsamı şu şekilde netleştirilsin:

> D-011 kararıyla Q2’yi 90° döndürmek, Q2 ile taşınan mevcut via-in-pad konumlarını yeniden yerleştirmek ve bu yön için yerel L3_VOUT/L3_VSAFE zone konturlarını değiştirmek T-022 kapsamındadır. Gerekirse scripts/pcb_zones.py veya yeni açıkça adlandırılmış zone betiği izinli yazma yollarına eklenir. Board outline, H1–H4, kenar konnektörleri, ağ adları, katman sırası, netclass ve genel DRC değişmez; L2 GND sürekliliği korunur. Zone refill sonrası VOUT/VSAFE via’ları, COUT/CEFIN uçları, HV clearance, gate izi, tüm dangling/unconnected uyarıları ve schematic parity raporlanır. Bir hata veya bağlantısız uç bırakılırsa rota tamamlandı sayılmaz.

## Açık varsayımlar

- **VARSAYIM:** Q2 90° konumunda local L3_VSAFE polygonu, diğer net ve U6 gate çevresindeki 0,6 mm HV açıklığını koruyarak bağlanabilir; T-022’de refill/DRC ile sınanmalı.
- **VARSAYIM:** BUS_POWER 7,0 mm B.Cu /VOUT ve 5,5 mm B.Cu /VSAFE test merkez hatları, gerçek uçlara yönlendirilince mevcut L2 GND referansını kabul edilebilir biçimde korur.
- **VARSAYIM:** COUT via-in-pad ve Q2 source via-in-pad için 0,6/0,3 mm via filled/capped üretim yöntemi kabul edilir; üretici teyidi gerekir.
- **VARSAYIM:** 17 drain via ve 15 source via akım paylaşımı 7,5 A çalışma için yeterlidir; üretim kaplama, termal model ve gerçek güç testi bunun yerine geçmez.

## Doğrulanamayanlar

- EFuse/COUT, Kelvin, ölçüm uçları ve gerçek load connection dahil tamamlanmış T-022 rotası; mevcut probe ara bağlantı/sığma denemesidir.
- Q2’nin 90° yönündeki yeni L3_VSAFE polygonunun final refill/strict DRC/parite sonucu.
- 12 source via alanının yeni zone’da bağlantı ve clearance sonucu; 0° zone testinde 0/15 via merkezi örtülür.
- Her iki buck’ın VIN–CIN–PGND gerçek akım dönüşü ve loop mm²; henüz route/akım yoğunluğu çözümü yok.
- 1 oz tüm katman, 20 µm barrel plate ve filled/capped via-in-pad için fab onayı.
- U6 taşımalı 180° alternatifin gerçek yerleşim/iz/DRC sonucu.

## Kaynaklar

- PR #66: dal wp/T-022 @ 0df40883fb982f3137ab2d50117740745defcb2e; main @ 0864afe384603f8244ca0459e1f8e52275adea79.
- reports/g5/T-022/D-010-fit-stop.md:3-38; reports/g5/T-022/q2_fit_probe.py:1-5, 19-38, 40-83, 86-123; reports/g5/T-022/q2-fit-probe.json:5-306.
- HANDOFF.md:5, 8, 29; reports/g2/PCB-HANDOFF.md:22-30, 36-38; tasks/T-022.md:21-46.
- PDU.kicad_dru:41-44; reports/g5/T-021/zones-review.md:21-24, 38, 51, 76-86.
- decisions/D-010-power-routing.md:57-66; KiCad 10.0.7 IPC-2581 export of PDU.kicad_pcb at the verified PR base.
- Probe DRC and the extra via-array/COUT-via test outputs were generated by KiCad 10.0.7 on temporary board copies; they were not written into the repository.
