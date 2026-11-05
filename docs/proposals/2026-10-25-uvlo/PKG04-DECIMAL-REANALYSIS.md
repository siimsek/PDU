# PKG-04 — UVLO 20×2 tarihsel logların SHA-256 + Decimal yeniden değerlendirmesi

Tarih: **2026-11-05**, Europe/Istanbul. Kaynak HEAD: `db6237a955f4314bc91a4f274f91491b7de9b4e3`. Yeni `ngspice` koşusu **YOK**. Kabul kararı **YOK**.

## Değiştirilmeyen tarihsel kaynak

- `simulation/proposals/2026-10-25-uvlo/results/num-study-tmax100n/num-study.json`, Git blob SHA-1: `193d9a274c91f58c4628317faa7903b066a62bb0`.
- Tarihsel koşu HEAD'i: `ebe56b233ba0a2aee40b056728965b181311937a`; eski rapor `n_protocol_pass=4/20`; geçmiş `provenance_consistent=false` aynen kaldı. Bu durum yeni temiz koşunun kanıtı olarak yeniden sınıflandırılmadı.
- 20/20 `decks/uvlo-<case>.cir` dosyası ve 40/40 `results/num-study-tmax100n/<case>.<gear|trap>.log` GitHub üzerinden bağımsız okundu.
- **40/40 log SHA-256**, tarihsel JSON'daki `log_sha256` değerleriyle; **20/20 kaynak deck SHA-256**, `source_deck_sha256` değerleriyle birebir eşleşti. Loglardan yeniden ayrıştırılan sayısal değerler, `missing`, `no_event` ve .meas beyanları da tutarlı. Hash uyuşmazlığı: **0**.
- Ölçüm sınıfı, deck'teki `.meas` işleminin türünden alındı; `WHEN/TRIG/INTEG` = zaman, `FIND/MAX/MIN/AVG/PP/RMS V(...)` = gerilim. Ham basılı ondalık metinler katsayı ve onluk üs olarak **tamsayı tabanlı exact decimal** ile karşılaştırıldı; float kararı kullanılmadı. Zaman farkı **≤ 0.0000001 s**; gerilim farkı **≤ 0.005 V**; her ikisi kapsayıcı. Diğer bütün başarısızlık koşulları ve önceki matris korunuyor.

## Sonuç: yalnız iki sınır hatası düzeltildi

**Önce: 4/20; yeniden değerlendirme: 6/20.** Bu yalnız eski logların yeni aritmetik ile yeniden yorumlanmasıdır; tmax doğruluk garantisi ve ürün kabulü değildir.

| Vaka | Eski | Exact Decimal | Gerekçe |
|---|---|---|---|
| `dip0v-10us-mbmin-tmin` | FAIL | **PASS** | `EN_R1`, `EN_RLAST` ham Gear `9.20405e-02` s, Trap `9.20404e-02` s; fark tam `1e-7` s |
| `dip0v-100us-mbmin-tmin` | FAIL | **PASS** | `EN_R1`, `EN_RLAST` aynı sınır eşitliği |
| Diğer 18 vaka | 4 PASS / 14 FAIL | 4 PASS / 14 FAIL | Değişiklik yok |

İki yeni PASS **resolution-sensitive**: basılan sayıların eşitliği fiziksel/matematiksel yakınsamayı kanıtlamaz. Hiçbir tolerans genişletilmedi.

## Tam 20-deck vaka matrisi (tmax 100 ns; Gear/Trap)

| Vaka | Exact durum |
|---|---|
| dip0v-10us-typ-ttyp | PASS |
| dip0v-50us-typ-ttyp | FAIL — Trap abort |
| dip0v-100us-typ-ttyp | FAIL — yöntem toleransı |
| dbldip0v-50us-gap100us-typ-ttyp | FAIL — Trap abort |
| dbldip0v-50us-gap30ms-typ-ttyp | FAIL — Trap abort |
| dip0v-10us-mbmin-tmin | PASS — sınır eşitliği |
| dip0v-50us-mbmin-tmin | FAIL — yöntem toleransı |
| dip0v-100us-mbmin-tmin | PASS — sınır eşitliği |
| dbldip0v-50us-gap100us-mbmin-tmin | FAIL — yöntem toleransı |
| dbldip0v-50us-gap30ms-mbmin-tmin | FAIL — yöntem toleransı |
| o3-dip0v-10us-typ-ttyp | PASS |
| o3-dip0v-50us-typ-ttyp | FAIL — Gear ve Trap abort |
| o3-dip0v-100us-typ-ttyp | FAIL — yöntem toleransı |
| o3-dbldip0v-50us-gap100us-typ-ttyp | FAIL — Gear ve Trap abort |
| o3-dbldip0v-50us-gap30ms-typ-ttyp | FAIL — Gear ve Trap abort |
| o3-dip0v-10us-mbmin-tmin | PASS |
| o3-dip0v-50us-mbmin-tmin | FAIL — yöntem toleransı, O1 süreklilik açık |
| o3-dip0v-100us-mbmin-tmin | PASS |
| o3-dbldip0v-50us-gap100us-mbmin-tmin | FAIL — yöntem toleransı |
| o3-dbldip0v-50us-gap30ms-mbmin-tmin | FAIL — yöntem toleransı |

**Abort:** 6 farklı vaka / 9 yöntem koşusu. `Timestep too small` kayıtları gerçek ve korunuyor; düğüm etiketi fiziksel kök neden kanıtı değil.

**O3 50 µs mbmin POST_O1_AVG:** Gear **2.769516 V**, Trap **0.2660205 V**, fark **2.5034955 V**. Bu fark yuvarlama değildir; süreklilik / toparlanma çözülmedi. Kararlı H2 ile O1 anlık H1 değerlendirmeleriyle karıştırılmamalıdır.

## Yerel testler ve yürütme sınırı

- Önceki `test_study_integrity.py`: **27/27 PASS** (bu turda tekrar).
- Önceki `test_locked_runner.py`: **9/9 PASS** (bu turda tekrar; yalnız sahte ngspice).
- `test_verifier_provenance.py`: **7/7 PASS** (bu turda tekrar; gerçek `verify_uvlo.py` değil, ayrılmış provenance işlevi).
- Güncel `verify_uvlo.py` **tam dosya entegrasyon testi çalıştırılmadı**, çünkü bu oturumun yerel alanında özel deponun tam klonu bulunmuyor; `ngspice` da kurulu değil. Doğrulayıcının tam entegrasyonu açık, geçmiş 259 kabul koşusu **yenilenmedi**.

## İlerleme kapısı

1. Gerçek `verify_uvlo.py` tam entegrasyon ve negatif testleri, tüm modüller içeren temiz dosya ağacında çalıştır; fail-closed yolu doğrula.
2. 259 Gear/tmax≤100 ns tam kabul koşusu yalnız kilitli girdilerle; 23/23 tarihsel regresyon beklenen FAIL; ham OUTA/EN/QINH/VGS ile M3 nedenselliği.
3. Sabit 20×2 için 100→50 ns, önceden tanımlı koşula göre 25 ns; hiçbir deck veya yöntem seçimi yapma. O3 sürekliliği açık.
4. Bütün fiziksel/BOM/tezgâh kapıları ayrı. `WP1/WP2 kabul = HAYIR`; `CI = kapalı`; `merge = HAYIR`.
