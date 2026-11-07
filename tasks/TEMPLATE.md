# T-xxx — <tek satırlık başlık>

- **ID:** T-xxx (BUILDER uygulama) / R-xxx (THINKER inceleme) / D-xxx (THINKER karar notu)
- **Rol:** BUILDER | THINKER
- **Boyut:** S (≤ ~30 dk) | M (≤ ~90 dk) — L yasak, böl
- **Model önerisi:** Opus (mimari/zor hata) | Sonnet (uygulama/belge) | Haiku (mekanik)
- **Durum:** Draft | Ready | InProgress | Review | Done | Blocked
- **Dal adı:** wp/<kart-id>
- **Bağımlılık:** — | <kart-id>, ...

## Hedef
En çok 3 satır: ne değişecek, neden.

## Girdiler
- Okunacak minimum dosya yolları (bölüm/satır belirt). Sonuç dosyaları THINKER kartında yalnız "(sonuç)" etiketiyle ve karşılaştırma turunda.

## İzinli yazma yolları
- `yol/` (gerekçe)
- `HANDOFF.md`, `tasks/queue.md`, bu kartın Durum'u

## Yasak
- Karta özgü yasaklar.

## Kabul kriterleri
- Ölçülebilir ve komutlu: `komut` → beklenen çıktı/sayı.

## Durdurma koşulu
- Aynı hata 2 denemede çözülmezse dur, Blocked; eksik karar → BLOCKED-ON-USER.

## Çıktı dosyaları
- `yol/dosya`
