# Açık çevrim buck güç katı

Bu depo, 20–26 V girişten 11 V / 7,5 A hedefleyen tek faz asenkron buck güç katının hesaplarını, LTspice simülasyonlarını ve yönergelerini tutar.

## Güncel durum

Ana güç katı LTspice'ta kuruldu ve simüle edildi: 100 kHz, 33 µH, BSZ065N06LS5, RBR40NS60A, CIN 2 × 220 µF, COUT 330 µF. Simülasyon verimi 20–26 V girişte %97,1–97,7'dir. Bunlar yalnız simülasyon sonucudur; parça verileri veri sayfasıyla doğrulanmadı ve fiziksel ölçüm yoktur.

- [LTspice sonuç raporu](buck/ltspice/SONUC.md)
- [LTspice şematiği](buck/ltspice/buck_guc_kati.asc)
- [Yol haritası: sonraki adımlar, nihai PCB'ye kadar](buck/YOL-HARITASI.md)

Aşağıdaki bölüm, simülasyondan önceki analitik başlangıç adayını kayıt olarak tutar; güncel seçim yukarıdaki rapordadır.

## Simülasyon öncesi analitik başlangıç adayı

[Parametre taraması](buck/PARAMETRE-KARSILASTIRMA.md) 11 V / 7,5 A / 82,5 W hedefinde farklı kombinasyonların analitik ön elemesini içerir. İlk aday olarak taramadaki 100 kHz noktası alınmıştı.

| Değer | Aday |
|---|---:|
| Giriş | 22,2 V DC nominal (çalışma aralığı 20–26 V) |
| Çıkış hedefi | 11 V, 7,5 A (82,5 W) |
| Anahtarlama frekansı | 100 kHz |
| Bobin | 39 µH |
| Giriş kondansatörü | 330 µF |
| Çıkış kondansatörü | 330 µF |
| Simülasyon yükü | 1,467 Ω |
| İlk ideal duty | %49,55 (22,2 V nominal girişte) |

Bu, analitik taramadan seçilmiş bir başlangıç adayıdır; verim bakımından optimum olduğu kanıtlanmadı. Taramadaki ESR varsayımları CIN için 15 mΩ, COUT için 20 mΩ'dur. L, CIN ve COUT aynı anda −%20 varsayıldığında akım ripple'ı 2,034 A p-p, çıkış ripple'ı 50,3 mV p-p, giriş ripple üst sınır hesabı 197,4 mV p-p olur. Bunlar LTspice veya fiziksel ölçüm sonuçları değildir. Önceki tek nokta hesap dosyası `buck/hesap.py`, CIN=470 µF ve COUT=220 µF referansını ayrıca tutar; bu değerler nihai seçim değildir.

22,2 V girişte ideal açık çevrim duty yaklaşık %49,55'tir. Bu duty 26 V girişte ideal olarak yaklaşık 12,88 V üretir; 12 V sınırı garanti edilmez. 1,467 Ω direnç yükü bu durumda yaklaşık 8,78 A çeker. Eşit çıkış gücüyle karşılaştırma yapılırken duty her giriş ve kayıplı aday için ayrıca ayarlanır.

## Dosyalar

- [Çalışma yönergeleri](CLAUDE.md)
- [Proje kapsamı ve varsayımlar](buck/PROJE-TANIMI.md)
- [Tasarım hesabı](buck/TASARIM-HESABI.md)
- [Hesap betiği](buck/hesap.py)
- [Hesap çıktısı](buck/hesap-sonuc.json)
- [Parametre karşılaştırması](buck/PARAMETRE-KARSILASTIRMA.md)
- [Parametre tarama betiği](buck/parametre_taramasi.py)
- [Tarama çıktısı](buck/tarama-sonuc.json)

Hesap çıktısı analitik sonuçtur; simülasyon veya fiziksel ölçüm değildir. LTspice sonuçları `buck/ltspice/` altında ayrı tutulur; laboratuvar ölçümü henüz yoktur.
