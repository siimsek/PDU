# D-004 — O1 ≤12.0 V için zamanlama stratejisi

- **Kart:** tasks/D-004.md
- **Yazan:** Codex (GPT-6), 2026-11-07
- **Kullanıcı kararı gerekli mi:** Hayır — öneri (d) ölçülebilir tam-zincir kabul sınırıdır; sonuç T5g fiziksel testinde doğrulanana kadar O1 ≤12.0 V kanıtı koşulludur.

## Soru
Üst anahtar kısa devresinde O1 anlık gerilimini ≤12.0 V tutan akım koruma yolunu, INA296A-Q1 için garanti edilmeyen yerleşme süresine dayanmadan nasıl kanıtlayacağız?

## Seçenekler

Aşağıdaki bağımsız HESAP'ta tek faz kısa devresi, 26 V giriş, 11.1605 V başlangıç barası, Ceff=370.6 µF, 20 mΩ kaynak direnci, faz başlangıç akımı 5.58 A ve 13.6 A geç akım tetik sınırı kullanıldı. L sınırı L=6.8 µH×0.8×f, f=0.05…0.5 tarandı. Hesap modeli ve tüm tablo raporu: [`reports/D-004/independent-calculation.md`](../reports/D-004/independent-calculation.md). Floor'ın arıza boyunca sabit tutulması, 16 A altındaki tipik L(I) eğrisine göre özellikle düşük L varsayımıdır; fiziksel ölçüm/garanti değildir.

| Seçenek | Temel değerler (etiketli) | Kriteri sağlıyor mu | Risk | Kanıt (belge + sayfa) |
|---|---|---|---|---|
| **(a) Sensör yolunu garanti değerli parçayla kur:** iki INA296A2-Q1 + TLV3601’i iki `INA301A1QDGKRQ1` ile değiştir; her faz için harici limit direnci. | **DATASHEET:** INA301A1-Q1 gain 20 V/V, CM 0–36 V, `t_p,max=1 µs` yalnız 1 mV input overdrive test koşulunda. 7.5 mΩ şöntte 1 mV=0.133 A; eşiğin garanti maxı ≤13.467 A olmalı ki 13.6 A’da bu overdrive oluşsun. Uygulama üst eşiği ≤13.3 A seçilirse daha fazla pay bırakır; mevcut hesaplı 13.5344 A köşesi bunu sağlamaz. INA301 1 µs + kartta verilen kalan yol 1.048 µs = 2.048 µs zincir varsayımıyla O1 tepe f=[0.05,0.10,0.15,0.20,0.25,0.30,0.40,0.50] için **[11.5267, 11.3906, 11.3464, 11.3256, 11.3148, 11.3089, 11.3041, 11.3044] V**. | **Koşullu geçer.** Model tüm L-floor taramasında ≤12 V. TI `t_p` max tablosu varsayılan 25°C koşullarında; full-temperature max ve uygulamadaki tam zincir bu datasheet satırından tek başına garanti olmaz. | `INA301A1QDGKRQ1` uygun gain/CM aralığında; limit ayarı ve alert hattı yeniden tasarlanmalı. Datasheet max propagation koşulu 1 mV overdrive. | TI INA301-Q1 Rev.B, p.1, 5–6; 1 mV overdrive satırı p.6; 36 V CM/gain p.1, 5. https://www.ti.com/lit/gpn/INA301-Q1 |
| **(b) Yalnız gerilim yolunu COUT ile kapat:** mevcut 1.048 µs gerilim zinciri + LM74502H 1.0 µs max; TLV3601, REF5025A ve bölücü worst-high eşik 11.5062 V. | **HESAP:** Ceff=370.6 µF durumunda O1 peak f sırasıyla **[12.3606, 12.0784, 11.9602, 11.8920, 11.8467, 11.8137, 11.7687, 11.7391] V**. ≤12.0 V için gereken toplam Ceff sırasıyla **[842.60, 467.16, 370.60, 370.60, 370.60, 370.60, 370.60, 370.60] µF**; 32 kapasitörün sağladığı 11.58125 µF/kapasitörle toplam adet **[73, 41, 32, 32, 32, 32, 32, 32]**. Bütün floor taramasını tek Ceff ile kapatmak için ≥842.60 µF ve 73 adet gerekir (+41 adet). | **Sayısal modelde evet; önerilmez.** En kötü L-floor için 73 adet gerekir ve eşik/indüktör model belirsizliğine bağlıdır. | Fazla kart alanı; exact component ripple/DC-bias/thermal corner needs recalculation. | R_OVT/R_OVB ve parça değerleri `design/pdu_v2_spec.yaml`; REF5025A-Q1, TLV3601 ve LM74502H TI datasheet'leri. LM74502H `tOVP_OFF,max=1.0 µs` @4.7 nF, p.7. |
| **(c) Vishay’den 16–40 A L(I) verisi al:** mevcut floor varsayımını ancak parça için sınırlandırılmış L(I) verisiyle değiştirmek. | **DATASHEET/AÇIK:** Vishay grafiği 16 A’ya kadar tipik; exact design MPN `IHLP4040DZER6R8M01` için kamuya açık datasheet 6.8 µH ±20% ve tipik saturation value verir, fakat 16–40 A guaranteed minimum L(I) vermiyor. Veri gelmezse (b)’deki mevcut-model peak vektörü aynen kalır. | **Şimdilik hayır.** 16–40 A verisi kamuya açık değil; yalnız yeni bir tipik eğri varsayımı kaldırmaz. Vishay’den min L(I) ve sıcaklık/tolerans kapsamı açık garanti edilirse yeniden hesaplanmalı. | Veri talebinin cevabı/doğrulanmış garantili alt sınır yok. | Vishay exact part datasheet doc 34193; D-004’te atıf yapılan doc 34207 tipik grafiği 16 A’da sonlanıyor. https://www.vishay.com/docs/34193/ihlp-4040dz-01.pdf · https://www.vishay.com/docs/34207/ihlp-4040dz-l1.pdf |
| **(d) T5g tam-zincir gecikme kabulü:** akım eşiğinin 13.6 A olduğu en geç köşeden MOSFET VGS<1 V’a kadar gecikmeyi ölç. | **HESAP + TEZGAH KABULÜ:** modelde ≤12 V için izin verilen gerçek delay f sırasıyla **[3.29, 4.45, 5.27, 5.94, 6.49, 6.97, 7.76, 8.40] µs**. En kötü f=0.05’te 3.29 µs. Ölçüm genişletilmiş belirsizliği U≤0.1 µs ise osiloskopta ölçülen zincir gecikmesi **≤3.0 µs** kabulü gerçek delay≤3.1 µs verir; O1 tepe vektörü **[11.9162, 11.6140, 11.5104, 11.4591, 11.4297, 11.4113, 11.3908, 11.3815] V**. Kabulde doğrudan O1 ölçümü de ≤12.0 V olmalı. | **Öneri; ölçüm öncesi koşullu.** Simülasyon değil, T5g fiziksel ölçümü kanıt olacak. | Gerçek L(I), sıcaklık ve board parasitics en kötü senaryo testinde temsil edilmeli; 26 V, min Ceff, gerçek source resistance ve her faz denenmeli. | Ölçüm aralığı kullanıcı T5g test düzeneğinde uygulanır; uncertainty≤0.1 µs test gereksinimidir. LM74502H tOVP_OFF max1 µs, 4.7 nF, TI datasheet p.7. |

### BUILDER karşılaştırması (bağımsız hesap sabitlendikten sonra)

| Büyüklük | Kendi sonuç | BUILDER sonucu | Fark | Yorum |
|---|---:|---:|---:|---|
| Yalnız gerilim yolu, f=0.05, nominal 11.3901 V eşik / benim 370.6 µF | 12.1480 V | 12.1464 V | +0.0016 V (+0.013%) | Yakın sayısal eşleşme; builder Ceff=378.7056 µF ve V-guarantee=11.76465 V kullanıyor. Bu benzerlik aynı model/parametre kullanıldığı anlamına gelmez. |
| Yalnız gerilim yolu, f=0.05, worst-high eşik | 12.3606 V | 12.1464 V | +0.2143 V (+1.766%) | Aynı koşullar değil: kendi hesabımda eşik toleranslarını yukarı yuvarladım ve L-floor’ı fault boyunca sabit tuttum; builder tipik 0–16 A L(I) eğrisinden 16 A üstüne eğim ekstrapolasyonu kullanıyor. İkisi de 12 V kriterini geçmiyor. |
| Akım yolu worst O1 | INA301 varsayılan 2.048 µs zincirinde 11.5267 V | 11.4106 V (mevcut zincir 2.5561 µs) | +0.1160 V (+1.016%) | Karşılaştırma doğrudan eş koşul değil: sensör ve L profili farklı; builder sonucu bağımsız öneri hesabının yerine kullanılmadı. |

**Körlük notu:** D-004 için bazı BUILDER sonuç dosyaları hesaplar tamamlanmadan önce yanlışlıkla açıldı; kullanıcıya bu durum çalışma sırasında bildirildi. Seçenek hesapları sonradan girdiler, devre değerleri ve üretici datasheet’lerinden bağımsız yeniden yapılıp karşılaştırma paketi ancak hesap kaydı oluşturulduktan sonra açıldı. Bu nedenle inceleme bağımsız hesap içeriyor fakat tam kör değildir.

## Öneri
(d) seçeneğini ana kabul kapısı yap: T5g’de gerçek O1 peak≤12.0 V, tam zincir gecikmesi≤3.0 µs (ölçüm U≤0.1 µs). INA301A1-Q1 (a) daha hızlı ve 20 V/V doğrudan alternatiftir, ancak mevcut max eşik overdrive şartını karşılamadığı ve datasheet tam-sıcaklık gecikme garantisi vermediği için tek başına kapanış sayılmaz. T5g geçmeden O1≤12.0 V kesin kanıtı verilmemeli.

## Kanıt
- TI INA301-Q1 Rev.B: A1 gain20 V/V ve 0–36 V common-mode; p.1 ve p.5. Total alert propagation delay max1 µs, input overdrive 1 mV koşulu; p.6. Datasheet: https://www.ti.com/lit/gpn/INA301-Q1
- TI TLV3601 Rev.E: input offset ±5 mV, input bias max5 µA, hysteresis max5 mV, comparator timing conditions; https://www.ti.com/lit/ds/symlink/tlv3601.pdf
- TI REF5025A-Q1: initial accuracy ±0.1%; https://www.ti.com/lit/ds/symlink/ref5025a-q1.pdf
- TI LM74502H-Q1: OVP gate turn-off max1 µs at C_GATE-SRC=4.7 nF; datasheet p.7. https://www.ti.com/lit/ds/symlink/lm74502h-q1.pdf
- Vishay IHLP-4040DZ-L1 doc34207 and exact commercial family doc34193: https://www.vishay.com/docs/34207/ihlp-4040dz-l1.pdf and https://www.vishay.com/docs/34193/ihlp-4040dz-01.pdf
- Hesap girdisi ve RK4 yöntemi: [`reports/D-004/independent-calculation.md`](../reports/D-004/independent-calculation.md).

## Açık varsayımlar
- **VARSAYIM:** f-floor tüm akım rampası boyunca sabit tutuldu; gerçek Vishay curve is only typical through16A, and future values beyond16A are not established.
- **VARSAYIM:** 2.048 µs in option(a) is INA301 1.0 µs plus 1.048 µs downstream budget; ALERT load, latch path and full temperature corner must be bench verified.
- **VARSAYIM:** 5.58 A initial phase current, 13.6 A latest OCP trip and 20 mΩ source resistance are the tabulated envelope; use actual test setup to confirm.
- **VARSAYIM:** high OVP trip threshold11.5062 V sums TLV3601 offset, input bias, hysteresis, REF5025 tolerance and divider resistor tolerance in the direction delaying the trip.

## Doğrulanamayanlar
- Vishay guaranteed minimum L(I) for the design inductor from16 to40A across tolerance and temperature — **doğrulanamadı**; https://www.vishay.com/docs/34193/ihlp-4040dz-01.pdf — published performance curve is typical and provides no guaranteed 16–40 A lower envelope.
- INA301-Q1 comparator propagation-delay maximum over the complete −40…125°C range under this exact shunt/alert loading — **doğrulanamadı**; https://www.ti.com/lit/gpn/INA301-Q1 — the table’s 1 µs max is listed for its stated test condition, while temperature plot is typical.
