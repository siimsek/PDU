#!/usr/bin/env python3
"""T-053: writes report.md from variants.json, isolated.json, recheck.json and the T-038 per-corner evidence on origin/wp/T-038.
Run from the repo root: python reports/g5/T-053/gen_report.py"""
import csv
import io
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "reports/g5/T-053"
C = ("f5_vt11.487_td300ns_ctyp_r200m_l0.8", "f5_vt11.765_td300ns_ctyp_r200m_l0.8")
F = lambda v, n=3: "—" if v is None else f"{v:.{n}f}".replace(".", ",")
load = lambda n: json.loads((OUT / n).read_text(encoding="utf-8"))
show = lambda p: subprocess.run(["git", "show", f"origin/wp/T-038:{p}"], cwd=ROOT, capture_output=True, encoding="utf-8", check=True).stdout


def main():
    V, I, R = load("variants.json"), load("isolated.json"), load("recheck.json")
    tags = list(dict.fromkeys(r["variant"] for r in V["rows"]))
    stall = {c: json.loads(show(f"reports/g5/T-038/stall/{c}.stall.json")) for c in C}
    wave = {c: [{k: float(v) for k, v in r.items()} for r in csv.DictReader(io.StringIO(show(f"reports/g5/T-038/stall/{c}.wave.csv")))] for c in C}
    fault = [r for r in wave[C[0]] if r["time"] >= 100e-6]
    imax = max(r["i(vm1)"] for r in fault); vinmin = min(r["v(vin)"] for r in fault)
    L_up, cin, cout = 0.8 * 6.8e-6, 18.8e-6, 659.904e-6
    e_l, e_cin, e_cout = 0.5 * L_up * imax ** 2, 0.5 * cin * 26 ** 2, 0.5 * cout * 11 ** 2
    rows, clean, fails = [], [], {}
    for t in tags:
        rs = [r for r in V["rows"] if r["variant"] == t]
        st = [r for r in rs if r["scenario"] in C]
        ne = [r for r in rs if r["scenario"] not in C]
        comp = sum(r["completed"] for r in rs)
        bad = [(r["scenario"], k) for r in rs for k, v in r["criteria"].items() if v is False]
        fails[t] = bad
        if comp == len(rs) and not bad:
            clean.append(t)
        peak = max((r["measures"].get("vraw_max_fault", 0) for r in rs), default=0)
        big = max((abs(x) for r in ne for k, x in r["delta_vs_original_criteria_measures"].items() if k != "vin_max"), default=0)
        rows.append(f"| {t} | {'/'.join(str(r['exit']) for r in st)} | {comp}/{len(rs)} | {len(bad)} | {F(peak)} | {F(big)} |")
    ramp = [r for r in I["rows"] if r["test"] == "ramp" and r["VEN_R"] == 1.0]
    ramp_t = "\n".join(f"| {r['variant']} | {F(r['vin_rise'])} | {F(r['vin_fall'])} |" for r in ramp)
    corners = "\n".join(f"| {r['VEN_R']:g} | {F(r['ideal_rise'], 2)} | {F(r['vin_rise'])} | {F(r['ideal_fall'], 2)} | {F(r['vin_fall'])} |".replace(".", ",", 1) for r in I["rows"] if r["test"] == "ramp" and r["variant"] == "base")
    dips = {t: sorted(r["width_us"] for r in I["rows"] if r["test"] != "ramp" and r["variant"] == t and r["disabled"]) for t in dict.fromkeys(r["variant"] for r in I["rows"])}
    dip_t = "\n".join(f"| {t} | {F(v[0], 1) if v else 'yok'} |" for t, v in dips.items())
    rc = [r for r in R["rows"] if r["scenario"].startswith("f5")]
    rc_txt = "; ".join(f"{t}: {', '.join(F(r['vraw_max_fault'], 4) for r in rc if r['variant'] == t)} V" for t in dict.fromkeys(r["variant"] for r in rc))
    dip_err = [r for r in R["rows"] if r["scenario"].startswith("f2")]
    err_txt = "; ".join(f"{r['variant']}: çıkış {r['exit']}, `{r['error_lines'][0]}`" for r in dip_err)
    all_fail = "; ".join(f"{t}: {', '.join(k + ' @ ' + s[:12] + '…' + s[-12:] for s, k in v)}" for t, v in fails.items() if v)
    f1 = [r for r in V["rows"] if r["scenario"] == "f1_worst" and r["variant"].startswith("sch0p45")][0]
    md = f"""# T-053 — F5 enable modelinin kontrollü yakınsama analizi

**Sonuç: AÇIK. `design/pdu_v2.cir` değiştirilmedi, 76 koşu yeniden yapılmadı.** Bu dosyadaki koşular deneydir ve resmi F5 sonucu değildir. Eski FAIL/AÇIK kayıtları olduğu gibi durur. Simülasyon fiziksel kanıt değildir.

## EN ile iç düğüm ayrımı

| Katman | Deck | Kaynak | Değer |
|---|---|---|---|
| Fiziksel EN/UVLO | `BVEN`, `BENS` içindeki `VEN_R`, `VEN_H` | DATASHEET TI SNVSBX7A s.6, s.13 §7.3.3 | VEN_R 0,95/1,00/1,05 V; VEN_H 0,1 V tipik, garantili aralık değil |
| İç durum `ens` | `BENS`, `CENS` | Model | VARSAYIM: 1 mA/1 nF, τ = 1 µs |
| İç çözümleme | `V(ens)>0.5` (`BSS`, `BEA`, `BSW1`, `BSW2`) | Model | VARSAYIM: TI belgesinde karşılığı yok |

Hiçbir varyant VEN_R veya VEN_H değerini değiştirmez. Varyantlar yalnız iç `V(ens)>0.5` çözümlemesinin önüne eklenir.

## Kilitlenme kanıtı

Köşe başına deck, SHA-256, komut, süre, simülatör, dalga ve çıkış `origin/wp/T-038` dalında `reports/g5/T-038/stall/` altındadır. İki köşede t_son {stall[C[0]]['t_last_s']:.9e} ve {stall[C[1]]['t_last_s']:.9e} s, çıkış {stall[C[0]]['exit']}, kabul edilmiş son pencerede işaret değişimi yok. Reddedilen adımlar görünmediği için tek nedenli mekanizma **kanıtlanmadı**; `V(ens)>0.5` hipotezi desteklendi ama ispat edilmedi.

## İzole EN deneyi

[run_isolated.py](run_isolated.py), [isolated.json](isolated.json). Deck'in dört satırı değiştirilmeden kullanıldı; girişler idealdir.

VEN_R taraması, temel model (HESAP oran 18,4; direnç toleransı yok):

| VEN_R V | İdeal yükselen VIN | Ölçülen | İdeal düşen VIN | Ölçülen |
|---|---:|---:|---:|---:|
{corners}

VEN_R 1,0 V, varyant etkisi:

| Varyant | Yükselen VIN | Düşen VIN |
|---|---:|---:|
{ramp_t}

26→10 V kısa düşüşte durumu kapatan en küçük genişlik:

| Varyant | µs |
|---|---:|
{dip_t}

Yani varyantlar eşiği en çok onlarca mV kaydırır ama kısa düşüş bağışıklığını değiştirir. TI belgesinden EN deglitch süresi bu kartta alınmadı; karşılaştırma ölçütü **AÇIK**.

## Tam devre matrisi

[run_t053.py](run_t053.py), [variants.json](variants.json). 9 senaryo × 8 varyant, koşu başı {V['limit_s']} s limit. Netlist SHA-256 öneki `{V['netlist_sha256'][:16]}`. Senaryolar: 2 kilitlenen köşe, 3 F5 komşusu, f1_worst, hotplug, UVLO rampası, 22→15 V düşüş.

| Varyant | Köşe çıkışları | Tamamlanan | Kriter FAIL | En yüksek vraw_max_fault V | Komşu sapması en çok V |
|---|---|---:|---:|---:|---:|
{chr(10).join(rows)}

Komşu sapması `vin_max` dışındaki kriter ölçümlerinin orijinalden en büyük mutlak farkıdır.

**OLGU:**
- Yakınsama τ ile tek yönlü değişmez: 0,05 µs zaman aşımı, 0,2 ve 1 µs biter, 5 µs zaman aşımı.
- Kriter FAIL: {all_fail}.
- Tekrarlanabilirlik: [recheck.json](recheck.json). {rc_txt}. Sapmalar deterministiktir.
- f2_dip çıkış 1: {err_txt}.
- f1_worst, Schmitt 0,45/0,55 varyantında `vraw_max_fault` {F(f1['measures']['vraw_max_fault'], 4)} V (fark {F(f1['delta_vs_original_criteria_measures']['vraw_max_fault'], 4)} V). Mevcut geçen bir F1 ölçümü de iç çözümlemeye duyarlıdır.

Tüm dokuz senaryoyu kriter FAIL olmadan bitiren varyantlar: {', '.join(clean)}. Bunların komşu varyantları başarısızdır, yani geçiş dar bir sayısal aralıktadır.

## Kapı kararı

Ana deck değişikliği için üç koşul arandı: fiziksel veya sayısal gerekçe, varyant değerinden bağımsız sonuç, geçen senaryolarda değişmezlik. Hiçbiri sağlanmadı. Kart durdurma koşulu uygulandı: T-038 RC denemesi ve bu matris olmak üzere iki kontrollü denemede güvenilir karşılaştırma yok. İki F5 köşesi **AÇIK** kalır; 21,107 V gibi varyant sayıları F5 sonucu olarak kullanılmaz.

Yeni bulgu: vraw ve VDS tepe değerleri iç `ens` çözümlemesine duyarlıdır. Geçmiş F5/F1 değerlerinin bu duyarlılığı kapsamlı biçimde ölçülmedi, **AÇIK**.

## Tezgâh gereksinimi

Sayılar model veya hesaptır, tezgâh limiti değildir. Akım sınırı ve test sırası bu raporla belirlenmez.

| Büyüklük | Değer | Etiket |
|---|---|---|
| Fault sonrası faz 1 tepe akımı | {F(imax, 2)} A (1 µs seyreltilmiş dalga) | SİM, kilitlenen koşu |
| VIN minimum | {F(vinmin, 2)} V | SİM |
| VIN yeniden etkinleşme | yaklaşık 18,43 V | SİM, kilitlenme noktası |
| Yükselen/düşen UVLO (VEN_R tipik, VEN_H tipik) | 18,4 / 16,56 V | HESAP |
| L enerji üst sınırı, ½·5,44 µH·I² | {F(e_l * 1e3, 1)} mJ | HESAP, doygunluk yok sayıldı |
| CIN enerji, ½·18,8 µF·26² | {F(e_cin * 1e3, 1)} mJ | HESAP, Ceff VARSAYIM |
| COUT enerji, ½·659,9 µF·11² | {F(e_cout * 1e3, 1)} mJ | HESAP, tipik Ceff |

UVLO civarında kısa devre maddesi `tasks/backlog.md` içinde (R-026) korunur. Ölçülecekler: VIN/EN, iki faz akımı, VOUT/VSAFE/O1, koruma süresi, yeniden başlatma, ısı. Akım sınırlı kaynakla, düşük akımdan başlanmalıdır. Model bu davranışı doğrulayamadı.

## THINKER'a açık soru

İki köşe için seçenekler: (a) yeniden etkinleşme anı için fiziksel gerekçeli alt model, (b) AÇIK tutup tezgâh testine bırakmak. Karar D-kartı ile verilmelidir; bu kart seçmez.
"""
    (OUT / "report.md").write_text(md, encoding="utf-8", newline="\n")
    print("clean", clean)
    print("fails", {k: len(v) for k, v in fails.items()})
    print(round(imax, 2), round(vinmin, 2), round(e_l * 1e3, 2), round(e_cin * 1e3, 2), round(e_cout * 1e3, 2))


if __name__ == "__main__":
    main()
