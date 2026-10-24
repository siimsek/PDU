# WP1 rev2 – Tezgâh test planı

> **DURUM: YAPILMADI.** Fiziksel test yapılmamıştır. Tüm sonuçlar ngspice davranışsal simülasyonudur (sim ≠ silikon).

| # | Test | Düzen | Ölçüm | Kabul (değiştirilmeyen kriter) |
|---|---|---|---|---|
| B1 | Trip/release eşiği | RAW'a programlanabilir kaynak, 10 mV/s yavaş rampa, -40/25/85 °C | INP düşüş anındaki RAW | 11,2929–11,5167 V içinde; 11,22 V'ta tetik yok |
| B2 | G1 – TLV3601 VIO @ VCM≈4,1 V | Komparatör tek başına, VCM 4,096 V, ofset tarama | VIO (VCM 0,3 V ve 4,096 V'ta, −40/25/85 °C; ≥ 10 adet, 2 lot önerilir) | rev2 P0-2: VCM kaynaklı ek ofset ≤ 4,1 mV (V varsayımı). Sınır: ≤ 11,97 mV toplam VCM terimi → 50 mV marj korunur (≈ 50 dB CMRR eşdeğeri); ≤ 29,89 mV → marj ≥ 0 (≈ 42 dB). Aşarsa WP2 TLV3201+REF35250 alternatifi |
| B3 | Rampa 0,07/0,17/0,23 V/µs | Güç kaynağı + MOSFET rampa üreteci RAW'da | O1 portu tepe (≥ 200 MHz prob, kısa toprak yayı) | O1 ≤ 12,0 V anlık |
| B4 | Buck high-side short | Buck üst FET'i köprüleyerek (kontrollü, sigortalı) 26 V; **rev2: 16 × C5750 RAW bankı takılı** | O1/bus/RAW tepe, VDS, INP | O1 ≤ 12,0 V; VDS ≤ 60 V |
| B5 | tPD(INP_L) gerçek kapı yükünde (rev2 P0-3) | 4× CSD18540Q5B takılı + RPU10, INP adımı; ayrıca 47 nF test yükü ile (veri sayfası koşulu) karşılaştırma; −40/25/125 °C | INP↓ → VGS < 1 V süresi | ≤ 1,05 µs (analitik en kötü oran 0,9685; aksi halde marj kapanmaz) |
| B6 | Startup 20 / 22,2 / 26 V | Batarya emülatörü, 4,5 A yük | bus max, FET_ON süresi | **normal bus ≤ 11,1605 V** (rev2 P1-2); O1 ≤ 12 V |
| B7 | Yanlış tetik | 11,1605 V + 10 mV/870 kHz ripple, 11,21 V | INP | Tetik yok |
| B8 | 0,45→4,5 A ve 7,5 A basamak | Elektronik yük | bus min/max | 10,78–**11,1605 V** (11,22 V yalnız yanlış-tetik test seviyesi; 7,5 A: bus max kabul, min tracking) |
| B9 | Toparlanma | B3/B4 sonrası | O1/S2E reset | 11 V ±2 % |
| B10 | -40 °C RAW bank ESR | Soğuk oda | ESR ölçümü + B4 tekrarı | 100 mΩ köşe raporlanır (stres) |
| B11 (rev2) | RAW bank efektif C | 16 × C5750X7S2A226M280KB, 11 V DC bias, LCR (veya şarj/deşarj yöntemi), −40/25/85 °C | Efektif C, ESR | ≥ 185,3 µF ürün min.; **kabul bütçesi 165 µF dürüst min. ile de kapanıyor** (94,2 mV @ 12,5 mΩ); < 165 µF ise `window_budget.py` yeniden ve WP1 açılır |
| B12 (rev2, WP3) | Buck döngü kararlılığı 185–483 µF | Ağ analizörü / yük basamağı, VIN 20/26 V | Faz/kazanç marjı, basamak tepkisi | WP3'te tanımlanacak (bu pakette kriter eklenmedi) |
| B13 (rev2 P0-4) | Gerçek TPS259824O (U3) üzerinden O1 | B3/B4 düzeni, U3 takılı, O1 portunda gerçek kablo/yük; RAW, VOUT ve O1 eşzamanlı (≥ 200 MHz, kısa toprak) | O1 tepe – RAW tepe farkı, çınlama | O1 ≤ 12,0 V anlık ve O1 ≤ RAW tepe + ölçüm belirsizliği; aşarsa yerleşim/snubber WP5 |
| B14 (rev2 P1-2) | Normal işletme bus tavanı | 20/22,2/26 V, 0–7,5 A, startup + basamaklar | VOUT ve O1 max | **≤ 11,1605 V**; 11,22 V yalnız B7 yanlış-tetik uyarım seviyesi |
| B15 (rev2, rev3 P1-03 genişletildi) | COUT11 / CREF12 / CIN11 / CBST10 efektif C | LCR, 5 V / 4,1 V bias | C_eff | COUT11 ≥ 2,2 µF; CREF12 0,1–10 µF; rev3: CIN11 @26 V ≥ 0,1 µF (TPS7A16 IN min); CBST10 @12–13,9 V ≥ 21 nF (Qg 288 nC / 13,86 V) ve WP3 açılış süresi için ölçülen değer kayda geçer |
| B16 (rev3 P0-01) | RAW bölücü güç/ısı | RAW 26 V sürekli (aşırı gerilim arıza durumu), U13 beslemeli (IN− clamp) ve beslemesiz (çift arıza, bilgi); termal kamera | RSNS10A/RSNS10B/RSNS11 gövde sıcaklığı, akım, 30 dk sonra bölücü oranı (trip kayması) | Her parça P ≤ 125 °C derating (≤ 107 mW 1206 ERA-8A), oran değişimi ≤ ±0,1 % (bütçedeki R_tol); aşarsa WP1 yeniden açılır |
| B17 (rev3 P0-02) | Arıza sonrası yüksüz yeniden kapanma | B4 sonrası kaynak 26 V → 11,1605 V iner, bus yükleri kopuk (bench: 30–50 ms yük yok); RAW/VOUT/O1 eşzamanlı | Bus/O1 tepe (sim INFO: 11,35–11,41 V) | O1 ≤ 12,0 V anlık (kabul); 11,1605 V normal sınırı bu pencerede **uygulanmaz** (normal rejim değil) ama ölçüm raporlanır; > 11,22 V ise WP3 (buck geri dönüş / yük-bağlı senaryo) açık kalır |
| B18 (rev3 P1-01) | FET SOA / enerji | B4 ve B6 sırasında QA/QB VDS ve akım (her FET için, akım probu veya şönt), Tc ölçümü | Tepe güç, enerji, darbe süresi, akım paylaşımı | SLPS488B Fig. 10 SOA, Tc'ye göre derating; `fet-soa-study.json` model tahmini ile karşılaştırılır |
