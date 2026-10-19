# IDA PDU — güncel doğrulama durumu

19 Ekim2026. **Üretime hazır değil.** Eski aktarım/ara denetim kayıtları [arşivde](archive/verification-before-calculation-sync-20261019.md) korunur.

## Son elektriksel tasarım kaydı

- Şema77 sembol/73 fiziksel parça/46 ağ/257 pin/218 tel/86 etiket.
- Short0; ERC0 hata/0 uyarı; açık pin ve örtüşme bulunmadı. Bu, O1 koruması veya gerçek devre kararlılığı kabulü değildir.
- Son düzeltmelerde referans/pin-net üyelikleri korunmuştur. İki RIMON değeri806 Ω oldu; sekiz COUT100 V2220 footprint/seçimi değişti.
- PCB72 footprint; F1 yok; iz0.197 unrouted hata/301 uyarı. Bakır açıklığı/courtyard hatası raporlanmıyor.
- 9 netclass/46 tam ağ ataması;35 µm nominal bakır/31,5 µm hesap varsayımı. Açık editörün önbellek riski ve kapalı tekrar uygulama yöntemi [repo rehberinde](REPOSITORY.md).

Kanıt: [bağımsız son denetim](../hardware/no-measurement-final-audit.md), [pad geri okuma özeti](../.konnect/diagnostics/no-measurement-final-pad-summary.json), [son DRC](../.konnect/diagnostics/cout-hv-main-drc.json).

## Ortak model kabulü

- Konnect export'undan24 senaryo; iki motor/48 koşu. Son tamamlanan rapor512 geçen/2 başarısız kontrol içerir.
- İki başarısız kontrol O1 OVP'dir: yaklaşık16,89 V tepe, kabul üst sınırı12 V. Bu sınır gevşetilmedi.
- Modeller aynı fiziksel girdileri/uyaranları kullanır; ideal bobin sözdizimi adaptörü dışında devre eşliği denetlenir. Bu, silikon eşliği değildir.
- Nominal IMON değerlendirmesi806 Ω ile; COUT düşük44/88 µF, tipik165 µF ve üst257,664 µF hassasiyetleriyle taranır. Üretici TDK modeli ayrıca çalıştırıldı; ortak model onun tam frekans karşılığı değildir.
- [Sayısal rapor](../simulation/verification-results.json), [okunur sonuçlar](../simulation/results.md). Yeniden çalıştırma yöntemi [repo rehberinde](REPOSITORY.md).

Yeni çalıştırıcı her denemeyi `simulation/latest-run.json` içine kaydeder. Tamamlanmayan/yürütme hatalı koşuda önceki kabul raporu yeni koşunun sonucu gibi kullanılmaz. Motor yürütme tamamlanması ile elektriksel kabul ayrı sonuçlardır.

## Statik hesap ve repo tutarlılığı

- Hesaplar netlist/BOM ref/değer/footprint eşliğine bağlıdır. IMON806 Ω ve100 V COUT doğrudan güncel veriden okunur; veri uyuşmazlığında hesap durur.
- FB statik ekranı10,8333–11,1605 V; IMON3,07165 V üst ekranı yayımlanmış kazanç alanında. Gerçek tüm sıcaklık/darbe kabulü değildir.
- UVLO20 V yeniden kalkışı başarısızdır:20,3318 V köşe, EN sızıntısı eksik. Statik scriptin çıkış1 vermesi bu açık kabulü korur.
- 73 satırlı canonical BOM doğrulandı;57 MPN alanı boş. Arşivdeki eski referanslar veya aday fiyatlar güncel satın alma kabulü değildir.
- Repo incelemesi belge bağlantıları, hash ve hesap eşliğini kontrol eder; ERC/DRC/SPICE veya fiziksel test yerine geçmez.

## Açık kabul kapıları

1. O1 en kötü durum gerilim koruması.
2. Gerçek kontrol döngüsü/faz marjı ve paylaşım.
3. F1, TVS, kablo, MOSFET hata enerjisi/SOA koordinasyonu.
4. UVLO politikası ve eksik sistem girdileri.
5. Kesin MPN, bobin/konnektör/mekanik ve özel footprint üretim incelemesi.
6. PCB yönlendirme ve üretim uyarılarının çözümü.
7. Gerçek yük/transient/termal/EMI ölçümleri.

Tam inceleme sırası: [kontrol listesi](REVIEW-CHECKLIST.md). Başarısız veya ölçülmemiş madde geçti olarak işaretlenmez.
