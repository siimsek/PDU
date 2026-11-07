# D-002 — T3 Gemstone O1 giriş spesifikasyonu

- **Kart:** tasks/D-002.md
- **Yazan:** Codex (GPT-6), 2026-11-07
- **Kullanıcı kararı gerekli mi:** Evet — üretici normal harici DC giriş aralığını veriyor; mutlak maksimum ve kısa süreli aşım dayanımı yayımlanmış kaynaklarda doğrulanamadı. U-002, T3 üreticisinden bu iki limit istenene kadar açık kalmalı.

## Soru
T3 Gemstone O1'in PDU tarafından beslenecek harici DC girişinde üreticinin söylediği çalışma aralığı, mutlak maksimum, kısa süreli aşım toleransı ve giriş koruması nedir; mevcut 12.0 V O1 sınırı bu verilerle destekleniyor mu?

## Seçenekler

| Büyüklük | Sonuç | Kriteri sağlıyor mu | Risk / yorum | Kanıt (belge + bölüm) |
|---|---|---|---|---|
| Harici DC giriş çalışma aralığı | **DATASHEET/üretici teknik özellik:** 5–12 V DC, 5 A. Kartın dış DC güç konektörü içindir; ayrı USB-C PD girişi 5–9 V/3 A’dır ve bu kararda kullanılmıyor. | **Bulundu.** 12.0 V verilen DC çalışma aralığının üst sınırıdır. | Sayfa bu aralığı açıkça veriyor, ancak “recommended range” ibaresi yerine Power/DC connector operating spec olarak sunuyor. | T3 Gemstone O1 “Technical Specs” ve FAQ, Power. https://t3gemstone.org/en/products/o1 (Technical Specs/FAQ); https://t3gemstone.org/en/shop/o1 (Product Information) |
| Mutlak maksimum harici giriş gerilimi | **doğrulanamadı.** 12.0 V, yayımlanan çalışma aralığının üst ucudur; mutlak maksimum olarak etiketlenmemiştir. | **Hayır / kaynak yok.** Mutlak maksimum çalışma limitiyle eşit sayılamaz. | SoC/PMIC bileşen sınırları kart konektörü mutlak maksimumu olarak kullanılmadı. | Üretici ürün sayfalarında mutlak maksimum tablosu yok; resmi board-spec sayfası: https://docs.t3gemstone.org/en/boards/o1/introduction |
| Kısa süreli aşım toleransı (V ve süre) | **doğrulanamadı.** Resmi teknik sayfada impuls/overshoot gerilimi veya süre sınırı yok. | **Hayır / kaynak yok.** 12 V üzeri transient için tolerans ileri sürülemez. | Üst sınırın üzerinde herhangi bir izin verilen süre/gerilim tahmini yapılmadı. | T3 Gemstone O1 resmi teknik sayfaları: https://t3gemstone.org/en/products/o1 ve https://t3gemstone.org/en/shop/o1 |
| Girişte TVS/OVP, seri koruma veya filtre | **doğrulanamadı.** Pazarlama/teknik özellik sayfası bir koruma devresi belirtmiyor. T3 resmi donanım deposunda V0.2 şema PDF’i mevcut; bu oturumdaki erişim PDF içeriğini okumadı. | **Bilinmiyor.** Kaynağın web sayfasında yazmaması koruma yok anlamına gelmez. | Şemadan/ürün görselinden koruma devresi çıkarılmadı. | T3 resmi donanım deposu, `design/t3-gem-o1-v0_2.pdf`: https://github.com/t3gemstone/hardware/blob/main/design/t3-gem-o1-v0_2.pdf |
| Mevcut PDU tepe değeri ile karşılaştırma | **HESAP (kart girdisi):** ≤11.41 V. Resmi 12.0 V DC çalışma üst sınırına göre en az `12.00−11.41=0.59 V` sayısal fark vardır. | **Normal DC aralığı bakımından evet.** Fiziksel ölçüm veya transient dayanımının kanıtı değildir. | 11.41 V değeri PDU hesap girdisidir; tezgâh ölçümü değildir. | PDU `docs/START-HERE.md` ve D-002 paket girdisi; T3 üretici spec bağlantısı yukarıda. |

## Öneri
PDU O1 anlık sınırını **12.0 V olarak koru**: bu değer üreticinin harici DC çalışma aralığının üst ucuyla uyumludur ve verilen HESAP tepe ≤11.41 V değeri 0.59 V altındadır. Bu, mutlak maksimumu veya geçici aşım toleransını kanıtlamaz; U-002’yi üreticiden bu iki yazılı sınır istenene kadar açık bırak.

## Kanıt
- T3 Gemstone, *T3 GEMSTONE O1 – Technical Specs / FAQ*, Power: External/DC connector 5–12 V / 5 A; USB-C PD 5–9 V / 3 A ayrı giriş. Resmi ürün sayfası: https://t3gemstone.org/en/products/o1
- T3 Gemstone, *Buy the T3 Gemstone O1*, Product Information: external input 5–12 V / 5 A ve USB-C PD 5–9 V / 3 A. Resmi mağaza sayfası: https://t3gemstone.org/en/shop/o1
- T3 Gemstone Foundation docs, *Board Specifications → Power Input*: resmi kart spec sayfası; okunabilir metin dökümünde giriş limitleri/absolute maximum ve transient süre tablosu yok. https://docs.t3gemstone.org/en/boards/o1/introduction
- T3 Gemstone resmi hardware repository, `design/t3-gem-o1-v0_2.pdf` (33 sayfalık v0.2 board schematic): https://github.com/t3gemstone/hardware/blob/main/design/t3-gem-o1-v0_2.pdf
- **HESAP girdisi:** PDU tepe ≤11.41 V; 12.00−11.41=0.59 V nominal işletim aralığı farkı. Simülasyon/hesap fiziksel O1 connector ölçümü değildir.

## Açık varsayımlar
- **VARSAYIM:** PDU `/O1` çıkışı Gemstone'un harici DC güç konektörüne uygulanacak; USB-C PD girişine değil.
- **VARSAYIM:** 5–12 V/5 A üretici ürün sayfasındaki aralık; uygun kaynak koşullarında normal çalışma girişidir. Üretici bunu absolute maximum olarak tanımlamıyor.
- **AÇIK:** PDU'nun 11.41 V HESAP tepe değeri gerçek kartta ölçülmedi; tasarım değeridir.

## Doğrulanamayanlar
- T3 Gemstone O1 harici DC konektörü için **mutlak maksimum giriş gerilimi** — **doğrulanamadı**; resmi ürün ve board-spec sayfaları yalnız 5–12 V / 5 A çalışma bilgisi veriyor. https://t3gemstone.org/en/products/o1 and https://docs.t3gemstone.org/en/boards/o1/introduction
- Kısa süreli **aşımın izin verilen gerilimi ve süresi** — **doğrulanamadı**; resmi ürün sayfalarında transient/overshoot rating yok. https://t3gemstone.org/en/products/o1
- Harici girişteki TVS/OVP veya diğer koruma elemanları ve seviyeleri — **doğrulanamadı**; resmi şema PDF’i bulundu fakat PDF içeriği bu oturumda okunabilir olarak alınamadı. https://github.com/t3gemstone/hardware/blob/main/design/t3-gem-o1-v0_2.pdf
