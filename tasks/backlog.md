# Backlog — engelleyici olmayan işler

Tek satır: `- [kaynak] konu — neden engelleyici değil — önerilen kart/rol`.

- [G4 N1] Vishay IHLP4040DZER6R8M01 6,8 µH L(I) eğrisi 16–40 A (Vishay'den iste veya tezgâhta ölç) — faz OC tetiği O1'i tüm L tabanlarında ≤11,41 V tutuyor (HESAP) — THINKER D-kartı veya U-maddesi.
- [G4 B5] UVLO düşüş eşiği (14,67–18,64 V, yalnız tipik histerezis) ve 18 V (3,0 V/hücre) kesimin BMS'te olup olmadığı — kullanıcı politikası; kart UVLO'su hücre koruması değil — U-maddesi (karar), BENCH T2.
- [G4 B4] Trimsiz yığılmış köşeler görünür FAIL (bara min 10,73 V, bırakma 11,26 V; SİM F3) — kabul kart başı trim T1b ile; FAIL kaydı silinmez — bilgi.
- [G4 B5] LM70880 EA gm maks yayımlanmamış (taramada 0,5–1,8 mS geçer) — tezgâh FRA T3 — BENCH.
- [G4 C] MLCC DC-bias grafikleri okunamadı (Ceff VARSAYIM) — Ceff payları muhafazakâr — THINKER datasheet okuma.

- [R-001] Startup PRE/CLR overlap creates a temporary nonstable latch state — no persistent set expected under no-fault sequence; verify /P5V_PROT, PRE, CLR and OVP_Q traces on bench — BENCH/THINKER.
- [R-001] BIAS→AGND is correct for the ≤60 V fault case, but exact VIN-to-VCC LDO dissipation needs actual VIN/IVCC and thermal budget — no thermal criterion currently supplied — THINKER/BENCH.
- [R-001] Define production R_TRIM replacement range, per-board trim procedure and RFB1 tolerance for complete VOUT corner analysis — current 442 Ω point is within calculated static window — BUILDER.
- [R-001 Tur 2] G4 N1-DECISION §2 hâlâ 8.97 A'yı normal tepe faz akımı olarak adlandırıyor; düzeltilmiş HESAP 5.58322 A — elektriksel akım-kapasitesi bulgusu kapanmış olsa da OCP/normal oranı anlatımının senkronlanması gerekiyor — BUILDER dokümantasyonu.
- [D-005] T3 O1 harici giriş mutlak maks / aşım toleransı yazılı üretici teyidi (bilgi amaçlı; 12,0 V kriteri korunuyor) — engelleyici değil.
- [D-001] Kompakt kart dışı sigorta yuvası (DIN-ray yerine kablo içi/panel tipi) — aynı DC kesme kanıtıyla THINKER araştırabilir; mekanik montaj bilinmiyor.
- [T-006 / D-007] F5 köşeleri f5_vt11.487_td300ns_ctyp_r200m_l0.8 ve f5_vt11.765_td300ns_ctyp_r200m_l0.8 TVS /VIN netlistinde iki kez zaman aşımı (exit -9) → kanıt yok; 4 denemede tamamlanmadı; çözücü ~215 µs'de tıkanıyor (VRAW→VIN, faz akımı ~32 A). O1 kısaltılmış pencerede 10,92 V (kanıtlı); kalan: VRAW tam pencere tepesi ve tıkanma kök nedeni (BQ1 ters yön 1 nS şüphesi) (bu ikisi dışındaki 47 F5 koşusu PASS; aynı parametreli diğer köşeler ≤11,07 V).
- [T-013 / R-012] Güç ağlarındaki ölçüm uçları (R_OVT/R_OV2T Kelvin VRAW, INA296 IN±, bölücüler, TP'ler) sınıf min genişlik kuralına takılır → yönlendirme kartında net-tie ya da gerekçeli DRC muafiyeti — BUILDER (yönlendirme).
