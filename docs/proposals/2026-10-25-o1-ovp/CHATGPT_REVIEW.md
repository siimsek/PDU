# WP1 – ChatGPT bağımsız inceleme talebi

**Durum:** ChatGPT incelemesi bekleniyor. Yanıt `CHATGPT_REVIEW_RESPONSE.md` dosyasına (şu an boş) yapıştırılmalıdır.
**Ek:** `review-bundle.zip` (manifest: `MANIFEST-SHA256.txt`; üretici modelleri dahil değildir).

## İstem (kopyala-yapıştır)

```
Sen bağımsız bir güç elektroniği inceleyicisisin. Ekteki review-bundle.zip, IDA PDU (6S LiPo 20–26 V → 11 V bus, 7 A / 77 W; 7,5 A / 82,5 W aşaması) için
"WP1 2026-10-25-o1-ovp" önerisidir: buck çıkışı (RAW) ile bus (VOUT) arasında TPS48000-Q1 + 4× CSD18540Q5B (sırt sırta, 2 paralel) +
TLV3601 + REF35409 + TPS7A1650 ile hibrit global aşırı gerilim koruması. Hedef: T3 Gemstone O1 portunda en yüksek ANLIK gerilim ≤ 12,0 V
(DC/transient belirsizliği varsayım olarak işaretlendi).

Lütfen Türkçe yanıtla ve şunları yap:
1. MANIFEST-SHA256.txt ile zip içeriğini karşılaştır; uyuşmazlık varsa belirt.
2. docs/proposals/2026-10-25-o1-ovp/BUDGET.md ve simulation/.../window_budget.py: her terimi GARANTİ (MIN/MAX) / TİPİK / VARSAYIM
   olarak sınıflandır; veri sayfası sayfa/tablo atıflarını kontrol et (SLUSEZ1B, SLPS488B, SNOSDB1E, SNAS809C, SBVS171F, SLVSEI3D).
   Özellikle: (a) A1 varsayımı – TLV3601 VIO'nun VCM≈4,1 V'ta ±5+4,1 mV kabulü; (b) tPD(INP_L) 1,05 µs'nin 47 nF test yükünden
   bizim 277 nC kapı yüküne aktarılması (çift sayım argümanı).
3. results/ ve o1ovp-results.json: buck-short-c92-esr12m5-wchi FAIL (12,0368 V) ve c92-wchi 4 mV marjı doğru yorumlanmış mı?
   Kriteri GEVŞETMEDEN hangi değişiklik (setpoint düşürme, daha hızlı kapı sürüşü, RAW kapasitesi, farklı FET/ölçek) en az riskle kapatır?
   Sayısal tahminini ve yanlış tetik (11,22 V) marjına etkisini ver.
4. Davranışsal modellerin (pdu-o1ovp-behavioral.lib) gizlediği riskleri listele (FET çığ, parazitik L, PD akımı, BST UVLO, TPS48000 pinleri).
5. KICAD-TRANSFER.md net ayrımı (14 düzenleme) ve candidate-bom.csv'de hata/eksik var mı?
6. Sonuç: "kabul / koşullu kabul / ret" ve gerekçe; en fazla 10 madde aksiyon listesi.
Uydurma veri üretme; bilmediğin yerde "doğrulanamadı" yaz. Simülasyonun silikon kanıtı olmadığını unutma.
```
