# G3 — kullanıcıdan gereken kararlar ve belgeler (en çok 8)

G1/G2 listelerinin yerini alır. Cevaplanmayan maddelerde G2 muhafazakâr varsayılanı geçerlidir (VARSAYIM).

| # | Karar / belge | Geçerli varsayılan | Değişirse etkilenen |
|---|---|---|---|
| 1 | **T3 Gemstone O1 datasheet'i** (gerçek mutlak maks giriş gerilimi) ve 12.0 V sınırının ölçüm belirsizliği payıyla mı uygulanacağı | 12.0 V sert, okunan tepe + belirsizlik ≤12.0 V | O1 marjı (HESAP 59 mV), COUT sayısı, BENCH T5c |
| 2 | **Tasarım ortam sıcaklığı / muhafaza / hava akışı** | 85 °C | LM70880 Tj 137.7 °C → FAIL; ≤72 °C ortamda geçer; direnç derating |
| 3 | **Yığılmış statik tolerans + yük adımı köşeleri:** üretimde bara ayarı (FB trim) mı, yoksa iki tolerans aynı anda değil kabulü mü? | İkisi birlikte → SİM F3 iki köşe FAIL | Trim seçilirse RFB2'ye paralel DNP trim direnci eklenir; aksi hâlde AÇIK kalır |
| 4 | **Ölçülmüş O1/S2E akımları** (sürekli/kalkış/tepe) | O1 zarfı 6.78 A, S2E 1.5 A kalkış | RILIM_O1 182 Ω (marj 0.45 A), port iz genişliği |
| 5 | **Batarya iç direnci, kablo uzunluğu/kesiti, hücre kesim politikası** | 20–200 mΩ, kablo 0.5–1 µH | F1 kesme kapasitesi (≥1040 A), hot-plug VIN tepe (SİM 42.1 V), UVLO düşüş politikası |
| 6 | **Molex PS-43045-001 + eş housing/crimp** ve **SMCJ33A** resmi datasheet'leri | Konnektör/TVS MPN AÇIK; TVS clamp 53.3 V VARSAYIM | J1–J3 seçimi; Q2/U5/U6/U10 mutlak maks payı (%82–89) |
| 7 | **DC sigorta + yuva** (≥10 A, ≥53.3 VDC, ≥1040 A kesme) datasheet'i | F1 MPN AÇIK | F1, I²t koordinasyonu |
| 8 | **MLCC serileri** (100 V 1210 4.7 µF, 25 V 0805 10 µF, küçük dekuplajlar) DC-bias eğrisiyle | 37 C satırı MPN'siz, Ceff %40–50 VARSAYIM | CIN/CEFOUT Ceff, VSAFE dV/dt, F4 sonucu |
