# G2 — PCB devir teslimi

Girdi: [`KICAD-CHANGE-LIST-FINAL.md`](KICAD-CHANGE-LIST-FINAL.md), [`design/pdu_v2_spec.yaml`](../../design/pdu_v2_spec.yaml), [`routing-g2.json`](routing-g2.json) (üretici: [`analysis/g2/routing.py`](../../analysis/g2/routing.py), girdiler [`routing-input-g2.json`](routing-input-g2.json)). Kök dizindeki `calculate_routing_rules.py` G3'te `reports/g2/routing-input-g2.json` planını okuyacak şekilde güncellendi (yoksa eski `.konnect` planına düşer); seçilen genişlikler ısınma ≤20 °C ve 50 mV düşüm kontrollerini geçer → [`hardware/routing-width-calculations.json`](../../hardware/routing-width-calculations.json). Etiketler: HESAP / VARSAYIM / AÇIK.

## 1. Katman sayısı: 4 katman (öneri)

| Ölçüt | 2 katman | 4 katman |
|---|---|---|
| SW sıcak döngüsü (VIN–CIN–PGND) | GND dönüşü bölünür; döngü alanı büyür | L2 kesintisiz GND, döngü L1–L2 arası 0.2 mm dielektrikle kapanır |
| Bara/hata akımı (BUS 7.5 A, O1 9.07 A, yüksek taraf kısası sırasında arızalı faz 61–86 A tepe, SİM F1/F5 `il1_max_fault`) | dış katman genişliği HESAP: BUS ≥4.91 mm, O1 ≥4.75 mm; dönüş de aynı genişlikte iz ister | Dış katman güç + L2 GND düzlemi dönüşü taşır |
| Analog/koruma (karşılaştırıcı bölücüsü, REF, mandal, COMP/FB) | SW bakırına yakın, referans düzlemi yok | L2 referansı altında, gürültüden ayrık |
| Termal yayılım (LM70880 ~2.8 W/adet VARSAYIM, Q2 0.65 W, Q1 0.58 W) | sınırlı | L2/L3 bakırına termal via |

**Karar: 4 katman, 1.6 mm, tüm katmanlar 1 oz (35 µm) bitmiş bakır istenir.** Hesap 31.5 µm alır (VARSAYIM %10 pay). İç katman 0.5 oz verilirse iç katmanda güç izi yürütülemez (HESAP: BUS iç katmanda ≥18.4 mm, O1 ≥23.9 mm); bu durumda güç yalnız dış katmanlarda ve dökümlerle taşınır.

Stackup (VARSAYIM, üretici onayı AÇIK): L1 bileşen + güç dökümleri / L2 kesintisiz GND / L3 güç dökümleri (VIN, VOUT, VSAFE) + yardımcı / L4 sinyal + ikincil GND dökümü.

## 2. Netclass genişlikleri ve via sayıları (HESAP, ΔT 20 °C, 31.5 µm dış katman, segment 30–50 mm, 50 mV düşüm bütçesi)

| Sınıf | Ağlar | Akım zarfı | Dış katman min genişlik | **Seçilen** (×1.1, `calculate_routing_rules.py` doğrulamalı) | Via (min) | Dayanak |
|---|---|---:|---:|---:|---:|---|
| INPUT_POWER | /VBAT, /F1_OUT, /ANODE, /VIN | 4.48 A | 2.94 mm | **3.3 mm** (ΔT 6.9 °C, 44.5 mV) | 9 | 82.5 W / %92 / 20 V |
| BUS_POWER | /VOUT, /VSAFE, /GND | 7.5 A | 4.91 mm | **5.5 mm** (ΔT 9.6 °C, 44.7 mV) | 15 | kapasite hedefi |
| PHASE_POWER | /SW_PHx, /ISNSx | 5.58 A | 2.35 mm (kısa tutulur) | **2.6 mm** (ΔT 16.9 °C, 42.2 mV) | 12 | faz tepe akımı |
| O1_PORT | /O1_11V | 9.07 A | 4.75 mm | **5.3 mm** (ΔT 15.8 °C, 44.8 mV) | 19 | ILIM_O1 max |
| S2E_PORT | /S2E_11V | 5.66 A | 2.97 mm | **3.3 mm** (ΔT 11.8 °C, 44.9 mV) | 12 | ILIM_S2E max |
| ANALOG | /FB, /FB_INJ, /COMP*, /OVP_*, /ISO_OV, /ISO_EN, /CLR_N, /REF_NR | <10 mA | 0.25 mm | 0.25 mm | — | — |
| GATE | /ISO_GATE, /GATE | tepe A (kapı) | 0.4 mm, kısa | 0.4 mm | — | LM74502H sink tipik 2.37 A |

Via sayısı iki yolun büyüğüdür: 0.5 A/via taraması ve 0.3 mm delik / 20 µm kaplama varil yoğunluğu 30 A/mm² (VARSAYIM). Üretici kaplama/termal kabulüyle yeniden hesaplanmadan DRC kuralına çevrilmez.

## 3. Kritik döngüler ve yerleşim grupları

1. **Giriş grubu:** J1 → F1 → D1 (TVS, J1'e en yakın) → Q1/U5 → CIN1–8. TVS dönüşü doğrudan L2 GND'ye en az 4 via.
2. **Buck grubu (×2):** her LM70880 için CIN–VIN–PGND sıcak döngüsü en küçük alan (CIN IC'nin VIN/PGND pinlerine bitişik, L1 katmanında); SW bakırı yalnız IC–L arası; RS Kelvin uçları pad iç kenarından, birbirine paralel, SW altından geçmeden; COMP/FB/RT/VDDA bileşenleri SW'nin karşı tarafında, L2 GND referanslı.
3. **COUT bankası:** 16× C5750 iki faz çıkışı arasında simetrik; Q2 drain'i bankanın ortasına bağlanır.
4. **Ayırıcı grubu:** Q2 (CSD19531Q5A) + U6 (LM74502H) + C_ISO_VS/VCAP + R_GS bitişik; GATE izi ≤10 mm; **hata akımı döngüsü** COUT → Q2 → VSAFE dökümü → CEFIN/eFuse IN → GND dönüşü L2 üzerinden kısa. Q2 drain/source pad'leri ≥1 in² (645 mm²) bakır (RθJA 50 K/W koşulu, DATASHEET).
5. **OVP mantık grubu:** U7, U8, U9, U10, R_OVT/R_OVB, R_OV2T/R_OV2B, R_Q, R_EN1/2, R_CLR/C_CLR, SW1; SW düğümlerinden ≥10 mm uzak, L2 GND üstünde. **R_OVT ve R_OV2T'nin VRAW ucu Kelvin olarak Q2 drain bakırından alınır** (yük akımı geçmeyen ayrı iz).
6. **eFuse grubu:** U3, U4, CEFIN1/2, CEFOUT1/2, D_REV1/2 (eFuse OUT–IN arasında, kısa), D2/D3, J2, J3. RILIM/RIMON/CDVDT pin yanında.
7. Test noktaları ve J_OVP_INJ_BUS kart kenarına yakın; prob GND noktaları her grubun yanında.

## 4. Termal

- LM70880: exposed pad altına via dizisi L2/L3 dökümüne (datasheet EVM θJA 18.6 K/W koşulu); 85 °C ortamda Tj tahmini 137.7 °C (VARSAYIM %92 verim) → **ortam ≤72 °C** (EVM benzeri bakır) veya termal ölçüm (BENCH T4). Kart toplam kaybı ~9.0 W.
- Q1, Q2: her biri ≥1 in² 1 oz bakır; Q2 7.5 A'da Tj ≈117 °C (85 °C ortam, VARSAYIM sıcak RDS×1.8).
- L1/L2: ısı akımı 8 A typ, Irms 4.21 A; bobin altında sinyal izi yok.

## 5. Güvenlik mesafeleri (hata gerilimi)

Normal en yüksek gerilim 26 V (VIN). Hata durumları: VIN TVS clamp 53.3 V (VARSAYIM), VRAW yüksek taraf kısasında SİM ≤34.1 V (F1/F5) — LM70880 BIAS bu nedenle `/VSAFE`'e taşındı (G3), ayırıcı FET VDS SİM ≤27.5 V. Dış katman kaplamasız 31–100 V için 0.6 mm (IPC-2221 B2 tablosu — bu turda standart metni yeniden okunmadı, VARSAYIM). Öneri: VIN/ANODE/VOUT ile mantık ağları arasında ≥0.6 mm; aynı ağ sınıfı içinde üretici minimumu.

## 6. Konnektör yerleşimi

J1 (giriş) ile J2/J3 (çıkış) kartın karşı kenarlarında; giriş akım yolu buck grubuna kısa, çıkış akımı eFuse grubundan konnektöre kısa ve geniş (O1 ≥4.75 mm). Konnektör MPN/eş seti AÇIK (BOM-OPEN): footprint pitch/kutup doğrulaması seçilen MPN ile yapılmalı.

## 7. Kart boyutu ve DFM varsayımları

- Mevcut geçici sınır 101.6 × 76.2 mm. Eklenenler: 8× 2220 COUT (~8 × 35 mm² + aralık), ayırıcı grubu (~150 mm²), OVP mantık grubu (~250 mm²), D_REV ×2 SMC. Tahmin: **110 × 80 mm** (VARSAYIM; yerleşim çalışmasıyla teyit).
- DFM (VARSAYIM, üreticiyle teyit): min iz/aralık 0.15/0.15 mm, via 0.3/0.6 mm, via-in-pad dolgulu (LM70880 EP), 1 oz tüm katmanlar, ENIG, stencil 0.12 mm; özel footprint'ler: LM70880 RRX, TPS25982 RGE, BSC160 TDSON, C5750 2220 (BOM-OPEN listesi).

## 8. KiCad'e aktarım öncesi kontrol

Exact MPN ↔ footprint pin haritası (özellikle U5 DBV, U6 DDF, U7 DCK, U9 DCU, U10 DGN, Q2 SON), ağ eşliği (`pdu_v2_spec.yaml` nets), clearance, güç döngüleri, DRC/short.
