# IDA PDU — Tasarım Doğrulama Durumu

**Tarih:** 2026-10-14 • **Sonuç:** Referans tasarım; fiziksel prototip ve üretim onayı yok.

| ID | Kontrol | Hedef/ölçüt | Mevcut kanıt | Durum |
|---|---|---|---|---|
| V-01 | O1 giriş ratingi | Kullanılan kart sürümü için resmi sınırlar | T3 donanım GitHub 5–12 V/5 A; ArduPilot overview 5–12 V/3 A çelişkisi | AÇIK |
| V-02 | O1 akım profili | Start/steady/peak | Ölçüm yok | AÇIK |
| V-03 | S2E girişi | 9–28 V; 12 V start typical 1.2 A, datasheet üst 1.5 A; work upper 0.22 A | SLAMTEC S2E v1.8 datasheet | KATALOG DOĞRULANDI; 11 V START AÇIK |
| V-04 | Buck seçimi | VIN aralığı ve akım | LM70880-Q1 4.5–80 V, 8 A datasheet/product page | KATALOG DOĞRULANDI |
| V-05 | Çıkış gerilimi | 11.0 V ±2% hedef | Ölçüm yok | AÇIK |
| V-06 | Toplam bütçe | ≥78 W planlama zarfı, 82.5 W hedef | Rating-based O1 upper envelope + S2E 12 V table | HESAP; ÖLÇÜM AÇIK |
| V-07 | Verim | Her giriş/yük koşulunda ölç | IDA PDU sim/bench yok; TI ref başka koşul | AÇIK |
| V-08 | Ripple/transient | Device pins within ratings; bus ±2% steady | Ölçüm yok; parasitic/loop model yok | AÇIK |
| V-09 | Surge/reverse | Ölçülen ESC transientinde no damage | SMCJ33A/80 V buck aday; waveform/energy missing | KRİTİK AÇIK |
| V-10 | Branch eFuse | Trip profiles and thermal rise acceptable | TPS259824ONRGET candidate and datasheet ILIM equation; circuit not laid out | AÇIK |
| V-11 | Termal | Worst-case sıcaklık limitlerinde marj | PCB ve ölçüm yok | AÇIK |
| V-12 | KiCad ERC/DRC | Kritik çözülmemiş hata 0 | KiCad 10.0.5 ile işlevsel blok sayfası SVG olarak açıldı; elektriksel şema/PCB yok | ERC/DRC ÇALIŞTIRILMADI |
| V-13 | LTspice | Tekrarlanabilir kaynak/log; kapsam açıklanmış | LTspice 26.1.1 batch; 4 giriş koşulunda 12–15 ms ortalaması 11.000 V civarı; IC makromodeli değil | ORTALAMA MODEL KOŞTU; SİLİKON/EMI/TERMAL DOĞRULAMA DEĞİL |
| V-14 | BOM/bütçe | Yerel toplam ve onaylı bütçe | Birkaç distributor fiyatı; PCB/assembly/kablo açık | AÇIK |

## Ölçüm formu

| Tarih | Kart sürümü | Vin | O1 mode | S2E mode | Iin | Iport1 | Iport2 | Vbus min/max | ripple | T hottest | Sonuç |
|---|---|---:|---|---|---:|---:|---:|---:|---:|---:|---|
| — | — | — | — | — | — | — | — | — | — | — | Ölçülmedi |

## Geçme koşulları

1. 20 V girişte en ağır eşzamanlı gerçek yük altında cihaz girişleri üretici sınırında, bus 11.0 V ±2% steady-state.
2. Kalkış/load step sırasında cihaz girişleri min rating altına düşmez; eFuse erken açmaz; tepe değerler absolute maximum altındadır.
3. Surge waveform/süre/enerji kaydedilir; TVS, fuse, reverse protection ve U1 pinindeki clamp koordine edilir.
4. Termal denge sonunda bileşen derating ve kablo/konnektör sınırları korunur.
5. ERC/DRC kapanır; BOM MPN'leri eşleşir; Gerber üretici kontrolünden geçer.

Bu koşullar fiziksel prototipte gösterilmedi. Katalog sınırları ürünün güvenli çalıştığını kanıtlamaz.
