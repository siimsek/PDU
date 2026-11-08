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
| [R-005](done/R-005.md) | THINKER | S | — (tur 2) | Done |
| [T-007](done/T-007.md) | BUILDER | M | T-006 | Done |
| [R-006](done/R-006.md) | THINKER | S | T-007 | Done |
| [T-008](done/T-008.md) | BUILDER | M | T-007, T-005b | Done |
| [R-007](done/R-007.md) | THINKER | S | T-008 | Done |
| [T-017](done/T-017.md) | BUILDER | S | — | Done |
| [R-008](done/R-008.md) | THINKER | S | T-017 | Done |
| [T-010](done/T-010.md) | BUILDER | M | T-017, R-008 | Done |
| [T-009](done/T-009.md) | BUILDER | M | T-010 | Done |
| [R-009](done/R-009.md) | THINKER | M | T-010, T-009 | Done |
| [T-011](done/T-011.md) | BUILDER | M | T-010 | Done |
| [R-010](done/R-010.md) | THINKER | S | T-011 | Done |
| [D-008](done/D-008.md) | THINKER | S | — | Done |
| [T-012](done/T-012.md) | BUILDER | M | T-011 | Done |
| [R-011](done/R-011.md) | THINKER | S | T-012 | Done |
| [T-013](done/T-013.md) | BUILDER | M | T-012, D-006 | Done |
| [R-012](done/R-012.md) | THINKER | S | T-013 | Done |
| [R-013](done/R-013.md) | THINKER | S | T-013, R-012 | Done |
| [T-014](done/T-014.md) | BUILDER | S | T-013, T-005a, T-005b | Done |
| [R-002](done/R-002.md) | THINKER | M | T-014 | Done |
| [D-009](done/D-009.md) | THINKER | S | T-013, T-014 | Done |
| [R-014](done/R-014.md) | THINKER | S | T-014, R-002, D-009 | Done |
| [T-018](T-018.md) | BUILDER | S | T-014 | Review |
| [T-019](T-019.md) | BUILDER | M | T-014 | Draft |
| [T-020](done/T-020.md) | BUILDER | M | T-013, D-009 | Done |
| [T-021](T-021.md) | BUILDER | M | T-020 | Review |
| [T-025](done/T-025.md) | BUILDER | S | — | Done |
| [D-010](done/D-010.md) | THINKER | M | T-021 | Done |
| [D-011](done/D-011.md) | THINKER | M | T-021 | Done |
| [T-022](done/T-022.md) | BUILDER | M | T-021, D-011 | Done |
| [R-018](done/R-018.md) | THINKER | M | T-022 | Done |
| [D-012](done/D-012.md) | THINKER | M | T-022 | Done |
| [T-023](T-023.md) | BUILDER | M | T-022 | InProgress |
| [T-024](T-024.md) | BUILDER | M | T-023 | Draft |

Paralel yürütülebilir: THINKER kartları birbirinden ve BUILDER kartlarından bağımsız. THINKER `queue.md`'yi değiştirmez (paralel PR çakışması); yalnız kendi kartının Durum'unu yazar, BUILDER birleştirirken kuyruğu eşitler.
