# TPS259824ONRGET / RGE0024M acceptance

2026-10-19: physical pin map and disposable placement accepted for prototype layout.

TI TPS259824ONRGET, VQFN RGE0024M, SLVSEI3D revised May 2026, pin map p5, package/land/stencil pp55-57, drawing 4223975/B 03/2018.
Source: https://www.ti.com/lit/ds/symlink/tps25982.pdf ; local hardware/_datasheets/tps25982.pdf.
Symbol PDU:TPS259824ONRGET; footprint PDU:TPS25982_RGE0024M.

- Physical 1 -> symbol 1 IN (power_in) -> pad 1 at (-1.9125, -1.25) mm, 0.575 x 0.24 mm; top view, counterclockwise from upper-left pin1.
- Physical 2 -> symbol 2 IN (power_in) -> pad 2 at (-1.9125, -0.75) mm, 0.575 x 0.24 mm; top view, counterclockwise from upper-left pin1.
- Physical 3 -> symbol 3 IN (power_in) -> pad 3 at (-1.9125, -0.25) mm, 0.575 x 0.24 mm; top view, counterclockwise from upper-left pin1.
- Physical 4 -> symbol 4 GND (power_in) -> pad 4 at (-1.9125, 0.25) mm, 0.575 x 0.24 mm; top view, counterclockwise from upper-left pin1.
- Physical 5 -> symbol 5 GND (power_in) -> pad 5 at (-1.9125, 0.75) mm, 0.575 x 0.24 mm; top view, counterclockwise from upper-left pin1.
- Physical 6 -> symbol 6 EN/UVLO (input) -> pad 6 at (-1.9125, 1.25) mm, 0.575 x 0.24 mm; top view, counterclockwise from upper-left pin1.
- Physical 7 -> symbol 7 ITIMER (passive) -> pad 7 at (-1.25, 1.9125) mm, 0.24 x 0.575 mm; top view, counterclockwise from upper-left pin1.
- Physical 8 -> symbol 8 ILIM (passive) -> pad 8 at (-0.75, 1.9125) mm, 0.24 x 0.575 mm; top view, counterclockwise from upper-left pin1.
- Physical 9 -> symbol 9 IMON (passive) -> pad 9 at (-0.25, 1.9125) mm, 0.24 x 0.575 mm; top view, counterclockwise from upper-left pin1.
- Physical 10 -> symbol 10 RETRY_DLY (passive) -> pad 10 at (0.25, 1.9125) mm, 0.24 x 0.575 mm; top view, counterclockwise from upper-left pin1.
- Physical 11 -> symbol 11 NRETRY (passive) -> pad 11 at (0.75, 1.9125) mm, 0.24 x 0.575 mm; top view, counterclockwise from upper-left pin1.
- Physical 12 -> symbol 12 LDSTRT (input) -> pad 12 at (1.25, 1.9125) mm, 0.24 x 0.575 mm; top view, counterclockwise from upper-left pin1.
- Physical 13 -> symbol 13 PG (open_collector) -> pad 13 at (1.9125, 1.25) mm, 0.575 x 0.24 mm; top view, counterclockwise from upper-left pin1.
- Physical 14 -> symbol 14 GND (power_in) -> pad 14 at (1.9125, 0.75) mm, 0.575 x 0.24 mm; top view, counterclockwise from upper-left pin1.
- Physical 15 -> symbol 15 dVdt (passive) -> pad 15 at (1.9125, 0.25) mm, 0.575 x 0.24 mm; top view, counterclockwise from upper-left pin1.
- Physical 16 -> symbol 16 IN (power_in) -> pad 16 at (1.9125, -0.25) mm, 0.575 x 0.24 mm; top view, counterclockwise from upper-left pin1.
- Physical 17 -> symbol 17 OUT (power_out) -> pad 17 at (1.9125, -0.75) mm, 0.575 x 0.24 mm; top view, counterclockwise from upper-left pin1.
- Physical 18 -> symbol 18 OUT (passive) -> pad 18 at (1.9125, -1.25) mm, 0.575 x 0.24 mm; top view, counterclockwise from upper-left pin1.
- Physical 19 -> symbol 19 OUT (passive) -> pad 19 at (1.25, -1.9125) mm, 0.24 x 0.575 mm; top view, counterclockwise from upper-left pin1.
- Physical 20 -> symbol 20 OUT (passive) -> pad 20 at (0.75, -1.9125) mm, 0.24 x 0.575 mm; top view, counterclockwise from upper-left pin1.
- Physical 21 -> symbol 21 OUT (passive) -> pad 21 at (0.25, -1.9125) mm, 0.24 x 0.575 mm; top view, counterclockwise from upper-left pin1.
- Physical 22 -> symbol 22 OUT (passive) -> pad 22 at (-0.25, -1.9125) mm, 0.24 x 0.575 mm; top view, counterclockwise from upper-left pin1.
- Physical 23 -> symbol 23 OUT (passive) -> pad 23 at (-0.75, -1.9125) mm, 0.24 x 0.575 mm; top view, counterclockwise from upper-left pin1.
- Physical 24 -> symbol 24 OUT (passive) -> pad 24 at (-1.25, -1.9125) mm, 0.24 x 0.575 mm; top view, counterclockwise from upper-left pin1.
- Physical 25 -> symbol 25 IN_EP (power_in) -> pad 25 at (0, -0.625) mm, 2.7 x 1.45 mm; top view, counterclockwise from upper-left pin1.
- Physical 26 -> symbol 26 GND_EP (power_in) -> pad 26 at (0, 0.925) mm, 2.7 x 0.85 mm; top view, counterclockwise from upper-left pin1.

24 perimeter leads plus two exposed pads reconcile to 26 symbol pins and 26 numbered copper pads. Exposed pad25 is VIN, pad26 is GND, never one common thermal pad. Four unnumbered paste-only rectangles implement the TI split stencil (two 1.188 x1.3 mm, two 1.188 x0.76 mm). Rounded lead radius 0.05 mm. EP coordinates are in the same top view as the perimeter; no mirror. No mechanical holes or embedded thermal vias; thermal via placement remains a PCB task.

Evidence: .konnect/diagnostics/efuse-place-results.json and efuse-read-results.json show actual live IPC placement and pad readback; every numbered pad coordinate/size matches the requested TI dimensions. efuse-accepted.svg, efuse-accepted-detail.png and symbols-acceptance.png were inspected. Source page images efuse-p56.png/efuse-p57.png were inspected. Footprint has pin1 mark, 4x4 mm fab outline and courtyard. Disposable reference text overlaps the pads; field placement remains a tooling/layout issue, not a pin-map error.

This record does not qualify protection behavior, thermal performance, solder process or complete board readiness.
