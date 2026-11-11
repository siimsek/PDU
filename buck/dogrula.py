#!/usr/bin/env python3
"""LTspice dogrulama kosulari: acik cevrim buck guc kati, gercek yuk senaryolari.

Ana sematige dokunmaz. Netlistleri gecici klasorde uretir, LTspice'i toplu kipte (-b)
kosar, .meas sonuclarini tablo olarak yazar. Buyuk .raw dosyalari repoya girmez.

Kullanim:
  python buck/dogrula.py tarama      # 9 aday (L x Cout) karsilastirmasi
  python buck/dogrula.py secilen     # secilen tasarim: 5 giris, yuk, kalkis, tolerans
  python buck/dogrula.py grafik      # buck/grafik/*.svg
  python buck/dogrula.py mevcut      # ana sematigin (eski degerler) yeniden kosusu

Siniflar: buradaki her sayi IDEAL ELEMANLI LTspice SIMULASYONUDUR; fiziksel olcum degildir.
Yuk gucleri icin kaynak/varsayim ayrimi OPTIMIZASYON.md dosyasindadir.
"""
from __future__ import annotations

import math
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

BURADA = Path(__file__).resolve().parent
LIB = BURADA / "ltspice" / "idealler.lib"
LTSPICE = os.environ.get("LTSPICE", r"C:\Program Files\ADI\LTspice\LTspice.exe")

VO = 11.0
VIN_NOKTALARI = (20.0, 22.2, 24.6, 25.2, 26.0)
VIN_ANA = 24.6

# --- Yukler (11 V'ta sabit guc yuku olarak modellenir; ikisinin de girisinde DC-DC var) ---
P_S2E_CALISMA = 12 * 0.22   # W  DATASHEET: 12 V'ta en cok 0,22 A calisma
P_S2E_KALKIS = 12 * 1.5     # W  DATASHEET: 12 V'ta en cok 1,5 A kalkis (suresi verilmemis)
P_O1_ZARF = VO * 5.0        # W  DATASHEET: DC giris 5 A anma (tuketim degil, ust zarf)
P_O1_TIPIK = 10.0           # W  TAHMIN (uretici tuketim yayimlamiyor)
P_O1_BOSTA = 4.0            # W  TAHMIN

MEVCUT = dict(L=33e-6, DCR=15e-3, Cout=330e-6, ESRo=15e-3, Cin=220e-6, ESRi=20e-3,
              Ron=10e-3, Vf=0.5, Rd=10e-3, f=100e3)
SECILEN = dict(MEVCUT, Cout=680e-6, ESRo=25e-3)


def eng(x: float) -> str:
    return f"{x:.6g}"


# ---------------------------------------------------------------- netlist
def netlist(p: dict, *, vin, surucu: str, yuk: list[str], tstop: float, meas: list[str],
            ic: str = "", kaynak: str = "ideal", tstart: float = 0.0, cikis_sabit: bool = False) -> str:
    T = 1 / p["f"]
    s = ["* dogrula.py"]
    if kaynak == "ideal":
        s.append(f"V1 vin 0 {vin}")
    else:  # batarya + kablo (VARSAYIM: 40 mohm, 1 uH)
        s += [f"V1 bat 0 {vin}", "Rbat bat b1 40m", "Lkab b1 vin 1u Rser=10m"]
    s += [f"Cin1 vin 0 {eng(p['Cin'])} Rser={eng(p['ESRi'])}",
          f"Cin2 vin 0 {eng(p['Cin'])} Rser={eng(p['ESRi'])}",
          "Vss vin s_in 0",
          f"XS1 s_in sw pwm 0 anahtar Ron={eng(p['Ron'])}",
          surucu,
          "Vsd 0 d_a 0",
          f"XD1 d_a sw diyot Vf={eng(p['Vf'])} Ron={eng(p['Rd'])}",
          f"L1 sw out {eng(p['L'])} Rser={eng(p['DCR'])}"]
    if cikis_sabit:
        s.append(f"Vkelepce out 0 {VO}")
    else:
        s.append(f"Cout out 0 {eng(p['Cout'])} Rser={eng(p['ESRo'])}")
        s += yuk
    s += [f'.lib "{LIB}"', f".tran 0 {eng(tstop)} {eng(tstart)} {eng(T / 200)}"]
    if ic:
        s.append(f".ic {ic}")
    s += [f".meas tran {m}" for m in meas]
    s.append(".end")
    return "\n".join(s) + "\n"


def surucu_ton(p: dict, ton: float, gecikme: float = 0.0) -> str:
    return f"Vdrv pwm 0 PULSE(0 10 {eng(gecikme)} 10n 10n {eng(ton)} {eng(1 / p['f'])})"


def surucu_duty(p: dict, pwl: str) -> str:
    """Duty'si zamanla degisen PWM (yalniz test netlistinde; ana sematikte yok)."""
    T = 1 / p["f"]
    return (f"Vsaw saw 0 PULSE(0 1 0 {eng(T - 20e-9)} 10n 10n {eng(T)})\n"
            f"Vdut dut 0 PWL({pwl})\n"
            "Bpwm pwm 0 V=if(V(dut)>V(saw),10,0)")


def yuk_r(amper: float) -> list[str]:
    return [f"Rload out 0 {eng(VO / amper)}"]


def yuk_guc(pwl_w: str, vmin: float = 5.0, ad: str = "y") -> list[str]:
    """Sabit guc yuku: I = P(t)/V; vmin altinda sabit akima doner."""
    return [f"Vp{ad} p{ad} 0 PWL({pwl_w})", f"B{ad} out 0 I=V(p{ad})/max(V(out),{vmin})"]


# ---------------------------------------------------------------- kosu
_CALISMA = None


def calisma() -> Path:
    global _CALISMA
    if _CALISMA is None:
        _CALISMA = Path(tempfile.mkdtemp(prefix="buck_dogrula_"))
    return _CALISMA


def kos(metin: str, ad: str = "k", raw: bool = False):
    d = calisma()
    cir = d / f"{ad}.cir"
    cir.write_text(metin, encoding="ascii")
    subprocess.run([LTSPICE, "-b", str(cir)], check=True, timeout=900)
    log = (d / f"{ad}.log").read_bytes()
    log = log.decode("utf-16-le") if log[:2] in (b"\xff\xfe",) or log[1:2] == b"\x00" else log.decode("latin1")
    m = {k.lower(): float(v) for k, v in re.findall(r"^(\w+):.*?=(-?[\d.]+(?:[eE][-+]?\d+)?)", log, re.M)}
    if not m:
        raise RuntimeError("olcum yok:\n" + log[-1500:])
    dalga = oku_raw(d / f"{ad}.raw") if raw else None
    for uz in (".raw", ".op.raw", ".db"):
        (d / f"{ad}{uz}").unlink(missing_ok=True)
    return (m, dalga) if raw else m


def oku_raw(yol: Path) -> dict[str, list[float]]:
    b = yol.read_bytes()
    isaret = "Binary:\n".encode("utf-16-le")
    i = b.index(isaret)
    bas = b[:i].decode("utf-16-le")
    nv = int(re.search(r"No\. Variables:\s*(\d+)", bas).group(1))
    npt = int(re.search(r"No\. Points:\s*(\d+)", bas).group(1))
    adlar = [s.split()[1] for s in bas.split("Variables:\n")[1].strip().splitlines()]
    veri = b[i + len(isaret):]
    kayit = struct.Struct(f"<d{nv - 1}f")
    sutun = {a: [] for a in adlar}
    for k in range(npt):
        r = kayit.unpack_from(veri, k * kayit.size)
        for a, v in zip(adlar, r):
            sutun[a].append(v)
    sutun["time"] = [abs(t) for t in sutun["time"]]
    return sutun


# ---------------------------------------------------------------- analitik yardimcilar
def duty_ccm(p: dict, vin: float, io: float) -> float:
    return (VO + p["Vf"] + io * (p["DCR"] + p["Rd"])) / (vin + p["Vf"] + io * (p["Rd"] - p["Ron"]))


def ton_ayarla(p: dict, vin: float, io: float) -> float:
    """Ideal regulasyon varsayimi: cikis 11 V'ta tutulurken ortalama bobin akimi = io olan Ton."""
    T = 1 / p["f"]

    def hata(ton: float) -> float:
        n = netlist(p, vin=vin, surucu=surucu_ton(p, ton), yuk=[], tstop=6e-3, cikis_sabit=True,
                    ic=f"I(L1)={io}", meas=["IL AVG I(L1) FROM 5m TO 6m"])
        return kos(n, "ton")["il"] - io

    d_ccm = duty_ccm(p, vin, io)
    # DCM tahmini: io = D^2 T (vin-VO)(vin+Vf) / (2 L (VO+Vf))
    d_dcm = math.sqrt(max(io, 1e-3) * 2 * p["L"] * (VO + p["Vf"]) / (T * (vin - VO) * (vin + p["Vf"])))
    a = min(d_ccm, d_dcm) * T
    ha = hata(a)
    b = a * (1.002 if ha < 0 else 0.998)
    hb = hata(b)
    for _ in range(12):
        if abs(hb) < 3e-3 or hb == ha:
            break
        a, ha, b = b, hb, b - hb * (b - a) / (hb - ha)
        b = min(max(b, 0.02 * T), 0.98 * T)
        hb = hata(b)
    return b


M_KARARLI = [
    "VO AVG V(out) FROM {a} TO {b}", "VPP PP V(out) FROM {a} TO {b}",
    "VMAX MAX V(out) FROM {a} TO {b}", "VMIN MIN V(out) FROM {a} TO {b}",
    "ILMIN MIN I(L1) FROM {a} TO {b}", "ILMAX MAX I(L1) FROM {a} TO {b}",
    "ILRMS RMS I(L1) FROM {a} TO {b}", "ISRMS RMS I(Vss) FROM {a} TO {b}",
    "IDAVG AVG I(Vsd) FROM {a} TO {b}", "IDRMS RMS I(Vsd) FROM {a} TO {b}",
    "ICORMS RMS I(Cout) FROM {a} TO {b}", "ICIRMS RMS I(Cin1)+I(Cin2) FROM {a} TO {b}",
    "VINPP PP V(vin) FROM {a} TO {b}",
    "PIN AVG V(vin)*I(Vss) FROM {a} TO {b}", "POUT AVG V(out)*(I(L1)-I(Cout)) FROM {a} TO {b}",
]


def olcumler(sablon: list[str], a: float, b: float) -> list[str]:
    return [m.format(a=eng(a), b=eng(b)) for m in sablon]


def kararli(p: dict, vin: float, io: float, *, direnc: bool = True, kaynak: str = "ideal",
            ton: float | None = None, _ince: int = 0) -> dict:
    """11 V'a ayarli Ton ile kararli durum. io: 11 V'taki yuk akimi."""
    ayarli = ton is None or _ince > 0
    ton = ton or ton_ayarla(p, vin, io)
    yuk = yuk_r(io) if direnc else yuk_guc(f"0 {io * VO}")
    ts = 16e-3
    n = netlist(p, vin=vin, surucu=surucu_ton(p, ton), yuk=yuk, tstop=ts, kaynak=kaynak,
                ic=f"V(out)={VO} I(L1)={io}", meas=olcumler(M_KARARLI, ts - 1e-3, ts))
    m = kos(n, "kararli")
    if ayarli and m["ilmin"] > 0.05 and abs(m["vo"] - VO) > 2e-3:
        # CCM ince ayar: cikis ripple'i kelepceli ayarda yok; kalan birkac mV'u Ton ile kapat
        if _ince < 3:
            return kararli(p, vin, io, direnc=direnc, kaynak=kaynak,
                           ton=ton + (VO - m["vo"]) / (vin * p["f"]), _ince=_ince + 1)
    m["ton"] = ton
    m["kayip_s1"] = m["isrms"] ** 2 * p["Ron"]
    m["kayip_d1"] = p["Vf"] * m["idavg"] + p["Rd"] * m["idrms"] ** 2
    m["kayip_l1"] = m["ilrms"] ** 2 * p["DCR"]
    m["kayip_co"] = m["icorms"] ** 2 * p["ESRo"]
    m["kayip"] = m["kayip_s1"] + m["kayip_d1"] + m["kayip_l1"] + m["kayip_co"]
    m["verim"] = m["pout"] / (m["pout"] + m["kayip"])
    return m


# ---------------------------------------------------------------- gecici durum testleri
def kalkis_sert(p: dict, vin: float, io: float, ton: float, yuk: list[str] | None = None, raw: bool = False):
    n = netlist(p, vin=vin, surucu=surucu_ton(p, ton), yuk=yuk or yuk_r(io), tstop=12e-3,
                meas=["IPK MAX I(L1)", "VPK MAX V(out)", "VSON AVG V(out) FROM 11m TO 12m"])
    return kos(n, "sert", raw)


def kalkis_yumusak(p: dict, vin: float, io: float, ton: float, sure: float = 5e-3,
                   yuk: list[str] | None = None, raw: bool = False):
    """Duty 0 -> D dogrusal rampa (yumusak kalkis VARSAYIMI; kontrol devresi tasarimi degildir)."""
    d = ton * p["f"]
    n = netlist(p, vin=vin, surucu=surucu_duty(p, f"0 0 {eng(sure)} {eng(d)}"), yuk=yuk or yuk_r(io),
                tstop=sure + 8e-3,
                meas=["IPK MAX I(L1)", "VPK MAX V(out)",
                      f"VSON AVG V(out) FROM {eng(sure + 7e-3)} TO {eng(sure + 8e-3)}"])
    return kos(n, "yumusak", raw)


def yuk_adimi(p: dict, vin: float, p0: float, p1: float, *, ton: float | None = None,
              t1: float = 4e-3, t2: float = 24e-3, tstop: float = 44e-3, raw: bool = False):
    """Sabit Ton (acik cevrim), sabit guc yuku p0 -> p1 -> p0 [W]."""
    io = p0 / VO
    ton = ton or ton_ayarla(p, vin, io)
    pwl = f"0 {p0} {eng(t1)} {p0} {eng(t1 + 20e-6)} {p1} {eng(t2)} {p1} {eng(t2 + 20e-6)} {p0}"
    n = netlist(p, vin=vin, surucu=surucu_ton(p, ton), yuk=yuk_guc(pwl), tstop=tstop,
                ic=f"V(out)={VO} I(L1)={io}",
                meas=[f"VMAX MAX V(out) FROM {eng(t1)} TO {eng(tstop)}",
                      f"VMIN MIN V(out) FROM {eng(t1)} TO {eng(tstop)}",
                      f"V1SON AVG V(out) FROM {eng(t2 - 2e-3)} TO {eng(t2)}",
                      f"V1PP PP V(out) FROM {eng(t2 - 2e-3)} TO {eng(t2)}",
                      f"V0SON AVG V(out) FROM {eng(tstop - 2e-3)} TO {eng(tstop)}",
                      f"V0PP PP V(out) FROM {eng(tstop - 2e-3)} TO {eng(tstop)}",
                      f"ILMAX MAX I(L1) FROM {eng(t1)} TO {eng(tstop)}"])
    r = kos(n, "adim", raw)
    (r[0] if raw else r)["ton"] = ton
    return r


def yuk_atma_sinir(p: dict, vin: float, p0: float, p1: float) -> dict:
    """Ideal kontrolcu siniri: yuk p0 -> p1 dustugu anda duty 0 olur (en iyi durum).

    Atma, bobin akiminin tepe aninda (iletim sonu) yapilir. Atma oncesi yuk sabit akimdir
    (sabit guc yuku acik cevrimde salinir ve siniri kirletir). vmax = 11 V + olculen artis.
    """
    io = p0 / VO
    ton = ton_ayarla(p, vin, io)
    d = ton * p["f"]
    t1 = 3e-3 + ton
    pwl = f"0 {io} {eng(t1)} {io} {eng(t1 + 1e-6)} {p1 / VO}"
    n = netlist(p, vin=vin, surucu=surucu_duty(p, f"0 {eng(d)} {eng(t1)} {eng(d)} {eng(t1 + 1e-7)} 0"),
                yuk=[f"Iyuk out 0 PWL({pwl})"], tstop=5e-3, ic=f"V(out)={VO} I(L1)={io}",
                meas=[f"VTEPE MAX V(out) FROM {eng(t1)} TO 5m",
                      f"VONCE AVG V(out) FROM {eng(3e-3 - 2e-4)} TO 3m"])
    m = kos(n, "atma")
    m["artis"] = m["vtepe"] - m["vonce"]
    m["vmax"] = VO + m["artis"]
    return m


def giris_adimi(p: dict, v0: float, v1: float, pw: float, raw: bool = False):
    """Sabit Ton, giris v0 -> v1 -> v0 (1 ms rampa), sabit guc yuku pw."""
    io = pw / VO
    ton = ton_ayarla(p, v0, io)
    vin = f"PWL(0 {v0} 4m {v0} 5m {v1} 20m {v1} 21m {v0})"
    n = netlist(p, vin=vin, surucu=surucu_ton(p, ton), yuk=yuk_guc(f"0 {pw}"), tstop=36e-3,
                ic=f"V(out)={VO} I(L1)={io}",
                meas=["VMAX MAX V(out) FROM 4m TO 36m", "VMIN MIN V(out) FROM 4m TO 36m",
                      "V1SON AVG V(out) FROM 18m TO 20m"])
    return kos(n, "giris", raw)


def acik_cevrim_egri(p: dict, vin: float, ton: float, amperler) -> list[tuple[float, float]]:
    """Sabit Ton ile yuk akimina gore kararli cikis (direnc yuk; hafif yukte DCM yukselmesi)."""
    s = []
    for a in amperler:
        r = VO / a
        ts = max(12e-3, 8 * r * p["Cout"])
        n = netlist(p, vin=vin, surucu=surucu_ton(p, ton), yuk=[f"Rload out 0 {eng(r)}"], tstop=ts,
                    ic=f"V(out)={VO}", meas=[f"VO AVG V(out) FROM {eng(ts - 1e-3)} TO {eng(ts)}"])
        s.append((a, kos(n, "egri")["vo"]))
    return s


# ---------------------------------------------------------------- raporlar
def tablo(basliklar: list[str], satirlar: list[list]) -> None:
    print("| " + " | ".join(basliklar) + " |")
    print("|" + "---|" * len(basliklar))
    for r in satirlar:
        print("| " + " | ".join(str(h) for h in r) + " |")
    print(flush=True)


P_HAFIF = P_O1_TIPIK + P_S2E_CALISMA               # 12,64 W
P_HAFIF_KALKIS = P_O1_TIPIK + P_S2E_KALKIS          # 28 W
P_ZARF = P_O1_ZARF + P_S2E_CALISMA                  # 57,64 W
P_ZARF_KALKIS = P_O1_ZARF + P_S2E_KALKIS            # 73 W
P_BOSTA = P_O1_BOSTA + P_S2E_CALISMA                # 6,64 W


def aday_olc(p: dict) -> dict:
    s = {}
    k = kararli(p, VIN_ANA, 7.5)
    s.update(vpp=k["vpp"] * 1e3, dil=k["ilmax"] - k["ilmin"], verim=k["verim"] * 100, kayip=k["kayip"])
    k26 = kararli(dict(p, L=p["L"] * 0.8), 26.0, 7.5)
    s.update(ipk26=k26["ilmax"], vpp26=k26["vpp"] * 1e3)
    a = yuk_adimi(p, VIN_ANA, P_HAFIF, P_HAFIF_KALKIS)
    s.update(a_vmax=a["vmax"], a_vmin=a["vmin"])
    z = yuk_adimi(p, VIN_ANA, P_ZARF, P_ZARF_KALKIS)
    s.update(z_vmax=z["vmax"], z_vmin=z["vmin"], z_pp=z["v1pp"] * 1e3, z0_pp=z["v0pp"] * 1e3)
    s["atma"] = yuk_atma_sinir(p, VIN_ANA, P_ZARF_KALKIS, P_BOSTA)["vmax"]
    c = kalkis_sert(p, 26.0, 7.5, kararli(p, 26.0, 7.5)["ton"])
    s.update(c_ipk=c["ipk"], c_vpk=c["vpk"])
    return s


def tarama() -> None:
    print("## Aday taramasi (LTspice, ideal elemanlar, 24,6 V ana nokta, Cout ESR 15 mΩ)\n")
    sat = []
    for L in (22e-6, 33e-6, 47e-6):
        for C in (330e-6, 470e-6, 680e-6):
            p = dict(MEVCUT, L=L, Cout=C)
            s = aday_olc(p)
            z0 = math.sqrt(L / C)
            sat.append([f"{L * 1e6:g}", f"{C * 1e6:g}", f"{z0:.3f}", f"{s['dil']:.2f}", f"{s['ipk26']:.2f}",
                        f"{s['vpp']:.1f}", f"{s['vpp26']:.1f}", f"{s['verim']:.2f}",
                        f"{s['a_vmin']:.2f}/{s['a_vmax']:.2f}", f"{s['z_vmin']:.2f}/{s['z_vmax']:.2f}",
                        f"{s['z0_pp']:.0f}", f"{s['z_pp']:.0f}", f"{s['atma']:.2f}",
                        f"{s['c_ipk']:.1f}", f"{s['c_vpk']:.1f}"])
            print(sat[-1], file=sys.stderr, flush=True)
    tablo(["L µH", "Cout µF", "Z0 Ω", "ΔIL A", "ILtepe 26V L−20% A", "ΔVo mV", "ΔVo 26V L−20% mV", "η %",
           "hafif adım Vmin/Vmax", "zarf adım Vmin/Vmax", "57,6 W salınım mV", "73 W salınım mV",
           "yük atma sınırı V", "sert kalkış Itepe A", "sert kalkış Vtepe V"], sat)


def secilen(p: dict = SECILEN, ad: str = "Secilen") -> None:
    print(f"## {ad}: L={p['L'] * 1e6:g} µH/{p['DCR'] * 1e3:g} mΩ, Cout={p['Cout'] * 1e6:g} µF/{p['ESRo'] * 1e3:g} mΩ, "
          f"Cin=2×{p['Cin'] * 1e6:g} µF/{p['ESRi'] * 1e3:g} mΩ, Ron={p['Ron'] * 1e3:g} mΩ, "
          f"Vf={p['Vf']:g} V+{p['Rd'] * 1e3:g} mΩ, {p['f'] / 1e3:g} kHz\n")

    print("### 1. Kararlı durum, 7,5 A direnç yük, Ton her girişte 11 V'a ayarlı (ideal regülasyon varsayımı)\n")
    sat, tonlar = [], {}
    for v in VIN_NOKTALARI:
        k = kararli(p, v, 7.5)
        tonlar[v] = k["ton"]
        sat.append([f"{v:g}", f"{k['ton'] * 1e6:.3f}", f"{k['vo']:.3f}", f"{k['vpp'] * 1e3:.1f}",
                    f"{k['ilmin']:.2f}–{k['ilmax']:.2f}", f"{k['isrms']:.2f}", f"{k['idavg']:.2f}",
                    f"{k['icorms']:.2f}", f"{k['kayip_s1']:.2f}", f"{k['kayip_d1']:.2f}", f"{k['kayip_l1']:.2f}",
                    f"{k['kayip']:.2f}", f"{k['verim'] * 100:.2f}"])
    tablo(["Vin V", "Ton µs", "Vo V", "ΔVo mV", "IL A", "S1 rms A", "D1 ort A", "Cout rms A",
           "P S1 W", "P D1 W", "P L1 W", "P toplam W", "η iletim %"], sat)

    print("### 2. Kararlı durum, gerçek yük senaryoları, 24,6 V, Ton 11 V'a ayarlı (sabit güç yükü)\n")
    sat = []
    for isim, pw in (("yalnız S2E çalışma", P_S2E_CALISMA), ("yalnız O1 boşta (tahmin)", P_O1_BOSTA),
                     ("yalnız O1 tipik (tahmin)", P_O1_TIPIK), ("O1 boşta + S2E", P_BOSTA),
                     ("O1 tipik + S2E", P_HAFIF), ("O1 tipik + S2E kalkış", P_HAFIF_KALKIS),
                     ("yalnız O1 zarf 5 A", P_O1_ZARF), ("O1 zarf + S2E", P_ZARF),
                     ("O1 zarf + S2E kalkış", P_ZARF_KALKIS)):
        k = kararli(p, VIN_ANA, pw / VO, direnc=False)
        kip = "DCM" if k["ilmin"] < 0.02 else "CCM"
        sat.append([isim, f"{pw:.2f}", f"{pw / VO:.2f}", f"{k['ton'] * 1e6:.3f}", kip, f"{k['vo']:.3f}",
                    f"{k['vpp'] * 1e3:.1f}", f"{k['ilmax']:.2f}", f"{k['verim'] * 100:.1f}"])
    tablo(["Senaryo", "P W", "I@11V A", "Ton µs", "Kip", "Vo V", "ΔVo mV", "IL tepe A", "η iletim %"], sat)

    print("### 3. Açık çevrim: Ton sabit (24,6 V / 7,5 A'ya ayarlı), giriş ve yük değişince kararlı çıkış [V]\n")
    amper = (0.24, 0.6, 1.15, 2.5, 5.24, 7.5)
    sat = []
    for v in VIN_NOKTALARI:
        e = acik_cevrim_egri(p, v, tonlar[VIN_ANA], amper)
        sat.append([f"{v:g}"] + [f"{vo:.2f}" for _, vo in e])
    tablo(["Vin V \\ yük A@11V"] + [f"{a:g}" for a in amper], sat)

    print("### 4. Yük adımları, 24,6 V, Ton sabit (kontrolcü tepki vermiyor = kötümser sınır)\n")
    sat = []
    for isim, p0, p1 in (("S2E kalkışı, O1 tipik", P_HAFIF, P_HAFIF_KALKIS),
                         ("O1 tipik→zarf→tipik, S2E çalışıyor", P_HAFIF, P_ZARF),
                         ("S2E kalkışı, O1 zarf", P_ZARF, P_ZARF_KALKIS),
                         ("O1 zarf→boşta→zarf, S2E çalışıyor", P_ZARF, P_BOSTA)):
        a = yuk_adimi(p, VIN_ANA, p0, p1)
        sat.append([isim, f"{p0:.1f}→{p1:.1f}", f"{a['vmin']:.2f}", f"{a['vmax']:.2f}", f"{a['v1son']:.2f}",
                    f"{a['v1pp'] * 1e3:.0f}", f"{a['v0son']:.2f}", f"{a['v0pp'] * 1e3:.0f}", f"{a['ilmax']:.1f}"])
    tablo(["Adım", "P W", "Vmin V", "Vmax V", "ara kararlı V", "ara salınım mV", "son kararlı V",
           "son salınım mV", "IL tepe A"], sat)

    print("### 5. Yük atma, ideal kontrolcü sınırı (yük düştüğü anda duty = 0; en iyi durum)\n")
    sat = []
    for v in VIN_NOKTALARI:
        sat.append([f"{v:g}", f"{yuk_atma_sinir(p, v, P_ZARF_KALKIS, P_BOSTA)['vmax']:.3f}",
                    f"{yuk_atma_sinir(p, v, 82.5, P_S2E_CALISMA)['vmax']:.3f}"])
    tablo(["Vin V", "73→6,6 W Vtepe V", "82,5→2,6 W Vtepe V"], sat)

    print("### 6. Soğuk kalkış\n")
    sat = []
    for v in VIN_NOKTALARI:
        c = kalkis_sert(p, v, 7.5, tonlar[v])
        y = kalkis_yumusak(p, v, 7.5, tonlar[v])
        sat.append([f"{v:g}", "7,5 A direnç", f"{c['ipk']:.1f}", f"{c['vpk']:.2f}", f"{y['ipk']:.1f}", f"{y['vpk']:.2f}"])
    for isim, pw, vmin in (("O1 tipik + S2E (12,6 W)", P_HAFIF, 5.0),):
        t = ton_ayarla(p, VIN_ANA, pw / VO)
        yk = yuk_guc(f"0 {pw}", vmin)
        c = kalkis_sert(p, VIN_ANA, 0, t, yk)
        y = kalkis_yumusak(p, VIN_ANA, 0, t, yuk=yk)
        sat.append([f"{VIN_ANA:g}", isim, f"{c['ipk']:.1f}", f"{c['vpk']:.2f}", f"{y['ipk']:.1f}", f"{y['vpk']:.2f}"])
    tablo(["Vin V", "Yük", "sert: IL tepe A", "sert: Vo tepe V", "5 ms duty rampası: IL tepe A",
           "5 ms duty rampası: Vo tepe V"], sat)

    print("### 7. Giriş değişimi, Ton sabit, O1 zarf + S2E (57,6 W)\n")
    sat = []
    for v0, v1 in ((24.6, 20.0), (24.6, 26.0), (22.2, 25.2)):
        g = giris_adimi(p, v0, v1, P_ZARF)
        sat.append([f"{v0:g}→{v1:g}→{v0:g}", f"{g['vmin']:.2f}", f"{g['vmax']:.2f}", f"{g['v1son']:.2f}"])
    tablo(["Vin V (1 ms rampa)", "Vmin V", "Vmax V", "ara kararlı V"], sat)

    print("### 8. Tolerans köşeleri (L ±%20, Cout ±%20, ESR ±%20), 7,5 A\n")
    sat = []
    for isim, kl, kc, ke, v in (("anma", 1, 1, 1, VIN_ANA), ("ripple en kötü: L−, C−, ESR+", 0.8, 0.8, 1.2, 26.0),
                                ("Z0 en yüksek: L+, C−, ESR−", 1.2, 0.8, 0.8, VIN_ANA),
                                ("Z0 en düşük: L−, C+, ESR−", 0.8, 1.2, 0.8, 26.0)):
        q = dict(p, L=p["L"] * kl, Cout=p["Cout"] * kc, ESRo=p["ESRo"] * ke)
        k = kararli(q, v, 7.5)
        z = yuk_adimi(q, v, P_ZARF, P_ZARF_KALKIS)
        at = yuk_atma_sinir(q, v, P_ZARF_KALKIS, P_BOSTA)
        c = kalkis_sert(q, v, 7.5, k["ton"])
        y = kalkis_yumusak(q, v, 7.5, k["ton"])
        sat.append([isim, f"{v:g}", f"{k['vpp'] * 1e3:.1f}", f"{k['ilmax']:.2f}", f"{z['vmin']:.2f}/{z['vmax']:.2f}",
                    f"{z['v1pp'] * 1e3:.0f}", f"{at['vmax']:.2f}", f"{c['ipk']:.1f}/{c['vpk']:.1f}",
                    f"{y['ipk']:.1f}/{y['vpk']:.2f}"])
    tablo(["Köşe", "Vin V", "ΔVo mV", "IL tepe A", "zarf adım Vmin/Vmax", "73 W salınım mV", "yük atma sınırı V",
           "sert kalkış A/V", "rampalı kalkış A/V"], sat)

    print("### 9. Giriş tarafı, batarya+kablo modeli (VARSAYIM 40 mΩ + 1 µH/10 mΩ), 7,5 A\n")
    sat = []
    for v in (20.0, VIN_ANA, 26.0):
        k = kararli(p, v, 7.5, kaynak="bat")
        sat.append([f"{v:g}", f"{k['vo']:.3f}", f"{k['vinpp'] * 1e3:.0f}", f"{k['icirms']:.2f}",
                    f"{k['icirms'] ** 2 * p['ESRi'] / 2:.2f}"])
    tablo(["Batarya V", "Vo V", "ΔVin mV t-t", "Cin toplam rms A", "Cin ESR kaybı W"], sat)
    n = netlist(p, vin="PWL(0 0 1u 26)", surucu="Vdrv pwm 0 0", yuk=yuk_r(7.5), tstop=3e-3, kaynak="bat",
                meas=["VINPK MAX V(vin)", "IBATPK MAX -I(V1)"])
    h = kos(n, "tak")
    print(f"Batarya 26 V sıcak takma (anahtar kapalı): V(vin) tepe {h['vinpk']:.1f} V, batarya akımı tepe {h['ibatpk']:.0f} A\n")


# ---------------------------------------------------------------- grafik (bagimsiz SVG)
RENK = ("#1f6fb4", "#d1492e", "#2a9d5c", "#8a5bbf")


def svg_ciz(yol: Path, baslik: str, paneller: list[dict]) -> None:
    """paneller: {ylabel, seriler:[(ad, t[], y[])], cizgiler:[(y, etiket)]} ; t saniye."""
    W, PH, SOL, SAG, UST = 900, 230, 70, 20, 44
    H = UST + PH * len(paneller) + 34
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="Segoe UI,Arial,sans-serif" font-size="12">',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
         f'<text x="{SOL}" y="24" font-size="15" font-weight="600" fill="#222">{baslik}</text>']
    tmax = max(max(t) for pn in paneller for _, t, _ in pn["seriler"])
    for i, pn in enumerate(paneller):
        y0 = UST + i * PH
        ph = PH - 34
        ys = [v for _, _, y in pn["seriler"] for v in y] + [c[0] for c in pn.get("cizgiler", [])]
        lo, hi = min(ys), max(ys)
        pay = (hi - lo) * 0.06 or 1
        lo, hi = lo - pay, hi + pay
        X = lambda t: SOL + (W - SOL - SAG) * t / tmax
        Y = lambda v: y0 + ph - ph * (v - lo) / (hi - lo)
        o.append(f'<rect x="{SOL}" y="{y0}" width="{W - SOL - SAG}" height="{ph}" fill="#fafafa" stroke="#bbb"/>')
        adim = 10 ** math.floor(math.log10((hi - lo) / 4))
        adim *= min((1, 2, 5, 10), key=lambda m: abs((hi - lo) / (adim * m) - 5))
        g = math.ceil(lo / adim) * adim
        while g <= hi:
            o.append(f'<line x1="{SOL}" x2="{W - SAG}" y1="{Y(g):.1f}" y2="{Y(g):.1f}" stroke="#e3e3e3"/>'
                     f'<text x="{SOL - 6}" y="{Y(g) + 4:.1f}" text-anchor="end" fill="#444">{g:g}</text>')
            g += adim
        for k in range(7):
            t = tmax * k / 6
            o.append(f'<text x="{X(t):.1f}" y="{y0 + ph + 15}" text-anchor="middle" fill="#444">{t * 1e3:.3g}</text>')
        o.append(f'<text transform="translate(16,{y0 + ph / 2:.0f}) rotate(-90)" text-anchor="middle" fill="#222">{pn["ylabel"]}</text>')
        for cy, et in pn.get("cizgiler", []):
            o.append(f'<line x1="{SOL}" x2="{W - SAG}" y1="{Y(cy):.1f}" y2="{Y(cy):.1f}" stroke="#b00" stroke-dasharray="6 4"/>'
                     f'<text x="{W - SAG - 4}" y="{Y(cy) - 4:.1f}" text-anchor="end" fill="#b00">{et}</text>')
        for j, (ad, t, y) in enumerate(pn["seriler"]):
            # piksel basina min/max zarfi: anahtarlama dalgaciligi kaybolmaz
            nb = W - SOL - SAG
            kova = {}
            for tt, v in zip(t, y):
                b = min(int(nb * tt / tmax), nb - 1)
                a = kova.get(b)
                kova[b] = (v, v) if a is None else (min(a[0], v), max(a[1], v))
            ust = [(SOL + b + 0.5, Y(kova[b][1])) for b in sorted(kova)]
            alt = [(SOL + b + 0.5, Y(kova[b][0])) for b in sorted(kova, reverse=True)]
            pts = " ".join(f"{x:.1f},{yy:.1f}" for x, yy in ust + alt)
            o.append(f'<polygon points="{pts}" fill="{RENK[j]}" fill-opacity="0.55" stroke="{RENK[j]}" stroke-width="1"/>')
            o.append(f'<rect x="{SOL + 10 + 250 * j}" y="{y0 + 8}" width="14" height="4" fill="{RENK[j]}"/>'
                     f'<text x="{SOL + 30 + 250 * j}" y="{y0 + 14}" fill="#222">{ad}</text>')
    o.append(f'<text x="{(SOL + W - SAG) / 2}" y="{H - 8}" text-anchor="middle" fill="#222">zaman (ms) — LTspice, ideal elemanlar; fiziksel ölçüm değildir</text>')
    o.append("</svg>")
    yol.parent.mkdir(exist_ok=True)
    yol.write_text("\n".join(o), encoding="utf-8")
    print(yol)


def grafik() -> None:
    g = BURADA / "grafik"
    p = SECILEN
    ton = kararli(p, VIN_ANA, 7.5)["ton"]
    _, s = kalkis_sert(p, VIN_ANA, 7.5, ton, raw=True)
    _, y = kalkis_yumusak(p, VIN_ANA, 7.5, ton, raw=True)
    svg_ciz(g / "kalkis.svg", "Soğuk kalkış, 24,6 V, 7,5 A direnç yük (seçilen değerler)", [
        dict(ylabel="V(out) [V]", cizgiler=[(12.0, "O1 çalışma üst sınırı 12 V")],
             seriler=[("sert kalkış (sabit Ton)", s["time"], s["V(out)"]), ("5 ms duty rampası", y["time"], y["V(out)"])]),
        dict(ylabel="I(L1) [A]", seriler=[("sert kalkış", s["time"], s["I(L1)"]), ("5 ms duty rampası", y["time"], y["I(L1)"])])])
    _, a = yuk_adimi(MEVCUT, VIN_ANA, P_ZARF, P_ZARF_KALKIS, raw=True)
    _, b = yuk_adimi(p, VIN_ANA, P_ZARF, P_ZARF_KALKIS, raw=True)
    svg_ciz(g / "yuk_adimi.svg", "S2E kalkış darbesi, O1 5 A zarfında (57,6→73→57,6 W sabit güç), 24,6 V, Ton sabit", [
        dict(ylabel="V(out) [V]", cizgiler=[(12.0, "12 V")],
             seriler=[("Cout 330 µF / 15 mΩ (eski)", a["time"], a["V(out)"]), ("Cout 680 µF / 25 mΩ (seçilen)", b["time"], b["V(out)"])]),
        dict(ylabel="I(L1) [A]", seriler=[("330 µF", a["time"], a["I(L1)"]), ("680 µF", b["time"], b["I(L1)"])])])
    n = netlist(p, vin=VIN_ANA, surucu=surucu_ton(p, ton), yuk=yuk_r(7.5), tstop=12.05e-3, tstart=12e-3,
                ic=f"V(out)={VO} I(L1)=7.5", meas=["VO AVG V(out)"])
    _, k = kos(n, "dalga", raw=True)
    t0 = k["time"][0]
    tt = [t - t0 for t in k["time"]]
    svg_ciz(g / "kararli.svg", "Kararlı durum, 24,6 V → 11 V / 7,5 A, 5 anahtarlama periyodu (seçilen değerler)", [
        dict(ylabel="V(out) [V]", seriler=[("V(out)", tt, k["V(out)"])]),
        dict(ylabel="I(L1) [A]", seriler=[("I(L1)", tt, k["I(L1)"])]),
        dict(ylabel="V(sw) [V]", seriler=[("V(sw)", tt, k["V(sw)"])])])


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if not Path(LTSPICE).exists():
        sys.exit(f"LTspice bulunamadi: {LTSPICE} (LTSPICE ortam degiskeniyle yol verilebilir)")
    kip = sys.argv[1] if len(sys.argv) > 1 else "secilen"
    try:
        if kip == "tarama":
            tarama()
        elif kip == "secilen":
            secilen()
        elif kip == "mevcut":
            secilen(MEVCUT, "Mevcut (eski) değerler")
        elif kip == "grafik":
            grafik()
        else:
            sys.exit(__doc__)
    finally:
        if _CALISMA:
            shutil.rmtree(_CALISMA, ignore_errors=True)


if __name__ == "__main__":
    main()
