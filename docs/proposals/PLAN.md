# PDU öneri planı (WP1–WP8)

Durum tarihi: 2026-10-25 (Europe/Istanbul). Bu plan yalnızca **öneri** dosyalarını kapsar; ana şema/PCB, `hardware/pdu-current-bom.csv`, `simulation/pdu-current.net` ve kayıtlı baseline sonuçları değiştirilmez.
Kaynak hiyerarşisi: KiCad > Konnect > hash-eşleşen sonuçlar > durum dokümanları > tarihli notlar.

| WP | Kapsam | Bağımlılık | Ana risk | Durum |
|---|---|---|---|---|
| WP1 | O1 aşırı gerilim koruması (bu paket, `2026-10-25-o1-ovp`) | — | Kısa-devre (buck high-side short) dalga formunda 12,0 V'a marj **1,2–9 mV (bütçe)**; sim wchi: c92/1 mΩ 4 mV PASS, **c92/12,5 mΩ 12,037 V FAIL → BLOKLAYICI**; G1 (TLV3601 VCM ofseti) açık | Simülasyon tamam, fiziksel test yok, ChatGPT incelemesi bekleniyor |
| WP2 | Kullanıcı kararı: bus setpoint'i düşürme (ör. 11,0 → 10,8 V) veya daha hızlı sürücü/daha fazla RAW C | WP1 sonuçları | O1/S2E alt sınırları ve ESC tarafı etkisi | Karar bekliyor |
| WP3 | 7,5 A / 82,5 W yük basamağı geçici penceresi (şu an yalnızca *tracking*) ve COUT nitelendirmesi | WP1 (RAW/VOUT ayrımı COUT'u RAW'a taşır) | 0,45→4,5 A dışındaki basamaklar repo kriteri değil | Açık |
| WP4 | U3/U4 TPS259824 SOA/termal/timer doğrulaması (OVP sonrası) | WP1 | eFuse modeli davranışsal; esr100m köşesinde `timestep too small` (xu3.ena) | Açık |
| WP5 | KiCad aktarımı (şema + PCB yerleşim, güç yolu 4× CSD18540Q5B, Kelvin ayrımı) | WP1, WP2 kararı | Parazitik L ve yerleşim, simülasyonda yok | `KICAD-TRANSFER.md` hazır, uygulanmadı |
| WP6 | Tezgâh testi (BENCH-TEST.md) | WP5 kartı | Sim ≠ silikon; tPD/IPD tipik değerler | Yapılmadı |
| WP7 | Tedarik (TR öncelikli, yurt dışı yedek) ve BOM birleştirme | WP2, WP5 | ERA-3ARB2051V ve TPS48000 TR'de bulunamadı; DigiKey'de ERA-3ARB2051V listelenmiyor | Kısmi |
| WP8 | CI: öneri ngspice iş akışı + bağımsız doğrulayıcı (`verify_candidate.py`) | WP1 | ngspice sürüm farkı (Ubuntu apt vs Debian 44.2) | Taslak `.github/workflows/proposal-ngspice.yml` |

Kritik yol: WP1 → (WP2 kullanıcı kararı) → WP5 → WP6. WP2 kararı verilmeden WP5'e geçilmemesi önerilir, çünkü kısa-devre marjı sınırda.
