# Açık çevrim buck güç katı

Bu depo, 20–26 V girişten 11 V / 7,5 A hedefleyen tek faz asenkron buck güç katının hesaplarını ve yönergelerini tutar. Eski şematikler ve arşiv, kullanıcı isteğiyle temizlendi. Yeni LTspice şematiğini birlikte sıfırdan kuracağız.

## LTspice çizimine başlayacağımız aday

L, CIN, COUT ve frekans değerleri karşılaştırılıyor; henüz verim açısından kazanan seçilmedi. [Parametre taraması](buck/PARAMETRE-KARSILASTIRMA.md) 11 V / 7,5 A / 82,5 W hedefinde farklı kombinasyonların analitik ön elemesini içerir. İlk LTspice çizimi için taramadaki 100 kHz adayı kullanılacak.

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

Hesap çıktısı analitik sonuçtur; simülasyon veya fiziksel ölçüm değildir. Gerçek bileşen modeli, LTspice sonuçları ve laboratuvar ölçümleri ayrı kaydedilecektir.
