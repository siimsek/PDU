# tasks/ — görev kartları

| Dosya | Ne | Yazan |
|---|---|---|
| `T-xxx.md` | BUILDER uygulama kartı | BUILDER (THINKER taslak: `Durum: Draft`) |
| `R-xxx.md` | THINKER inceleme kartı → çıktı `reviews/R-xxx.md` | THINKER / kullanıcı |
| `D-xxx.md` | THINKER karar notu kartı → çıktı `decisions/D-xxx-*.md` | THINKER / kullanıcı |
| [`queue.md`](queue.md) | sıra + durum (kartla aynı) | herkes |
| [`backlog.md`](backlog.md) | engelleyici olmayan bulgular, sonraki işler (tek satır) | herkes |
| [`BLOCKED-ON-USER.md`](BLOCKED-ON-USER.md) | kullanıcı kararı/ölçümü bekleyen `U-xxx` maddeleri | herkes |
| `done/` | biten kartlar (`git mv`) | BUILDER |

Kurallar: şablon [`TEMPLATE.md`](TEMPLATE.md); zorunlu alanlar ve kuyruk tutarlılığı `python scripts/check_workflow.py` ile denetlenir. Boyut S ≤ ~30 dk, M ≤ ~90 dk, L yasak. Bir karta en çok 2 inceleme turu. Ayrıntı: [`docs/WORKFLOW.md`](../docs/WORKFLOW.md).

Paket: `python scripts/make_pack.py --task <ID> --for {codex|chatgpt|checker}` → `packs/<ID>-<for>.md` (git'te yok).
