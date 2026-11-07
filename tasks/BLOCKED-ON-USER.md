# Kullanıcıdan beklenenler

Röle modu: kullanıcı dosya yüklemez. Belge isteyen maddeler önce THINKER kartıyla (resmi siteden) denenir; kullanıcıya yalnız ajanların yapamadığı kalır ve prompt'un sonunda tek soru olarak sorulur. Cevap gelince madde `Done (tarih, kaynak)` olur.

| ID | Gereken | Engellediği | Durum |
|---|---|---|---|
| U-001 | **T-1: O1 ve S2E gerçek akım ölçümü** (fiziksel; ajan yapamaz — prosedür aşağıda, sonuçları sohbete yazmanız yeterli, dosyayı Claude Code commit eder) | RILIM_O1/S2E ve J2 kararının doğrulanması (BENCH T-1); KiCad'i engellemez | Açık |
| U-002 | T3 Gemstone O1 giriş spec'i — **önce D-002 (THINKER, web)**; yalnız D-002 "doğrulanamadı" derse kullanıcıya bağlantı/üretici sorusu | O1 marjı (HESAP ≤11,41 V vs 12,0 V); kriter değişmez | Açık (mutlak maksimum ve transient için T3 teyidi gerekli) |
| U-003 | F1 sigorta belgesi — **önce D-001 (THINKER, web)**; yalnız hiçbir seçenekte DC kesme kapasitesi okunamazsa kullanıcı kararı | D-001, T-004, T-005b | D-001'de |
| U-004 | Şema gözle kontrolü — **R-002 render tabanlı yapar** (kicad-cli SVG/PDF dışa aktarımı + netlist); kullanıcı için isteğe bağlı | KICAD-READY kabulü | Bekliyor (T-012) |
| U-005 | **Birleştirme yetkisi** — tek cevap: "yetki veriyorum" (BUILDER, kriterleri geçen PR'ları birleştirir; KiCad/tasarım PR'ında tek satır onay sorar) veya "her PR'ı sor" | Kartların main'e girmesi | Done (2026-11-07, "Yetki veriyorum") |

## U-001 prosedürü — O1/S2E gerçek akımı (kart gelmeden)

1. Ekipman: laboratuvar kaynağı 0–30 V / ≥10 A (akım sınırı ayarlı), akım probu ≥20 A DC + ≥1 MHz **veya** 10 mΩ %0,5 şönt + diferansiyel prob, osiloskop (≥4 Mnokta kayıt), 6,5 hane DMM.
2. Kaynağı **11,0 V**'a, akım sınırını O1 için **9,0 A**, S2E için **5,5 A**'ya ayarla (eFuse ILIM üst değerleri; daha yükseği kartın davranışını temsil etmez).
3. Kaynak → (şönt veya prob) → yükün kendi kablosu/konnektörü. Şönt kullanılıyorsa kaynağın eksi ucuna (düşük taraf) koy.
4. Osiloskop: 10 µs/div ile **açılış** (güç verme anı, 50 ms pencere), sonra 1 ms/div ile **çalışma profili** (O1: motor/ESC kalkış, en zor manevra; S2E: dönme başlangıcı ve kararlı) — her biri en az 3 kez.
5. Kaydet: tepe akım, açılış tepe + süresi, 10 ms kayan RMS maksimum, ortalama; kaynak geriliminin en düşük değeri (kaynak sınıra girdiyse not et).
6. Sonuç: özet değerleri (tepe, açılış tepe/süre, RMS, ortalama, ekipman) Claude Code sohbetine yazın; Claude `reports/g5/inputs/T-1/` altına commit eder.
7. Kabul (BENCH T-1): O1 tepe < 7,23 A ve RMS ≤ 7,0 A; S2E tepe < 4,36 A. Aşılırsa durum RILIM/konnektör/COUT kararını yeniden açar — kriter değişmez.
