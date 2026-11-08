# Kullanıcıdan beklenenler

Kullanıcıya soru sorulmaz (2026-11-07): kararları THINKER verir. Burada yalnız **fiziksel** işler (tezgâh ölçümü) ve bilgi amaçlı dış iletişim maddeleri durur; hiçbiri tasarım akışını engellemez. Sonuçları sohbete yazmanız yeterli, dosyayı Claude Code commit eder.

| ID | Gereken | Engellediği | Durum |
|---|---|---|---|
| U-001 | **T-1: O1 ve S2E gerçek akım ölçümü** (fiziksel; ajan yapamaz — prosedür aşağıda, sonuçları sohbete yazmanız yeterli, dosyayı Claude Code commit eder) | RILIM_O1/S2E ve J2 kararının doğrulanması (BENCH T-1); KiCad'i engellemez | Açık |
| U-002 | T3 O1 mutlak maks / aşım toleransı — D-002 ve D-005 resmi kaynakta bulamadı. 12,0 V kriteri (üretici çalışma aralığının üst ucu) korunuyor; **engelleyici değil**. İsterseniz T3'e yazılı soru (bilgi amaçlı) | — | Bilgi (engellemez) |
| U-003 | F1 sigorta belgesi — **önce D-001 (THINKER, web)**; yalnız hiçbir seçenekte DC kesme kapasitesi okunamazsa kullanıcı kararı | D-001, T-004, T-005b | D-001'de |
| U-004 | Şema gözle kontrolü — **R-002 render tabanlı yapar** (kicad-cli SVG/PDF dışa aktarımı + netlist); kullanıcı için isteğe bağlı | KICAD-READY kabulü | Bekliyor (T-012) |
| U-005 | **Birleştirme yetkisi** — tek cevap: "yetki veriyorum" (BUILDER, kriterleri geçen PR'ları birleştirir; KiCad/tasarım PR'ında tek satır onay sorar) veya "her PR'ı sor" | Kartların main'e girmesi | Done (2026-11-07, "Yetki veriyorum") |
| U-006 | F1 kart dışı mı? — Kullanıcı "hangisi daha iyiyse" dedi (2026-11-07); BUILDER kararı: **kart dışı** Eaton PV-10A10F + CHPV1U (D-001; DC kesme değeri doğrulanan tek set, sigorta bataryaya yakın → kabloyu da korur) | T-004 | Done (2026-11-07) |
| U-007 | **T5g tezgâh ölçümü** (fiziksel): faz akımı 13,6 A geçişinden TP_ISO_GATE VGS <1 V'a tam zincir gecikmesi ≤3,0 µs (U ≤0,1 µs), 26 V, min Ceff, her faz; T5c ile doğrudan O1 tepe ≤12,0 V (BENCH-ACCEPTANCE T5g). Kart üretilince | O1 ≤12,0 V fiziksel kanıtı (R-001 #3) | Bekliyor (kart) |
| U-008 | R-020 ikinci turda kalan faz 1 Kelvin paralelliği; R-021 geometrik olarak doğruladı (RS1 180°) | T-023 adım 3 | Done (R-021) |
| U-009 | R-021: dört sense viasının güç bakırıyla teması; R-021 Tur 2 kapanışı (yalnız bu dar kapsam) | T-023 adım 3 | Done (R-021 Tur 2) |
| U-010 | R-021 ikinci turda kalan RS2.2 pad çıkış kesiti; R-022 doğruladı (5,50 mm) | T-023 adım 3 | Done (R-022) |

## U-001 prosedürü — O1/S2E gerçek akımı (kart gelmeden)

1. Ekipman: laboratuvar kaynağı 0–30 V / ≥10 A (akım sınırı ayarlı), akım probu ≥20 A DC + ≥1 MHz **veya** 10 mΩ %0,5 şönt + diferansiyel prob, osiloskop (≥4 Mnokta kayıt), 6,5 hane DMM.
2. Kaynağı **11,0 V**'a, akım sınırını O1 için **9,0 A**, S2E için **5,5 A**'ya ayarla (eFuse ILIM üst değerleri; daha yükseği kartın davranışını temsil etmez).
3. Kaynak → (şönt veya prob) → yükün kendi kablosu/konnektörü. Şönt kullanılıyorsa kaynağın eksi ucuna (düşük taraf) koy.
4. Osiloskop: 10 µs/div ile **açılış** (güç verme anı, 50 ms pencere), sonra 1 ms/div ile **çalışma profili** (O1: motor/ESC kalkış, en zor manevra; S2E: dönme başlangıcı ve kararlı) — her biri en az 3 kez.
5. Kaydet: tepe akım, açılış tepe + süresi, 10 ms kayan RMS maksimum, ortalama; kaynak geriliminin en düşük değeri (kaynak sınıra girdiyse not et).
6. Sonuç: özet değerleri (tepe, açılış tepe/süre, RMS, ortalama, ekipman) Claude Code sohbetine yazın; Claude `reports/g5/inputs/T-1/` altına commit eder.
7. Kabul (BENCH T-1): O1 tepe < 7,23 A ve RMS ≤ 7,0 A; S2E tepe < 4,36 A. Aşılırsa durum RILIM/konnektör/COUT kararını yeniden açar — kriter değişmez.
