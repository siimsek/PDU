# IDA PDU — kalıcı AI çalışma düzeni

Bu belge Codex CLI, ChatGPT ve GitHub üzerinden sürdürülecek çalışmaları düzenler. Mevcut elektriksel gereksinimler, kanıt sınıfları, test sınırları ve tasarım kararlarının yerini almaz.

## Bu çalışmanın tabanı ve sınırları

- G1 dalı `wp/g1-ai-analysis`, `main` üzerindeki 19 Ekim tasarım tabanından (`a1dbeeb46e806ff65dbb4bea20fa9cabb5691bb2`) oluşturuldu. G1 hesabı ve karar kanıtları `reports/g1/` altındadır.
- PR #1 / `wp/baseline-2026-10-24` içindeki WP1/WP2 öneri ve test kanıtları ayrı kalır; G1 bunları salt okunur girdi olarak karşılaştırır. PR #1 veya `main` üzerinde çalışılmaz.
- Mevcut kapsam analiz, hesap, SPICE, BOM, karar ve tezgâh kabul kriterleridir. Kullanıcı ayrıca onaylayana kadar `*.kicad_*`, PCB üretim dosyaları ve ana devre değiştirilmez.
- G1 geçişinde fiziksel test yapılmadı. Güncel açık FAIL/INCOMPLETE durumları ve WP1/WP2 karşılaştırması için `reports/g1/G1-SUMMARY.md` ve `reports/g1/PREVIOUS-WP-COMPARISON.md` esas alınır.

## Görev başlangıcı

Her görevde önce repo kökünde aşağıdaki bilgileri kaydet ve oku:

```powershell
git status -sb
git branch --show-current
git rev-parse HEAD
git remote -v
```

- Kirli çalışma ağacında değişiklik yapan adımlara geçme. Kullanıcı dosyalarını silme, stash etme, resetleme, üzerine yazma veya başka dala taşıma. Önce hangi dosyanın kullanıcı çalışması olduğunu belirle; bağımsız okumayı sürdürebilirsin.
- G1 commit zincirini koru. `reset`, `rebase`, force push ve geçmişi yeniden yazma kullanma.
- İlgili önceki raporları, başarısız logları, proje talimatlarını ve `AGENTS.md` dosyalarını oku. WP1/WP2 karşılaştırması gerekiyorsa PR dalını ayrı salt okunur Git nesneleri veya ayrı inceleme worktree’si üzerinden al; PR dalını G1 çalışma ağacına birleştirme.
- `main` ve PR #1'e commit, push, yorum veya merge yapma.

## Yerel analiz, test ve kanıt

- Hesap kodunu `analysis/`, G1 rapor/çıktılarını `reports/g1/` altında tut. Önceden var olan hesap, model ve doğrulama altyapısını kullan; kanonik girdileri sessizce değiştirme.
- Her hesapta kullanılan değerleri, birimleri, köşe/tolerans varsayımlarını, iki bağımsız hesap yolunu ve farkını kaydet. Kaynak kanıtı varsa üretici datasheet’inde tam parça ve PDF sayfasını belirt.
- Simülasyon ailesi ve koşu sayısı için görevdeki bütçeye uy. Koşu başlamadan önce girdileri/hash’leri sabitle; tamamlanmayan koşu PASS değildir. Çözücü hatasını ve ilk/son denemeleri silmeden sakla.
- Her komutun tam biçimini, araç/çözücü sürümünü, çıkış kodunu, koşu kimliğini ve sonucu raporla. Test exit code’u ile elektriksel kriter sonucunu ayrı tut.
- Her sayısal sonucu `HESAP`, `DATASHEET`, `SİM`, `VARSAYIM` veya `AÇIK` olarak sınıflandır. Bir ölçüt FAIL olduysa eşiği gevşetme veya FAIL’i kaldırma; gereksinim değişecekse kullanıcı kararını ve eski sonucu birlikte koru.
- Eksik model, yakınsamayan koşu, bilinmeyen MPN/stok, ölçülmemiş yük veya test edilmemiş fiziksel sınır için “doğrulanamadı”, “AÇIK” ya da “INCOMPLETE” yaz. Simülasyon fiziksel test sayılmaz.
- MPN, fiyat, stok veya üretici garantisini uydurma. Parça belirsizse aday olduğunu ve eksik doğrulamayı açıkça belirt.
- Açık FAIL kapanmadan PASS ilan etme. Bir doğrulama eski kanıta dayanıyorsa yeni koşu gibi sunma.

## Gizlilik, dosya bütünlüğü ve değişiklik kapsamı

- Commit öncesi değişen/takip edilen dosyaları listele; gizli anahtar, token, parola, kişisel erişim bilgisi ve özel yerel yolu tara. Ham kanıt loglarını, lisanslı modelleri, cache’leri, geçici/ara dosyaları yalnız kapsam açıkça gerektiriyorsa ekle.
- Büyük dosya eklemeden önce boyut, tür, kaynak ve yeniden üretilebilirlik gerekçesini denetle. Ham SPICE deck/log’u sonuç iddiası için gerekiyorsa koru; gerekmiyorsa türetilmiş büyük dalga biçimi ve cache’i commit etme.
- Görev dışı dosyaları değiştirme. `*.kicad_*` dosyalarının diff’te olmadığını commit öncesi doğrula.
- Çalışma sonucunu küçük, anlamlı commit’lere ayır. Commit mesajı kapsamı söylesin; kullanıcı isteğinde belirtilen dizinlerin dışında dosya ekleme.

## GitHub, PR incelemesi ve yayın

- Yalnız aktif çalışma dalına normal push yap. G1 için dal `wp/g1-ai-analysis`’tir; örnek ilk push:

```powershell
git push -u origin wp/g1-ai-analysis
```

- Force push kullanma. Push öncesi remote dalın varlığını ve uç commit’lerini kontrol et; remote’da ayrışma varsa durup geçmişi koruyarak incele.
- Taslak PR’ı `main`’e karşı aç. PR açıklamasında kapsamı, test komutu/çıkış kodunu, simülasyon PASS/FAIL/INCOMPLETE sayısını, açık fiziksel testleri ve ilgili rapor/log bağlantılarını belirt.
- ChatGPT veya başka bağımsız incelemeyi GitHub’daki commit/PR kanıtlarına bağla. Teknik bulguları ilgili PR’da veya PR’a bağlı açık görevde izlenebilir kıl; `main`’e merge etme.
- Merge, üretim veya fiziksel kabul onayı bu iş akışının otomatik adımı değildir; açık kararlar ve FAIL’ler PR’da görünür kalır.

## Görev sonu raporu

Her görev sonunda yalnızca istenen kapsamda şunları bildir:

- Dal, HEAD commit ve push/PR bağlantısı.
- Eklenen/değişen dosyalar.
- Çalıştırılan komutlar, exit code’lar ve doğrulanan sonuçlar.
- Açık FAIL/INCOMPLETE bulguları, eksik girdiler ve fiziksel doğrulama durumu.

## Bu dalda kayıtlı G1 açıkları

G1’de 7/7 analiz testi geçti ve 5 simülasyon ailesi tamamlandı; family 2 ile family 4 kriter FAIL’leri raporda tutuldu. O1 OVP fiziksel olarak doğrulanmadı; 7,5 A nominal eFuse akım-limit toplamı hedefin biraz altında; F1, kaynak/kablo kısa devre koordinasyonu, U3 arıza davranışı, döngü kararlılığı, gerçek port akımları ve PCB termali açık. PR #1 WP1/WP2’deki ESL abortları, N-01 ve tarihsel UVLO FAIL/eksikleri bu G1 sonucu ile kapanmaz.
