# Görev kuyruğu

Sıra yukarıdan aşağı. Durum kartla aynı olmalı (`python scripts/check_workflow.py` denetler). Biten kart `tasks/done/`'a taşınır, satır burada `Done` kalır.

| ID | Rol | Boyut | Bağımlılık | Durum |
|---|---|---|---|---|
| [T-001](done/T-001.md) | BUILDER | S | — | Done |
| [R-001](done/R-001.md) | THINKER | M | T-015 (tur 2) | Done |
| [D-003](done/D-003.md) | THINKER | M | — | Done |
| [D-004](done/D-004.md) | THINKER | M | — | Done |
| [T-015](done/T-015.md) | BUILDER | S | D-003, D-004 | Done |
| [T-002](done/T-002.md) | BUILDER | S | T-001 | Done |
| [T-003](done/T-003.md) | BUILDER | M | T-001 | Done |
| [D-001](done/D-001.md) | THINKER | M | — | Done |
| [D-002](done/D-002.md) | THINKER | S | — | Done |
| [D-005](done/D-005.md) | THINKER | S | D-002 | Done |
| [T-004](done/T-004.md) | BUILDER | S | D-001 (Done) | Done |
| [D-006](done/D-006.md) | THINKER | S | T-003 | Done |
| [T-005a](done/T-005a.md) | BUILDER | M | T-002 | Done |
| [R-003](done/R-003.md) | THINKER | M | — (tur 2: J2) | Done |
| [T-005b](done/T-005b.md) | BUILDER | M | T-002, T-004, R-003 | Done |
| [T-016](done/T-016.md) | BUILDER | S | R-003 tur 2 | Done |
| [T-006](done/T-006.md) | BUILDER | M | T-002, T-005a | Done |
| [D-007](done/D-007.md) | THINKER | S | — | Done |
| [R-004](done/R-004.md) | THINKER | S | T-006 | Done |
| [R-005](R-005.md) | THINKER | S | — (tur 2) | Ready |
| [T-007](done/T-007.md) | BUILDER | M | T-006 | Done |
| [R-006](done/R-006.md) | THINKER | S | T-007 | Done |
| [T-008](T-008.md) | BUILDER | M | T-007, T-005b | Ready |
| [T-009](T-009.md) | BUILDER | M | T-008 | Draft |
| [T-010](T-010.md) | BUILDER | M | T-009 | Draft |
| [T-011](T-011.md) | BUILDER | M | T-010 | Draft |
| [T-012](T-012.md) | BUILDER | M | T-011 | Draft |
| [T-013](T-013.md) | BUILDER | M | T-012, D-006 | Draft |
| [T-014](T-014.md) | BUILDER | S | T-013, T-005a, T-005b | Draft |
| [R-002](R-002.md) | THINKER | M | T-014 | Draft |

Paralel yürütülebilir: THINKER kartları birbirinden ve BUILDER kartlarından bağımsız. THINKER `queue.md`'yi değiştirmez (paralel PR çakışması); yalnız kendi kartının Durum'unu yazar, BUILDER birleştirirken kuyruğu eşitler.
