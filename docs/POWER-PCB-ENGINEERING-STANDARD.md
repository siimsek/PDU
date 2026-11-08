<!-- Bu başlık T-026 ile eklendi. Aşağıdaki "KAYNAK METİN" işaretinden sonrası kaynakla bayt bayt aynıdır. -->
# Güç PCB'si Mühendislik Standardı — kalıcı kopya

- **Kaynak:** [`decisions/R-020-engineering-standard-source.md`](../decisions/R-020-engineering-standard-source.md), SHA-256 `5c03f55e43b985e87191ea46efc52dc3321ad9b196f42ecd7bb8056901c9fcfe`, 32155 bayt.
- **Geçerli sürüm:** Standart 1.0 (2026-11-08). Değişiklik yalnız yeni kaynak, D-kararı ve ayrı kartla yapılır; bu kopya elle düzeltilmez.
- **Zorunluluk:** Bu andan sonraki bütün şematik ve PCB aşamaları bu standarda uyar. Kaynak metnin "İlk uygulama" ve §5 bölümleri R-020 anına ait anlık görüntüdür; açılışta repo durumuyla doğrulanır.
- **Çelişki kuralı:** Standart ile mevcut sert kriterler ayrışırsa **daha kısıtlayıcı olan** uygulanır; eşik gevşetilmez, fark D-kararına taşınır.

## T-026 çelişki taraması

| Konu | Standart | Repo | Karar |
|---|---|---|---|
| İnceleme kararının adı | `ONAY / KOŞULLU / RET` (§5, "RED kullanılıyorsa şablon esas") | `RED` (`reviews/TEMPLATE.md`, `docs/WORKFLOW.md`) | `RED` kullanılır; standardın kendi kuralı |
| Sinyal/gate sınıf adları | `ANALOG` 0,25, `GATE` ≥0,4 (§1) | Netclass adları `CONTROL_SENSE` 0,25 ve `AUX_LOCAL` 0,5; `PCB-HANDOFF` §2 `GATE` 0,4 | Çelişki yok, ad farkı; ölçü olarak daha kısıtlayıcı olan geçerli, netclass değişmez |
| Sert elektrik sınırları (E-01…E-06) | O1 ≤12,0 V; bara ≤11,1605 V; bara min ≥10,78 V; U3/U4 IN <30 V; HV 0,6 mm; gate ≤10 mm; Kelvin ≤15 mm | `CLAUDE.md`, `AGENTS.md`, `PDU.kicad_dru`, `tasks/T-023.md` ile aynı | Çelişki yok |
| Dış katman min/seçili genişlik (§1 tablo) | 2,94/3,3; 4,92/5,5; 2,35/2,6; 4,76/5,3; 2,97/3,3 | `reports/g2/routing-g2.json`, `PDU.kicad_dru` | Çelişki yok; standart yine de işe başlarken yeniden okumayı ister |
| Ara adımda açık uçlar (§4 G5) | Ara kartlarda izinli, nihai kartta 0 | `T-022` ve `T-023` devir listeleri, `T-024` kabulü | Çelişki yok |
| `via_dangling` uyarıları (§4) | UUID/net/koordinat/gerekçe ile tek tek | T-022 raporu tür ve sayı verir; UUID düzeyi yok | **Eksik:** T-023 kapanışı ve T-024'te tamamlanır, kural gevşetilmez |

---- KAYNAK METİN ----

# PDU — AI Destekli Şematik, Güç PCB'si ve Doğrulama Mühendisliği Standardı

> **Sürüm:** 1.0 — 2026-11-08  
> **Hedef repo:** `siimsek/PDU`  
> **Kullanım:** Bu belgeyi Claude Code'un verdiği `SONRAKİ PROMPT → Codex` metniyle **birlikte** Codex'e ver. Bu bir talimat eki ve kalıcı standart adayıdır; GitHub'daki bir dosyanın zaten oluşturulduğunu **iddia etmez**.  
> **İlk uygulama:** R-020 / T-023 adım 2 incelemesi; sonra şematik + PCB bütünsel denetim ve repoya kalıcı entegrasyon.  
> **Kapsam:** Şematik → parça seçimi → hesap → SPICE → footprint/pin → placement → routing → DFM/termal/EMI → test → fiziksel kabul.

## 0. ÇALIŞTIRMA SÖZLEŞMESİ — HER İKİ AJAN İÇİN ZORUNLU

1. **Tek geçerli gerçek, o oturumda doğrulanan repo durumu ve birincil teknik belgedir.** Bu belge ile gelen commit/PR/sayısal bilgiler kontrol edilecek; farklıysa doğrulanan gerçek esas alınacak. Önce `git status -sb`, `git rev-parse HEAD`, ilgili `gh pr view`, `AGENTS.md`/`CLAUDE.md`, `docs/WORKFLOW.md`, `docs/START-HERE.md`, `HANDOFF.md`, ilgili kart ve dosya/satır kanıtı. Çalışma dalı, güncel/remote HEAD, dirty state, izinler raporlanacak.
2. **Rolleri ve izinleri bozma.** Codex = THINKER (bağımsız analiz, R/D notu, izinli T taslağı); Claude Code = BUILDER (kartın izin verdiği dosyalarda değişiklik, test, commit/PR). `main`'e doğrudan yazma, force push, gizli kanıt silme, otomatik kural gevşetme, kart dışı değişiklik yasak. Ayrı klonda ve temiz iş ağacında çalış; KiCad GUI üzerinden kaydetme. Bağımsız inceleme hesabı BUILDER raporundan kopyalanmaz.
3. **Kaynak derecelendirmesi:** `[DATASHEET: üretici, rev, sayfa/şekil, URL]`, `[HESAP: girdiler/formül/birim]`, `[KOMUT: sürüm/HEAD/çıktı]`, `[SİM: model/senaryo/sonuç]`, `[VARSAYIM]`, `[AÇIK: doğrulanamadı]`, `[TEZGAH]`. `PASS` yalnız ilgili kriter ve test gerçekten karşılandıysa. Tipik değer garantili maksimum değildir; SPICE/DRC fiziksel doğrulama değildir.
4. **Kritik tasarım koşullarını sessizce değiştirme.** Bir üretici önerisi mevcut tasarımla çelişirse önce uygulanabilirliğini, topoloji farkını, kazanımı ve düzeltmenin diğer kritik kurallara etkisini değerlendir; gerekiyorsa D-kararı ve ayrı küçük T-kartı. Sonuçsuz kıyaslamayı 'zorunlu değişiklik' diye sunma.
5. **Önce R-020 kapsamını sonuçlandır.** Bu standardın şematik/termal/tüm kart denetimi **R-020'nin altı kararını gölgeleyip geciktirmemeli**. R-020 kapsamı dışındaki tespitleri risk/kanıt ile backlog'a veya ayrı denetim kartına taşı. R-020 kararını, R-020'ye ait kanıtlardan ver. Böylece koşullu onay ile tüm kart/üretim onayını karıştırma.
6. **Kalıcı entegrasyon şartı:** Bu dosyanın içerik ve kaynaklarını Codex'in izinli `decisions/` veya `tasks/` çıktısında ulaşılabilir biçimde koru; standart dosyası kullanıcı eki olarak kalıp kaybolmasın. Codex, `docs/`'a **yazmayacak**; bunun için izinli yazma yolları olan küçük bir BUILDER T-kartı taslağı açacak. Claude, o kart kapsamında `docs/POWER-PCB-ENGINEERING-STANDARD.md` dosyasını oluşturacak ve `AGENTS.md`, `CLAUDE.md`, `docs/WORKFLOW.md` içindeki uygun atıfları kart izin veriyorsa güncelleyecek; izin dışıysa ayrı kart. Belgenin tam metni GitHub üzerinden Claude'a aktarılmadan 'entegre edildi' deme. Codex'in PR'ına sığmıyorsa **tam metni izinli bir D-karar ekinde veya T-kartı ekinde tut**; şüpheli eksiklik varsa eksikliği yaz. `main`'e alınıp diğer rolün okumasıyla doğrulanınca kalıcı say.
7. **Kapanış döngüsü:** Her önemli adım `Codex → gerekçeli karar ve görev → Claude Code → KiCad/şematik uygulama ve test → Codex bağımsız inceleme` zincirinden geçer. Raporlar ve kaynaklar GitHub'daki PR/commit ile ilişkilendirilir. Son mesajdaki `SONRAKİ PROMPT` tek kod bloğunda ve **en fazla 15 satır** olur; PR/dal, karar, engeller, belge standardı referansı, Claude işi ve kabul testleri geçer.
8. **Kullanıcıdan yalnız fiziksel görev beklenir.** Teknik tercih mümkünse belgeli D-kararında çözülür; üretici teyidi/PCB fab/tezgâh ölçümü henüz yapılmamışsa 'AÇIK'. Hakemlik en fazla iki tur (repodaki WORKFLOW kuralı). Başarısızlıklar ve tamamlanmayan testler kayıtlardan silinmez.

## 1. MİMARİ VE DEĞİŞMEZ PROJE KISITLARI

**En güncel repo dosyalarından tekrar doğrula.** 2026-11-08'de incelenen `main` / PR #70 belgelerinde hedef mimari: 6S LiPo, nominal 20–26 V giriş → ters polarite/TVS ve Q1/U5 → 2 faz LM70880-Q1 (`U1`,`U2`) buck → `/VOUT` 11 V ortak bara ve 32 COUT → Q2 + U6 (`LM74502H`) ayırıcı → `/VSAFE` → `U3/U4` TPS25982 eFuse → O1 ve S2E çıkışları. Bu, önceki 3.3/5/12 V çoklu çıkış tasarım varsayımıyla karıştırılmayacak. Gerçek şematik ve spec esastır.

### Sert elektriksel sınırlar

| ID | Değişmez kabul şartı | Kanıt/kaynak önceliği |
|---|---|---|
| E-01 | O1 herhangi bir geçici olayda anlık tepe `≤ 12.0 V` | `REQUIREMENTS`, `DESIGN-RULES`, tam koruma zinciri; bench şart |
| E-02 | Kararlı bara üst sınırı `≤ 11.1605 V` | güncel gereksinim/sim/hesap |
| E-03 | Bara yük adımı alt sınırı `≥ 10.78 V` | güncel gereksinim/sim/hesap |
| E-04 | `U3/U4 IN < 30 V` mutlak sınır; mümkünse güvenlik payı | eFuse datasheet + fault analizi |
| E-05 | HV–mantık açıklığı: mevcut `0.6 mm` kuralı gevşetilemez | `PDU.kicad_dru` + `tasks/T-023.md`; geçerlilik kapsamını denetle |
| E-06 | U6/Q2 GATE iz uzunluğu `≤ 10 mm`, INA296–RS Kelvin gerçek rota `≤ 15 mm` ve karttaki paralellik/SW-altı yasakları | `PCB-HANDOFF`, `T-023` |
| E-07 | Stackup/DFM (4 katman, 1.6 mm, tüm katman 1 oz, via 0.6/0.3, via-in-pad) **teyitsiz varsayımdır** | fab onayı henüz yok |
| E-08 | F5'te 49 koşudan 47 tamamlanıp geçti; iki köşe **AÇIK**; hiçbir sonuç fiziksel garanti değildir | `reports/g2/VERIFY.md`, gerçek güncel JSON ve run logu |

### Mevcut PCB tasarım kuralları — iş başında yeniden oku

| Sınıf | Mevcut seçilen dış iz (mm) | Mevcut dış minimum (mm) | Not |
|---|---:|---:|---|
| INPUT_POWER | 3.3 | 2.94 | `/ANODE`, `/VIN`; ince uç istisnası ayrı denetlenir |
| BUS_POWER | 5.5 | 4.92 | `/VOUT`, `/VSAFE`; `/GND` plane olduğu için genel min-track istisnası |
| PHASE_POWER | 2.6 | 2.35 | `/SW_PHx`, `/ISNSx`, yük taşıyan ile algılama dalını ayır |
| O1_PORT | 5.3 | 4.76 | `/O1_11V` |
| S2E_PORT | 3.3 | 2.97 | `/S2E_11V` |
| ANALOG | 0.25 | proje sınıfına göre | üretici/DRU açıklıkları korunur |
| GATE | ≥0.4 | proje sınıfına göre | kısa çevrim, dönüşüyle birlikte |

**Uyarı:** Bu sayılar tek başına kabul değildir. Mevcut `routing-g2.json`, `PCB-HANDOFF.md`, `PDU.kicad_pro` ve `.kicad_dru` ile karşılaştır; gerçek **dolu zone boğazı, kesintisiz akım kesiti, via/termal ve dal akımı** hesaplanmadan genişlik yeterliliği kanıtlanmış sayılmaz. `neck-down` kuralı pad çevresinde en fazla `1.5 mm` ve padde sonlanan kısa daralma için ayrı `pcb_drc.py` denetimine tabidir. Fault akımını sürekli akım gibi ölçülendirme; süre, I²t, endüktans ve SOA'yı ayrıca hesapla.

## 2. ŞEMATİK: TÜM PARÇALARA UYGULANACAK TAM KAPSAMLI DENETİM

**Öncelikli yeni özellik:** Yerleşim incelemesiyle yetinme. Tüm gerçek şematik referanslarını (`PDU.kicad_sch` ve hiyerarşik alt sayfalar), gerçek KiCad export netlist'ini, `design/pdu_v2_spec.yaml`, `design/bom-v2.csv`, `design/footprint-map.csv`, SPICE modellerini ve analiz parametrelerini eşleştir.

### 2.1 Eksiksizlik ve izlenebilirlik

- Otomatik **ref envanteri** çıkar: bütün symbol UUID/ref, value, tam MPN, tolerans, güç/gerilim/sıcaklık derecesi, DNP, pin numarası/adı, elektriksel pin tipi, her pinin net adı, footprint, pad boyutu/numarası, BOM satırı, SPICE model/parametre karşılığı.
- Şematik ↔ BOM ↔ spec ↔ PCB ↔ footprint ↔ SPICE arasında **birleşik tek tablo** kur. Çoklu-unit, gizli güç pinleri, stacked pin, NC, global/hiyerarşik etiket, güç bayrağı, pin swap ve eşdeğer pad gibi durumları doğru ayrıştır. Net adları sadece isim eşitliğiyle değil elektriksel pin kimliğiyle eşleştir.
- `187 BOM satırı = 180 PCB ref` gibi olası farklılıkları DNP, test elemanı, board-only item, aynı referansın birden çok satırı, elle eklenen bağlantı gibi **gerçek nedeni kanıtlanmadan** hata veya normal kabul etme. Sayıları güncel commit üzerinden say.
- Her parça için durum: `DOĞRULANDI / KOŞULLU / HATALI / BELGE YOK / İNCELENMEDİ`; incelenmeyeni asla geçildi sayma. Tüm referanslar kapsanmadıkça **full-schematic audit complete** yazma.
- ERC 0 olsa bile tasarım çalışır anlamına gelmez. ERC + veri sayfası pin ve çalışma koşulu + bağımsız formül + senaryo kontrolü ayrı kapılardır.

### 2.2 Her parça için elektriksel kontroller

1. **Mutlak ve önerilen çalışma sınırları:** VIN/VOUT, VCC/BIAS/VDDA, I/O, diferansiyel ve common-mode, sıcaklık, VDS/VGS, akım ve geçici/fault gerilimleri; margin ve `typ/max` ayrımı.
2. **Pasifler:** R değeri/tolerans/direnç gücü/sıcaklık katsayısı, kondansatör DC-bias altında **efektif kapasite**, ESR/ESL ve ripple; gerilim dereceleri, endüktör `L(I)`, Isat/Irms/DCR/kayıp, TVS pulse rating, diot ters/ileri akımı ve ısınma.
3. **Koruma ve fail-safe:** reverse polarity, giriş kısa devre/surge, TVS ile MOSFET/eFuse gerilim zarfı, GATE kapanma sırası, mantık VCC=0, POR/UVLO, CLR/PRE yarış durumu, latch reset, bağımsız kaba OVP, OUT–IN ters transient, tek arıza senaryoları.
4. **Kontrol/dinamik:** iki faz zamanlama/senkronizasyon/akım paylaşımı, feedback kaynağı, trim ve uzaktan algılama, compensation/loop kararlılığı ve PVT toleransları, yük adımı, başlangıç, kısa devre ve yük kopması.
5. **Bağlantı/üretim:** şematik sembolün resmi pinout'la, footprint pad/ölçülerin üretici land pattern'la uyumu, polarlık, polarize kondansatör/diyot, test/konnektör pin 1 işareti, montaj yönü.
6. **Güvenilirlik:** gerçek sıcaklık/ripple/derating, besleme gücü bilançosu, I²R, soft-start/inrush, şönt transient enerjisi, MOSFET SOA ve göreve bağlı çevresel koşullar.

### 2.3 Topolojiye özgü ayrıntılı şematik kontrol listesi

| Alt devre/parça grubu | Zorunlu elektriksel kontrol | Kanıt |
|---|---|---|
| Giriş `J1`, `D1`, `U5/Q1`, CIN/CBIN | 6S gerilim zarfı; giriş yönü; TVS standoff/clamp vs korunan pinler; kablo/kaynak endüktansı; ters polarite MOSFET pinout, VGS/VCAP, gate, UVLO; kondansatör voltaj ve bias | Datasheet pin/pulse + hesap/bench |
| Buck `U1/U2` LM70880, `L1/L2`, `RS1/RS2` | master/slave ayarları, interleaving/sync, EN/PG, BIAS/VDDA/AGND, ISNS+/VOUT/FB/COMP, CBOOT/SW4/RBOOT, VCC bypass, RT/CONFIG ve NC; L(I)/Isat/I²t; current share | TI pin/typical application + hesap/SPICE |
| `CIN1…8`, `CBIN1/2`, `COUT` bankası | bulk + HF bypass ayrımı, toplam **efektif** C, akım/ESR/ESL, VOUT fault tepe, konnektör aralığı, üretici önerisiyle karşılaştırma | DC-bias datasheet + full-system model |
| U6/Q2 ayırıcı | LM74502H VS/VCAP/GATE/SRC/EN/OV; CVCAP hesap ve efektif C; Q2 VDS/VGS/RDS(ON)/Qg/SOA; G-S direnci, switch-off gecikmesi; tek MOSFET topolojisinde ters akım sınırlaması | Resmi datasheet + gate charge/SOA + bench |
| OVP/OC/REF/latch/LDO | TLV3601 giriş VCM/offset/overdrive ve **garantili gecikme koşulu**; REF5025A referans min/max; INA296A2 gain/CMRR/settling ve 4-wire shunt; SN74LVC1G74 PRE/CLR/logic-state; POR; referans kaybı | Datasheet koşulları + worst case hesap |
| `U3/U4` TPS25982, CEFIN/CEFOUT, D_REV, ILIM/IMON | doğru **alt varyant** ve mod; max IN/OUT; ILIM tablo min/max, inrush/dVdt, ITIMER/RETRY/UVLO; thermal pad, CEFIN fiziksel bypass, ILIM parazitik C; OUT–IN negatif transient ve Schottky | TI datasheet tablosu + transient hesap/bench |
| `J2/J3`, TP, JP, kablo | exact mating set, kontak ısıl derating, AWG, pin polaritesi, fixture kısa devre ve erişim, açık lehim köprüsü normal durum | Molex/ilgili üretici + footprint pin map |

**Dikkat:** Datasheet'te önerilen bir kondansatör değeri, mevcut kapasitörün **yerleşimini** düzeltmeye yöneltir; otomatik şema/BOM değişikliği yetkisi vermez. Topoloji/veri sayfası revizyonu farkı önce D-kararında gerekçelendirilir. Sadece `typ` üzerinden `≤12 V garanti` iddiası kurulmaz.

### 2.4 Şematik onay kapısı (ayrı T-kartı)

- [ ] `kicad-cli sch erc` ve netlist export; hatalar/istisnalar UUID ve kural ile kayıtlı.
- [ ] Güncel ref, pin, MPN, PCB pad ve BOM parity otomatik karşılaştırıldı; **0 açıklanmayan fark**.
- [ ] Kritik analog/koruma pinleri üretici dokümanıyla **pin-pin** incelendi.
- [ ] Tüm parçalarda abs-max/önerilen aralık, pasif derating ve fault PVT kontrolü var.
- [ ] Güç dengesi, iki faz, kompanzasyon, oc/ovp kararları, startup ve fault durumları test edildi veya açık istisna kayıtlı.
- [ ] Şematik değişikliğinden önce/sonra aynı özlü hesap/test; izinli kart ve bağımsız THINKER onayı var.

## 3. PCB YERLEŞİM / YÖNLENDİRME KURALLARI — ELEKTRİKSEL RİSK ÖNCELİKLİ

**P0:** Bağlantı/termal/fault açısından üretime engel olabilecek konu; **P1:** performans/EMI/güvenilirlik; **P2:** üretim/okunabilirlik/ergonomi. Önceliği kanıtla, güzellik puanıyla değiştirme.

| Kod | Kural | Somut ölçüm / test | Kaynak |
|---|---|---|---|
| L01 P0 | Buck iki faz için **VIN–CIN–PGND yüksek di/dt döngüsü** en küçük **etkin** loop alanında; F.Cu yerel PGND dönüşü + doğrudan L2 referansı. | Her CIN pad→VIN ve GND→PGND gerçek yol, katman/via, geometrik alan ve mümkünse çözülmüş akım merkezi; sadece pad-centroid yeterli değil. | TI LM708x0 §7.4.1, Şekil 7-28/29 |
| L02 P0 | Yakın **HF bypass** ile bulk CIN ayrı işlev görür. TI LM708x0 0402 HF bypass ve ek 1206/1210 bulk önerir; CBIN1/2 0603 10 nF mevcut tasarımını bununla karşılaştır. | Her faz için bypass değeri, paket, IC VIN–PGND pad mesafesi, döngü, bölgesel impedans. Uymazsa miktar ve etkisi. | TI LM708x0 §7.4.1, Şekil 7-29 |
| L03 P0 | LM70880 SW→bobin kısa, yeterli akım kesitli ama **gereksiz büyük SW adası/anten yok**. SW, COMP/FB/RT/INA ve test kollarından ayrık. | SW pad/trace/zone alanı, bobin padi/yönü, iz-via, yakın ağ mesafesi, testpad ek dalı. | TI LM708x0 §7.4.1 |
| L04 P0 | CBOOT/SW4/RBOOT, CVCC/VDDA ve feedback çevresindeki küçük parçalar ilgili pinlere yakın. | Gerçek pin→pad ve dönüş yolu, layer/via, SW coupling; mevcut ref/MPN kontrol. | TI LM708x0 §7.4.1 |
| L05 P0 | U11/U12 INA296, RS padlerinden **ayrı Kelvin** algılar. Güç taşımayan IN+ ve IN−; T-023 paralellik şartı ve SW altından geçmeme. | Her kolun **gerçek routed centerline ≤15 mm**, RS pad kenarı, katman, güç tap ayrımı, iki kutup paralelliği/kuplajı ve L2 dönüşü. | TI INA296 §Layout + T-023 |
| L06 P0 | U6/Q2 GATE/SRC **komple kapı şarj/deşarj döngüsü** küçük; R_GS ve CVCAP uygun pozisyonda. | U6–Q2 GATE ≤10 mm, R_GS kol uzunluğu/çevrimi, SRC dönüşü, VCAP–VS kondansatör, termal etki. | TI LM74502H §11.1 |
| L07 P0 | eFuse U3/U4 IN–GND bypass ve geri dönüş kısa; giriş/çıkış bakır ve ısı padleri, signal GND güvenli. ILIM/IMON/ITIMER gibi hassas destek elemanları pinde. | Her pin–kondansatör–GND döngüsü, ilave parazitik C; ILIM <30 pF tavsiye kısıtı projeye uygunlukla denetlenir. | TI TPS25982 §11.1 |
| L08 P0 | COUT 32'li banka iki faz ve Q2/ayırıcı açısından yük adımı ve fault akımıyla dengeli; tek noktadan besleme boğazı ve akım paylaşımı kontrol. | Her faz/RS→COUT/Q2, en dar bakır, via, eşdeğer direnç/ESL, fault peak; COUT seri/parallel dal sınıflandırması. | Repo `PCB-HANDOFF`, T-021/022 |
| L09 P0 | L2 (In1.Cu) **kesintisiz GND referansı**; körü körüne AGND-PGND ayrımı/split yok. L3 güç zonu ve B.Cu adaları L2'nin yerine geçmez. | L2 bağlı ada/filled area, antipad delikleri, hassas izlerin gerçek referans katmanı ve yüksek di/dt dönüşü, şönt tap etkisi. | TI LM708x0, ADI AN-1119 |
| L10 P0 | Güç izlerinin gerçek **en dar bağlı bakır** kesiti, via sayısı/kaplaması, ısıl bütçesi; yalnız track-width DRC yeterli değil. | Track+filled-zone kesitleri, efektif segment uzunluğu, via current share belirsizliği, sıcaklık, IR drop, short I²t/SOA. | IPC-2152 kapsamı + routing-g2 |
| L11 P0 | 0.6 mm HV netleri ve karmaşık analog taplar için clearance fiziksel olarak korunur. | Pad/track/zone/via, mask/edge ve DRC kuralının kapsamadığı pad-pad boşlukları, üretici toleransı. | repo DRU/PCB-HANDOFF |
| L12 P0 | TVS/Schottky/eFuse ve giriş anahtarı koruduğu terminale yakın; loop endüktansını düşür. | TVS güç ve GND dönüşü, `D_REV`, CEFOUT transient kolu, konnektör → MOSFET → buck akım yolu. | TI TPS25982 §8.4/11.1 |
| L13 P0 | Bobin/RS/güç MOSFET termali; LM70880 exposed-pad/PGND viaları; doğru derating. | Tj tahmini gerçek bakır/stackup ile; ECAD via/pad bağlantısı, termal poligon; EVM eşdeğerliğini kanıtlamadan 'sağlandı' deme. | TI LM708x0 thermal + EVM |
| L14 P1 | FB/COMP, OVP/OC, REF, UVLO, latch ve sensör sinyalleri yüksek dv/dt/dI/dt alanından ayrılır. | Net bazında layer, yakındaki SW alanı, sinyal ve L2 referans sürekliliği, ground via, probe branching. | TI/ADI layout |
| L15 P1 | OVP Kelvin: Q2 drain VRAW algılama hattı yük akımı üstünden ölçülmez; hata anı gerilim düşümü/mekânsal fark incelenir. | Q2 drain tap noktası, her comparator divider pin konumu; ölçüm/hesap ve O1 margin. | repo PCB-HANDOFF/PROTECTION |
| L16 P1 | GND via sayısı = körlemesine her GND pad için bir via değil. Yakın temiz dönüşü planla; L2 antipadlerden parçalanmasın. | Net bazında connected-component/zone-tap/return path, tek ada, floating copper, via_dangling istisna kanıtı. | KiCad DRC + repo D-012 |
| L17 P1 | Güç rayları için montaj, konnektör ve prob erişimi korunur. | 3D courtyard/3D board, M3 keepout, TP probe-GND, TP_SW bobin gövdesi, 18 AWG mating/strain relief. | fab/Molex + repo D-006/D-008 |
| L18 P1 | EMI analizi **sistem seviyesinde**: güç/batarya kabloları, ek filtre gerekip gerekmediği, regülatör frekansları. | Gerçek parasitik model, gerekiyorsa LISN/near-field/oscilloscope; PCB değişikliği yanında giriş filtre kararlılığı. | ADI AN-1119 + TI EMI app notes |
| L19 P2 | Etiket, üretim çıktısı, polarite, fiducial, lehim/stencil, tombstone ve mask dam kontrolü. | fab yetenekleri + KiCad DRC + CAM/Gerber/assembly çizimleri; yalnız görünüşle onaylama. | fab DFM ve üretici paket çizimleri |

### Mesafe kuralı: 'yakın' ne demek?

- Evrensel `her kondansatör IC'ye X mm'de` standardı **yoktur**. Mesafeyi gerçek pin–pad geometrisi, akım çevrimi, seri endüktans, referans düzlemi, izolasyon ve üretici Şekil üzerinden değerlendir. Kaynak olmayan milimetre eşiği uydurma.
- Yakın olması gerekenler: HF CIN–VIN/PGND, CBOOT–SW4, CVCC, VDDA, RS–INA296 sense, U6 GATE/SRC–Q2, U3/U4 CEFIN, REF decoupling, ILIM/ITIMER, TVS korunacak giriş, Q2/R_GS.
- **Uzak/izole olması gerekenler:** yüksek dv/dt SW bakırı ↔ FB/COMP/OC/REF, sense hatları, LDO/latch; yüksek akım dönüşleri ↔ hassas analog GND; sıcak bobin/FET ↔ sıcaklığa duyarlı kapasitör.
- GND adalarını keyfî bölme. TI TPS25982'nin yerel signal-GND önerisini, L2 sürekli referansın bütünlüğünü bozmayacak topoloji özelinde uygula; tek noktaya bağlama kuralını körlemesine tüm karta dayatma.
- Kelvin iki kol için sırf eşit uzunluk iyi diye yakınlık/paralellik/aynı referans koşulunu göz ardı etme. `IN+ F.Cu`, `IN− B.Cu` farklı katmanları **otomatik PASS sayma**; kartın açık `paralel` kabul kriteri nasıl karşılanacak, gerekçeli çöz.

## 4. BÜTÜNSEL TEST / GEÇİŞ KAPILARI

Her kapı için `girdi commit → komut/sürüm → ham dosya → beklenen kriter → ölçülen → PASS/FAIL/AÇIK` kaydı gerekir.

| Kapı | Kontrol | Geçiş şartı |
|---|---|---|
| G0 | Git/HANDOFF/kart/PR doğruluğu; dirty tree/izinli yollar | kaynak ve revizyon biliniyor; örtülü değişiklik yok |
| G1 | Sch ↔ netlist ↔ spec ↔ BOM ↔ PCB footprint/pin | tüm ref/pinler açıklanmış; **0 açıklanmayan** uyuşmazlık |
| G2 | Schematic ERC + datasheet pin/abs-max/pasif/önerilen çalışma/koruma hata analizi | ERC 0; manuel elektronik inceleme ayrı kaydedilmiş |
| G3 | Buck, koruma, startup, load step, tolerans, loss, thermal ve SPICE | tüm test sonuçları dürüst; tamamlanmayan ve FAIL açık, O1 sınırı gevşetilmez |
| G4 | Placement: hot loop, HF bypass, SW, Kelvin, GATE, eFuse ve testpoint | kritik geometrik/termal kısıtlar gerçek ölçülerle kanıtlı |
| G5 | Routing + DRC + zone refill + schematic parity | ilgili kart için izinli açık çift sayısı; **nihai kartta** unconnected=0, error=0, short=0, parity=0; warning tek tek açıklanmış |
| G6 | Power SI/PI/thermal/EMI ve gerçek bakır kesiti | worst-case hesap/analiz; sim/hesap limitleri, açık varsayımlar ve bench ihtiyaçları |
| G7 | Fab/DFM/BOM/CAM + devre kartı fiziksel test | fab stackup/pad/via kabulü + as-built ve tezgâh; önceki G0–G6 tek başına 'üretime kesin hazır' değildir |

**G5 bağlam kuralı:** R-020/T-023 bir ara adımdır; 116 bağlantısız çift **bu ara adımda** beklenen olabilir. Dolayısıyla R-020'yi nihai G5 `unconnected 0` ile yanlış biçimde RET etme. Ama T-023 final ve T-024 nihai kapıda bu açıklar kabul edilemez. Yeni açık uç eklemek de yasaktır.

### Bağımsız test disiplini

- İlk hesapta yalnız **tasarım girdileri** ve gerçek geometriden ölçülen veriyi kullan; BUILDER `step2-audit.json` ve `step2-report.md` rakamlarını bağımsız hesabı bitirene kadar kıyas için açma (teslimin nerede olduğunu biliyor olabilirsin). Daha sonra farkı sayısal ve gerekçeli belirt.
- `kicad-cli sch erc` ve `pcb drc --refill-zones --schematic-parity` sürüm/argümanlarını `--help` ile doğrula, KiCad 10.0.7 hedefi. Diğer sürümle aynı sonucu varsayma. `python scripts/pcb_rules.py --check`, `python scripts/pcb_drc.py`, `python analysis/check_consistency.py`, `python -m pytest -q`, `python scripts/check_workflow.py` mevcut kartlara göre çalıştırılır. Büyük `run_all.py` gereksiz yere R-020'yi bloklamaz.
- DRC'deki `via_dangling` gibi uyarıları sadece sayı olarak değil **UUID/net/koordinat/kural/bağlı bakır ve gerekçe** ile incele. Zone refill öncesi/sonrası farkları ayrıca göster.
- Güç sıcak döngüsü hesaplarını **pad-merkez shoelace** ile `gerçek akım merkez çizgisi / akım dağılımı` olarak etiketleme. Akım çözücü/uygun field-solver yoksa “bu yöntemle doğrulanamadı”, gereken veri/model/ölçüm yaz.
- Kazancı ve riski birlikte ölç: ilgili değişiklikten **önce/sonra** aynı geometri/DRC/route length/clearance/thermal raporu; yeni bağlantı, net ve footprint uyuşmazlığı yok.

## 5. İLK ÇALIŞMA: R-020 / PR #70 (CLAUDE'DAN GELEN GÖREVİ KORU)

**Aşağıdaki referanslar yalnız yönlendirme/başlangıç ipucudur; açılışta tekrar doğrula:** `main @ 684357c`; PR `#70`, `wp/T-023 @ cf9e820`, R-020 planı. Codex kendi ayrı klonunda `gh pr view 70` ve `git rev-parse HEAD` çıktısını raporlar. Kaynak çelişirse GitHub kanıtı esastır.

İncelemenin asli çıktısı: `reviews/R-020.md` + `tasks/R-020.md` (`ID: R-020`, `Durum: Review`, `Bağımlılık: T-022`); `wp/R-020` dalı + taslak PR, `tasks/queue.md` değiştirilmez. Karar `ONAY / KOŞULLU / RET` (repo şablonunda `RED` kullanılıyorsa gerçek şablon esas); en çok iki tur.

**T-023 adım 2 için ayrı ayrı karar ver:**

1. Kelvin: IN+ F.Cu, IN− B.Cu; dört gerçek bağlantının 15 mm sınırı ve RS'den ayrı Kelvin çıkışı; fakat **'paralel' şartı** sağlanmış mı? Alternatif waypoint/layer/INA296–RS yerleşim düzeltmesini clearance koruyarak karşılaştır.
2. `R_GS` Q2'den yaklaşık 11 mm uzak, raporda gate kolu 16.015 mm; gate discharge çevrimi ve placement ilişkisi; taşınmalı mı? U6–Q2 gate 10 mm sınırı korunacak.
3. `TP_ISO_GATE` yeni `(97.4,44.6)` ve 1.2 mm dalı: test erişimi ve gürültü/kapasitif yük/komşu bakır açısından uygun mu?
4. `TP_ISNS1P/1N/2P/2N` için yanlış uzun analog dallar oluşturmadan erişilebilir ölçüm konumu/alternatifi: taşınmalı mı, hedef koordinat ve açıklık gerekçesi?
5. `U12.7–U14.2` paylaşılan GND via: dönüş/SI/ground-bounce ve L2 sürekliliği; ayrı via için ölçülü alternatif var mı?
6. Adım 3 (FB/COMP/OVP/OC) için B.Cu sinyal kanalı, L2 referansı ve 0.6 mm HV açıklığı; başlayabilir mi? Hâlâ 116 açık çift beklentisini bağımsız DRC ile yeniden değerlendir.

**İlk referans teslim:** `reports/g5/T-023/step2-report.md`, `step2-audit.json`, `step2-gnd-applied.json`, `drc-step2.json`, `scripts/pcb_route_signals.py`, `tasks/T-023.md`, `PDU.kicad_pcb`. Bunlar `wp/T-023` dalına aittir; `main`'de olduğunu varsayma. İlgili karar önce kendi ölçümünle, sonra Builder raporuyla karşılaştırılarak gerekçelendirilecek.

**R-020 ile karıştırılmayacak ayrı sistem denetimi:** `G1–G7` bütünsel şematik/PCB süreç denetimi. Codex, R-020 sonucu ayrıca bir **kalıcı standart entegrasyon T-kartı** ve gerekiyorsa bağımsız **tam şematik elektriki denetim T/R-kartları** planlar. Kartları küçük iş paketlerine böl (S/M, L yok). Eski T-024 kapanış kartının tekrarını açma; T-024'e girdi olacak sorulara atıf yap. İzin listesi düzenlemesi gereken her dosya için kart hazırla. Kanıtsız genel iyileştirmeleri R-020 engeline dönüştürme.

## 6. TESLİMAT VE OTOMATİK DEVİR ŞARTLARI

### Codex THINKER çıktısı

- **İlk:** `R-020` bağımsız inceleme; altı soruya somut gerekçe/ölçüm/alternatif, adım 3 GO/NO-GO, engelleyici adedi, test/PR/HEAD referansı.
- **Sonra:** ayrı `D-...` / `T-...` kartında bu standardın bütünsel uygulama planı. İlk kaynak belge ve **tam maddeler** GitHub'da Claude erişimine açık olmalı; yalnız 'MD ekini oku' yetersizdir, çünkü ajanlar ayrı oturumda/klonda çalışır. İzinli `decisions/` veya `tasks/` yoluna tam metin aktarılamadıysa Claude'a verilemeyen kısım **AÇIK**, entegrasyon **TAMAMLANMADI** diye yaz.
- Her şematik referansının inceleneceği ölçülebilir `component-audit.csv/json` çıktısını ancak ayrı kartla BUILDER'a uygulat (Codex `design/` veya `scripts/` yazamaz). Başarısız/dokümansız parçalar sayısal olarak listelenmeli.
- Belgeyi sistem kuralı hâline getirmek için yeni T-kartı açıkça `docs/POWER-PCB-ENGINEERING-STANDARD.md` üretimini, referans kaynağını, `AGENTS.md`/`CLAUDE.md`/WORKFLOW atıflarını, eski şartlarla çelişki taramasını ve `check_workflow` testini içermeli. İzin matrisi gerektiğinde kartları ayır.
- Sonunda **tek, ≤15 satırlık** `SONRAKİ PROMPT → Claude Code` bloğu: `R-020` PR/dal/karar, engelleyici sayısı, altı kararın kısa özeti, adım 3 izni, yeni standart D/T kartı ve GitHub yolu, Claude'un kesin görevleri/komutları, sonrasında Codex bağımsız inceleme.

### Claude Code BUILDER çıktısı

- R-020 kararına göre önce mevcut `T-023` kapsamında değişiklikleri uygula; başka iş paketlerinin koduna/PCB'sine sıçrama. Her adımda zone refill, gerçek ölçüm, DRC/parite, test, before/after raporu, commit/push/taslak PR.
- Kalıcı standart dosyası için **ayrı izinli kart** geldiğinde tüm metni repoya işle; kaynak/boşluk/tolerans ayrımlarını koru, mevcut `DESIGN-RULES`, `PCB-HANDOFF`, `routing-g2` ile çelişkileri D-kararına bildir, sessiz düzeltme yapma.
- Bütünsel şematik taraması için kaynak tablo/otomatik pin/ref kontrolü ve parça-kapsam raporunu gerçekten üret. Her `HATALI` değişiklik yalnız ayrı onaylı kartla, regresyon testleriyle yapılır.
- Her aşamadan sonra tek `SONRAKİ PROMPT → Codex` ver: bağımsız doğrulamaya ihtiyaç duyan PR, test/ölçüm dosyaları, güncel SHA ve açık koşullar.

## 7. BİRİNCİL TEKNİK KAYNAKLAR (BAĞLANTI + UYGULAMA)

> Üretici PDF'leri zamanla revizyon değiştirebilir. **Tek bir sabit sayfa numarasını gerçek kabul etme:** dosyayı aç, kapaktaki revizyonu ve doğru bölüm/şekli güncelle; varsa eski/yeni sayfa farkını not et.

1. Texas Instruments, **LM70840/LM70860/LM70880** datasheet, **§7.4.1 Layout Guidelines, §7.4.2 Layout Example**, Input Current Loop (Şekil 7-28), PCB Top Layer (Şekil 7-29): https://www.ti.com/lit/ds/symlink/lm70840.pdf  
   Özellikle 0402 HF bypass + 1206/1210 bulk, VIN/PGND sıcak döngü, yakın SW/bobin, CBOOT/VCC/FB, solid GND ve termal via.
2. Texas Instruments, **LM70880-Q1 Evaluation Module** ve kullanıcı kılavuzu: https://www.ti.com/tool/LM70880QEVM  
   EVM geometrisi kıyas amaçlıdır; kartımızın termal/EMI sonuçlarının aynısı olduğunu kanıtlamaz.
3. Texas Instruments, **INA296A/INA296B** datasheet, **§9.3–§9.4 Layout; Kelvin/4-wire; 0.1 µF bypass** (revizyona göre bölüm sayısı değişebilir): https://www.ti.com/lit/ds/symlink/ina296b.pdf
4. Texas Instruments, **TPS25982** datasheet, **§Layout Guidelines**: https://www.ti.com/lit/ds/symlink/tps25982.pdf  
   IN/GND yakın decoupling, ILIM parazitik C, VIN thermal pad ve iç FET akım dağılımı, destek pinleri, kısa koruma kolları. TI güncel revizyonunu doğrula.
5. Texas Instruments, **LM74502/LM74502H** datasheet **§11 Layout** ve GATE/SRC/VCAP: https://www.ti.com/lit/ds/symlink/lm74502h.pdf  
   Güçlü gate discharge için gerçek Qg, koşullu geçiş süresi ve kaynak dönüşü denetimi.
6. Analog Devices, **AN-1119**, switching power PCB'de kritik AC/DC/sensitive akım yolları, grounding/EMI ve ısı: https://wiki.analog.com/resources/app-notes/an-1119
7. IPC, **IPC-2152** conductor width/current/temperature yaklaşımı (kapsamı ve kabul durumu): https://quicksearch.dla.mil/qsDocDetails.aspx?ident_number=277660 ve resmi örnek: https://www.ipc.org/TOC/IPC-2152.pdf  
   Erişilmemiş standardın tam tablolarını hayal edip sayısal kural türetme; repo hesabını varsayımlarıyla doğrula.
8. KiCad **10.0 Schematic Editor/ERC**: https://docs.kicad.org/10.0/en/eeschema/eeschema.html  
   ERC yalnız belirli bağlantı türlerini kontrol eder; fonksiyonel doğruluğun ispatı değil.
9. KiCad **10.0 PCB Editor/DRC**: https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html  
   `refill-zones`, `schematic-parity`, custom rules, ERC/DRC kapsamı ve sınırları.

## 8. BAŞARI ÖLÇÜTÜ VE SON RAPOR ŞABLONU

**Kesin başarı iddiası yalnız kanıtla:**

- `[ ]` R-020 altı karar kapandı, gerçek HEAD + PR kaydı var.
- `[ ]` T-023'in ilgili alt adımı, 0 **yeni** DRC hatası/parite/short ve ölçülen rota kriterleriyle değerlendirildi; paralellik ayrı karar aldı.
- `[ ]` Şematikte tek bir bileşen bile gözden kaçmaması için otomatik referans/pin kapsama aracı ve ayrı küçük kart planı mevcut.
- `[ ]` Tüm parça grupları için datasheet, çalışma noktası, fault, termal, net ve footprint denetim matrisi var veya eksik alanlar açıkça sayılı.
- `[ ]` Kalıcı mühendislik standardı, `docs/` entegrasyonu için yetkili kart ve GitHub'dan erişilebilir eksiksiz içerikle devredildi.
- `[ ]` Mevcut simülasyon FAIL ve 2 F5 açık köşe saklandı; fiziksel test gereksinimleri ayrı kaldı.
- `[ ]` Claude'a gidecek sonraki promptta **bu standardın kalıcı uygulanması**, kart/PR linki ve test kapıları yer aldı.

**Kısa rapor biçimi:** `HEAD/PR` → `Kapsam` → `Bağımsız ölçüm ve kaynak` → `R-020 altı karar` → `Engelleyici tablo` → `Açık üretici/fiziksel varsayımlar` → `Kalıcı standart/şematik denetim T-kartı` → `SONRAKİ PROMPT → Claude Code`.
