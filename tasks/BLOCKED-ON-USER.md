# Kullanıcıdan beklenenler

Her madde: ID, ne gerekiyor, neyi engelliyor, nasıl teslim edilir. Cevap gelince madde `Done (tarih, kaynak)` olur; kartın Durum'u güncellenir.

| ID | Gereken | Engellediği | Durum |
|---|---|---|---|
| U-001 | **T-1: O1 ve S2E gerçek akım ölçümü** (prosedür aşağıda) | RILIM_O1/S2E ve J2 kararının doğrulanması (BENCH T-1); KiCad'i engellemez | Açık |
| U-002 | **T3 Gemstone O1 datasheet/spec** (mutlak maks giriş, kısa süreli aşım) — PDF veya resmi bağlantı `reports/g5/inputs/` altına | O1 marjı (HESAP ≤11,41 V vs 12,0 V); kriter değişmez | Açık |
| U-003 | **F1 sigorta + yuva resmi belgesi** (DC kesme kapasitesi açık yazan; aday Littelfuse 0456020.ER) | D-001, T-004, T-005b (F1 footprint) | Açık |
| U-004 | **Şemanın KiCad GUI'de blok blok gözle kontrolü** (R-002 kontrol listesiyle) | T-012 sonrası; KICAD-READY kapısının kabulü | Bekliyor (T-012) |
| U-005 | **PR birleştirme kararları** (wp/workflow-setup ve sonraki kart dalları) | Kartların main'e girmesi | Açık |

## U-001 prosedürü — O1/S2E gerçek akımı (kart gelmeden)

1. Ekipman: laboratuvar kaynağı 0–30 V / ≥10 A (akım sınırı ayarlı), akım probu ≥20 A DC + ≥1 MHz **veya** 10 mΩ %0,5 şönt + diferansiyel prob, osiloskop (≥4 Mnokta kayıt), 6,5 hane DMM.
2. Kaynağı **11,0 V**'a, akım sınırını O1 için **9,0 A**, S2E için **5,5 A**'ya ayarla (eFuse ILIM üst değerleri; daha yükseği kartın davranışını temsil etmez).
3. Kaynak → (şönt veya prob) → yükün kendi kablosu/konnektörü. Şönt kullanılıyorsa kaynağın eksi ucuna (düşük taraf) koy.
4. Osiloskop: 10 µs/div ile **açılış** (güç verme anı, 50 ms pencere), sonra 1 ms/div ile **çalışma profili** (O1: motor/ESC kalkış, en zor manevra; S2E: dönme başlangıcı ve kararlı) — her biri en az 3 kez.
5. Kaydet: tepe akım, açılış tepe + süresi, 10 ms kayan RMS maksimum, ortalama; kaynak geriliminin en düşük değeri (kaynak sınıra girdiyse not et).
6. Dosyalar: ham osiloskop CSV'leri + özet tablo `reports/g5/inputs/T-1/` (tarih, ekipman, prob, yük sürümü).
7. Kabul (BENCH T-1): O1 tepe < 7,23 A ve RMS ≤ 7,0 A; S2E tepe < 4,36 A. Aşılırsa durum RILIM/konnektör/COUT kararını yeniden açar — kriter değişmez.
