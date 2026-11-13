#!/usr/bin/env python3
"""LTspice dogrulama kosulari: acik cevrim buck guc kati, gercek yuk senaryolari.

Ana sematige dokunmaz. Netlistleri gecici klasorde uretir, LTspice'i toplu kipte (-b)
kosar, .meas sonuclarini tablo olarak yazar. Buyuk .raw dosyalari repoya girmez.

Kullanim:
  python buck/dogrula.py tarama      # 9 aday (L x Cout) karsilastirmasi
  python buck/dogrula.py secilen     # secilen tasarim: 5 giris, yuk, kalkis, tolerans
  python buck/dogrula.py pencere     # L/Cout/ESR kabul pencerelerinin kenarlari
  python buck/dogrula.py grafik      # buck/grafik/*.svg
  python buck/dogrula.py mevcut      # ana sematigin (eski degerler) yeniden kosusu
  python buck/dogrula.py sayisal     # olcum altyapisi regresyonu: anahtar zamanlama titremesi, Ton yakinsamasi
  python buck/dogrula.py kararlilik  # sabit guc yuku (CPL): darbe suresi 1-200 ms, sonum/buyume, kose model setleri
  python buck/dogrula.py zarf        # genel modul zarfi: 0-82,5 W, CR/CC/CP yuk adimlari, yuk atma gecikmesi
  python buck/dogrula.py stres       # ideal OLMAYAN senaryolar: anahtarlama zili, sicak takma, S1 kisa devre

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
# Ana sematikteki degerler: 1. sira adaylar; kesin secim degil (PARCA-HEDEFLERI.md).
# L1 el sarim Magnetics Kool Mu 40u 0077536A7, 22 sarim (33 uH, DCR HESAP 7,81 mohm @20 C; olculunce guncellenir),
# Cout Nichicon UHE1E102MHD6TO (35 mohm = maks EMPEDANS, ESR varsayimi),
# Cin 2 x TDK B41859D7108M000 (15 mohm), S1 STP100N6F7 (5,6 mohm maks),
# D1 STPS40M60CT iki bacak paralel (~0,38 V + 8 mohm; iki veri sayfasi noktasindan YAKLASIK).
SECILEN = dict(L=33e-6, DCR=7.81e-3, Cout=1000e-6, ESRo=35e-3, Cd=470e-6, Rdal=0.22,
               Cin=1000e-6, ESRi=15e-3, Ron=5.6e-3, Vf=0.38, Rd=8e-3, f=100e3)
L_DUSUK, L_YUKSEK = 0.70, 1.20     # -%20 tolerans ve tepe akimda -%10 dusum birlikte; +%20 tolerans
ESR_MIN, ESR_MAX = 15e-3, 35e-3    # Cout 100 kHz ESR kabul penceresi (tolerans dahil)
# L: 33 uH (el sarim) veya 47 uH (satin alinan, DCR yuksek parca). 22 uH tipik yukte DCM'de kaldigi icin pencere disi.
# DCR (el sarim) kabul penceresi: 6,5-15 mohm (6,5 mohm en dusuk denenen sonum kosesi).
CIFTLER = ((33e-6, 1000e-6), (39e-6, 1000e-6), (47e-6, 1000e-6))
VO_MIN, VO_MAX = 9.0, 12.0         # S2E alt siniri, O1 ust siniri
RIPPLE_MAX = 0.165                 # V t-t; cikisin %1,5'i (S2E siniri +-%3)


# --- Kose model setleri (FZ-E). Her deger icin kaynak sinifi OPTIMIZASYON.md §8'dedir. ---
# D1 cifti (iki bacak paralel), STPS40M60C Doc ID 018813 Rev 1 Tablo 4 (diyot basina) noktalarindan dogrusal model:
#   25 C tipik, 10-20 A toplam: 0,430 / 0,470 V  -> 0,39 V + 4 mohm      (artimsal direnc ALT senaryosu)
#   125 C tipik, 10-20 A toplam: 0,325 / 0,385 V -> 0,265 V + 6 mohm
#   25 C azami, 10-20 A toplam: 0,460 / 0,505 V  -> 0,415 V + 4,5 mohm   (kayip UST senaryosu)
# 7,5 A toplamda (3,75 A/bacak) egri bu dogrulardan daha diktir; veri sayfasinda o noktanin sayisi yoktur.
# S1: RDS(on) 4,7 tipik / 5,6 azami (25 C); en dusuk deger YAYIMLANMAMIS (4,7 tipik kullanildi);
#     100 C carpani ~1,40 (egriden). Cout ESR: uretici ESR yayimlamaz; 15 ve 10 mohm SENARYODUR (olcum yok).
EN_AZ_SONUM = dict(SECILEN, DCR=6.5e-3, ESRo=ESR_MIN, Ron=4.7e-3, Vf=0.39, Rd=4e-3)       # + L x1,2, Cout x0,8 kosede
EN_AZ_SONUM_SICAK = dict(EN_AZ_SONUM, ESRo=10e-3, DCR=7.81e-3, Vf=0.265, Rd=6e-3, Ron=6.6e-3)  # ESR 10 mohm TAHMIN
EN_COK_KAYIP = dict(SECILEN, DCR=10.3e-3, Ron=7.84e-3, Vf=0.415, Rd=4.5e-3)                # 100 C bakir/RDS(on), 25 C azami VF
SOGUK = dict(SECILEN, ESRo=120e-3, ESRi=38e-3)                                              # -10 C Zmax'in tamami ESR sayilir (UST SINIR)
LF_ESIK = 0.020                    # V t-t; bunun altindaki yavas (LC) salinim "sonmus" sayilir
P_TAM = VO * 7.5                   # 82,5 W modul zarfi


def eng(x: float) -> str:
    return f"{x:.6g}"


def eng9(x: float) -> str:
    """Ton icin: 6 basamak 10 ps'ye yuvarlar (kelepceli ayarda 1,6 mA); 9 basamak kullanilir."""
    return f"{x:.9g}"


# Test netlistlerinde kullanilan ideal modeller. idealler.lib ile AYNI degerler; tek fark anahtarin
# Vh=-0.5 (yumusak gecis) olmasidir. Neden: Vh=0 (sert gecis) ile LTspice anahtarlama anini zaman
# adimina gore +-1 ns kaydirir (periyottan periyoda titreme); bu LC'yi uyarir, ripple olcumunu
# 64 -> 70 mV'a cikarir ve Vo(Ton) egrisini basamakli yapar (`dogrula.py sayisal`). Ana sematik ve
# idealler.lib degismez; sert=True ile kutuphanedeki model aynen kullanilir (regresyon icin).
MODEL_TEST = """.subckt anahtar A B CP CN params: Ron=10m
S1 A B CP CN SWM
.model SWM SW(Ron={Ron} Vt=5 Vh=-0.5)
.ends
.subckt diyot A K params: Vf=0.5 Ron=10m
D1 A K DM
.model DM D(Ron={Ron} Vfwd={Vf})
.ends"""


# ---------------------------------------------------------------- netlist
def netlist(p: dict, *, vin, surucu: str, yuk: list[str], tstop: float, meas: list[str],
            ic: str = "", kaynak: str = "ideal", tstart: float = 0.0, cikis_sabit: bool = False,
            sert: bool = False, ek: list[str] | None = None, maxstep: float | None = None) -> str:
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
        if p.get("Cd", 0) > 0:
            s += [f"Cd out d_son {eng(p['Cd'])}", f"Rd d_son 0 {eng(p['Rdal'])}"]
        s += yuk
    s += ek or []
    s.append(f'.lib "{LIB}"' if sert else MODEL_TEST)
    s.append(f".tran 0 {eng(tstop)} {eng(tstart)} {eng(maxstep or T / 200)}")
    if ic:
        s.append(f".ic {ic}")
    s += [f".meas tran {m}" for m in meas]
    s.append(".end")
    return "\n".join(s) + "\n"


def surucu_ton(p: dict, ton: float, gecikme: float = 0.0) -> str:
    return f"Vdrv pwm 0 PULSE(0 10 {eng(gecikme)} 10n 10n {eng9(ton)} {eng(1 / p['f'])})"


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


def yuk_tipli(tip: str, noktalar: list[tuple[float, float]]) -> list[str]:
    """(t, P[W] @11 V) noktalarindan yuk: 'cp' sabit guc, 'cc' sabit akim (P/11), 'cr' direnc (11^2/P)."""
    if tip == "cp":
        return yuk_guc(" ".join(f"{eng(t)} {eng(w)}" for t, w in noktalar))
    if tip == "cc":
        return ["Iyuk out 0 PWL(" + " ".join(f"{eng(t)} {eng(w / VO)}" for t, w in noktalar) + ")"]
    if tip == "cr":
        return ["Vg g 0 PWL(" + " ".join(f"{eng(t)} {eng(w / VO ** 2)}" for t, w in noktalar) + ")",
                "Byr out 0 I=V(out)*V(g)"]
    raise ValueError(tip)


# ---------------------------------------------------------------- kosu
_CALISMA = None
_MASAUSTU = None
MASAUSTU_ADI = "buck_dogrula"


def calisma() -> Path:
    global _CALISMA
    if _CALISMA is None:
        _CALISMA = Path(tempfile.mkdtemp(prefix="buck_dogrula_"))
    return _CALISMA


def ltspice_kos(cir: Path) -> None:
    """LTspice'i toplu kipte kosar.

    Windows'ta LTspice -b her baslatildiginda on plandaki pencerenin odagini alir. Bunu onlemek
    icin surec gorunmeyen ayri bir masaustunde (CreateDesktop) baslatilir; kullanicinin ekrani
    ve klavye odagi etkilenmez.
    """
    if os.name != "nt":
        subprocess.run([LTSPICE, "-b", str(cir)], check=True, timeout=900)
        return
    import ctypes
    from ctypes import wintypes as w

    class STARTUPINFOW(ctypes.Structure):
        _fields_ = [("cb", w.DWORD), ("lpReserved", w.LPWSTR), ("lpDesktop", w.LPWSTR), ("lpTitle", w.LPWSTR),
                    ("dwX", w.DWORD), ("dwY", w.DWORD), ("dwXSize", w.DWORD), ("dwYSize", w.DWORD),
                    ("dwXCountChars", w.DWORD), ("dwYCountChars", w.DWORD), ("dwFillAttribute", w.DWORD),
                    ("dwFlags", w.DWORD), ("wShowWindow", w.WORD), ("cbReserved2", w.WORD),
                    ("lpReserved2", ctypes.c_void_p), ("hStdInput", w.HANDLE), ("hStdOutput", w.HANDLE),
                    ("hStdError", w.HANDLE)]

    class PROCESS_INFORMATION(ctypes.Structure):
        _fields_ = [("hProcess", w.HANDLE), ("hThread", w.HANDLE), ("dwProcessId", w.DWORD),
                    ("dwThreadId", w.DWORD)]

    u = ctypes.WinDLL("user32", use_last_error=True)
    k = ctypes.WinDLL("kernel32", use_last_error=True)
    u.CreateDesktopW.restype = w.HANDLE
    u.CreateDesktopW.argtypes = [w.LPCWSTR, w.LPCWSTR, ctypes.c_void_p, w.DWORD, w.DWORD, ctypes.c_void_p]
    k.CreateProcessW.argtypes = [w.LPCWSTR, w.LPWSTR, ctypes.c_void_p, ctypes.c_void_p, w.BOOL, w.DWORD,
                                 ctypes.c_void_p, w.LPCWSTR, ctypes.POINTER(STARTUPINFOW),
                                 ctypes.POINTER(PROCESS_INFORMATION)]
    k.WaitForSingleObject.argtypes = [w.HANDLE, w.DWORD]
    k.GetExitCodeProcess.argtypes = [w.HANDLE, ctypes.POINTER(w.DWORD)]
    k.TerminateProcess.argtypes = [w.HANDLE, w.UINT]
    k.CloseHandle.argtypes = [w.HANDLE]

    global _MASAUSTU
    if _MASAUSTU is None:
        _MASAUSTU = u.CreateDesktopW(MASAUSTU_ADI, None, None, 0, 0x10000000, None)  # GENERIC_ALL
        if not _MASAUSTU:
            raise OSError(ctypes.get_last_error(), "CreateDesktop basarisiz")
    si = STARTUPINFOW()
    si.cb = ctypes.sizeof(si)
    si.lpDesktop = MASAUSTU_ADI
    pi = PROCESS_INFORMATION()
    komut = ctypes.create_unicode_buffer(f'"{LTSPICE}" -b "{cir}"')
    if not k.CreateProcessW(None, komut, None, None, False, 0, None, None, ctypes.byref(si), ctypes.byref(pi)):
        raise OSError(ctypes.get_last_error(), "LTspice baslatilamadi")
    try:
        if k.WaitForSingleObject(pi.hProcess, 900_000) != 0:
            k.TerminateProcess(pi.hProcess, 1)
            raise TimeoutError(f"LTspice zaman asimi: {cir}")
        kod = w.DWORD()
        k.GetExitCodeProcess(pi.hProcess, ctypes.byref(kod))
        if kod.value:
            raise RuntimeError(f"LTspice cikis kodu {kod.value}: {cir}")
    finally:
        k.CloseHandle(pi.hProcess)
        k.CloseHandle(pi.hThread)


def kos(metin: str, ad: str = "k", raw: bool = False):
    d = calisma()
    cir = d / f"{ad}.cir"
    # Ayni adli onceki kosunun ciktisi basarisiz yeni kosuya kanit olmasin.
    for uz in (".log", ".raw", ".op.raw", ".db"):
        (d / f"{ad}{uz}").unlink(missing_ok=True)
    cir.write_text(metin, encoding="ascii")
    ltspice_kos(cir)
    log = (d / f"{ad}.log").read_bytes()
    log = log.decode("utf-16-le") if log[:2] in (b"\xff\xfe",) or log[1:2] == b"\x00" else log.decode("latin1")
    m = {k.lower(): float(v) for k, v in re.findall(r"^(\w+):.*?=(-?[\d.]+(?:[eE][-+]?\d+)?)", log, re.M)}
    if not m:
        raise RuntimeError("olcum yok:\n" + log[-1500:])
    beklenen = {ad.lower() for ad in re.findall(r"^\s*\.meas(?:ure)?\s+tran\s+(\w+)", metin, re.I | re.M)}
    eksik = beklenen - m.keys()
    gecersiz = {ad for ad in beklenen & m.keys() if not math.isfinite(m[ad])}
    if eksik or gecersiz:
        raise RuntimeError(f"Eksik olcumler: {sorted(eksik)}; gecersiz olcumler: {sorted(gecersiz)}\n{log[-1500:]}")
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


def rs_esdeger(p: dict, vin: float, io: float) -> float:
    """CCM'de LC'ye seri gorunen ortalama direnc: DCR + D Ron + (1-D) Rd."""
    d = duty_ccm(p, vin, io)
    return p["DCR"] + d * p["Ron"] + (1 - d) * p["Rd"]


def dil_ccm(p: dict, vin: float, io: float) -> float:
    d = duty_ccm(p, vin, io)
    return (VO + p["Vf"] + io * (p["DCR"] + p["Rd"])) * (1 - d) / (p["L"] * p["f"])


def il_baslangic(p: dict, vin: float, io: float) -> float:
    """.ic icin bobin akimi: iletim baslangicindaki VADI degeri (ortalama degil).
    Ortalama ile baslatmak dIL/2'lik bir basamak uyarimi yaratir ve LC'yi sallar."""
    return max(io - dil_ccm(p, vin, io) / 2, 0.0)


TON_TOL_V = 1e-3      # V: Ton ayarinin cikis gerilimi cinsinden hedef dogrulugu (11 V'un %0,01'i)
_TON_ONBELLEK: dict = {}


def ton_ayarla(p: dict, vin: float, io: float) -> float:
    """Ideal regulasyon varsayimi: cikis 11 V'ta tutulurken ortalama bobin akimi = io olan Ton.

    Cikis 11 V'a kelepcelenir (LC'nin oturmasi beklenmez; DCM'de RC sabiti onlarca ms'dir) ve
    I(L1) ortalamasi olculur. Kok, iki yandan sarilmis sekant (regula falsi, Illinois) ile aranir.
    Olcut fizikseldir: akim hatasi x esdeger seri direnc <= TON_TOL_V (CCM'de 1 mV ~ 0,4 ns), ayrica
    akim hatasi <= io'nun %0,5'i (DCM). Yakinsamazsa sonuc KULLANILMAZ, hata verilir.
    """
    anahtar = (tuple(sorted(p.items())), vin, io)
    if anahtar in _TON_ONBELLEK:
        return _TON_ONBELLEK[anahtar]
    T = 1 / p["f"]
    rs = rs_esdeger(p, vin, io)
    tol = min(TON_TOL_V / rs, max(0.005 * io, 1e-3))
    tau = p["L"] / rs
    ts = max(6e-3, 5 * tau + 1e-3)
    il0 = il_baslangic(p, vin, io)

    def hata(ton: float) -> float:
        n = netlist(p, vin=vin, surucu=surucu_ton(p, ton), yuk=[], tstop=ts, cikis_sabit=True,
                    ic=f"I(L1)={eng(il0)}", meas=[f"IL AVG I(L1) FROM {eng(ts - 1e-3)} TO {eng(ts)}"])
        return kos(n, "ton")["il"] - io

    d_ccm = duty_ccm(p, vin, io)
    # DCM tahmini: io = D^2 T (vin-VO)(vin+Vf) / (2 L (VO+Vf))
    d_dcm = math.sqrt(max(io, 1e-3) * 2 * p["L"] * (VO + p["Vf"]) / (T * (vin - VO) * (vin + p["Vf"])))
    a = min(d_ccm, d_dcm) * T - 10e-9          # PULSE kenarlari (10 n) iletimi 10 ns uzatir
    ha = hata(a)
    # koku saran ikinci nokta: adim buyuterek ara
    adim = (0.002 if ha < 0 else -0.002) * T
    b, hb = a, ha
    for _ in range(8):
        b = min(max(b + adim, 0.02 * T), 0.98 * T)
        hb = hata(b)
        if hb * ha <= 0:
            break
        a, ha = b, hb
        adim *= 2
    else:
        raise RuntimeError(f"ton_ayarla: kok sarilamadi (Vin={vin} V, Io={io} A)")
    sonuc, hs = (a, ha) if abs(ha) < abs(hb) else (b, hb)
    for _ in range(25):
        if abs(hs) <= tol:
            break
        c = b - hb * (b - a) / (hb - ha)
        hc = hata(c)
        if hc * hb < 0:
            a, ha = b, hb
        else:
            ha *= 0.5                              # Illinois: ayni yanda kalan ucu hafiflet
        b, hb = c, hc
        if abs(hc) < abs(hs):
            sonuc, hs = c, hc
    if abs(hs) > tol:
        raise RuntimeError(f"ton_ayarla yakinsamadi: Vin={vin} V, Io={io} A, kalan akim hatasi "
                           f"{hs * 1e3:.1f} mA (olcut {tol * 1e3:.1f} mA)")
    _TON_ONBELLEK[anahtar] = sonuc
    return sonuc


M_KARARLI = [
    "VO AVG V(out) FROM {a} TO {b}", "VPP PP V(out) FROM {a} TO {b}",
    "VMAX MAX V(out) FROM {a} TO {b}", "VMIN MIN V(out) FROM {a} TO {b}",
    "ILMIN MIN I(L1) FROM {a} TO {b}", "ILMAX MAX I(L1) FROM {a} TO {b}",
    "ILRMS RMS I(L1) FROM {a} TO {b}", "ISRMS RMS I(Vss) FROM {a} TO {b}",
    "IDAVG AVG I(Vsd) FROM {a} TO {b}", "IDRMS RMS I(Vsd) FROM {a} TO {b}",
    "ICORMS RMS I(Cout) FROM {a} TO {b}", "ICIRMS RMS I(Cin1)+I(Cin2) FROM {a} TO {b}",
    "VINPP PP V(vin) FROM {a} TO {b}",
    "PIN AVG V(vin)*I(Vss) FROM {a} TO {b}",
]


def olcumler(sablon: list[str], a: float, b: float) -> list[str]:
    return [m.format(a=eng(a), b=eng(b)) for m in sablon]


def kararli(p: dict, vin: float, io: float, *, direnc: bool = True, kaynak: str = "ideal",
            ton: float | None = None, sert: bool = False) -> dict:
    """11 V'a ayarli Ton ile kararli durum. io: 11 V'taki yuk akimi.

    Ton yalniz ton_ayarla() ile bulunur; sonradan kosullu ince ayar YAPILMAZ (eski surum CCM'de
    cikisa bakarak Ton'u oynatiyordu, DCM'de oynatmiyordu). Olcum son 1 ms'dir (100 periyot);
    bir onceki 1 ms ile farki 'kayma' olarak verilir: oturmamis kosu boyle gorulur.
    """
    ton = ton or ton_ayarla(p, vin, io)
    yuk = yuk_r(io) if direnc else yuk_guc(f"0 {io * VO}")
    ts = 16e-3
    dalli = p.get("Cd", 0) > 0
    ek_m = (["ICDRMS RMS I(Cd) FROM {a} TO {b}", "POUT AVG V(out)*(I(L1)-I(Cout)-I(Cd)) FROM {a} TO {b}"]
            if dalli else ["POUT AVG V(out)*(I(L1)-I(Cout)) FROM {a} TO {b}"])
    n = netlist(p, vin=vin, surucu=surucu_ton(p, ton), yuk=yuk, tstop=ts, kaynak=kaynak, sert=sert,
                ic=f"V(out)={VO} I(L1)={eng(il_baslangic(p, vin, io))}",
                meas=olcumler(M_KARARLI + ek_m, ts - 1e-3, ts)
                + [f"VO2 AVG V(out) FROM {eng(ts - 2e-3)} TO {eng(ts - 1e-3)}"])
    m = kos(n, "kararli")
    m["kayma"] = m["vo"] - m["vo2"]
    if m["ilmin"] > 0.05 and (abs(m["vo"] - VO) > 5e-3 or abs(m["kayma"]) > 2e-3):
        print(f"UYARI kararli: Vin={vin} V, Io={io} A: Vo={m['vo']:.4f} V, kayma {m['kayma'] * 1e3:.1f} mV/ms "
              f"(beklenen 11 V +-5 mV, oturmus)", file=sys.stderr, flush=True)
    m["ton"] = ton
    m["kayip_s1"] = m["isrms"] ** 2 * p["Ron"]
    m["kayip_d1"] = p["Vf"] * m["idavg"] + p["Rd"] * m["idrms"] ** 2
    m["kayip_l1"] = m["ilrms"] ** 2 * p["DCR"]
    m["kayip_co"] = m["icorms"] ** 2 * p["ESRo"]
    m["kayip_dal"] = (m["icdrms"] ** 2 * p["Rdal"]) if dalli else 0.0
    m["kayip"] = m["kayip_s1"] + m["kayip_d1"] + m["kayip_l1"] + m["kayip_co"] + m["kayip_dal"]
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


def lc_periyot(p: dict) -> float:
    """LC dogal periyodu, anahtarlama periyodunun tam katina yuvarlanmis."""
    T = 1 / p["f"]
    return round(2 * math.pi * math.sqrt(p["L"] * p["Cout"]) / T) * T


def yuk_adimi(p: dict, vin: float, p0: float, p1: float, *, ton: float | None = None,
              t1: float = 4e-3, sure: float = 20e-3, kuyruk: float = 20e-3, tip: str = "cp",
              ek: list[str] | None = None, raw: bool = False):
    """Sabit Ton (acik cevrim), yuk p0 -> p1 -> p0 [W @11 V]; tip: cp / cc / cr. Darbe suresi `sure`.

    Tepe ve dip yaninda yavas (LC) salinimin ZARFI olculur: cikis 4,8 kHz RC'den gecirilir (100 kHz
    ripple ~20 kat zayiflar) ve darbenin son iki LC periyodundaki tepe-tepe degerleri (lfa, lfb)
    karsilastirilir. durum: sonmus (lfb < LF_ESIK) / sonuyor (lfb < 0,98 lfa) / surekli salinim
    (oran 0,98-1,02: cok yavas sonen, cok yavas buyuyen veya sinir cevrimine oturmus) / buyuyor
    (lfb > 1,02 lfa). 'surekli salinim' ve 'buyuyor' kabul edilmez: tepe degeri darbe suresine baglidir.
    Darbe 4 LC periyodundan kisaysa zarf degerlendirilemez (durum = 'kisa').
    """
    io = p0 / VO
    ton = ton or ton_ayarla(p, vin, io)
    t2 = t1 + sure
    tstop = t2 + kuyruk
    tw = lc_periyot(p)
    yuk = yuk_tipli(tip, [(0, p0), (t1, p0), (t1 + 20e-6, p1), (t2, p1), (t2 + 20e-6, p0)])
    son = min(2e-3, sure / 2)
    meas = [f"VMAX MAX V(out) FROM {eng(t1)} TO {eng(tstop)}",
            f"VMIN MIN V(out) FROM {eng(t1)} TO {eng(tstop)}",
            f"V1SON AVG V(out) FROM {eng(t2 - son)} TO {eng(t2)}",
            f"V1PP PP V(out) FROM {eng(t2 - son)} TO {eng(t2)}",
            f"V0SON AVG V(out) FROM {eng(tstop - 2e-3)} TO {eng(tstop)}",
            f"V0PP PP V(out) FROM {eng(tstop - 2e-3)} TO {eng(tstop)}",
            f"ILMAX MAX I(L1) FROM {eng(t1)} TO {eng(tstop)}",
            f"LF0 PP V(lf) FROM {eng(tstop - tw)} TO {eng(tstop)}"]
    zarf = sure >= 4 * tw
    if zarf:
        meas += [f"LFA PP V(lf) FROM {eng(t2 - 2 * tw)} TO {eng(t2 - tw)}",
                 f"LFB PP V(lf) FROM {eng(t2 - tw)} TO {eng(t2)}"]
    n = netlist(p, vin=vin, surucu=surucu_ton(p, ton), yuk=yuk, tstop=tstop,
                ic=f"V(out)={VO} I(L1)={eng(il_baslangic(p, vin, io))}",
                ek=["Rlf out lf 10k", "Clf lf 0 3.3n"] + (ek or []), meas=meas)
    r = kos(n, "adim", raw)
    m = r[0] if raw else r
    m["ton"] = ton
    if not zarf:
        m["lfa"] = m["lfb"] = float("nan")
        m["oran"], m["durum"] = float("nan"), "kısa"
    else:
        m["oran"] = m["lfb"] / m["lfa"] if m["lfa"] > 0 else float("nan")
        if m["lfb"] < LF_ESIK:
            m["durum"] = "sönmüş"
        elif m["oran"] < 0.98:
            m["durum"] = "sönüyor"
        elif m["oran"] <= 1.02:
            m["durum"] = "sürekli salınım"
        else:
            m["durum"] = "büyüyor"
    # Kisa darbe icin kararlilik degerlendirilemez; gecmis olmakla karistirilmaz.
    m["kararli"] = m["durum"] in ("sönmüş", "sönüyor")
    return r


def yuk_atma_sinir(p: dict, vin: float, p0: float, p1: float, gecikme: int = 0) -> dict:
    """Kontrolcu siniri: yuk p0 -> p1 dustukten `gecikme` PWM periyodu sonra duty 0 olur.

    gecikme = 0 ideal (en iyi) durumdur. Atma, bobin akiminin tepe aninda (iletim sonu) yapilir.
    Atma oncesi yuk sabit akimdir (sabit guc yuku acik cevrimde salinir ve siniri kirletir).
    vmax = 11 V + olculen artis.
    """
    io = p0 / VO
    ton = ton_ayarla(p, vin, io)
    T = 1 / p["f"]
    d = (ton + 10e-9) * p["f"]
    t1 = 3e-3 + ton + 10e-9
    tk = t1 + gecikme * T
    pwl = f"0 {io} {eng9(t1)} {io} {eng9(t1 + 1e-6)} {p1 / VO}"
    n = netlist(p, vin=vin, surucu=surucu_duty(p, f"0 {eng(d)} {eng9(tk)} {eng(d)} {eng9(tk + 1e-7)} 0"),
                yuk=[f"Iyuk out 0 PWL({pwl})"], tstop=5e-3 + gecikme * T,
                ic=f"V(out)={VO} I(L1)={eng(il_baslangic(p, vin, io))}",
                meas=[f"VTEPE MAX V(out) FROM {eng9(t1)} TO {eng(5e-3 + gecikme * T)}",
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
                ic=f"V(out)={VO} I(L1)={eng(il_baslangic(p, v0, io))}",
                meas=["VMAX MAX V(out) FROM 4m TO 36m", "VMIN MIN V(out) FROM 4m TO 36m",
                      "V1SON AVG V(out) FROM 18m TO 20m"])
    return kos(n, "giris", raw)


def acik_cevrim_egri(p: dict, vin: float, ton: float, amperler) -> list[tuple[float, float]]:
    """Sabit Ton ile yuk akimina gore kararli cikis (direnc yuk; hafif yukte DCM yukselmesi)."""
    s = []
    for a in amperler:
        r = VO / a
        ts = max(12e-3, 8 * r * (p["Cout"] + p.get("Cd", 0.0)))
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


def pencere() -> None:
    """Kabul pencerelerinin kenarlarini kosar: uc L/Cout cifti, ESR 15-35 mohm, tolerans koseleri.

    Karar: (1) butun yuk adimlarinda ve yuk atmada Vo 9-12 V, (2) 26 V kose ripple'i <= 165 mV,
    (3) S2E kalkis darbesi (57,6 -> 73 W) 200 ms surdugunde de Vo 9-12 V icinde VE yavas salinim
    sonuyor. Eski surum (3)'u yalniz 20 ms'lik darbeyle siniyordu; yavas buyuyen salinim (zaman sabiti
    ~0,2 s) 20 ms'de gorunmuyordu. 20 ms sutunu regresyon icin yazdirilir, tek basina karar degildir.
    """
    print("## Kabul penceresi doğrulaması (LTspice, 24,6 V; sönüm dalı Cd=470 µF + Rd=0,22 Ω; köşeler: L −%30/+%20, Cout ve Cd −%20)\n")
    sat = []
    for L, C in CIFTLER:
        p = dict(SECILEN, L=L, Cout=C)
        r_anma = kararli(dict(p, ESRo=ESR_MAX), VIN_ANA, 7.5)
        r_kose = kararli(dict(p, L=L * L_DUSUK, Cout=C * 0.8, Cd=p.get("Cd", 0.0) * 0.8, ESRo=ESR_MAX), 26.0, 7.5)
        a_anma = yuk_adimi(dict(p, ESRo=ESR_MIN), VIN_ANA, P_ZARF, P_ZARF_KALKIS)
        o_anma = yuk_adimi(dict(p, ESRo=ESR_MIN), VIN_ANA, P_HAFIF, P_ZARF)
        q = dict(p, L=L * L_YUKSEK, Cout=C * 0.8, Cd=p.get("Cd", 0.0) * 0.8, ESRo=ESR_MIN)
        a_kose = yuk_adimi(q, VIN_ANA, P_ZARF, P_ZARF_KALKIS)
        o_kose = yuk_adimi(q, VIN_ANA, P_HAFIF, P_ZARF)
        u_anma = yuk_adimi(dict(p, ESRo=ESR_MIN), VIN_ANA, P_ZARF, P_ZARF_KALKIS, sure=200e-3)
        u_kose = yuk_adimi(q, VIN_ANA, P_ZARF, P_ZARF_KALKIS, sure=200e-3)
        atma = yuk_atma_sinir(dict(q, ESRo=ESR_MAX), VIN_ANA, P_ZARF_KALKIS, P_BOSTA)
        hepsi = (a_anma, o_anma, a_kose, o_kose, u_anma, u_kose)
        vmin = min(x["vmin"] for x in hepsi)
        vmax = max(max(x["vmax"] for x in hepsi), atma["vmax"])
        eski = (min(x["vmin"] for x in hepsi[:4]) >= VO_MIN
                and max(max(x["vmax"] for x in hepsi[:4]), atma["vmax"]) <= VO_MAX and r_kose["vpp"] <= RIPPLE_MAX)
        gecti = (vmin >= VO_MIN and vmax <= VO_MAX and r_kose["vpp"] <= RIPPLE_MAX
                 and u_anma["kararli"] and u_kose["kararli"])
        sat.append([f"{L * 1e6:g}", f"{C * 1e6:g}", f"{r_anma['ilmax'] - r_anma['ilmin']:.2f}", f"{r_kose['ilmax']:.2f}",
                    f"{r_anma['vpp'] * 1e3:.0f} / {r_kose['vpp'] * 1e3:.0f}",
                    f"{a_anma['vmin']:.2f}–{a_anma['vmax']:.2f}", f"{o_anma['vmin']:.2f}–{o_anma['vmax']:.2f}",
                    f"{a_kose['vmin']:.2f}–{a_kose['vmax']:.2f}", f"{o_kose['vmin']:.2f}–{o_kose['vmax']:.2f}",
                    f"{u_anma['vmin']:.2f}–{u_anma['vmax']:.2f} {u_anma['durum']}",
                    f"{u_kose['vmin']:.2f}–{u_kose['vmax']:.2f} {u_kose['durum']} (×{u_kose['oran']:.3f})",
                    f"{u_kose['lfb'] * 1e3:.0f}", f"{atma['vmax']:.2f}",
                    "geçti" if eski else "kaldı", "GEÇTİ" if gecti else "KALDI"])
        print(sat[-1], file=sys.stderr, flush=True)
    tablo(["L µH", "Cout µF", "ΔIL A", "IL tepe köşe A", "ΔVo ESR 35 mΩ: anma / köşe mV",
           "S2E kalkışı @zarf, 20 ms V", "O1 tipik→zarf V", "köşe: S2E kalkışı @zarf, 20 ms V", "köşe: O1 tipik→zarf V",
           "anma: 73 W 200 ms V, sönüm", "köşe: 73 W 200 ms V, sönüm (LC periyodu başına oran)",
           "köşe: 200 ms sonunda yavaş salınım mV t-t", "köşe yük atma sınırı V",
           "eski karar (yalnız 20 ms)", f"KARAR: {VO_MIN:g}–{VO_MAX:g} V, ≤{RIPPLE_MAX * 1e3:.0f} mV, 200 ms'de sönümlü"], sat)


# ---------------------------------------------------------------- FZ-C: olcum altyapisi regresyonu
def sayisal() -> None:
    """Sert (Vh=0, idealler.lib) ve yumusak (Vh=-0.5, test modeli) anahtarla ayni olcumler yan yana."""
    import statistics
    p = SECILEN
    print("## Ölçüm altyapısı regresyonu (LTspice; 24,6 V, 7,5 A direnç yük)\n")
    print("### 1. Anahtar iletim süresinin periyottan periyoda titremesi ve Vo(Ton) doğrusallığı\n")
    sat = []
    for ad, sert in (("idealler.lib (Vh=0, sert geçiş)", True), ("test modeli (Vh=−0,5, yumuşak geçiş)", False)):
        n = netlist(p, vin=VIN_ANA, surucu=surucu_ton(p, 4.589e-6), yuk=yuk_r(7.5), tstop=16e-3, tstart=15e-3,
                    ic=f"V(out)={VO} I(L1)=7.5", sert=sert, meas=["VPP PP V(out) FROM 15m TO 16m"])
        m, w = kos(n, "jit", raw=True)
        t, sw = w["time"], w["V(sw)"]
        ons, son = [], None
        for i in range(1, len(t)):
            a, b = sw[i - 1], sw[i]
            if (a - VIN_ANA / 2) * (b - VIN_ANA / 2) < 0:
                tc = t[i - 1] + (VIN_ANA / 2 - a) / (b - a) * (t[i] - t[i - 1])
                if b > a:
                    son = tc
                elif son is not None:
                    ons.append(tc - son)
                    son = None
        xs, ys, pp = [], [], []
        for k in range(0, 21, 2):
            ton = 4.580e-6 + k * 1e-9
            n = netlist(p, vin=VIN_ANA, surucu=surucu_ton(p, ton), yuk=yuk_r(7.5), tstop=16e-3, sert=sert,
                        ic=f"V(out)={VO} I(L1)=7.5",
                        meas=["VO AVG V(out) FROM 15m TO 16m", "VPP PP V(out) FROM 15m TO 16m"])
            r = kos(n, "tar")
            xs.append(ton * 1e9), ys.append(r["vo"]), pp.append(r["vpp"] * 1e3)
        mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
        egim = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
        kal = max(abs(y - (my + egim * (x - mx))) for x, y in zip(xs, ys)) * 1e3
        sat.append([ad, f"{statistics.mean(ons) * 1e9:.3f}", f"{(max(ons) - min(ons)) * 1e9:.3f}",
                    f"{statistics.pstdev(ons) * 1e12:.0f}", f"{m['vpp'] * 1e3:.1f}", f"{egim * 1e3:.3f}",
                    f"{kal:.2f}", f"{min(pp):.1f}–{max(pp):.1f}"])
    tablo(["Anahtar modeli", "iletim süresi ort. ns (Ton 4589 ns)", "titreme t-t ns", "titreme std ps",
           "ΔVo mV t-t", "dVo/dTon mV/ns (beklenen Vin/T = 2,46)", "doğrudan sapma maks mV (Ton 4580–4600 ns)",
           "ΔVo aralığı mV (aynı tarama)"], sat)
    print("### 2. Beş girişte ripple: HESAP (ESR || Rd || Rload) ve iki anahtar modeli\n")
    import hesap
    sat = []
    for v in VIN_NOKTALARI:
        ton = ton_ayarla(p, v, 7.5)
        y = kararli(p, v, 7.5, ton=ton)
        x = kararli(p, v, 7.5, ton=ton, sert=True)
        h = hesap.nokta(v)
        sat.append([f"{v:g}", f"{ton * 1e6:.4f}", f"{h['dvout'] * 1e3:.1f}", f"{y['vpp'] * 1e3:.1f}", f"{y['vo']:.4f}",
                    f"{x['vpp'] * 1e3:.1f}", f"{x['vo']:.4f}"])
    tablo(["Vin V", "Ton µs", "HESAP ΔVo mV", "yumuşak: ΔVo mV", "yumuşak: Vo V", "sert: ΔVo mV", "sert: Vo V"], sat)
    print("### 3. Ton ayarının yakınsaması (kelepçeli çıkış; ölçüt 1 mV eşdeğeri veya io'nun %0,5'i)\n")
    sat = []
    for v in VIN_NOKTALARI:
        h = []
        for io in (0.24, 0.6, 1.15, 2.5, 7.5):
            h.append(f"{ton_ayarla(p, v, io) * 1e6:.4f}")
        sat.append([f"{v:g}"] + h)
    tablo(["Vin V \\ yük A", "0,24", "0,6", "1,15", "2,5", "7,5"], sat)
    print("Yakınsamayan nokta olsaydı koşu hata ile dururdu (ton_ayarla sonucu sessizce kullanmaz).\n")


# ---------------------------------------------------------------- FZ-D/E: CPL kararliligi
def kose_seti(p: dict, kl: float = L_YUKSEK, kc: float = 0.8) -> dict:
    return dict(p, L=p["L"] * kl, Cout=p["Cout"] * kc, Cd=p.get("Cd", 0.0) * kc)


CPL_SETLERI = (
    ("anma (şematik)", SECILEN),
    ("pencere köşesi: L+%20, C−%20, ESR 15 mΩ", kose_seti(dict(SECILEN, ESRo=ESR_MIN))),
    ("el sarım: L+%8, C−%20, ESR 15 mΩ", kose_seti(dict(SECILEN, ESRo=ESR_MIN), 1.08)),
    ("en az sönüm: köşe + DCR 6,5, Ron 4,7, Rd 4 mΩ", kose_seti(EN_AZ_SONUM)),
    ("en az sönüm sıcak: köşe + ESR 10 mΩ (TAHMİN), Rd 6 mΩ", kose_seti(EN_AZ_SONUM_SICAK)),
    ("anma L/C, ESR 15 mΩ, Rd 4 mΩ", dict(SECILEN, ESRo=ESR_MIN, Ron=4.7e-3, Vf=0.39, Rd=4e-3)),
    ("anma L/C, ESR 10 mΩ (TAHMİN), Rd 4 mΩ", dict(SECILEN, ESRo=10e-3, Ron=4.7e-3, Vf=0.39, Rd=4e-3)),
    ("en çok kayıp (sıcak bakır/RDS, VF azami)", EN_COK_KAYIP),
    ("soğuk: ESR 120 mΩ (Zmax −10 °C, üst sınır)", SOGUK),
)


def cpl_hesap(p: dict, vin: float, p0: float, p1: float) -> dict:
    """hesap.cpl() ile ayni model (Cd + Rd sonum dali dahil): duty p0'da 11 V'a ayarli, yuk p1."""
    import hesap
    io = p0 / VO
    d = duty_ccm(p, vin, io)
    rs = p["DCR"] + d * p["Ron"] + (1 - d) * p["Rd"]
    return hesap.cpl(p["L"], p["Cout"], p["ESRo"], rs, d * vin - (1 - d) * p["Vf"], p1,
                     p.get("Cd", 0.0), p.get("Rdal", 1.0))


def darbe_karari(sure: float, aralik: bool, durum: str) -> str:
    """Kisa darbe kararlilik gecisi kaniti degildir; gorulen ihlal veya buyume kalir."""
    if not aralik or durum in ("sürekli salınım", "büyüyor"):
        return "KALDI"
    if sure < 200e-3 or durum == "kısa":
        return "BELİRSİZ"
    return "GEÇTİ" if durum in ("sönmüş", "sönüyor") else "BELİRSİZ"


def kararlilik(hizli: bool = False) -> None:
    print("## Sabit güç yükü (CPL) ile açık çevrim kararlılığı (LTspice + HESAP), 24,6 V, Ton sabit\n")
    print("### 1. Darbe süresinin etkisi: pencere köşesi (39,6 µH, 800 µF, ESR 15 mΩ, Cd 376 µF + Rd 0,22 Ω), 57,64 → 73 → 57,64 W\n")
    q = kose_seti(dict(SECILEN, ESRo=ESR_MIN))
    h = cpl_hesap(q, VIN_ANA, P_ZARF, P_ZARF_KALKIS)
    sat = []
    for sure in (1e-3, 5e-3, 20e-3, 50e-3, 200e-3) + (() if hizli else (500e-3,)):
        a = yuk_adimi(q, VIN_ANA, P_ZARF, P_ZARF_KALKIS, sure=sure)
        aralik = VO_MIN <= a["vmin"] and a["vmax"] <= VO_MAX
        sat.append([f"{sure * 1e3:g}", f"{a['vmin']:.2f}", f"{a['vmax']:.2f}", f"{a['v1pp'] * 1e3:.0f}",
                    "—" if math.isnan(a["oran"]) else f"{a['lfa'] * 1e3:.0f} → {a['lfb'] * 1e3:.0f}",
                    "—" if math.isnan(a["oran"]) else f"{a['oran']:.3f}", a["durum"],
                    "içinde" if aralik else "DIŞINDA",
                    darbe_karari(sure, aralik, a["durum"])])
        print(sat[-1], file=sys.stderr, flush=True)
    tablo(["Darbe ms", "Vmin V", "Vmax V", "darbe sonu t-t mV", "yavaş salınım, son iki LC periyodu mV",
           "oran", "sönüm", f"{VO_MIN:g}–{VO_MAX:g} V", "karar"], sat)
    print(f"HESAP (aynı köşe, 73 W): denge {h['vo']:.3f} V, Pkritik {h['pkritik']:.1f} W, sönüm {h['sonum']:+.1f} 1/s"
          f" → LC periyodu başına oran {math.exp(-h['sonum'] * lc_periyot(q)):.3f}, zaman sabiti {1e3 / abs(h['sonum']):.0f} ms\n")

    print("### 2. Model setleri × yük: 200 ms darbe (şematik Cd=470 µF + Rd=0,22 Ω; C−%20 setlerinde Cd=376 µF); HESAP ile SİM yan yana\n")
    sat = []
    yukler = ((P_ZARF, P_ZARF_KALKIS), (P_TAM / 2, P_TAM), (P_TAM / 4, 0.75 * P_TAM))
    for ad, ps in CPL_SETLERI:
        for p0, p1 in yukler:
            h = cpl_hesap(ps, VIN_ANA, p0, p1)
            a = yuk_adimi(ps, VIN_ANA, p0, p1, sure=200e-3)
            bek = math.exp(-h["sonum"] * lc_periyot(ps))
            aralik = VO_MIN <= a["vmin"] and a["vmax"] <= VO_MAX
            # sonum |.| < 10 1/s ise (zaman sabiti > 100 ms) 200 ms'de sonme/buyume ayirt edilemez
            uyum = ("evet" if (h["sonum"] > 0) == a["kararli"] else
                    "evet (sınırda)" if abs(h["sonum"]) < 10 and (a["oran"] < 1) == (h["sonum"] > 0) else "HAYIR")
            sat.append([ad, f"{p0:.1f}→{p1:.1f}", f"{h['pkritik']:.0f}", f"{h['sonum']:+.0f}", f"{bek:.3f}",
                        f"{a['oran']:.3f}", a["durum"], f"{a['vmin']:.2f}", f"{a['vmax']:.2f}", f"{a['lfb'] * 1e3:.0f}",
                        uyum, "içinde" if aralik else "DIŞINDA", "GEÇTİ" if aralik and a["kararli"] else "KALDI"])
            print(sat[-1], file=sys.stderr, flush=True)
    tablo(["Model seti", "P W", "HESAP Pkritik W", "HESAP sönüm 1/s", "HESAP oran/periyot", "SİM oran/periyot",
           "SİM sönüm", "Vmin V", "Vmax V", "200 ms sonunda yavaş salınım mV", "HESAP–SİM aynı yönde",
           f"{VO_MIN:g}–{VO_MAX:g} V", "karar"], sat)
    print("oran < 1 söner, > 1 büyür. 'sönmüş' satırlarda SİM oranı gürültüdür (salınım 20 mV altında).\n")

    print("### 3. Sönüm dalı karşılaştırması ve Rd kabul aralığı (dalsız vs Cd=376 µF [−%20] + Rd_toplam 0,15–0,60 Ω), 41,25 → 82,5 W, 200 ms\n")
    import hesap
    sat = []
    for ad, ps in CPL_SETLERI[1:5]:
        for dal_ad, cd, rd in (("dalsız (eski)", 0.0, 1.0),
                               ("470 µF (−%20) + 0,15 Ω (alt kenar)", 470e-6 * 0.8, 0.15),
                               ("470 µF (−%20) + 0,22 Ω (SEÇİLEN)", 470e-6 * 0.8, 0.22),
                               ("470 µF (−%20) + 0,35 Ω (Rd + Cd ESR)", 470e-6 * 0.8, 0.35),
                               ("470 µF (−%20) + 0,60 Ω (soğuk Cd ESR)", 470e-6 * 0.8, 0.60)):
            ps_dal = dict(ps, Cd=cd, Rdal=rd)
            io = P_TAM / 2 / VO
            d = duty_ccm(ps_dal, VIN_ANA, io)
            rs = ps_dal["DCR"] + d * ps_dal["Ron"] + (1 - d) * ps_dal["Rd"]
            pk = hesap.cpl_dalli_pkritik(ps_dal["L"], ps_dal["Cout"], ps_dal["ESRo"], rs,
                                         d * VIN_ANA - (1 - d) * ps_dal["Vf"], cd, rd)
            a = yuk_adimi(ps_dal, VIN_ANA, P_TAM / 2, P_TAM, sure=200e-3)
            aralik = VO_MIN <= a["vmin"] and a["vmax"] <= VO_MAX
            sat.append([ad, dal_ad, f"{pk:.0f}", a["durum"], f"{a['vmin']:.2f}", f"{a['vmax']:.2f}",
                        f"{a['lfb'] * 1e3:.0f}", "içinde" if aralik else "DIŞINDA",
                        "GEÇTİ" if aralik and a["kararli"] else "KALDI"])
            print(sat[-1], file=sys.stderr, flush=True)
    tablo(["Model seti", "Sönüm dalı", "HESAP Pkritik W", "SİM sönüm", "Vmin V", "Vmax V",
           "200 ms sonunda yavaş salınım mV", f"{VO_MIN:g}–{VO_MAX:g} V", "karar"], sat)
    print("Rd_toplam = ayrık Rd direnci + Cd kondansatörünün ESR'si. Yalnız tabloda listelenen direnç ve model setleri sınanmıştır.\n")


# ---------------------------------------------------------------- FZ-B: genel modul zarfi
def zarf() -> None:
    p = SECILEN
    print("## Genel modül zarfı: 0–7,5 A / 82,5 W (LTspice, şematik değerleri)\n")
    print("Genel modül için gerilim toleransı, ripple ve geçici durum sınırları KULLANICI TARAFINDAN ONAYLANMADI; "
          "bu yüzden aşağıda genel GEÇTİ/KALDI kararı yoktur. 9–12 V sütunu yalnız O1/S2E uyumluluğudur.\n")
    print("### 1. Kararlı durum, Ton her noktada 11 V'a ayarlı (yük tipi kararlı noktayı değiştirmez)\n")
    sat = []
    for v in VIN_NOKTALARI:
        for ad, io in (("düşük 0,24 A", 0.24), ("%25", 1.875), ("%50", 3.75), ("%75", 5.625), ("%100", 7.5)):
            k = kararli(p, v, io)
            sat.append([f"{v:g}", ad, f"{k['ton'] * 1e6:.3f}", "DCM" if k["ilmin"] < 0.02 else "CCM", f"{k['vo']:.3f}",
                        f"{k['kayma'] * 1e3:+.1f}", f"{k['vpp'] * 1e3:.1f}", f"{k['ilmax']:.2f}", f"{k['kayip']:.2f}"])
    tablo(["Vin V", "Yük", "Ton µs", "Kip", "Vo V", "kayma mV/ms", "ΔVo mV", "IL tepe A", "iletim kaybı W"], sat)
    print("0 A (tam yüksüz): sabit Ton'da çıkış giriş gerilimine tırmanır; açık çevrimde tanımlı değildir, "
          "geri besleme (Adım 6) gerektirir. DCM satırlarında 'kayma' sıfır değilse 16 ms'de oturmamıştır "
          "(RC sabiti onlarca ms); Ton kelepçeli ayardan gelir.\n")

    print("### 2. Yük adımları, Ton sabit (açık çevrim), yük tipi CP / CC / CR\n")
    sat = []
    for v in (20.0, VIN_ANA, 26.0):
        for p0, p1 in ((P_TAM / 4, 0.75 * P_TAM), (P_TAM / 2, P_TAM)):
            for tip in ("cp", "cc", "cr"):
                a = yuk_adimi(p, v, p0, p1, tip=tip, sure=200e-3 if tip == "cp" else 50e-3)
                sat.append([f"{v:g}", tip.upper(), f"{p0:.1f}→{p1:.1f}→{p0:.1f}", f"{a['vmin']:.2f}", f"{a['vmax']:.2f}",
                            f"{a['v1son']:.2f}", f"{a['v0son']:.2f}", a["durum"], f"{a['ilmax']:.1f}",
                            "içinde" if VO_MIN <= a["vmin"] and a["vmax"] <= VO_MAX else "DIŞINDA"])
                print(sat[-1], file=sys.stderr, flush=True)
    tablo(["Vin V", "Tip", "P W (@11 V)", "Vmin V", "Vmax V", "ara kararlı V", "son kararlı V", "sönüm",
           "IL tepe A", "O1/S2E 9–12 V"], sat)

    print("### 3. Tam yük atma 82,5 → 0 W: kontrolcü gecikmesi 0–3 PWM periyodu (duty gecikme sonunda 0)\n")
    sat = []
    for ad, ps in (("anma", p), ("köşe L+%20, C−%20, ESR 35 mΩ", kose_seti(dict(p, ESRo=ESR_MAX))),
                   ("soğuk ESR 120 mΩ (üst sınır)", SOGUK)):
        for v in (VIN_ANA, 26.0):
            h = [f"{yuk_atma_sinir(ps, v, P_TAM, 0.0, g)['vmax']:.3f}" for g in (0, 1, 2, 3)]
            sat.append([ad, f"{v:g}"] + h)
    tablo(["Model", "Vin V", "0 periyot V", "1 periyot V", "2 periyot V", "3 periyot V"], sat)
    print("Yük anında kesildiğinde ilk sıçrama yaklaşık ΔI·(ESR || Rd) ile belirlenir; ardından enerji Cout ve Cd koluna aktarılır.\n")


# ---------------------------------------------------------------- FZ-H: ideal olmayan senaryolar
# S1: STB/STP100N6F7 veri sayfasi degerlerinden TURETILMIS yaklasik VDMOS (ST SPICE modeli DEGILDIR):
# RDS(on) 4,7 mohm tipik, Ciss 1980 p, Coss 970 p ve Crss 86 p @25 V, plato ~5 V @7,5 A. Rg ic direnci TAHMIN.
# D1: STPS40M60C cifti; 25 C tipik VF noktalarina (10/20/40 A toplam) ve Cj egrisine uydurulmus Schottky.
MODEL_GERCEK = """.model S1M VDMOS(Rg=2 Vto=4.5 Kp=100 Rd=2.4m Rs=0.5m Rb=3m Cgdmax=0.7n Cgdmin=0.06n Cgs=1.9n Cjo=2.6n M=0.3 Vj=0.7 Is=10p)
.model D1M D(Is=2.8u N=1.04 Rs=2.4m Cjo=7n M=0.45 Vj=0.5 Eg=0.69 Xti=2)"""


def netlist_gercek(vin: float, *, lbus: float = 20e-9, rg: float = 10.0, mlcc: float = 0.0,
                   snub: tuple[float, float] | None = None, io: float = 7.5, tstop: float = 0.6e-3) -> str:
    """Parazitikli anahtarlama hucresi (VARSAYIM degerler): elektrolitik ESL 26 nH/adet, bara lbus,
    TO-220 bacaklari (S1 drain 3,5 n, source 7,5 n ortak-kaynak; D1 2 x 3,5 n), MLCC ESL 1 n / 5 mohm.
    Kapi: sw'ye gore yuzen ideal 0/10 V kaynak + rg (surucu SECILMEDI; yalniz gecis hizi senaryosu)."""
    p = SECILEN
    T = 1 / p["f"]
    ton = (VO + 0.42 + io * 0.012) / (vin + 0.4) * T
    s = ["* dogrula.py stres", f"V1 bus 0 {vin}",
         f"Cin1 bus 0 {eng(p['Cin'])} Rser={eng(p['ESRi'])} Lser=26n",
         f"Cin2 bus 0 {eng(p['Cin'])} Rser={eng(p['ESRi'])} Lser=26n",
         f"Lbus bus hot {eng(lbus)} Rser=1m"]
    if mlcc:
        s.append(f"Cm hot 0 {eng(mlcc)} Rser=5m Lser=1n")
    s += ["Ld hot d 3.5n", "M1 d g s S1M", "Ls s sw 7.5n",
          f"Vg gd sw PULSE(0 10 0 5n 5n {eng9(ton)} {eng(T)})", f"Rg gd g {eng(rg)}",
          "Lk sw k 3.5n", "D1 a k D1M", "La 0 a 3.5n"]
    if snub:
        s += [f"Rsn sw sn {eng(snub[0])}", f"Csn sn 0 {eng(snub[1])}"]
    s += [f"L1 sw out {eng(p['L'])} Rser={eng(p['DCR'])} Rpar=10k", f"Cout out 0 {eng(p['Cout'])} Rser={eng(p['ESRo'])} Lser=15n"]
    if p.get("Cd", 0) > 0:
        s += [f"Cd out d_son {eng(p['Cd'])} Lser=15n", f"Rd d_son 0 {eng(p['Rdal'])}"]
    s += [f"Rload out 0 {eng(VO / io)}", MODEL_GERCEK,
          f".tran 0 {eng(tstop)} 0 1n", f".ic V(out)={VO} I(L1)={eng(io - 0.95)}"]
    a, b = eng(tstop - 20 * T), eng(tstop)
    s += [f".meas tran {m}" for m in (
        f"VDSPK MAX V(d,s) FROM {a} TO {b}", f"VRPK MAX V(k,a) FROM {a} TO {b}",
        f"VSWMAX MAX V(sw) FROM {a} TO {b}", f"VSWMIN MIN V(sw) FROM {a} TO {b}",
        f"VHOTPK MAX V(hot) FROM {a} TO {b}",
        f"PS1 AVG V(d,s)*Id(M1) FROM {a} TO {b}", f"PD1 AVG V(a,k)*I(D1) FROM {a} TO {b}",
        f"VO AVG V(out) FROM {a} TO {b}", f"VOPP PP V(out) FROM {a} TO {b}")]
    if snub:
        s.append(f".meas tran PSN AVG V(sw,sn)*I(Rsn) FROM {a} TO {b}")
    s.append(".end")
    return "\n".join(s) + "\n"


def stres() -> None:
    p = SECILEN
    print("## İdeal olmayan senaryolar (LTspice). Parazitik ve kaynak değerleri VARSAYIMDIR; fiziksel ölçüm yoktur\n")
    print("### 1. Anahtarlama zili: veri sayfasından türetilmiş VDMOS + Schottky, 7,5 A (ST SPICE modeli değil)\n")
    sat = []
    for ad, vin, kw in (
            ("temel: bara 20 nH, Rg 10 Ω, MLCC yok, snubber yok", 26.0, {}),
            ("bara 10 nH", 26.0, dict(lbus=10e-9)),
            ("bara 40 nH", 26.0, dict(lbus=40e-9)),
            ("Rg 4,7 Ω", 26.0, dict(rg=4.7)),
            ("Rg 22 Ω", 26.0, dict(rg=22.0)),
            ("MLCC 4,7 µF etkin", 26.0, dict(mlcc=4.7e-6)),
            ("MLCC + snubber 4,7 Ω / 1 nF", 26.0, dict(mlcc=4.7e-6, snub=(4.7, 1e-9))),
            ("MLCC + snubber 2,2 Ω / 2,2 nF", 26.0, dict(mlcc=4.7e-6, snub=(2.2, 2.2e-9))),
            ("MLCC + snubber 10 Ω / 470 pF", 26.0, dict(mlcc=4.7e-6, snub=(10.0, 470e-12))),
            ("snubber 4,7 Ω / 1 nF, MLCC yok", 26.0, dict(snub=(4.7, 1e-9))),
            ("bara 40 nH, Rg 4,7 Ω (en sert)", 26.0, dict(lbus=40e-9, rg=4.7)),
            ("temel, 28 V", 28.0, {}),
            ("bara 40 nH, Rg 4,7 Ω, 28 V", 28.0, dict(lbus=40e-9, rg=4.7)),
            ("MLCC + snubber 4,7 Ω / 1 nF, 28 V", 28.0, dict(mlcc=4.7e-6, snub=(4.7, 1e-9)))):
        m = kos(netlist_gercek(vin, **kw), "zil")
        sat.append([ad, f"{vin:g}", f"{m['vdspk']:.1f}", f"{m['vrpk']:.1f}", f"{m['vswmin']:.1f}", f"{m['vhotpk']:.1f}",
                    f"{m['ps1']:.2f}", f"{m['pd1']:.2f}", f"{m.get('psn', 0) * 1e3:.0f}", f"{m['vopp'] * 1e3:.0f}"])
        print(sat[-1], file=sys.stderr, flush=True)
    tablo(["Senaryo", "Vin V", "S1 VDS tepe V (anma 60)", "D1 ters tepe V (anma 60)", "V(sw) dip V", "hücre barası tepe V",
           "S1 toplam kayıp W", "D1 kayıp W", "snubber kaybı mW", "ΔVo mV (Cout ESL 15 nH)"], sat)
    print("Tepe değerler modele ve yerleşime bağlıdır; kart üzerinde ölçülmeden doğrulanmış sayılmaz (PROTOTİPTE ÖLÇÜLECEK).\n")

    print("### 2. Batarya sıcak takma: 26 V basamak, anahtar kapalı, yüksüz; kaynak R / L süpürmesi; tepe V(Cin)\n")
    ls = (0.2e-6, 0.5e-6, 1e-6, 2e-6, 5e-6, 10e-6)
    sat = []
    for r in (5e-3, 10e-3, 20e-3, 40e-3, 80e-3):
        h = []
        for l in ls:
            n = "\n".join(["* sicak takma", "V1 bat 0 PWL(0 0 1u 26)", f"Rk bat b1 {eng(r)}", f"Lk b1 vin {eng(l)}",
                           f"Cin1 vin 0 {eng(p['Cin'])} Rser={eng(p['ESRi'])} Lser=26n",
                           f"Cin2 vin 0 {eng(p['Cin'])} Rser={eng(p['ESRi'])} Lser=26n",
                           ".tran 0 5m 0 1u", ".meas tran VPK MAX V(vin)", ".meas tran IPK MAX I(Lk)", ".end"]) + "\n"
            m = kos(n, "tak")
            h.append(f"{m['vpk']:.1f}{'*' if m['vpk'] > 35 else ''} / {m['ipk']:.0f}")
        sat.append([f"{r * 1e3:g}"] + h)
    tablo(["R kaynak mΩ \\ L kaynak µH (V tepe / A tepe)"] + [f"{l * 1e6:g}" for l in ls], sat)
    print("* = 35 V anma gerilimi aşıldı. 6S paket iç direnci ve kablo endüktansı ölçülmedi.\n")

    print("### 3. S1 kısa devre arızası: 11 V kararlı durumdan duty = 1 (ideal elemanlar), çıkış ve bobin akımı\n")
    sat = []
    for v in (VIN_ANA, 26.0):
        for ad, yuk, io in (("7,5 A direnç", yuk_r(7.5), 7.5), ("0,24 A direnç", yuk_r(0.24), 0.24),
                            ("57,6 W sabit güç", yuk_guc(f"0 {P_ZARF}"), P_ZARF / VO)):
            d = (ton_ayarla(p, v, io) + 10e-9) * p["f"]
            n = netlist(p, vin=v, surucu=surucu_duty(p, f"0 {eng(d)} 3m {eng(d)} 3.0001m 2"), yuk=yuk, tstop=30e-3,
                        kaynak="bat", ic=f"V(out)={VO} I(L1)={eng(il_baslangic(p, v, io))}",
                        meas=["VPK MAX V(out)", "IPK MAX I(L1)", "VSON AVG V(out) FROM 29m TO 30m"])
            m = kos(n, "kisa")
            sat.append([f"{v:g}", ad, f"{m['vpk']:.1f}", f"{m['vson']:.1f}", f"{m['ipk']:.0f}",
                        "AŞILIR" if m["vpk"] > 25 else "içinde"])
    tablo(["Batarya V", "Yük", "Vo tepe V", "Vo son V", "IL tepe A", "Cout 25 V anması"], sat)
    print("Kaynak: batarya + kablo VARSAYIMI (40 mΩ + 1 µH / 10 mΩ). Bobin doğrusal alınmıştır; gerçek bobin bu akımda "
          "doyar (L/L0 ≈ %60), tepe akım daha yüksek olur.\n")


def secilen(p: dict = SECILEN, ad: str = "Secilen") -> None:
    dal_bilgi = f", Cd={p['Cd'] * 1e6:g} µF+Rd={p['Rdal']:g} Ω" if p.get("Cd", 0) > 0 else ""
    print(f"## {ad}: L={p['L'] * 1e6:g} µH/{p['DCR'] * 1e3:g} mΩ, Cout={p['Cout'] * 1e6:g} µF/{p['ESRo'] * 1e3:g} mΩ{dal_bilgi}, "
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

    print("### 4. Yük adımları, 24,6 V, Ton sabit (kontrolcü tepki vermiyor; genel en kötü durum olduğu kanıtlanmadı)\n")
    sat = []
    for isim, p0, p1 in (("S2E kalkışı, O1 tipik", P_HAFIF, P_HAFIF_KALKIS),
                         ("O1 tipik→zarf→tipik, S2E çalışıyor", P_HAFIF, P_ZARF),
                         ("S2E kalkışı, O1 zarf", P_ZARF, P_ZARF_KALKIS),
                         ("O1 zarf→boşta→zarf, S2E çalışıyor", P_ZARF, P_BOSTA)):
        a = yuk_adimi(p, VIN_ANA, p0, p1, sure=200e-3)
        sat.append([isim, f"{p0:.1f}→{p1:.1f}", f"{a['vmin']:.2f}", f"{a['vmax']:.2f}", f"{a['v1son']:.2f}",
                    f"{a['v1pp'] * 1e3:.0f}", f"{a['v0son']:.2f}", f"{a['v0pp'] * 1e3:.0f}", f"{a['ilmax']:.1f}",
                    a["durum"]])
    tablo(["Adım (200 ms)", "P W", "Vmin V", "Vmax V", "ara kararlı V", "ara salınım mV", "son kararlı V",
           "son salınım mV", "IL tepe A", "yavaş salınım"], sat)

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

    print("### 8. Tolerans köşeleri (L −%30/+%20, Cout ve Cd ±%20, ESR 15/35 mΩ), 7,5 A\n")
    sat = []
    for isim, kl, kc, esr, v in (("anma", 1, 1, p["ESRo"], VIN_ANA),
                                 ("ripple en kötü: L−, C−, ESR 35 mΩ", L_DUSUK, 0.8, ESR_MAX, 26.0),
                                 ("sönüm en zayıf: L+, C−, ESR 15 mΩ", L_YUKSEK, 0.8, ESR_MIN, VIN_ANA),
                                 ("Z0 en düşük: L−, C+, ESR 15 mΩ", L_DUSUK, 1.2, ESR_MIN, 26.0)):
        q = dict(p, L=p["L"] * kl, Cout=p["Cout"] * kc, Cd=p.get("Cd", 0.0) * kc, ESRo=esr)
        k = kararli(q, v, 7.5)
        z = yuk_adimi(q, v, P_ZARF, P_ZARF_KALKIS, sure=200e-3)
        at = yuk_atma_sinir(q, v, P_ZARF_KALKIS, P_BOSTA)
        c = kalkis_sert(q, v, 7.5, k["ton"])
        y = kalkis_yumusak(q, v, 7.5, k["ton"])
        sat.append([isim, f"{v:g}", f"{k['vpp'] * 1e3:.1f}", f"{k['ilmax']:.2f}", f"{z['vmin']:.2f}/{z['vmax']:.2f}",
                    f"{z['v1pp'] * 1e3:.0f}", z["durum"], f"{at['vmax']:.2f}", f"{c['ipk']:.1f}/{c['vpk']:.1f}",
                    f"{y['ipk']:.1f}/{y['vpk']:.2f}"])
    tablo(["Köşe", "Vin V", "ΔVo mV", "IL tepe A", "zarf adım (200 ms) Vmin/Vmax", "73 W darbe sonu t-t mV",
           "yavaş salınım", "yük atma sınırı V", "sert kalkış A/V", "rampalı kalkış A/V"], sat)

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
             seriler=[("Cout 330 µF / 15 mΩ (eski)", a["time"], a["V(out)"]), ("seçilen (1000 µF / 35 mΩ + 470 µF / 0,22 Ω)", b["time"], b["V(out)"])]),
        dict(ylabel="I(L1) [A]", seriler=[("eski", a["time"], a["I(L1)"]), ("seçilen", b["time"], b["I(L1)"])])])
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
        elif kip == "pencere":
            pencere()
        elif kip == "mevcut":
            secilen(MEVCUT, "Mevcut (eski) değerler")
        elif kip == "grafik":
            grafik()
        elif kip == "sayisal":
            sayisal()
        elif kip == "kararlilik":
            kararlilik("hizli" in sys.argv[2:])
        elif kip == "zarf":
            zarf()
        elif kip == "stres":
            stres()
        else:
            sys.exit(__doc__)
    finally:
        if _CALISMA:
            shutil.rmtree(_CALISMA, ignore_errors=True)


if __name__ == "__main__":
    main()
