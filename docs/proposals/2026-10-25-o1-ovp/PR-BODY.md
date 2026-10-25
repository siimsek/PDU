# PR #1 gövde metni – WP1 rev3 (öneri; KiCad/baseline/ana BOM değişmedi)

> Bu dosya PR açıklaması için önerilen metindir; PR'a kullanıcı tarafından aktarılır.

## Özet
WP1 `2026-10-25-o1-ovp` – O1 portu için hibrit global OVP önerisi (TPS48000-Q1 + 4× CSD18540Q5B + TLV3601 + REF35409 + TPS7A1650), **rev3** (ChatGPT Tur 2 incelemesi 6390966776 Tur 3 yorumu 6394334358, Tur 4 yorumu 6394790371 ve Tur 5 yorumu 6394867878; hiçbirinde kabul yok; yanıtlar: `docs/proposals/2026-10-25-o1-ovp/CHATGPT_REVIEW_RESPONSE.md` → "Tur 2" … "Tur 5").

**Karar: WP1 tamamlanmadı. Merge/üretim için uygun değil (P0-03, P0-05/N-01 açık).**

## Sert kriterler (değiştirilmedi)
- O1 anlık tepe ≤ 12,0 V; normal bus ≤ 11,1605 V; 11,22 V yalnız yanlış-tetik uyaranı.
- Hiçbir FAIL silinmedi/gizlenmedi. Davranışsal modeller; sim ≠ silikon. LTspice bulut ortamında çalıştırılmadı.

## rev3 değişiklikleri
- **Model rev3** (`bc63e66`): TPS48000 iç düğümü `ov`→`ovs` (OV pini ile büyük/küçük harf çakışması; rev1/rev2'de OV yedeği ölüydü). rev2 lib kopyası + `model-compare/` eski/yeni regresyon.
- **P0-01** RAW bölücü RSNS10A 1,0 k + RSNS10B 1,05 k + RSNS11 1,15 k, 1206 ERA-8ARB: en kötü parça 85,1 mW = 125 °C derate'in %79,4'ü (`rsns_power.py --check` exit 0).
- **P0-02** O1_GLOBAL_PEAK (0…tran sonu) + arıza öncesi/toparlanma rejim kontrolleri (INP > 2,5 V, VGS > 6 V); negatif öz-test (`regime-selftest/`, exit 0): FET hiç açılmazsa runner ve doğrulayıcı FAIL.
- **P0-04** "garanti marjı" → koşullu marj (BUDGET.md §0).
- **P1-01** SOA teşhisi; **P1-02/P1-05** pin tabloları ve U12 EN; **P1-03** BOM derating notları, RBLD11 1206, RPD10/RSRC10 yalnız sim; **P2-02** çıkış kodları.
- **Tur 3** (`e8cce67`): P2-A `model_compare.py` açılış tetik sayacı yalnız `INFO:startup_no_ovp_trip` (gerçek: rev2 2 / rev3 0 tamamlanmış deck; 29/27 bench açılış bus INFO'suydu); Ek-P1 `regime_selftest.py` Part B tamamlanmış sentetik yanlış-rejim 12/12; P1-05 U12 pin tablosu EN = V5_OVP; P2-B RESULTS B18→B19, MODELS Dbody ifadesi. `1b72e0f`: temiz yeniden koşu `wp1-rev3-tur3` (ölçümler birebir aynı) + `model-compare/rebind_rev3.py`.
- **Tur 4** (`e4b4046`): P2-T4-01 `regime_selftest.py` Part B fail-closed (2×6 matris zorunlu, her enjeksiyonda yalnız ilgili rejim kontrolü FAIL); P2-T4-02 `rebind_rev3.py` vaka/anahtar/rev2-değer kümesi tam eşitlik; `regime-selftest/guard_negative_test.py` 10/10 (CI adımı). Runner/doğrulayıcı/deck değişmedi → kabul koşusu yeniden yapılmadı.
- **Tur 5** (`da1674a`): P2-T5-01 `rebind_rev3.py` türetilmiş alanları fail-closed yeniden hesaplıyor (`d = rev3 − rev2` toleranslı, rev2/rev3 `verdict` yeniden `judge()` ile, `changed` yeniden); P2-T5-02 ham ng satırları dict öncesi sayılıyor, tekrar CASE → exit 2; `guard_negative_test.py` **20/20** (C1–C9 yeni). Runner/doğrulayıcı/deck değişmedi; kontrol amaçlı tam koşu `wp1-rev3-tur5-check` (commit'lenmedi) ölçüm/hüküm olarak `wp1-rev3-tur3` ile birebir aynı.
- Teşhis: `solver-study/`, `slew-study/` (WP2 kontrollü açılış seçeneği), `soa-study/`, `u3-latch-study/`.

## Temiz koşu (wp1-rev3-tur3, girdiler `e8cce67`, sonuç `1b72e0f`, ngspice-44.2, Debian 13)
| Komut | Çıkış |
|---|---|
| `gen_o1ovp.py` | 0 (deck farkı yok) |
| `run_o1ovp.py --label wp1-rev3-tur3` | **2** – 2534 PASS / 4 kabul FAIL / 4 tamamlanmadı |
| `verify_candidate.py` | **2** – 1766 / 0 FAIL / 4 MISSING |
| `verify_candidate.py --baseline-regression` | 1 – O1 16,89 V FAIL (beklenen) |
| `rsns_power.py --check` | 0 |
| `regime-selftest/regime_selftest.py` | 0 (A 4/4, B 12/12) |
| `model-compare/rebind_rev3.py` + `model_compare.py --resummarize` | 0 / 0 |
| Tur 4 (`e4b4046` kodu): `regime_selftest.py` / `rebind_rev3.py` / `guard_negative_test.py` | 0 (A 4/4, B 12/12) / 0 / 0 (10/10) |
| Tur 5 (`da1674a` kodu): `run_o1ovp.py --label wp1-rev3-tur5-check` (worktree, commit'lenmedi) / `verify_candidate.py` / `rebind_rev3.py` / `guard_negative_test.py` | 2 (2534/4/4, `tur3` ile birebir) / 2 (1766/0/4 MISSING) / 0 / 0 (**20/20**) |
| `solver-study` / `slew-study` / `soa-study` | 0 / 0 / 0 |
| `u3-latch-study` | **1** (N-01) |

- **O1 global maks 11,90318 V** (buck-short-c165-esr12m5-wchi; 96,8 mV marj).
- **Normal bus maks 11,09192 V** (bus_recov, c483-wchi; 68,6 mV marj).
- **Yanlış tetik 11,22 V: 22/22 deck tetik yok** (INP 4,9995 V, VGS 11,6 V); mc-nofalse O1 11,19781 V.
- Monte Carlo: mc-ramp O1 11,11178–11,57673 V; mc-short O1 11,57582–11,7582 V.
- Model rev2↔rev3 regresyonu (`model-compare/`, exit 0): kabul FAIL 0/0; tamamlanmadı 2 → 4; O1 global maks 11,90272 → 11,90318 V; s023 O1 farkları (±0,54 V) davranışsal U3 mandalından (N-01).
- INFO: postfault bus 11,29486–11,47708 V (24 deck); bench açılış bus 11,150–11,167 V (46 deck). TRACKING 7,5 A bus min 10,649–10,7584 V.

## Açık bloklayıcılar
1. **P0-03**: 4 ESL deck (c185/c165-esr12m5-esl2n-typ/wchi) 12,264–12,270 ms'de duruyor; açılışta RAW ≈13,33 V çınlama → komparatör yanlış tetiği. Çözücü değişikliği çözmüyor (20/20). RPU10 330/1000 Ω ESL deck'lerini tamamlıyor ama s023 toparlanma VGS min 2,563/0,931 V (< 6 V) → FAIL; sabit RPU10 kabul edilmedi. WP2: 10 Ω hızlı kapatma korunarak ayrı açılış slew sınırlama ↔ RAW sönümleme sayısal karşılaştırması, sonra B19.
2. **P0-05 / N-01**: 100 mΩ stres köşesi O1 PASS'i davranışsal U3 mandalına dayanıyor; U3 açılmaz varsayımıyla 12,50–13,04 V.
3. P1-01 SOA marjı 1,085× (grafik okuma ±%25) – B18.
4. KiCad sembol/footprint (DGX-19, Q10–Q13) doğrulanmadı/oluşturulmadı; WP3 buck döngü kararlılığı.
5. Tezgâh testleri B2/B5/B10/B11/B13–B19 yapılmadı; LTspice çalıştırılmadı; TR stoğu doğrulanamadı.

## Bütünlük
`docs/proposals/2026-10-25-o1-ovp/MANIFEST-SHA256.txt` (`sha256sum -c` ile doğrulanır).
