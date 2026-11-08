# R-002 tur 1 engelleyicisi: KiCad 10.0.7 ile taze ERC ve netlist (BUILDER çıktısı)

R-002 tur 1, PR #53: KOŞULLU, 1 engelleyici. Codex'in ortamında KiCad 9.0.2 kurulu olduğu için KiCad 10 şeması yüklenemedi. Bu dosya aynı commit için üretilen çıktıları kaydeder. Bağımsız doğrulama değildir; değerlendirme R-002 tur 2'nindir.

## Yöntem

- Kaynak: `wp/T-014` `5a2985cc18d0867dc3030feb3117807254bd96ef`, `git archive` ile temiz dizine çıkarıldı.
- Blob kontrolü (`git hash-object` = commit): `PDU.kicad_sch` 1f64061d70fe, `PDU.kicad_pro` 1b1ffa6f0ac0, `design/pdu_v2_spec.yaml` 88497c83ce83.
- Araç: `kicad-cli version` → 10.0.7. Komutlar temiz dizinde çalıştırıldı:
  - `kicad-cli sch erc --format json --severity-all`
  - `kicad-cli sch export netlist`

## Sonuçlar

| Kontrol | Sonuç | Dosya |
|---|---|---|
| ERC | exit 0; KiCad 10.0.7; **0 ihlal**. `ignored_checks` 4: `single_global_label`, `four_way_junction`, `simulation_model_issue`, `footprint_filter` | [erc.json](erc.json) |
| Netlist | exit 0; 180 bileşen, 74 net | [netlist.net](netlist.net) |
| Önceki T-014 netlistiyle fark | `date`, `source`, `tool` satırları hariç **0 satır** | [../netlist.net](../netlist.net) |
| R-002 karşılaştırıcısı (`reports/R-002/compare_netlist_spec.py`, blob aa3f582a, değiştirilmedi) | 180 ref kümesi eşleşti; değer/MPN/footprint 180 ref; 422 pin anahtarı; **0 fark**; spec anahtarı olmayan 26 düğüm. `input_*` dışındaki alanların tümü Codex'in `netlist-spec-check.json` çıktısıyla aynı | [netlist-spec-check.json](netlist-spec-check.json) |
| BUILDER karşılaştırıcısı (`check_consistency.py --schematic B1…B7`) | `pass: true`, 0 hata | [check-B1-B7.txt](check-B1-B7.txt) |

## Sınırlar

- **PyYAML bu makinede yok.** Karşılaştırıcı değiştirilmeden çalıştırıldı, ancak `yaml.safe_load` yerine geçici bir ayrıştırıcı kullanıldı (yalnız `parts` bölümü; tanımadığı satırda hata verir; repoya eklenmedi). Bu nedenle sonuç gerçek PyYAML ile doğrulanmış değildir. Sonuçların Codex çıktısıyla aynı olması bunu destekler; R-002 tur 2 `netlist.net` üzerinde gerçek PyYAML ile yeniden koşabilir.
- **`netlist.net` satır 4:** `source` alanındaki mutlak yerel yol `PDU.kicad_sch` ile değiştirildi (kişisel yol sızdırmama kuralı). Başka satır değişmedi.
- **Kişisel yol:** önceki `reports/g5/T-012…T-014/netlist.net` dosyalarının `source` alanında yerel yol var; arşivle birlikte 157 izli dosyada benzer yol bulunuyor. Geçmiş yeniden yazılmadı (yasak); backlog maddesi önerilir.

## Spec anahtarı olmayan 26 düğüm

| Düğümler | Ağ | Dayanak |
|---|---|---|
| U1, U2: AGND (17), PGND (23–26, 30) | /GND | Pin işlevi gereği toprak; spec'te ayrı anahtar yok (12 düğüm) |
| U3, U4: RETRY_DLY (10), NRETRY (11) | /GND | `reports/g4/B2-B6.md`: yeniden deneme yok, TPS25982 p.30/p.32 (burada yeniden okunmadı) (4 düğüm) |
| U3, U4: GND_EP (26) | /GND | Açık pad toprağı (2 düğüm) |
| U3, U4: IN_EP (25) | /VSAFE | IN açık padi; U3/U4 IN ağıyla aynı (2 düğüm) |
| U3, U4: **LDSTRT (12)** | /GND | **AÇIK:** repoda gerekçe bulunamadı (2 düğüm) |
| U3, U4: **ITIMER (7)** | açık (`unconnected-`) | **AÇIK:** repoda gerekçe bulunamadı (2 düğüm) |
| U1, U2: NC (10) | açık (`unconnected-`) | NC pini (2 düğüm) |

Yanlış ağ kanıtı yok. LDSTRT ve ITIMER bağlantıları için TPS25982 datasheet kontrolü gereklidir; bu çıktı o pinlerin doğruluğunu kanıtlamaz.
