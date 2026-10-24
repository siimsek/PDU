# PDU öneri planı (WP1–WP8)

Durum tarihi: 2026-10-25 (Europe/Istanbul). Bu plan yalnızca **öneri** dosyalarını kapsar; ana şema/PCB, `hardware/pdu-current-bom.csv`, `simulation/pdu-current.net` ve kayıtlı baseline sonuçları değiştirilmez.
Kaynak hiyerarşisi: KiCad > Konnect > hash-eşleşen sonuçlar > durum dokümanları > tarihli notlar.

| WP | Kapsam | Bağımlılık | Ana risk | Durum |
|---|---|---|---|---|
| WP1 | O1 aşırı gerilim koruması (`2026-10-25-o1-ovp`), rev2: RAW bankı 16 × C5750X7S2A226M280KB (COUT21–28); inceleme (99a541a) bulguları işlendi (`CHATGPT_REVIEW_RESPONSE.md`): 165/176 µF + ESL köşeleri, normal bus ≤ 11,1605 V iddiası, P1-4 pasif MPN'leri, COUT11 10 µF, CREF12 1 µF, CBYP13 | — | Garanti marjı ≥ 72,0 mV (ömür ≥ 57,2 mV); V/Ç varsayımlarına bağlı (A1 VCM, tPD aktarımı, dürüst min. C, ESL) | **Koşullu / açık bloklayıcı** – `wp1-rev2-2`: 1799 PASS / **2 kabul FAIL** (`buck-short-c185/c165-esr12m5-esl2n-typ` ngspice yakınsamadı, açılışta pu_ovp 12,26 ms); sim PASS tek başına tamamlanma değildir; B2/B5/B11/B13–B15 tezgâh testleri ve WP3 gerekli |
| WP2 | Kullanıcı kararı: rev2 RAW bankının (+8 × 2220) kabulü. Yedek seçenekler: (a) **TLV3201 + REF35250** (VIO tüm VCM'de garantili; P0-2 V varsayımını kaldırır, bölücü yeniden hesaplanır), (b) daha hızlı kapatma (garanti verisi yok), (c) TI vendor modelleriyle PSpice karşılaştırması (CSD18540 ngspice'ta geçersiz). Bus setpoint düşürme gereksinim değişikliğidir | WP1 sonuçları | Alan/maliyet/tedarik; VCM varsayımı | Karar bekliyor |
| WP3 | Buck döngü kararlılığı / başlangıç / akım sınırı 165–483 µF RAW ile (kompanzasyon RCOMP 9,53k / CCOMP 4,7n / CHF 47p ~88 µF için seçilmişti) – faz/kazanç marjı kriteri tanımlanacak; 7,5 A / 82,5 W basamak penceresi (bus min yalnız *tracking*; bus max ≤ 11,1605 V WP1'de kabul); od200 (200 mV overdrive) bilgi koşusu yalnız bilgi amaçlı | WP1 | Kompanzasyon değişikliği ana şemayı etkiler | Açık – **PCB üretim blokörü** |
| WP4 | U3/U4 TPS259824O SOA/termal/timer ve **gerçek model karşılaştırması** (SLVMD37 Cadence-şifreli → PSpice gerekli; ngspice'ta çalışmaz). U3 OVP 16,32 V min → O1'i 12 V'ta korumaz; O1 ≤ RAW argümanı (Ç) tezgâhta B13 ile doğrulanacak | WP1 | eFuse modeli davranışsal; esr100m köşesinde `timestep too small` (xu3.ena) | Açık |
| WP5 | KiCad aktarımı (şema + PCB yerleşim, güç yolu 4× CSD18540Q5B, Kelvin ayrımı) | WP1, WP2 kararı | Parazitik L ve yerleşim, simülasyonda yok | `KICAD-TRANSFER.md` hazır, uygulanmadı |
| WP6 | Tezgâh testi (BENCH-TEST.md) | WP5 kartı | Sim ≠ silikon; tPD/IPD tipik değerler | Yapılmadı |
| WP7 | Tedarik (TR öncelikli, yurt dışı yedek) ve BOM birleştirme | WP2, WP5 | ERA-3ARB2051V ve TPS48000 TR'de bulunamadı; DigiKey'de ERA-3ARB2051V listelenmiyor; rev2 C5750X7S2A226M280KB: DigiKey stok 0 / 24 hf, TR'de görülmedi | Kısmi |
| WP8 | CI: öneri ngspice iş akışı + bağımsız doğrulayıcı (`verify_candidate.py`) + garanti bütçe kapısı (`window_budget.py`, ≥ 50 mV) | WP1 | ngspice sürüm farkı (Ubuntu apt vs Debian 44.2) | `.github/workflows/proposal-ngspice.yml` (YAML pyyaml ile doğrulandı; GitHub'da henüz koşmadı) |

PCB üretim blokörleri (rev2): TPS48000 DGX ve CSD18540 SON5x6 ayak izleri oluşturulup TI çizimine göre doğrulanmalı; KiCad sembol pin eşlemesi (özellikle TLV3601 SC-70-5) doğrulanmalı; WP3 döngü kararlılığı; Murata/Yageo MPN parametreleri ve stok doğrulaması (bu turda kısmen doğrulanamadı); ERA-3ARB2051V tedariki.

Kritik yol: WP1 rev2 → WP2 (bank kabulü) + **WP3 (185–483 µF ile buck kararlılığı)** → WP5 → WP6. WP3 kararlılık sonucu olmadan WP5'e geçilmemesi önerilir.
