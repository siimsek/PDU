"""Synchronize ordinary documentation/BOM candidates, never KiCad sources."""
raise SystemExit('Historical updater disabled: it contains superseded component choices. Read docs/PROJECT-STATE.md and update current reports explicitly.')
from pathlib import Path
import csv
import json
import shutil

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent

def replace(path, pairs):
    text=path.read_text(encoding='utf-8')
    for a,b in pairs:
        text=text.replace(a,b)
    path.write_text(text,encoding='utf-8')

replace(ROOT/'docs/design.md',[
    ('5 A + 2.5 A eFuse hedefi yalnızca tasarım kapasitesidir; O1 3 A kaynağına göre fazla yüksek olabilir.',
     'Mevcut 4.96 A / 2.53 A nominal kesme eşikleri tasarım ayarlarıdır; gerçek cihaz akımları olarak kullanılmaz.'),
    ('Başlangıç O1 akım sınırı 5.0 A ve S2E 2.5 A olarak alınmıştır; O1 için kaynaklardaki 3 A/5 A çelişkisi nedeniyle bu ayar fiziksel kart sürümü doğrulanmadan güvenli kabul edilmez.',
     'Mevcut 301 Ω / 604 Ω dirençler yaklaşık 4.96 A / 2.53 A nominal kesme eşiği verir. Bunlar korunmuş devre ayarlarıdır; gerçek cihaz yükü olarak kabul edilmez ve ölçüm olmadan son hedef sayılmaz.'),
    ('**Kaynaklar arasındaki uyumsuzluk:** T3\'ün kendi t3gemstone/hardware deposu 5–12 V / 5 A yazarken ArduPilot genel bakış sayfası 5–12 V / 3 A yazıyor. 3 A geçici port sınırı daha düşük kaynak değerine dayanır; bu değer O1\'in gerçek tüketimi değildir ve kalkışta erken eFuse açmasına yol açabilir. Kart sürümü/etiketi ve gerçek akım ölçümü olmadan ne 3 A ne de 5 A çalışma akımı kabul edilmelidir.',
     '**Doğrulanmış kaynaklar:** T3 güncel güç bağlantısı belgesi ve hardware deposu DC giriş için 5–12 V / 5 A ratingi verir. Eski ArduPilot 3 A kaydı güncel üretici sınırının yerine kullanılmaz. Gerçek tüketim ve kalkış akımı ölçülmedi.'),
    ('ayar yaklaşık 5.0 A → T3 Gemstone O1','korunmuş nominal kesme eşiği 4.96 A → T3 Gemstone O1'),
    ('O1 5.0 A ve S2E 2.5 A nominal eFuse ayarları 7.5 A nominal toplam sağlar;',
     'O1 4.96 A ve S2E 2.53 A mevcut nominal kesme eşikleri yaklaşık 7.49 A toplam verir;'),
    ('O1 için 3 A/5 A kaynak çelişkisi çözülmeden 5 A ayarı cihaz bağlantısına bırakılmamalıdır.',
     'Bu eşikler gerçek yük profili ölçülmeden onaylanmış cihaz akım hedefleri değildir.'),
    ('Yaklaşık 5.0 A eFuse nominal ayarı; T3 donanım deposundaki 5 A rating ile eşleşen geçici aday',
     'Mevcut 301 Ω ile yaklaşık 4.96 A kesme eşiği; gerçek yük hedefi değil'),
    ('ArduPilot kaynağı 3 A diyor; fiziksel kart sürümü, gerçek akım, jak polaritesi/ölçüsü, kablo ve konnektör doğrulanmadan 5 A uygulanmamalı',
     'Resmî DC rating 5–12 V / 5 A; akım profili, jak, kablo ve konnektör ölçümü açık'),
    ('TPS259824ONRGET varyantının 16.9 V OVP girişi 11 V rail için uygundur. O1\'in gerçek sınırı 3 A ise bu güç dağılımı 7 A hedefini taşımaz; akım profili ölçülmeden 5 A ayar uygulanmamalı.',
     'TPS259824ONRGET varyantının 16.9 V OVP eşiği O1\'in belirtilen 12 V giriş üst sınırını korumaz. Düzeltilmiş model bu testi iki motorda da geçemedi. Yeni hızlı koruma ve gerçek akım ölçümü kapanmadan PCB onayı yok.'),
    ('O1 kaynaklarında 3 A ve 5 A rating çelişkisi; tüketim bilinmiyor',
     'O1 resmî DC ratingi doğrulandı; tüketim ve kalkış akımı bilinmiyor'),
    ('74 sembol','77 sembol'),('100 kΩ pull-up ile 82.5 kΩ pulldown, 11 V\'ta PG yüksek seviyesini 4.97 V yapar.',
     '100 kΩ pull-up ile 18 kΩ pulldown, 11 V\'ta PG yüksek seviyesini 1.678 V yapar; harici alıcı bağlı değildir.'),
    ('PG 4.97 V','PG 1.678 V'),
    ('F1, giriş bulk kondansatörü ve IC ayak izleri açık kaldı.',
     'F1, ölçülmüş giriş bulk ihtiyacı, hızlı O1 aşırı gerilim koruması ve IC ayak izleri açık kaldı.')])
replace(ROOT/'docs/learning-guide.md',[
    ('O1 5 A + S2E 2.5 A eFuse ayarı varsayımdır ve ',
     'Mevcut 301 Ω/604 Ω yaklaşık 4.96 A/2.53 A kesme eşiği verir; bunlar ölçülmüş cihaz akımları değildir. '),
    ("O1'in 3 A/5 A kaynak çelişkisi çözülmelidir.","O1'in resmî DC ratingi 5–12 V / 5 A olarak doğrulandı; gerçek tüketim ve açılış akımı ölçülmelidir."),
    ('T3 donanım deposundaki 5–12 V / 5 A bilgisini ve ArduPilot sayfasındaki 5–12 V / 3 A bilgisini yan yana yaz. 5 A kapasitenin gerçek tüketim olmadığını belirt.',
     'T3 güncel güç bağlantısı belgesi ile t3gemstone/hardware deposunun aynı 5–12 V / 5 A DC ratingini verdiğini kaydet. Bu kapasiteyi gerçek tüketim olarak kullanma. O1 için 12 V üstünü kesen koruma testi kapanmadan PCB\'ye geçme.')])
replace(ROOT/'docs/verification.md',[
    ('**Sonuç:** Elektrik şeması kuruldu, ERC 0 hata. PCB ayak izi, ölçülmüş Ceff ve prototip kanıtı yok.',
     '**Sonuç:** Elektrik şeması düzeltildi, ERC 0 hata/0 uyarı. İki motor ortak devreyi çalıştırdı; O1 aşırı gerilim testi başarısız. PCB onayı yok.'),
    ('T3 donanım GitHub 5–12 V/5 A; ArduPilot overview 5–12 V/3 A çelişkisi | AÇIK',
     'T3 güncel güç bağlantısı belgesi ve hardware GitHub deposu 5–12 V/5 A diyor; gerçek tüketim ölçülmedi | RESMÎ RATING UYUMLU; YÜK ÖLÇÜMÜ AÇIK'),
    ('O1 kaynağı 3 A/5 A çelişkili','O1 resmî DC ratingi 5–12 V/5 A; gerçek yük ölçülmedi'),
    ('PG 100 kΩ/82.5 kΩ','PG 100 kΩ/18 kΩ'),('74 sembol','77 sembol')])
path=ROOT/'docs/verification.md'
lines=path.read_text(encoding='utf-8').splitlines()
for i,line in enumerate(lines):
    if line.startswith('| V-08 |'):
        lines[i]='| V-08 | Ripple/transient | Cihaz uçlarında bara ±2% | Güncel iki fazlı ideal PWM: 20 V\'ta faz ripple 1.647 A, 26 V\'ta 2.141 A. 0.45→4.5 A yük adımı yaklaşık 10.804–10.996 V. 2 ns/1 ns yakınsaması denetlendi | DAVRANIŞSAL MODEL; O1 OVP BAŞARISIZ; KART ÖLÇÜMÜ AÇIK |'
    if line.startswith('| V-13 |'):
        lines[i]='| V-13 | LTspice/ngspice | Tekrarlanabilir ortak devre, açık model kapsamı | 20 senaryo ×2 motor; export edilen devreden aynı pin ve değerler. Sonuç sayıları simulation/verification-results.json içinde. O1 aşırı gerilim kabulü başarısız | TAMAMLANMADI; SİLİKON VE TERMAL KANIT YOK |'
path.write_text('\n'.join(lines)+'\n',encoding='utf-8')
path=ROOT/'hardware/bom.csv'
with path.open(encoding='utf-8',newline='') as f:
    reader=csv.DictReader(f);fields=reader.fieldnames;rows=list(reader)
assert all(None not in r and None not in r.values() for r in rows), 'Malformed BOM: refusing to overwrite'
for r in rows:
    if r['Ref']=='RPG1B,RPG2B':
        r['Candidate MPN']='18 kOhm, 1%'
        r['Status']='PG unloaded monitor: 1.678V nominal at11V; <=4.654V at30V with adverse1% resistor tolerances. Future logic VIH unverified.'
    if r['Ref']=='RPG1,RPG2':
        r['Status']='100k top /18k bottom. Replaces former82.5k pulldown; external logic is not connected.'
    if r['Ref']=='RILIM_O1,RILIM_S2E':
        r['Status']='Existing301/604Ohm unchanged; not measured load targets. Official O1 DC rating5-12V/5A is confirmed; actual current/startup measurement and OVP correction remain open.'
existing={r['Ref'] for r in rows}
for refs,qty,candidate,desc,status,source in [
    ('RBOOT1,RBOOT2','2','1 Ohm, 1%, 0603','Series bootstrap resistor, one in each47nF CBOOT path','Added per LM70880 Table5-1, VCC8V mode','https://www.ti.com/lit/ds/symlink/lm70880-q1.pdf'),
    ('CIN_U5','1','22 nF, 100V, X7R, 0603','LM74700 input bypass from ANODE toGND','Added; confirm selected capacitor effective capacitance/rating before procurement','https://www.ti.com/lit/ds/symlink/lm74700-q1.pdf')]:
    if refs not in existing:
        r={k:'' for k in fields};r.update({'Ref':refs,'Qty':qty,'Candidate MPN':candidate,'Description / minimum rating':desc,'Status':status,'Source':source});rows.append(r)
temporary=path.with_suffix('.csv.tmp')
with temporary.open('w',encoding='utf-8',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)
temporary.replace(path)

# Generate the current report from observed measurements and acceptance results.
result=json.loads((HERE/'verification-results.json').read_text())
lt=json.loads((HERE/'ltspice-results.json').read_text())
ng=json.loads((HERE/'ngspice-results.json').read_text())
old=HERE/'results.md';archive=HERE/'legacy_models/results-before-alignment.md'
if old.exists() and not archive.exists():shutil.copy2(old,archive)
lines=['# PDU — LTspice / ngspice güncel doğrulama','',
    'Tarih: 2026-10-18. Kaynak: Konnect dışa aktarımı `pdu-current.net`.',
    '**Karar: TAMAMLANMADI — O1 aşırı gerilim koruması başarısız; PCB onayı yok.**','',
    '## Yapılan düzeltmeler','',
    '- RBOOT1/RBOOT2: 1 Ω, her47nF bootstrap kondansatörüyle seri.',
    '- CIN_U5: 22nF, ANODE–GND.',
    '- RPG1B/RPG2B: 18kΩ; üst dirençler100kΩ. PG uçları harici mantık yüküne bağlı değil.',
    '- U1–U4 MPN alanları mevcut kesin Value kodlarıyla dolduruldu. U1–U4/F1 footprint boş; F1 MPN atanmadı. O1 akım ayarı değiştirilmedi.','',
    '## Kaynak ve model eşleşmesi','',
    '73 fiziksel parça,257 pin,46 dışa aktarılan ağ (5 NC,2 yeni bootstrap ara ağı dahil). Dört PWR_FLAG ile şemada77 sembol var. İki faz aynı VOUT barasına, aynı COMP düğümüne ve doğru SYNC uçlarına bağlı. Önceki251 pinin yalnızca CBOOT1.1/CBOOT2.1 uçları yeni seri dirençler nedeniyle ara ağa taşındı; diğer bağlantılar korundu.',
    'Konnect son kayıtlı şema denetimi: kısa devre0, ERC0hata/0uyarı, açık pin0, orphan0, floating tel ucu0, sembol/etiket örtüşmesi0.218yatay/dikey tel,86etiket; parça merkezleri, etiketler ve tel uçları1.27mmızgarada. Kanıt: `schematic-final-checks.json`; görüntü: `../PDU_electrical_fixes_final.png`.',
    'Aynı ortak devre/test uyaranları kullanılır. Tek sözdizimi farkı ideal bobin adaptörüdür; LTspice gizli1mΩ Rser kapatılır. İki motorda DCR açıkça23.3mΩ. `parity-manifest.json`, `test-cases.json`, `model-aliases.json` ve `verification-results.json` izlenebilir kanıttır.','',
    '## Çalıştırılan kontroller','',
    f"{result['case_count']} senaryo ×2 motor = {result['engine_runs']} koşu. {result['passed']} kabul kontrolü geçti, {result['failed']} kontrol başarısız. Motorların çalışması ve birbirine benzemesi, devrenin bütün gereksinimleri sağladığı anlamına gelmez.",
    'Kapsam:20/22.2/26V kalkış; boş yük;0.45→4.5A yük adımı; ortak barada7.5A;44µF Ceff senaryosu; ters batarya; VIN tarafından geri besleme; yükselen/düşen buck UVLO; eFuse UVLO/OVP; her portta aşırı yük ve kısa devre/kilit/sıfırlama;20/26V iki fazlı PWM;26V için2ns/1ns zaman adımı yakınsaması. O1/S2E yükleri yapay test akımlarıdır.','',
    '## Sayısal sonuçlar','']
for name in ['startup-20v','bus-7p5a','load-step','interleaved-20v','interleaved-26v','interleaved-26v-refined','efuse-ovp']:
    lines.append(f'### {name}\n')
    for k,a in lt[name]['measures'].items():
        b=ng[name]['measures'].get(k)
        unit='s' if 'delay' in k else ('A' if k.startswith(('i1_','i2_','iphase')) else 'V')
        lines.append(f'- {k}: LTspice {a:.9g} {unit}; ngspice {b:.9g} {unit}.')
    lines.append('')
lines+=['## Kapanmayan koruma bulgusu','',
    'O1 resmî güç bağlantısı sayfası ve t3gemstone/hardware DC giriş üst sınırını12V olarak veriyor. Mevcut TPS259824O16.9V OVP ile bundan önce kesmez. OVP testindeki O1_PEAK ölçümü12V\'u geçiyor; bu gerçek tasarım uyumsuzluğu iki motorda da görülüyor. TPS3701→EN adayı9.9µs+212µs tipik gecikme nedeniyle hızlı gerilim yükselişine çözüm değildir ve ana şemaya eklenmedi. Daha hızlı koruma yolu seçimi, fiziksel pin/footprint kabulü ve gecikme/tolerans testleri gerekiyor.','',
    '## Modelin sınırları','',
    'LM70880/TPS25982/LM74700 resmî PSpice kütüphaneleri şifrelidir. Bu davranışsal modeller üretici silikon modeli değildir. Bootstrap anahtarlaması, BIAS/CONFIG/SYNC iç davranışı, gerçek COMP çevrim kararlılığı, verim, termal/SOA, sigorta açma ve TVS enerjisi doğrulanmadı. Model16.9V OVP eşiğinde gecikmesiz keser:16.89V gerçek donanım için üst sınır değildir; gerçek aşım daha büyük olabilir. Startup-done durumu dVdt düğümünden türetilir; ağır yükte uzayan başlangıç akım sınırlaması doğrulanmadı. Ceff88/44µF varsayımıdır. Eski tek fazlı kaynaklar/loglar `legacy_models/` altında saklandı; önceki dosya adları güncel iki fazlı testlere eşlendi. Güncel test otoritesi `pdu-*.log` ve `pdu-*.ng.log` dosyalarıdır.','',
    '## Yeniden üretme','',
    '1. Konnect `export_netlist` ile `simulation/pdu-current.net` dosyasını güncelle.',
    '2. `python simulation/build_models.py` ve `python simulation/build_benches.py` çalıştır.',
    '3. `python simulation/run_ngspice.py` çalıştır. LTspice\'ta `test-cases.json` içindeki her `file` kaydını açıp çalıştır (bu oturumda LTspice MCP kullanıldı).',
    '4. `python simulation/verify_results.py` çalıştır. Kritik O1 OVP bulgusu kapanana kadar sıfırdan farklı çıkış kodu beklenir; bu başarısızlık kaldırılmamalıdır.','',
    'Kaynaklar: [O1 güç bağlantısı](https://docs.t3gemstone.org/tr/boards/o1/peripherals/introduction#güç-bağlantısı), [Gemstone hardware](https://github.com/t3gemstone/hardware), [LM70880](https://www.ti.com/lit/ds/symlink/lm70880-q1.pdf), [LM74700](https://www.ti.com/lit/ds/symlink/lm74700-q1.pdf), [TPS25982](https://www.ti.com/lit/ds/symlink/tps25982.pdf), [ngspice model uyumluluğu](https://ngspice.sourceforge.io/modelparams.html).']
old.write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('Ordinary docs and candidate BOM synchronized; no KiCad sources touched.')
