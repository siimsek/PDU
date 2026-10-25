# WP1 rev3 – ChatGPT bağımsız inceleme talebi (3. tur)

**Durum:** 2. tur (ChatGPT review 6390966776, karar **RET**, PR #1) bulgularına yanıt: `CHATGPT_REVIEW_RESPONSE.md` → "Tur 2". 3. tur incelemesi bekleniyor.
**Kaynak:** zip paketi yok; ChatGPT repo dosyalarını GitHub bağlantısıyla doğrudan okur (repo özel → GitHub bağlantısı açık olmalı). Bütünlük: `MANIFEST-SHA256.txt`. Üretici modelleri (yeniden dağıtılamaz) repoda yoktur – yalnız yol ve sha256 ile atıf.

## İstem (kopyala-yapıştır)

```
Sen bağımsız bir güç elektroniği inceleyicisisin. GitHub siimsek/PDU PR #1 (https://github.com/siimsek/PDU/pull/1),
dal wp/baseline-2026-10-24, en son commit (PR'daki HEAD) – "WP1 2026-10-25-o1-ovp" önerisinin rev3'ü: RAW ile VOUT arasında
TPS48000-Q1 + 4× CSD18540Q5B + TLV3601 + REF35409 + TPS7A1650 hibrit global OVP.
Sert kriterler: O1 portunda ANLIK tepe ≤ 12,0 V; normal bus ≤ 11,1605 V; 11,22 V yalnız yanlış-tetik test seviyesi (ayrı kontroller).

Türkçe yanıtla:
1. docs/proposals/2026-10-25-o1-ovp/CHATGPT_REVIEW_RESPONSE.md "Tur 2": 2. tur her bulgunun (P0-01…P2-02) durumu ve kanıtı yeterli mi?
2. P0-01: simulation/proposals/2026-10-25-o1-ovp/rsns_power.py + rsns-power.json, hardware/proposals/2026-10-25-o1-ovp/candidate-bom.csv
   (RSNS10A/RSNS10B/RSNS11 1206 ERA-8ARB, RBLD11 1206) – derating ve kelepçe varsayımları doğru mu?
3. P0-02: gen_o1ovp.py / run_o1ovp.py / verify_candidate.py – O1_GLOBAL_PEAK (0..tran sonu) ve normal-rejim pencereleri
   (ramp 0–14,9 / 25,1–40 ms; short 24–29 / 55–80 ms; 46–50 ms yalnız INFO) gerekçesi yeterli mi?
4. P0-03 (açık): model rev3 (ov→ovs; model-compare/ + results/model-compare/model-compare.json eski/yeni regresyon) sonrası
   4 ESL deck (c185/c165-esr12m5-esl2n-typ/wchi) 12,264–12,270 ms'de duruyor; kök neden açılışta RAW ≈13,33 V çınlama →
   komparatör yanlış tetiği (RESULTS.md §A). solver-study/ (20/20 tamamlanmadı) ve slew-study/ (RPU10 10/100/330/1k Ω;
   330 Ω ESL deck'lerini tamamlıyor ama efuse-ovp-s023-wchi toparlanma rejimini bozuyor) – sonraki en düşük riskli adım?
   regime-selftest/: FET hiç açılmazsa runner/doğrulayıcı FAIL veriyor mu?
5. P1-01: soa-study/ + results/soa-study/fet-soa-study.json (SLPS488B Fig. 10 okuması) yöntemi ve varsayımları.
6. BUDGET.md §0 koşullu marj terminolojisi, BENCH-TEST.md B16–B19.
   u3-latch-study/ (N-01): 100 mΩ stres köşesi U3 açılmaz varsayımıyla 12,50–13,04 V – değerlendirme ve kapatma yolu.
7. Sonuç: kabul / koşullu kabul / ret; en fazla 10 aksiyon.
Uydurma veri üretme; bilmediğin yerde "doğrulanamadı" yaz. Simülasyon silikon kanıtı değildir.
Sohbette yanıtladıktan sonra tam incelemeni GitHub PR #1'e yorum olarak da gönder.
```
