# WP2 2026-10-25-uvlo – ChatGPT bağımsız inceleme talebi (1. tur)

**Durum:** 1. tur inceleme bekleniyor. Yanıt `CHATGPT_REVIEW_RESPONSE.md` dosyasına işlenecek.
**Kaynak:** zip paketi yok. ChatGPT dosyaları GitHub bağlantısıyla doğrudan okur (repo özel, GitHub bağlantısı açık olmalı). Bütünlük kontrolü `MANIFEST-SHA256.txt` ile yapılır.
**İncelenecek commit:** `<FINAL_COMMIT_SHA>` (entegrasyondan sonra doldurulacak; PR'daki HEAD ile aynı olmalı).

## İstem (kopyala-yapıştır)

```
Sen bağımsız bir güç elektroniği inceleyicisisin. Repo: GitHub siimsek/PDU, PR #1 (https://github.com/siimsek/PDU/pull/1),
commit <FINAL_COMMIT_SHA>. Konu: "WP2 2026-10-25-uvlo" önerisi. Bu öneri 20,0 V'ta garanti açılış/yeniden başlatma,
18,0 V aşırı deşarj kapanması ve motorboating'siz UVLO sağlamayı hedefliyor.
Seçilen çözüm C3: TLV3202 (A: VIN UVLO, REF35409 tabanlı eşik; B: ≥ 60 ms oranlı yeniden başlatma zamanlayıcısı) +
TMUX1102 anahtarlı bölücü histerezisi. LM70880 RUV1 DNP. WP1 OVP hibriti (TPS48000 + TLV3601 + REF35409 + TPS7A1650) DEĞİŞMEDİ.
Sert kriterler: O1 anlık tepe ≤ 12,0 V; normal bus ≤ 11,1605 V; 11,22 V yalnız OVP yanlış tetik uyarısı. Açık maddeler: P0-03, N-01.

Okunacak dosyalar:
- docs/proposals/2026-10-25-uvlo/{REQUIREMENTS,ARCHITECTURE,BUDGET,MODELS,RESULTS,KICAD-TRANSFER,BENCH-TEST}.md
- simulation/proposals/2026-10-25-uvlo/{uvlo_budget.py,gen_uvlo.py,run_uvlo.py,verify_uvlo.py,pdu-uvlo-behavioral.lib,
  pdu-uvlo-block.inc,pdu-circuit-uvlo.inc,test-cases-uvlo.json}, results/{uvlo-budget.json,uvlo-verify.json}
- hardware/proposals/2026-10-25-uvlo/{candidate-bom.csv,SOURCING.md,sourcing.csv}
- docs/proposals/2026-10-25-uvlo/MANIFEST-SHA256.txt

Türkçe yanıtla:
1. Gereksinim yorumu: E_START = 20,0 V EMF, R_total 0,25 Ω, P_IN 94,05 W (η 0,88 varsayım), MARGIN_DYN 0,10 V – uygun mu?
2. Bütçe: katı doğrusal köşe yöntemi, E_REF %0,296, ERA-3ARB %0,4, VIO_C3 (CMRR gerçek REFD'de), RHB/RDEN/RUV2 katı %3.
   Marjlar a +18,5 / b +23,4 / c +29,5 / d +156 / e +71 mV. Eksik veya iyimser terim var mı?
3. C3 topolojisi: VCC < 2,7 V bölgesi, TMUX1102 SEL eşiği, S_UV ≤ 4,90 V (26 V), OUTA → RTT/CTT, DTT + RDIS boşaltma.
   Alternatifler A0/A1/B/D/C2'nin ret gerekçeleri doğru mu?
4. Modeller (MODELS.md): UVLO_BUCK COMP 0–5 V kenetlemesi (windup artefaktı) gerekçesi yeterli mi, yoksa bir sorunu mu gizliyor?
5. Sonuçlar (RESULTS.md): 300 µs dip sonrası 30,6 ms'de yeniden başlama (kısmi zamanlayıcı boşalması), VOUT 11,43 V anormal rejim
   geçişi (INFO), RAW 12,87 V aşımı (U10 UVLO'su VIN'den). TPS48000 TDRV_EN yeniden kurma gecikmesi modelde yok → P0-03 riski.
   Değerlendirme ve en düşük riskli çözüm?
6. Doğrulayıcı: bilinen-başarısız regresyonlar (baseline 180k/10k, yanlış RBU, nodelay seq) gerçekten FAIL veriyor mu?
   Pencereler sert kriterleri gevşetiyor mu?
7. Tedarik riski (ERA-3ARB, Türkiye fiziksel stok yok/doğrulanamadı) ve BENCH-TEST B-U1…B-U14 yeterli mi?
8. Sonuç: kabul / koşullu kabul / ret; en fazla 10 aksiyon.
Uydurma veri üretme; bilmediğin yerde "doğrulanamadı" yaz. Simülasyon silikon kanıtı değildir.
Sohbette yanıtladıktan sonra tam incelemeni GitHub PR #1'e yorum olarak da gönder.
```
