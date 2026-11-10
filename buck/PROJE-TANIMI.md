# Proje Tanımı — Açık Çevrim Buck Güç Katı

**Tarih:** 10 Kasım 2026
**Durum:** L / f / CIN / COUT kombinasyonları analitik olarak karşılaştırılıyor; verim kazananı seçilmedi. Yeni LTspice devresi henüz kullanıcıyla kurulmadı.

## Amaç

6S LiPo için kabul edilen 20–26 V DC girişten 11 V / 7,5 A (82,5 W) hedefleyen tek faz, asenkron buck güç katısını hesaplamak ve LTspice'ta birlikte sıfırdan kurup incelemek.

Bu, **açık çevrim güç katıdır**. 11 V yalnız nominal çalışma hedefidir; Vin değiştiğinde sabit duty çıkışı regüle etmez. 12 V üst sınırı, kalkış davranışı veya yük güvenliği garanti edilmez.

## Devre sınırı

- DC giriş kaynağı
- S1 anahtarı ve LTspice `PULSE` sürme kaynağı
- D1 serbest geçiş diyodu
- L1 bobin
- CIN ve COUT
- RLOAD simülasyon yükü

Elektronik PWM kontrolcüsü, MOSFET sürücüsü, op-amp, geri besleme, kompanzasyon, soft-start, ikinci faz, koruma devreleri ve PCB bu çalışmanın kapsamında değildir. PULSE kaynağı yalnızca simülasyon anahtarlamasıdır.

## Önceki referans hesap noktası

Yeni karşılaştırmada bütün adaylar aynı 11 V / 7,5 A / 82,5 W çıkış hedefinde değerlendirilecek. Gerçek kayıplı simülasyonda duty her kombinasyonda hedef çıkışa göre ayrı ayarlanacak. [Parametre karşılaştırması](PARAMETRE-KARSILASTIRMA.md) farklı L/f/C adaylarını içerir.

| Parametre | Aday değer | Seçim ölçütü / açıklama |
|---|---:|---|
| Vin | 20–26 V; nominal 22,2 V | İdeal duty hesabı |
| Vo hedefi | 11 V | Nominal çalışma noktası |
| Iout tasarım noktası | 7,5 A | 82,5 W |
| fsw | 100 kHz | Başlangıç frekansı; optimize edilmiş değil |
| L1 | 39 µH | 26 V'ta yaklaşık %21,7 nominal ripple; −%20 toleransta yaklaşık %27,1 |
| CIN | 470 µF | 15 mΩ ESR varsayımı ve −%20 L toleransıyla yaklaşık 0,167 V giriş ripple hesabı |
| COUT | 220 µF | 20 mΩ ESR varsayımıyla yaklaşık 52,3 mV ripple; −%20 L toleransında |
| RLOAD | 1,467 Ω | 11 V ve 7,5 A eşdeğer yükü; 82,5 W harcar |

Bu tablodaki 52,3 mV yalnız L toleransını içerir. COUT da −%20 olduğunda yaklaşık 55,13 mV çıkar ve 55 mV hedefi az farkla aşılır. 220 µF nihai seçim değildir. Tarama her iki kapasitörün toleransını da içerir.

ESR değerleri yalnızca sonraki kayıplı simülasyon için model varsayımlarıdır, seçilmiş kondansatör verisi değildir. Gerçek parça MPN'leri, gerilim/akım dereceleri ve sıcaklık koşulları ayrıca veri sayfasıyla doğrulanmalıdır.

## Güvenli kullanım sınırı

22,2 V giriş için hesaplanan ideal duty `D = 11/22,2 ≈ 0,4955` değeridir. Bu duty sabit tutulursa 20 V girişte ideal çıkış 9,91 V, 26 V girişte 12,88 V olur. 1,467 Ω simülasyon direnci 26 V girişte yaklaşık 8,78 A çeker. Gerçek O1, RPLIDAR S2E veya hassas bir yük bu açık çevrim devreye bağlanmaz.

İlk devre yalnız LTspice simülasyonunda kurulacaktır. Analitik hesap, simülasyon ve fiziksel ölçüm ayrı sonuçlardır; bu depoda şu anda LTspice devresi veya LTspice sonucu yoktur.
