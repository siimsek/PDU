# Açık çevrim buck güç katı

20–26 V girişten (6S batarya, ana çalışma noktası 24,6 V) 11 V / 7,5 A (82,5 W) hedefleyen tek faz, asenkron, açık çevrim buck güç katı. Beslenecek yükler T3 Gemstone O1 ve SLAMTEC RPLIDAR S2E'dir.

**Aşama: ANA GÜÇ DEVRESİ.** Güç katının değerleri ve parça kriterleri belirlendi ve LTspice'ta doğrulandı. Belirli parça numarası seçilmedi; PWM, geri besleme ve soft-start henüz yok. Bu aşamanın son hâli `ANA-GUC-DEVRESI` dalında saklanır.

**Nerede kaldık, sırada ne var:** [YOL-HARITASI.md](YOL-HARITASI.md) · **Çalışma kuralları (yapay zekâ araçları dahil):** [AGENTS.md](AGENTS.md)

![LTspice şematiği](buck/ltspice/buck_guc_kati.svg)

## Devre değerleri

| Eleman | Şematikteki değer | Kabul aralığı | Kısa neden |
|---|---|---|---|
| V1 | 24,6 V | 20–26 V | 6S batarya; normal çalışma noktası 24,6 V |
| Vdrv | 100 kHz, Ton = 4,65 µs | — | 24,6 V'ta 11 V veren iletim süresi |
| L1 | 33 µH, DCR 15 mΩ | 33–47 µH, Isat ≥ 12 A, DCR ≤ 15 mΩ | Akım ripple'ı %25; tipik yükte sürekli iletim |
| Cout | 1000 µF, ESR 25 mΩ | 1000 µF, ESR 15–35 mΩ, ≥ 25 V | Sabit güç yüküyle sönüm; tolerans köşesinde 12 V altında kalır |
| Cin1, Cin2 | 2 × 1000 µF, ESR 20 mΩ | toplam ripple akımı ≥ 4,5 A, ≥ 35 V | Giriş ripple akımı 3,8 A RMS |
| S1 | ideal anahtar, `Ron=12m` | RDS(on) ≤ 12 mΩ, VDS ≥ 55 V | İletim kaybı 0,32 W |
| D1 | ideal diyot, `Vf=0.5 Ron=10m` | VF ≤ 0,58 V @ 7,5 A, VRRM ≥ 45 V | İletim kaybının üçte ikisi diyotta |
| Rload | 1,467 Ω | ≥ 100 W | 11 V / 7,5 A test yükü |

Kriterlerin tamamı ve nedenleri: [buck/PARCA-HEDEFLERI.md](buck/PARCA-HEDEFLERI.md). Seçim süreci ve test sonuçları: [buck/OPTIMIZASYON.md](buck/OPTIMIZASYON.md).

LTspice sonucu (24,6 V giriş, kararlı durum, 19–20 ms): Vo = 11,001 V, çıkış ripple'ı 46,5 mV t-t, bobin akımı 6,55–8,45 A. Fiziksel ölçüm yoktur.

Açık çevrim: Ton sabitken giriş veya yük değişirse çıkış 11 V'ta kalmaz; soft-start yoktur (sert kalkışta LTspice 53,1 A / 16,9 V gösterir). **Gerçek O1 veya S2E bağlanmaz.**

## LTspice'ta deneme

1. `buck/ltspice/buck_guc_kati.asc` dosyasını aç, **Run** (koşan adam simgesi) düğmesine bas.
2. `out` telinin üstüne tıkla → çıkış gerilimi. L1'in gövdesine tıkla → bobin akımı.
3. İlk ~10 ms kalkış salınımıdır; kararlı durum için 19–20 ms arasını büyüt (fareyle sürükle).
4. Grafikte iz adına (`V(out)`) **Ctrl + sol tık** → ortalama ve RMS değeri.
5. Değer değiştirmek için parçanın üstündeki değere sağ tıkla, yaz, yeniden Run. S1 ve D1 de aynı şekilde değişir (`Ron=…`, `Vf=…`).

Şematikteki tek yönerge `.tran 20m` satırıdır (simülasyon süresi); LTspice bunu şematikte ister.

Beklenen (24,6 V giriş, 19–20 ms): V(out) ortalama ≈ 11,00 V, ripple ≈ 47 mV t-t, I(L1) ≈ 6,6–8,4 A.

## Dosyalar

| Dosya | Ne işe yarar |
|---|---|
| [YOL-HARITASI.md](YOL-HARITASI.md) | Güncel durum, adımlar ve tamamlanma ölçütleri, karar günlüğü |
| [AGENTS.md](AGENTS.md) | Çalışma kuralları: neyin nasıl yapılacağı, araçlar, PCB aşaması kuralları |
| [buck/ltspice/buck_guc_kati.asc](buck/ltspice/buck_guc_kati.asc) | LTspice şematiği (çift tıkla aç, Run) |
| [buck/PARCA-HEDEFLERI.md](buck/PARCA-HEDEFLERI.md) | Parça kriterleri (en az/en çok değerler) ve nedenleri, Türkiye'de bulunurluk, parça arama istemi |
| [buck/OPTIMIZASYON.md](buck/OPTIMIZASYON.md) | Yük gereksinimleri, değerlerin nasıl seçildiği, test sonuçları, açık riskler |
| [buck/hesap.py](buck/hesap.py) | Analitik hesap: ripple, akımlar, kayıplar, LC dinamiği (`python buck/hesap.py`) |
| [buck/dogrula.py](buck/dogrula.py) | LTspice doğrulama koşuları (`python buck/dogrula.py secilen` / `pencere` / `tarama` / `grafik`) |
| `buck/grafik/*.svg` | `dogrula.py grafik` ile üretilen dalga şekilleri |
| `buck/ltspice/anahtar.asy`, `diyot.asy`, `idealler.lib` | İdeal anahtar ve diyot parçaları; şematikle aynı klasörde durmalı, elle açmak gerekmez |
| [buck/ltspice/sematik_uret.py](buck/ltspice/sematik_uret.py), [asc_gorsel.py](buck/ltspice/asc_gorsel.py) | Şematiği ve yukarıdaki görseli üretir |
| [CLAUDE.md](CLAUDE.md) | Claude Code için `AGENTS.md` ve `YOL-HARITASI.md` dosyalarına yönlendirme |
