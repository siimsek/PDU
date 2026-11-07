# Görev kuyruğu

Sıra yukarıdan aşağı. Durum kartla aynı olmalı (`python scripts/check_workflow.py` denetler). Biten kart `tasks/done/`'a taşınır, satır burada `Done` kalır.

| ID | Rol | Boyut | Bağımlılık | Durum |
|---|---|---|---|---|
| [T-001](done/T-001.md) | BUILDER | S | — | Done |
| [R-001](R-001.md) | THINKER | M | — | Ready |
| [T-002](T-002.md) | BUILDER | S | T-001 | Ready |
| [T-003](T-003.md) | BUILDER | M | T-001 | Ready |
| [D-001](D-001.md) | THINKER | M | — | Ready |
| [D-002](D-002.md) | THINKER | S | — | Ready |
| [T-004](T-004.md) | BUILDER | S | D-001 (Done) | Draft |
| [T-005a](T-005a.md) | BUILDER | M | T-002 | Draft |
| [T-005b](T-005b.md) | BUILDER | M | T-002, T-004 | Draft |
| [T-006](T-006.md) | BUILDER | M | T-002, T-005a | Draft |
| [T-007](T-007.md) | BUILDER | M | T-006 | Draft |
| [T-008](T-008.md) | BUILDER | M | T-007, T-005b | Draft |
| [T-009](T-009.md) | BUILDER | M | T-008 | Draft |
| [T-010](T-010.md) | BUILDER | M | T-009 | Draft |
| [T-011](T-011.md) | BUILDER | M | T-010 | Draft |
| [T-012](T-012.md) | BUILDER | M | T-011 | Draft |
| [T-013](T-013.md) | BUILDER | M | T-012, T-003 + kullanıcı kart ölçüsü kararı | Draft |
| [T-014](T-014.md) | BUILDER | S | T-013, T-005a, T-005b | Draft |
| [R-002](R-002.md) | THINKER | M | T-014 | Draft |

Paralel yürütülebilir: T-001 ∥ R-001 ∥ D-001 ∥ D-002 (farklı roller, farklı yazma yolları). T-002/T-003 T-001'den sonra.
