# Repo düzeni ve yeniden çalıştırma

## Dosyaların rolü

- Kökteki PDU KiCad üçlüsü ve library tabloları: ana tasarım. Dosya yolları korundu; repo düzenlemesi sırasında kaynak içerikleri değiştirilmedi.
- `hardware/lib/`: proje sembolleri ve footprintleri; proje tablolarından çözülür.
- `docs/PROJECT-STATE.md`: güncel amaç/durum/devam noktası. `REVIEW-CHECKLIST.md`: açık işler ve özel parça incelemesi.
- `docs/design.md`, `SON-TESLIM.md`: ayrıntılı hesap/kararlar ve yönlendirme sınırları; tarihli eski bölümler güncel özetle birlikte okunur.
- `hardware/pdu-current-bom.csv`: netlistle doğrulanmış mevcut parça dökümü; satın alma tamamlanmış değil. `bom.csv`: aday/seçim ve eski fiyat notları; fiyatlar güncel teklif sayılmaz.
- `hardware/validation/`: deneme KiCad projeleri, pin/pad kayıtları ve renderlar. Ana PDU yerine açılmaz.
- `simulation/`: dışa aktarılmış netlist, ortak davranış modelleri, test girdileri, loglar ve sayısal sonuçlar. `candidate-*`, `history/`, `legacy_models/` tarihli çalışmalar; ana devreyle aynı kabul edilmez.
- `.konnect/diagnostics/`: araç geri okumaları/kanıtlar ve yardımcı kod. `*-calls*.json` yerel geçici MCP istekleri; otomatik toplu replay yapılmaz.
- `docs/archive/`: eski kök görselleri/netlistler ve eski README. Dosyalar silinmeden arşivlendi.
- `hardware/functional-blocks.kicad_sch`, `simulation/buck-average.*`: eski başlangıç/öğrenme girdileri; güncel ana tasarım değil.

Kaynak önceliği: ana KiCad → yeni Konnect export/geri okuma → kaynak hash'ine bağlı test sonuçları → güncel durum özeti → tarihli eski notlar. Bir fark bulunursa sessizce varsayım yapma; kaynağı ve kanıtı yeniden bağla.

## Araçlar ve yerel veri

Son kullanılan sürümler: KiCad10.0.7, Konnect0.13.0, LTspice26.1.1. Python komutları repo kökünden çalıştırılır. ngspice yolu yerel kurulumla belirtilir. Bu sürümler otomatik yükseltme talimatı değildir.

PowerShell ortam örneği:

```powershell
$env:PDU_LTSPICE = 'C:\Program Files\ADI\LTspice\LTspice.exe'
$env:PDU_NGSPICE = 'F:\Spice64\bin\ngspice_con.exe'
# Gerekirse farklı Konnect kurulumunu belirt:
# $env:PDU_KONNECT_EXE = 'C:\your-install\konnect.exe'
```

Ortak devre/test üreticileri Python standart kütüphanesini kullanır. Ayrı üretici veri/figür inceleme kodu PyMuPDF ve curl_cffi kullanır; bunlar ana iki-motor koşusunun gereksinimi değildir.

### Üretici verileri

`hardware/_datasheets/` yerel önbellektir; Git'e alınmaz. TDK model lisansı izinsiz yeniden dağıtımı yasakladığından bias/precision model dosyaları da Git dışında bırakılır; mevcut yerel dosyalar silinmez.

- Resmî URL, revizyon, model koşulları ve hash'ler: [COUT qualification](../hardware/COUT-qualification.md) ve `hardware/validation/c5750/vendor-file-hashes.json`.
- Ayrı TDK AC bench için resmî bias-model ZIP'ini indirip kendi koşullarıyla edin; `C5750X7S2A226M280KB_b_LTspice.mod` dosyasını `hardware/validation/c5750/` içine koy. Şifreli modeli değiştirme/çözme.
- Native LTC4365 adayları kurulu LTspice'ın `lib/sub/LTC4365-1.sub` dosyasını kullanır; aday üreticisindeki yerel yolu kurulumuna göre ayarla. Bu deney ana devrenin çalışması için gerekmiyor.
- Render/datasheet alıntıları ve türetilmiş geometri inceleme içindir; üçüncü taraf dosyalara genel bir yeniden lisanslama iddiası yapılmıyor.

### Konnect/IPC

[MCP/API kaydı](../.konnect/MCP-API.md) ve [başlatıcı](../.konnect/start-pdu-api.ps1) yerel Windows oturumunu açıklar. Config/socket/PID dosyaları makineye özeldir ve Git dışında tutulur. Başka makinede yerel yolları yeniden kur. CUA veya doğrudan KiCad kaynak metin düzenlemesiyle bypass yapılmaz.

## Ortak iki-motor doğrulama

1. Konnect `export_netlist` ile kayıtlı ana şemayı `simulation/pdu-current.net` olarak dışa aktar.
2. Konnect `export_bom` ile `hardware/pdu-current-bom.raw.csv` üret; alanlar `Reference,Value,Footprint,MPN,Tolerance,TCR,Specification,Voltage`.
3. Aşağıdaki komutları çalıştır:

```powershell
python simulation/canonical_bom.py
python calculate.py --output hardware/calculation-summary.json
python simulation/check_static_corners.py
python simulation/run_all.py
```

Canonicalizer yalnız benzersiz ref/değer/footprint eşliğinde yedi `?` aktarım farkını düzeltir; ham CSV'yi korur. Statik denetim UVLO20 V kalkış kabulü açık olduğu için şu an çıkış1 döndürür. Ortak koşu motorları bitirse de iki O1 kabulü başarısız olduğundan çıkış1 döndürür. Bunlar gizlenecek yürütme hataları değil, açık elektriksel kabul sonuçlarıdır.

`run_all.py` model ve24 senaryoyu yeniden üretir, LTspice ve ngspice çalıştırır, kabul/eşlik raporunu yazar. Her denemenin ilerleme/tamamlanma/yürütme hatası `simulation/latest-run.json` içinde tutulur. Çıkış1 tamamlanan elektriksel kabulün başarısızlığı, çıkış2 yürütmenin tamamlanmaması anlamına gelir; eski sonuç yeni koşu gibi kullanılmaz. Üretici silikon modeli değildir. `sync_documentation.py` eski seçimleri geri yazabildiğinden tarihsel yardımcı olarak devre dışı bırakıldı.

## Yönlendirme profilini yeniden uygulama

KiCad editörleri ve Proje Yöneticisi temiz kapatıldıktan sonra:

```powershell
python .konnect/ApplyRoutingRules.py --check
python .konnect/ApplyRoutingRules.py
```

Kilit varsa araç yazmaz ve kilit silmez. Tüm değişiklikler Konnect MCP üzerinden yapılır.9 sınıf/46 ağ ve menü boyutlarını geri okuyarak doğrular. Açık editörün eski proje önbelleği profili geri yazabildiği için kapanış sırası önemlidir. Kapalı-proje tam uygulama son checkpoint'te çalıştırılmış sayılmaz; açık kartta ek menü yazımı reddedilmişti.35 µm nominal bakır/31,5 µm hesap varsayımı ve istisnalar [teslim kaydında](SON-TESLIM.md).

## Git'e giren ve yerel kalanlar

Ana kaynaklar, özel kütüphaneler, hesap/test kodu, metin log/sonuçlar ve inceleme kanıtları sürümlenir. Büyük raw dalgalar, SQLite önbellekleri, kilitler, kullanıcı arayüz durumu, otomatik geçmiş, yerel IPC config'leri ve kısıtlı üretici modelleri `.gitignore` ile yerelde kalır.29 MB'lık eski convergence logu da yereldir; başarısızlığın özeti raporda korunur.

Commit/push repo durumunu saklar; failed O1 testini, unrouted kartı veya üretim kabulünü kapatmaz. Force push kullanılmaz. Yeni tasarım değişiminde ilgili rapor/kanıt da güncellenir.

## Checkpoint tutarlılık kontrolü

```powershell
python tools/check_repository.py
```

Bu komut yerel belge bağlantıları,73 satırlı BOM'un seçili alanları ve kaydedilmiş simülasyon dosyalarının çalışma kopyası/Git index hash'lerini inceler. KiCad kaynağı açmaz, yeni ERC/DRC/SPICE çalıştırmaz. Repo tutarlılığı geçerken elektriksel kabulün başarısız olduğunu ayrı raporlar. Son kayıt [repository-review.json](repository-review.json) dosyasındadır.

Git attributes, aktif CAD kaynaklarını ve hash'e bağlı model/netlist dosyalarını satır sonu dönüşümünden korur. Eski öğrenme şeması önceki normalize Git gösterimini korur; aktif tasarım otoritesi değildir.
