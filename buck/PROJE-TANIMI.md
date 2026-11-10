# Proje Tanımı — Aşama 1: Açık Çevrim Buck

**Tarih:** 10 Kasım 2026

## Ana hedef

6S LiPo kaynağından (20–26 V) **11 V / 7.5 A (82.5 W)** hedeflenen tek faz **asenkron buck güç katını** hesaplamak, LTspice'ta **çizilmiş ve düzenlenebilir** devreyle ideal/kayıplı simülasyonları yapmak ve sonuçları kıyaslamak.

**İlk aşamada yalnız bunlar:** Vin kaynağı, S1 anahtarı, D1 serbest geçiş diyodu, L1 bobin, CIN, COUT ve direnç yükü. Anahtarın periyodik açılıp kapanması için LTspice'ta `VCTRL PULSE(...)` kullanılır. Bu, fiziksel PWM kontrolcü devresi değildir.

### Doğrudan LTspice'ta açılacak çizimler

- [buck-ideal.asc](buck-ideal.asc): ideal açık çevrim devre
- [buck-kayipli.asc](buck-kayipli.asc): kaynak, anahtar, bobin, kondansatör ESR ve diyot kayıpları ile aynı devre
- [buck-ideal.cir](buck-ideal.cir) ve [buck-kayipli.cir](buck-kayipli.cir): karşılaştırma amaçlı eşdeğer **metinsel** netlistler; görsel şema yerine geçmezler.

**Kullanım:** Windows LTspice > File > Open > `.asc` dosyasını seç > Run. Vin / Iout değerlerini şematikteki `.param` satırlarından değiştir. `V(VOUT)` ve `I(L1)` dalga şekillerine bak; SPICE Error Log'da `.meas` sonuçlarını incele. Varsayılan: Vin=22.2 V, Iout=7.5 A, f=100 kHz.

## Kapsam dışı

Elektronik PWM üreteci, op-amp, karşılaştırıcı, MOSFET sürücü, geri besleme, Tip III kompanzasyon, yumuşak başlatma, ikinci faz, koruma devreleri, KiCad şematiği, PCB ve gerçek cihaz bağlantıları bu aşamaya **dahil değildir**. Önceki çalışmalar silinmemiştir, [arşivde](../archive/buck-onceki-calisma-2026-11-10/README.md) durur.

## Başlangıç değerleri

| Parametre | Değer |
|---|---:|
| Vin | 20 / 22.2 / 26 V |
| Vo hedef | 11 V |
| Iout tasarım | 7.5 A |
| f | 100 kHz |
| L1 | 33 µH |
| CIN | 440 µF (2 × 220 µF eşdeğeri) |
| COUT | 1360 µF (2 × 680 µF eşdeğeri) |
| RLOAD | 1.467 Ω (11 V, 7.5 A hedefinde) |

Değerler ilk adaylardır; "en verimli / kararlı" oldukları simülasyonla henüz kanıtlanmadı. **Açık çevrimde 11 V regülasyonu veya 12 V üst sınırı garanti edilemez.** Koruma sistemi doğrulanmadan O1, RPLIDAR S2E gibi gerçek cihazları bağlama.

## Aşama 1 testleri

İdeal ve kayıplı şema; giriş 20 / 22.2 / 26 V, nominal ve hafif yük; bobin akımı ve çıkış dalgalanması; ilk kalkış aşımı; sabit duty ile giriş değişimi; L/C tolerans deneyi. Kabul: LTspice görüntüsü, parametreler, ölçümler, hesap–simülasyon farklarının açıklaması.

Aşama 1 onaylanmadan kontrolcü, sürücü, koruma, PCB çalışmasına geçilmez. Hesap, varsayım, simülasyon ve fiziksel ölçümü birbirinden ayrı tut.
