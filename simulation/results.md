# PDU — LTspice / ngspice güncel doğrulama

Başlangıç kaydı:2026-10-18; güncel checkpoint:2026-10-19. Kaynak: Konnect dışa aktarımı `pdu-current.net`.
**Karar: TAMAMLANMADI — O1 aşırı gerilim koruması başarısız; PCB onayı yok.**

## Yapılan düzeltmeler

- RBOOT1/RBOOT2: 1 Ω, her47nF bootstrap kondansatörüyle seri.
- CIN_U5: 22nF, ANODE–GND.
- RPG1B/RPG2B: 18kΩ; üst dirençler100kΩ. PG uçları harici mantık yüküne bağlı değil.
- U1–U4 MPN alanları mevcut kesin Value kodlarıyla dolduruldu. Bu simülasyon kaydı sırasında U1–U4/F1 footprint boştu;2026-10-19 tarihinde U1–U4 prototip footprintleri atandı. F1 MPN/footprint hâlâ boş; elektriksel pin-net üyeliği ve değerler korunmuştur. O1 akım ayarı değiştirilmedi.

## Kaynak ve model eşleşmesi

73 fiziksel parça,257 pin,46 dışa aktarılan ağ (5 NC,2 yeni bootstrap ara ağı dahil). Dört PWR_FLAG ile şemada77 sembol var. İki faz aynı VOUT barasına, aynı COMP düğümüne ve doğru SYNC uçlarına bağlı. Önceki251 pinin yalnızca CBOOT1.1/CBOOT2.1 uçları yeni seri dirençler nedeniyle ara ağa taşındı; diğer bağlantılar korundu.
Konnect son kayıtlı şema denetimi: kısa devre0, ERC0hata/0uyarı, açık pin0, orphan0, floating tel ucu0, sembol/etiket örtüşmesi0.218yatay/dikey tel,86etiket; parça merkezleri, etiketler ve tel uçları1.27mmızgarada. İlk düzeltme kanıtı `schematic-final-checks.json`; son denetim `../hardware/no-measurement-final-audit.md`; güncel görüntü `../PDU_schematic_finished.png`.
Aynı ortak devre/test uyaranları kullanılır. Tek sözdizimi farkı ideal bobin adaptörüdür; LTspice gizli1mΩ Rser kapatılır. İki motorda DCR açıkça23.3mΩ. `parity-manifest.json`, `test-cases.json`, `model-aliases.json` ve `verification-results.json` izlenebilir kanıttır.

## Çalıştırılan kontroller

24 senaryo ×2 motor =48 koşu.806ohm IMON dirençleriyle IMON nominal gerilim kontrolleri,100V COUT seçimi için165uF ve257.66uF başlangıç/yük-adımı hassasiyet testleri eklendi. Son tamamlanan genişletilmiş koşuda512 kabul kontrolü geçti,2 O1 kontrolü başarısız. Motorların çalışması ve birbirine benzemesi, devrenin bütün gereksinimleri sağladığı anlamına gelmez. Çalıştırma: `python simulation/run_all.py`; başarısız O1 kabulü nedeniyle çıkış kodu1 beklenir. Ayrı aday koruma çalışması `global-ovp-candidate-results.json`, statik köşeler `static-corner-results.json` içindedir. Bu dosyanın aşağıdaki güç katı sayıları değişmeyen nominal davranışla uyumludur; güncel sayısal otorite `verification-results.json` dosyasıdır. Ayrı LTC4365aday kaydının25V hamkapasitör koşulu değişikliköncesi tarihsel taramadır; ana COUT artık100V'dur. Adayın12V aşımı başarısızlığı devam eder.
Kapsam:20/22.2/26V kalkış; boş yük;0.45→4.5A yük adımı; ortak barada7.5A;44µF Ceff senaryosu; ters batarya; VIN tarafından geri besleme; yükselen/düşen buck UVLO; eFuse UVLO/OVP; her portta aşırı yük ve kısa devre/kilit/sıfırlama;20/26V iki fazlı PWM;26V için2ns/1ns zaman adımı yakınsaması. O1/S2E yükleri yapay test akımlarıdır.

## Sayısal sonuçlar

### startup-20v

- bus_avg: LTspice 10.9960175 V; ngspice 10.996 V.
- o1_avg: LTspice 10.9879169 V; ngspice 10.9879 V.
- s2e_avg: LTspice 10.9919672 V; ngspice 10.992 V.
- iphase1_avg: LTspice 2.25028062 A; ngspice 2.25028 A.
- iphase2_avg: LTspice 2.25028062 A; ngspice 2.25028 A.
- pg1_max: LTspice 1.67683399 V; ngspice 1.67683 V.
- pg2_max: LTspice 1.67745173 V; ngspice 1.67745 V.

### bus-7p5a

- bus_avg: LTspice 10.9959764 V; ngspice 10.996 V.
- o1_avg: LTspice 10.9878769 V; ngspice 10.9879 V.
- s2e_avg: LTspice 10.9919262 V; ngspice 10.9919 V.
- iphase1_avg: LTspice 3.75028062 A; ngspice 3.75028 A.
- iphase2_avg: LTspice 3.75028062 A; ngspice 3.75028 A.
- pg1_max: LTspice 1.67682683 V; ngspice 1.67683 V.
- pg2_max: LTspice 1.67744458 V; ngspice 1.67745 V.

### load-step

- bus_min: LTspice 10.8045616 V; ngspice 10.8041 V.
- bus_max: LTspice 10.9960175 V; ngspice 10.996 V.
- o1_final: LTspice 10.9879169 V; ngspice 10.9879 V.
- s2e_final: LTspice 10.9919672 V; ngspice 10.992 V.

### interleaved-20v

- bus_avg: LTspice 10.9961843 V; ngspice 10.9961 V.
- bus_pp: LTspice 0.000622749329 V; ngspice 0.000623193 V.
- i1_avg: LTspice 3.75003607 A; ngspice 3.75 A.
- i2_avg: LTspice 3.75003607 A; ngspice 3.75 A.
- i1_pp: LTspice 1.64673042 A; ngspice 1.64705 A.
- i2_pp: LTspice 1.64673042 A; ngspice 1.64705 A.
- phase_delay: LTspice 1.14925e-06 s; ngspice 1.14925e-06 s.

### interleaved-26v

- bus_avg: LTspice 10.9959192 V; ngspice 10.9961 V.
- bus_pp: LTspice 0.000814437866 V; ngspice 0.000815091 V.
- i1_avg: LTspice 3.74994573 A; ngspice 3.75 A.
- i2_avg: LTspice 3.74994573 A; ngspice 3.75 A.
- i1_pp: LTspice 2.14030933 A; ngspice 2.14064 A.
- i2_pp: LTspice 2.14030933 A; ngspice 2.14064 A.
- phase_delay: LTspice 1.14925e-06 s; ngspice 1.14925e-06 s.

### interleaved-26v-refined

- bus_avg: LTspice 10.9960162 V; ngspice 10.9961 V.
- bus_pp: LTspice 0.000815391541 V; ngspice 0.000815123 V.
- i1_avg: LTspice 3.7499788 A; ngspice 3.75 A.
- i2_avg: LTspice 3.7499788 A; ngspice 3.75 A.
- i1_pp: LTspice 2.14056969 A; ngspice 2.14066 A.
- i2_pp: LTspice 2.14056969 A; ngspice 2.14066 A.
- phase_delay: LTspice 1.14925e-06 s; ngspice 1.14925e-06 s.

### efuse-ovp

- o1_off: LTspice 2.99643955e-11 V; ngspice 2.99644e-11 V.
- s2e_off: LTspice 5.98577507e-11 V; ngspice 5.98578e-11 V.
- o1_reset: LTspice 10.9918995 V; ngspice 10.9919 V.
- s2e_reset: LTspice 10.9959497 V; ngspice 10.9959 V.
- o1_peak: LTspice 16.8899746 V; ngspice 16.89 V.

## Kapanmayan koruma bulgusu

O1 resmî güç bağlantısı sayfası ve t3gemstone/hardware DC giriş üst sınırını12V olarak veriyor. Mevcut TPS259824O16.9V OVP ile bundan önce kesmez. OVP testindeki O1_PEAK ölçümü12V'u geçiyor; bu gerçek tasarım uyumsuzluğu iki motorda da görülüyor. TPS3701→EN adayı9.9µs+212µs tipik gecikme nedeniyle hızlı gerilim yükselişine çözüm değildir ve ana şemaya eklenmedi. Daha hızlı koruma yolu seçimi, fiziksel pin/footprint kabulü ve gecikme/tolerans testleri gerekiyor.

## Modelin sınırları

LM70880/TPS25982/LM74700 resmî PSpice kütüphaneleri şifrelidir. Bu davranışsal modeller üretici silikon modeli değildir. Bootstrap anahtarlaması, BIAS/CONFIG/SYNC iç davranışı, gerçek COMP çevrim kararlılığı, verim, termal/SOA, sigorta açma ve TVS enerjisi doğrulanmadı. Model16.9V OVP eşiğinde gecikmesiz keser:16.89V gerçek donanım için üst sınır değildir; gerçek aşım daha büyük olabilir. Startup-done durumu dVdt düğümünden türetilir; ağır yükte uzayan başlangıç akım sınırlaması doğrulanmadı. Ceff88/44µF varsayımıdır. Eski tek fazlı kaynaklar/loglar `legacy_models/` altında saklandı; önceki dosya adları güncel iki fazlı testlere eşlendi. Güncel test otoritesi `pdu-*.log` ve `pdu-*.ng.log` dosyalarıdır.

## Yeniden üretme

1. Konnect `export_netlist` ile `simulation/pdu-current.net` dosyasını güncelle.
2. `python simulation/build_models.py` ve `python simulation/build_benches.py` çalıştır.
3. `python simulation/run_ngspice.py` çalıştır. LTspice'ta `test-cases.json` içindeki her `file` kaydını açıp çalıştır (bu oturumda LTspice MCP kullanıldı).
4. `python simulation/verify_results.py` çalıştır. Kritik O1 OVP bulgusu kapanana kadar sıfırdan farklı çıkış kodu beklenir; bu başarısızlık kaldırılmamalıdır.

Kaynaklar: [O1 güç bağlantısı](https://docs.t3gemstone.org/tr/boards/o1/peripherals/introduction#güç-bağlantısı), [Gemstone hardware](https://github.com/t3gemstone/hardware), [LM70880](https://www.ti.com/lit/ds/symlink/lm70880-q1.pdf), [LM74700](https://www.ti.com/lit/ds/symlink/lm74700-q1.pdf), [TPS25982](https://www.ti.com/lit/ds/symlink/tps25982.pdf), [ngspice model uyumluluğu](https://ngspice.sourceforge.io/modelparams.html).
