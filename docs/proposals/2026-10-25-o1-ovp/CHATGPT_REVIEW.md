# WP1 rev2 – ChatGPT bağımsız inceleme talebi (2. tur)

**Durum:** ChatGPT incelemesi bekleniyor (rev2). 1. tur (99a541a) bulgularına yanıt: `CHATGPT_REVIEW_RESPONSE.md`.
**Ek:** `review-bundle-rev2.zip` (manifest: `MANIFEST-SHA256.txt`; üretici modelleri dahil değildir – yalnız yol ve sha256 ile atıf).

## İstem (kopyala-yapıştır)

```
Sen bağımsız bir güç elektroniği inceleyicisisin. Ekteki review-bundle-rev2.zip, IDA PDU (6S LiPo 20–26 V → 11 V bus, 7 A / 77 W;
7,5 A / 82,5 W aşaması) için "WP1 2026-10-25-o1-ovp" önerisinin rev2'sidir: buck çıkışı (RAW) ile bus (VOUT) arasında TPS48000-Q1 +
4× CSD18540Q5B + TLV3601 + REF35409 + TPS7A1650 ile hibrit global OVP; rev2'de RAW bankı 16 × C5750X7S2A226M280KB.
Sert kriterler: T3 Gemstone O1 portunda ANLIK tepe ≤ 12,0 V; normal bus ≤ 11,1605 V; 11,22 V yalnız yanlış-tetik test seviyesi.

Türkçe yanıtla:
1. MANIFEST-SHA256.txt ile zip içeriğini karşılaştır.
2. CHATGPT_REVIEW_RESPONSE.md: 1. tur her bulgunun (P0-1…P2) durumu ve kanıtı yeterli mi? Kabul etmediğin varsa gerekçe ver.
3. BUDGET.md / window_budget.py: G/T/V/Ç sınıflandırmasını denetle; 165 µF "dürüst minimum" ve ESR 12,5 mΩ / ESL 2 nH makul mü?
   A1 (TLV3601 VIO @ VCM≈4,1 V) için hesaplanan tolerans (+7,87 mV @ 50 mV hedef) ve gate_discharge_wc.py (oran 0,9685) argümanı.
4. RESULTS.md: buck-short-c185/c165-esr12m5-esl2n-typ yakınsamaması (açılışta, pu_ovp, 12,26 ms) – teşhis doğru mu,
   kriteri gevşetmeden ve modeli bozmadan nasıl kapatılır?
5. KICAD-TRANSFER.md §2b pin tabloları ve candidate-bom.csv (yeni MPN'ler, COUT11 10 µF, CREF12 1 µF, CBYP13) hata/eksik.
6. Sonuç: kabul / koşullu kabul / ret; en fazla 10 aksiyon.
Uydurma veri üretme; bilmediğin yerde "doğrulanamadı" yaz. Simülasyon silikon kanıtı değildir.
```
