# PDU — güncel ilk PCB yerleşimi

19 Ekim2026. Önceki yerleşim kaydı [arşivde](../docs/archive/pcb-layout-before-calculation-sync-20261019.md) korunur. Bu kart yönlendirilmiş veya üretime hazır değildir.

## Kayıtlı durum

- 72 footprint; F1 MPN/footprint bekliyor. Geçici101,6×76,2 mm sınır, köşe başlangıcı50,8/50,8 mm. Kasa onayı yok.
- U1/U2=`PDU:LM70880_RRX0029B_RectLands`: prototip bakır yaklaşımı; üretici CAD'inin aynısı değil.
- U3/U4=`PDU:TPS25982_RGE0024M`: pad25=IN, pad26=GND ayrı.
- Q1=`PDU:TDSON-8-1_Konnect`: stock bakır/paste, uyarlanmış maske.
- COUT1–8=`PDU:TDK_C5750_2220_Recommended`:22 µF100 V2220; sekiz canlı pad geri okumasında1=VOUT/2=GND,1,30×4,50 mm geometri doğrulandı.
- RIMON1/2=806 Ω. REN1/2, büyük COUT kılıfları için sağa1,27 mm alındı; courtyard çakışmaları giderildi.
- Giriş, iki faz, kapasitör bankları, O1/S2E ve ortak kontrol için ilk blok yerleşimi var. Yüksek frekanslı döngü/Kelvin/termal/EMI kabulü açık.

## Son kaydedilmiş kontroller

- İz sayısı0. DRC197 hata: tamamı bağlantısız öğe.301 uyarı:199 silk-over-copper,72 alan eşliği,21 silk overlap,5 kütüphane eşliği,3 silk-edge,1 eksik F1.
- Bakır kısa devresi/clearance/courtyard hatası raporlanmıyor. Bu sonuç bağlantısız padleri fiziksel olarak bağlamaz.
- Şemadan PCB dry-run son kayıtta noop; yalnız F1 atanmamış. Şema short0/ERC0/0.
- 35 µm nominal bakır/31,5 µm hesap varsayımıyla9 sınıf/46 ağ profili.70 µm uygulanmış sayılmaz. Açık editör profili eski önbellekten geri yazabilir.

Kanıt: [DRC](../.konnect/diagnostics/cout-hv-main-drc.json), [pad özeti](../.konnect/diagnostics/no-measurement-final-pad-summary.json), [bağımsız denetim](no-measurement-final-audit.md), [PCB PNG](PDU_blocks_placed.png).

## Sıradaki işler

O1 OVP ve gerçek kontrol döngüsü tasarımını kapat; kesin F1/MPN/mekanik girdileri tamamla. Sonra güç döngüleri, Kelvin, toprak düzlemi, termal via, boyun/via akım hesabı ve yönlendirme. Metin alanları/kütüphane uyuşmazlıkları ve stencil üretim incelemesi ayrıca açık. Mevcut Konnect API referans/değer metin konumlarını ve Description alanını düzeltemiyor; D1–D3 refresh'te desteklenmeyen alan var.

[Proje devam noktası](../docs/PROJECT-STATE.md), [özel parça kontrolü](../docs/REVIEW-CHECKLIST.md), [yönlendirme kuralları](../docs/SON-TESLIM.md).
