#!/usr/bin/env python3
"""hesap.py degerlerini LTspice batch ile sinar (tek faz ve 180 derece cift faz).

Calistir: python buck/ltspice_sina.py  ->  buck/ltspice-sonuc.json
Anahtar ve diyot davranissal modeldir; anahtarlama kaybi icermez. Fiziksel olcum degildir.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

import hesap as H

LT = os.environ.get("PDU_LTSPICE", r"C:\Program Files\ADI\LTspice\LTspice.exe")
TMP = Path(tempfile.mkdtemp(prefix="buck-lt-"))
T = 1 / H.F
BAS, SON = 40e-3, 50e-3
KOUT = H.COUT_ADET * H.COUT_UF
EOUT = H.COUT_ESR_ADET / H.COUT_ADET
KIN = H.CIN_ADET * H.CIN_UF
EIN = H.CIN_ESR_ADET / H.CIN_ADET
MODEL = f""".model SWI SW(Ron={H.RDS} Roff=10Meg Vt=2.5 Vh=1)
.model DFW D(Ron=1m Roff=10Meg Vfwd={H.VF})
"""
OLC = ["AVG V(out)", "MAX V(out)", "MIN V(out)", "MAX V(in)", "MIN V(in)", "RMS I(Cin)", "AVG -V(src)*I(V1)", "AVG V(out)*I(R1)"]
AD = ["VAVG", "VMAX", "VMIN", "VINMAX", "VINMIN", "ICIN", "PIN", "POUT"]


def faz(i: int, l: float, dcr: float, duty: float, gecikme: float) -> str:
    return f"""S{i} in sw{i} ctl{i} 0 SWI
D{i} 0 sw{i} DFW
L{i} sw{i} out {l} Rser={dcr}
Vp{i} ctl{i} 0 PULSE(0 5 {gecikme} 5n 5n {duty * T - 5e-9} {T})
"""


def kos(ad: str, vin: float, fazlar: list, ek_olc: list | None = None) -> dict:
    govde = "".join(faz(i + 1, *p) for i, p in enumerate(fazlar))
    olc = OLC + (ek_olc or [])
    adlar = AD + [f"X{i}" for i in range(len(ek_olc or []))]
    mlar = "".join(f".meas tran {a} {o} FROM {BAS} TO {SON}\n" for a, o in zip(adlar, olc))
    net = f"""* {ad}
V1 src 0 {vin}
Rs src in {H.RS_KAYNAK}
Cin in 0 {KIN} Rser={EIN}
{govde}Cout out 0 {KOUT} Rser={EOUT}
R1 out 0 {H.VO / H.IO}
{MODEL}.tran 0 {SON} {BAS} 100n
{mlar}.end
"""
    yol = TMP / f"{ad}.cir"
    yol.write_text(net, encoding="utf-8", newline="\n")
    subprocess.run([LT, "-b", str(yol)], timeout=280, check=False)
    ham = yol.with_suffix(".log").read_bytes()
    log = ham.decode("utf-16") if b"\x00" in ham[:200] else ham.decode("utf-8", "replace")
    r = {}
    for a in adlar:
        m = re.search(rf"^{a.lower()}:.*?=\s*([-\d.eE+]+)", log, re.M | re.I)
        if not m:
            raise RuntimeError(f"{ad}: {a} olcumu yok\n{log[:1500]}")
        r[a] = float(m.group(1))
    return r


def ozet(r: dict) -> dict:
    return {"Vo_ort_V": r["VAVG"], "dVo_mV": (r["VMAX"] - r["VMIN"]) * 1e3, "Cin_rms_A": r["ICIN"], "dVin_mV": (r["VINMAX"] - r["VINMIN"]) * 1e3,
            "Pin_W": r["PIN"], "Pout_W": r["POUT"], "verim_anahtarlama_haric": 100 * r["POUT"] / r["PIN"]}


def main() -> None:
    sonuc = {"not": "SIM; davranissal anahtar/diyot, anahtarlama kaybi yok. Fiziksel olcum degildir.", "tek_faz": {}, "cift_faz": {}}
    t = H.topoloji("A", 1, False, H.CIN_ADET, {})
    c = H.topoloji("C", 2, False, 1, {})
    l1 = t["L_secilen_uH"] * 1e-6
    l2 = c["L_secilen_uH"] * 1e-6
    for v in H.VIN:
        d = H.duty_gercek(v, 1, H.RS_KAYNAK)
        r = kos(f"tek_{v:g}".replace(".", "p"), v, [(l1, H.DCR_TEK, d, 0)], ["MAX I(L1)", "MIN I(L1)"])
        o = ozet(r)
        o.update({"duty": d, "IL_max_A": r["X0"], "IL_min_A": r["X1"], "dI_A": r["X0"] - r["X1"]})
        sonuc["tek_faz"][f"{v:g}"] = o
    # L -%20: 26 V en kotu dalgalanma
    d = H.duty_gercek(26.0, 1, H.RS_KAYNAK)
    r = kos("tek_lmin", 26.0, [(l1 * (1 - H.L_TOL), H.DCR_TEK, d, 0)], ["MAX I(L1)", "MIN I(L1)"])
    o = ozet(r)
    o.update({"duty": d, "IL_max_A": r["X0"], "IL_min_A": r["X1"], "dI_A": r["X0"] - r["X1"]})
    sonuc["tek_faz_Lmin_26"] = o
    dcr2 = H.DCR_TEK * 2
    for v in H.VIN:
        d = H.duty_gercek(v, 2, H.RS_KAYNAK)
        r = kos(f"cift_{v:g}".replace(".", "p"), v, [(l2, dcr2, d, 0), (l2, dcr2, d, T / 2)], ["AVG I(L1)", "AVG I(L2)"])
        o = ozet(r)
        o.update({"duty": d, "I_faz1_A": r["X0"], "I_faz2_A": r["X1"]})
        sonuc["cift_faz"][f"{v:g}"] = o
    # paylasim: faz 2 duty +%1 mutlak (0.01), akim paylasim dongusu yok
    d = H.duty_gercek(22.2, 2, H.RS_KAYNAK)
    for dd in (0.005, 0.01):
        r = kos(f"cift_dengesiz_{int(dd * 1000)}", 22.2, [(l2, dcr2, d, 0), (l2, dcr2, d + dd, T / 2)], ["AVG I(L1)", "AVG I(L2)"])
        sonuc[f"cift_faz_duty_farki_{dd}"] = {"I_faz1_A": r["X0"], "I_faz2_A": r["X1"], "Vo_ort_V": r["VAVG"]}
    cikti = Path(__file__).with_name("ltspice-sonuc.json")
    cikti.write_text(json.dumps(sonuc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(sonuc, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
