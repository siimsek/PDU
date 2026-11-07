# D-005 — T3 Gemstone O1 giriş koruma zinciri

- **Kart:** tasks/D-005.md
- **Yazan:** Codex (GPT-6), 2026-11-07
- **Kullanıcı kararı gerekli mi:** Evet — D-002'deki mutlak maksimum ve kısa süreli aşım soruları hâlâ yanıtlanmadı; U-002 açık kalmalı ve T3'ten yazılı sınırlar istenmeli.

## Soru

T3 Gemstone O1'in harici DC girişinden ilk aktif elemana kadar giriş koruma zincirinin parça kimlikleri, mutlak maksimum gerilimleri ve varsa TVS kelepçe koşulları resmi şemadan çıkarılabiliyor mu; en zayıf halka 12.0 V O1 kriterini ve kısa süreli aşım güvenliğini kanıtlıyor mu?

## Seçenekler

| Seçenek | Temel değerler (etiketli) | Kriteri sağlıyor mu | Risk | Kanıt (belge + sayfa) |
|---|---|---|---|---|
| Şemadaki giriş zincirini kullan | Resmi PDF'in içindekilerinde sayfa 06 “Power_Input” başlığı okunuyor; eleman etiketleri/MPN/değerleri mevcut görüntü çözünürlüğünde okunamadı (**doğrulanamadı**). | **Hayır.** İlk eleman ve zincirin zayıf halkası belirlenemedi. | MPN/değer tahmini mutlak maksimum veya TVS kelepçesini yanlış gösterebilir. | T3 Gemstone resmi hardware deposu, `design/t3-gem-o1-v0_2.pdf`, sayfa 2 içindekiler ve sayfa 6 Power_Input: https://github.com/t3gemstone/hardware/blob/main/design/t3-gem-o1-v0_2.pdf |
| Mevcut yayımlanmış DC çalışma aralığını geçici sınır olarak tut | **DATASHEET/ürün bilgisi:** harici DC girişi 5–12 V, 5 A. Bu aralık mutlak maksimum veya transient dayanımı olarak tanımlanmıyor. | **Yalnız normal DC aralığı için.** 12.0 V üzeri izinli tepe/süreyi kanıtlamaz; O1’in ≤12.0 V kriterini gevşetmek için dayanak oluşturmaz. | DC işletim aralığı dışındaki kısa aşım dayanımı bilinmiyor. | T3 Gemstone O1 resmi teknik özellik/SSS: https://t3gemstone.org/en/products/o1 ; resmi ürün bilgisi: https://t3gemstone.org/en/shop/o1 |
| Üreticiden yazılı mutlak maksimum ve transient sınırı al | İstenen: harici DC konektörü için absolute maximum, izin verilen transient gerilimi/süresi/enerjisi ve varsa upstream TVS/eFuse sınırları. Bu oturumda üretici belgesi bulunamadı. | **Evet, U-002'yi kapatabilecek tek kanıt yolu.** | Yanıt alınana kadar gerçek tolerans bilinmez. | D-002-O1-spec.md ve resmi T3 ürün/board sayfaları. |

## Öneri

T3 O1 giriş koruma zinciri için bileşen düzeyinde sonuç vermek şu anda **doğrulanamadı**. Resmi PDF'in ilgili sayfası iki okuma denemesinden sonra da parça/gerilim değerleri çıkarılacak kadar okunaklı değildi; hiçbir parça veya limit tahmin edilmedi. O1 PDU kriterini 12.0 V olarak koru, **U-002'yi açık bırak** ve T3'ten DC giriş absolute maximum ile transient genlik/süre sınırını yazılı iste.

## Kanıt

- T3 Gemstone resmi hardware deposu, `design/t3-gem-o1-v0_2.pdf` (v0.2, 33 sayfalık PDF; sayfa 6 “Power_Input”): https://github.com/t3gemstone/hardware/blob/main/design/t3-gem-o1-v0_2.pdf
- T3 Gemstone O1 resmi teknik özellikleri: harici DC 5–12 V / 5 A; bunlar normal çalışma değerleridir, absolute maximum/transient tablosu değildir: https://t3gemstone.org/en/products/o1
- D-002 mevcut sonucu: https://github.com/siimsek/PDU/blob/main/decisions/D-002-O1-spec.md
- Erişim denemeleri: GitHub ikili PDF metin fetch'i içerik vermedi; web PDF rendering'de sayfa 6 başlığı görülse de parça etiketleri ve değerler güvenilir biçimde çözülemedi. Bu nedenle zincirin ilk aktif elemanı ve her parçanın datasheet'i araştırma girdisi olarak doğrulanamadı.

## Açık varsayımlar

- **VARSAYIM:** PDU O1 portu T3 Gemstone'un harici DC girişine bağlanacak; USB-C PD girişi bu kararın kapsamı dışındadır.
- **AÇIK:** 5–12 V / 5 A üretici çalışma aralığıdır; 12 V'un mutlak maksimum veya transient sınırı olduğu varsayılmadı.
- **AÇIK:** Girişte koruma yoktur sonucuna varılmadı; şema okunamadığı için yalnız bu oturumda doğrulanamadı.

## Doğrulanamayanlar

- Harici DC girişten ilk aktif elemana kadar parça kimlikleri/değerleri ve zincir sırası — **doğrulanamadı**; https://github.com/t3gemstone/hardware/blob/main/design/t3-gem-o1-v0_2.pdf — sayfa 6 mevcut görüntü çözünürlüğünde okunamadı.
- Giriş konnektörü, TVS/eFuse/regülatör mutlak maksimum gerilimi ve TVS kelepçe akımı/gerilimi — **doğrulanamadı**; şemadaki exact MPN'ler okunamadığı için resmi üretici datasheet'lerine bağlanamadı; https://github.com/t3gemstone/hardware/blob/main/design/t3-gem-o1-v0_2.pdf
- T3 O1 harici DC giriş absolute maximum ve kısa süreli transient genlik/süre sınırları — **doğrulanamadı**; resmi ürün sayfalarında yayımlanmamış; https://t3gemstone.org/en/products/o1
