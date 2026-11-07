# T-013: PCB proje kurulumu (iz/via/döküm yok)

Tarih 2026-11-07. KiCad 10.0.7. Kart `tasks/T-013.md`, karar `decisions/D-006-board-size.md`.

## Üretim zinciri (tekrarlanabilir, GUI yok)

```bash
"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe" sch export netlist -o reports/g5/T-013/netlist.net PDU.kicad_sch
"C:\Program Files\KiCad\10.0\bin\python.exe" scripts/pcb_setup.py   # kart, delikler, ayak izleri, kaba yerleşim
python scripts/pcb_rules.py                                         # stackup, netclass (.kicad_pro), PDU.kicad_dru
python scripts/pcb_drc.py                                           # boş kart DRC + parite DRC + darboğaz denetimi + SVG
"C:\Program Files\KiCad\10.0\bin\python.exe" scripts/pcb_neck_probe.py   # R-012 #2: deneme izleriyle kural + denetim kanıtı
```

| Kontrol | Komut | Sonuç |
|---|---|---|
| Boş kart DRC (kurallar yüklü, şema ayak izleri çıkarılmış geçici kopya) | `pcb_drc.py` → [drc-empty.json](T-013/drc-empty.json) | **0 ihlal, 0 bağlanmamış** |
| Şema paritesi | `kicad-cli pcb drc --schematic-parity` → [drc-placed.json](T-013/drc-placed.json) | **0** (180 ayak izi, 74 net) |
| Yerleşimli kart DRC | aynı dosya, özet [drc-summary.json](T-013/drc-summary.json) | Hatalar yalnız `unconnected_items` 402 (iz yok, beklenen). Courtyard çakışması 0, kenar ihlali 0. Uyarılar: silk_overlap 199, silk_over_copper 199, silk_edge_clearance 15 (kaba yerleşimde etiket metinleri; son yerleşimde temizlenir) |
| Kural ↔ routing-g2 | `python scripts/pcb_rules.py --check` | `{"pass": true, "errors": []}` |
| Darboğaz denetimi (R-012 #2) | `pcb_drc.py` → `drc-summary.json` `neck_down` | 780 ince adımlı güç padi; ihlal 0 (henüz iz yok) |
| Darboğaz deneme izleri | `pcb_neck_probe.py` → [neck-probe.json](T-013/neck-probe.json) | PASS: A (0,3 × 1,0 mm, U1 pad 1'den) DRC ✓ denetim ✓; B (0,3 × 3,0 mm, aynı pad) DRC ✓ ama denetim **uzunluk 3,00 > 1,5**; C (0,3 mm, serbest alan) DRC **track_width** + denetim **pad'de bitmiyor**; D (3,3 mm) ikisi de ✓ |
| Testler | `pytest scripts/test_pcb_setup.py` | 9 geçti |

## Uygulanan değerler

- **Dış hat (D-006):** 120 × 85 mm Edge.Cuts. Yardımcı eksen ve ızgara orijini sol-alt köşede (KiCad konumu 30, 115). Raporlardaki koordinatlar D-006 sistemindedir: orijin sol-alt, y yukarı.
- **Katmanlar:** 4 bakır katman (F.Cu, In1.Cu, In2.Cu, B.Cu). Stackup 1,6 mm (VARSAYIM; üretici onayı AÇIK, PCB-HANDOFF §1):
  - Maske 0,01 / Cu 0,035 / prepreg 0,2 / Cu 0,035 / çekirdek 1,04 / Cu 0,035 / prepreg 0,2 / Cu 0,035 / maske 0,01.
  - Bakır tüm katmanlarda 1 oz. FR4 εr 4,5, ENIG.
  - L1–L2 arası 0,2 mm, SW sıcak döngüsü için (HANDOFF §1).
- **Montaj delikleri (D-006 §7, VARSAYIM):**
  - 4× `MountingHole:MountingHole_3.2mm_M3` (NPTH Ø3,2): (6,6), (114,6), (6,79), (114,79).
  - Öznitelikler: board-only, BOM dışı, pos dışı.
  - Her deliğin çevresinde r = 4,0 mm kural alanı: iz, via ve döküm yok (VARSAYIM: M3 başı / pul Ø ≈ 7 mm + pay).
- **Eski içerik:** G1 prototipinin 72 ayak izi ve 101,6 × 76,2 dış hattı (76 öğe) kaldırıldı. Kart netlistten yeniden kuruldu.

### Netclass (PDU.kicad_pro) ve kurallar (PDU.kicad_dru)

| Sınıf | Netler | `track_width` (= routing-g2 `selected_width_mm`) | DRU min (= `outer_width_min_mm` yukarı yuvarlanmış) |
|---|---|---:|---:|
| INPUT_POWER | /ANODE, /VIN | 3.3 | 2.94 |
| BUS_POWER | /VOUT, /VSAFE, /GND | 5.5 | 4.92 (/GND hariç) |
| PHASE_POWER | /SW_PH1/2, /ISNS1/2 | 2.6 | 2.35 |
| O1_PORT | /O1_11V | 5.3 | 4.76 |
| S2E_PORT | /S2E_11V | 3.3 | 2.97 |

**Değişiklikler** (G1 proje dosyasından; `pcb_rules.py` günlüğü):
- Genişlikler 4.5/6.0/3.5/4.5/2.5 → 3.3/5.5/2.6/5.3/3.3.
- Sınıf adları O1_POWER → O1_PORT ve S2E_POWER → S2E_PORT (routing-g2 adları).
- `/VBAT` kalıbı düşürüldü (G5'te net yok).
- `Net-(CBOOTx-Pad1)` → `/CBOOT_Rx` (T-007 adlı RBOOT neti).
- `/VSAFE` BUS_POWER'a eklendi.
- `/ISO_GATE` ve `/ISO_VCAP` AUX_LOCAL'a (0,5 mm) eklendi. HANDOFF §2 GATE sınıfı ≥0,4 mm ister.

**Kural kararları** (THINKER incelemesine açık, R-012):
1. `opt` = seçilen genişlik (yönlendirici varsayılanı), `min` = dış katman HESAP alt sınırı.
2. **/GND min genişlik kuralı dışında.** GND dönüşü L2 düzleminden akar (HANDOFF §1). 0603 GND bağlantıları 4,9 mm olamaz.
3. **Darboğaz (R-012 #2'den sonra sınırlandı):**
   - **Kapsam:** her güç sınıfı için yalnız o sınıfın ağında **ince adımlı padi** (dar kenar ≤ 0,65 mm, VARSAYIM) olan ayak izlerinin courtyard'ı. Liste PDU.kicad_pcb padlerinden üretilir: {'INPUT_POWER': ['Q1', 'U1', 'U10', 'U2', 'U5'], 'BUS_POWER': ['U1', 'U11', 'U12', 'U2', 'U3', 'U4', 'U6'], 'PHASE_POWER': ['U1', 'U11', 'U12', 'U2'], 'O1_PORT': ['U3'], 'S2E_PORT': ['U4']}. Eski genel `intersectsCourtyard('*')` kaldırıldı.
   - **Uzunluk ve uç:** KiCad DRU iz uzunluğunu koşul olarak alamıyor (B denemesi: courtyard'a değen iz bütünüyle istisna alıyor). Bu yüzden `pcb_drc.py` denetimi var: sınıf min'inden dar her güç izi ≥ 0,25 mm, ≤ 1,5 mm (VARSAYIM: pad boyu ≤ 0,6 + courtyard payı) ve aynı ağdaki listeli bir ince adımlı padde bitmeli. Denetim ihlali kapıyı (pass) düşürür.
4. **Aynı ayak izinin padleri arası 0,15 mm** (DFM min, HANDOFF §7 VARSAYIM). SOT-23-6, VSSOP ve SC-70 paketlerinin pad aralığı tasarım gereği 0,15 mm'dir. Bu kural olmadan 26 sahte boşluk hatası çıkıyordu.
5. **HV boşluğu 0,6 mm:** /ANODE, /VIN, /VOUT, /VSAFE ile GND dışı netler arasında, yalnız iz/döküm/via (HANDOFF §5: TVS kelepçesi 53,3 V). Paket içi pad aralıkları kapsam dışıdır.

## Kaba yerleşim (PCB-HANDOFF §3 grupları, D-006 §3)

Grup bölgeleri `Dwgs.User` katmanında dikdörtgen ve etiket olarak çizildi. Parçalar bölgeye raf yöntemiyle yerleşti (en uzun önce, aralık 0,4 mm; COUT bankası 0,15 mm). Hiçbir bölge taşmadı, her parça bir gruba atandı. Görsel: [placement.svg](T-013/placement.svg), [placement.png](T-013/placement.png). Koordinatlar: [placement.json](T-013/placement.json).

| Grup | Bölge (x0, y0, x1, y1) mm |
|---|---|
| Giriş (J1, D1, Q1/U5, CBIN, CIN_U5) | batı şeridi x 0,5–24 |
| Buck faz 1 / faz 2 | x 25–57, y 58–84,5 / y 0,5–27; IC + CIN sütunu sabit, kalan parçalar yanındaki dikdörtgenlerde |
| COUT bankası 32× C5750 | (24,5, 28,5, 90, 57): 8 × 4 ızgara, iki faz arasında (D-006 ~63 × 25 mm şerit) |
| Buck ortak kontrol | (58, 58, 75, 84,5) |
| OVP + OC mantık, REF, mandal, LDO | (76, 58, 108, 84,5): faz 1 SW bölgesinden ≥19 mm, faz 2'den ≥31 mm |
| Ortak bara ayırıcı (Q2, U6) | (90,5, 28,5, 98,5, 57): COUT bankası ile eFuse arasında |
| eFuse + çıkış | doğu: x 99–119,5 |
| Test noktaları / fixture | (58, 9,5, 98, 27) |

**Sıcak döngü (R-012 #1, HANDOFF §3.2):**
- CIN1–4 U1'e, CIN5–8 U2'ye atandı. Önceden giriş grubundaydılar; HANDOFF §3.1'deki "CIN1–8" giriş zinciri ifadesi yerine §3.2'deki "CIN IC'nin VIN/PGND pinlerine bitişik" şartı esas alındı.
- RRX0029B'de VIN padleri 1–3 ve 27–29 ile PGND padleri 23–26 aynı (−y) kenarda. CIN'ler (1210, pad 1 = /VIN) IC ile aynı açıda, o kenardan dışa doğru tek sütun halinde dizildi; aralık 0,3 mm.
- U1 180° döndürüldü: VIN/PGND kenarı kart içine, SW padleri batıya (L1) bakıyor. U2 0°'de: SW doğuya (L2) bakıyor.
- Merkez uzaklıkları: U1–CIN1…4 = 5,64 / 9,23 / 12,82 / 16,41 mm; U2–CIN5…8 aynı. Önceden en yakın CIN 29,60 / 43,28 mm idi. İlk CIN'in courtyard'ı IC'ninkinden 0,3 mm uzakta.

**Kenara sabitlenenler:**
- J1: batı kenarı, y = 42,5, 90°. Micro-Fit ağzı batıya bakar.
- J3: doğu kenarı, y = 32,6, 270°. Ağız doğuya bakar.
- J2 (dikey Mini-Fit): doğu kenarı, y = 46.
- J_OVP_INJ_BUS: güney kenarı, x = 78.

## Kapsam dışı / AÇIK (sonraki yerleşim-yönlendirme işi)

- İz, via ve bakır dökümü yok (kart yasağı). Q1/Q2 ≥645 mm² bakır, LM70880 EP via dizisi ve L2 GND / L3 güç dökümleri yönlendirme kartında çizilecek.
- Kaba yerleşim bölge düzeyindedir. Sıcak döngü (CIN–VIN–PGND), RS Kelvin, GATE ≤10 mm ve INA296 ≤15 mm gibi parça içi mesafeler ayrıntılı yerleşimde sağlanacak.
- Silkscreen uyarıları (413) kaba yerleşimin etiket metinleridir. Hata değildir, son yerleşimde temizlenir.
- Güç ağlarındaki ölçüm uçları (R_OVT/R_OV2T Kelvin VRAW, INA296 girişleri, bölücüler, TP'ler) ince ve uzun iz ister. Sınıf min kuralı bunları da işaretler; yönlendirme kartında net-tie veya gerekçeli DRC muafiyetiyle çözülmeli (backlog).
- Delik yerleri ve keep-out muhafaza bilinmediği için VARSAYIM. Stackup ve bakır kalınlığı üretici DFM onayı bekliyor (AÇIK).

## Araç notları ve sapmalar

- **Araç:** ayak izleri ve pad netleri KiCad'in kendi API'siyle (`pcbnew` 10.0.7, KiCad'in Python'u) yazıldı. `kicad_sexpr.py` stackup ve doğrulama için kullanıldı. T-002 TOOLING kararı şema içindi; PCB'de ayak izi örnekleme pcbnew yazıcısıyla daha güvenli. GUI ve elle metin düzenleme yok.
- **pcbnew hatası:** 10.0.7 SWIG ile kart öğesi silmek tip tablosunu bozuyor (sonraki `FootprintLoad` tipsiz nesne döndürüyor). Bu yüzden eski kart düzenlenmedi, `CreateEmptyBoard()` ile yeniden kuruldu.
- **Sapma (izinli yol dışı; R-012 tur 1'de bu kapsamla kabul edildi):** yeni betikler `scripts/pcb_setup.py`, `scripts/pcb_rules.py`, `scripts/pcb_drc.py`, `scripts/pcb_neck_probe.py` ve `scripts/test_pcb_setup.py`. Kart yalnız KiCad dosyalarını ve `reports/g5/` yolunu sayıyor. Betikler tekrarlanabilirlik için gerekli (TOOLING kuralı: düzenleme yalnız betikle). R-012'de kabul veya ret istenir.
