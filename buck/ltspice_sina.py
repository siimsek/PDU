#!/usr/bin/env python3
"""Açık çevrim LTspice .asc şematiklerini Windows LTspice'ta batch çalıştırır.
Kaynak şematiği değiştirmez. Çıktı: buck/ltspice-sonuc.json.
Gerçek LTspice çalıştırması olmadan PASS iddiası yapılmaz.
"""
from __future__ import annotations
import json, os, re, subprocess, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
LTSPICE=os.environ.get("PDU_LTSPICE",r"C:\Program Files\ADI\LTspice\LTspice.exe")
RESULT=["VAVG","VMAX","VMIN","VSTARTPK","ILMAX","ILMIN","ISTARTPK","PIN","POUT"]
def run_case(mode: str, vin: float, iout: float=7.5, fixed_duty: float|None=None):
    source=(ROOT/f"buck-{mode}.asc").read_text(encoding="utf-8")
    source=source.replace(".param Vin=22.2 Vout=11 Iout=7.5 Fsw=100k",
        f".param Vin={vin:g} Vout=11 Iout={iout:g} Fsw=100k")
    if fixed_duty is not None:
        source=re.sub(r"\.param Duty=[^\r\n]*",f".param Duty={fixed_duty:.10g}",source)
    with tempfile.TemporaryDirectory(prefix="buck1-") as folder:
        path=Path(folder)/f"{mode}.asc"
        path.write_text(source,encoding="utf-8",newline="\n")
        proc=subprocess.run([LTSPICE,"-b",str(path)],capture_output=True,timeout=180,check=False)
        logpath=path.with_suffix(".log")
        if not logpath.exists():
            raise RuntimeError(f"LTspice günlük oluşturmadı: {mode}, {vin}; kod={proc.returncode}; {proc.stderr[:400]!r}")
        raw=logpath.read_bytes()
        log=raw.decode("utf-16") if b"\x00" in raw[:200] else raw.decode("utf-8","replace")
        values={}
        for name in RESULT:
            mat=re.search(rf"^{name.lower()}:.*?=\s*([-+\d.eE]+)",log,re.M|re.I)
            if not mat: raise RuntimeError(f"{mode}, Vin={vin}: {name} ölçümü yok; günlük: {log[-1500:]}")
            values[name]=float(mat.group(1))
        values["ripple_mV"]=(values["VMAX"]-values["VMIN"])*1e3
        values["delta_IL_A"]=values["ILMAX"]-values["ILMIN"]
        values["verim_anahtarlama_kaybi_haric_pct"]=100*values["POUT"]/values["PIN"] if values["PIN"]>0 else None
        return values

def main():
    if not Path(LTSPICE).is_file():
        raise SystemExit(f"LTspice bulunamadı: {LTSPICE}. PDU_LTSPICE ortam değişkenini ayarla.")
    cases=[]
    for mode in ("ideal","kayipli"):
        for vin in (20,22.2,26):
            cases.append((mode,vin,7.5,None))
    for vin in (20,26):
        cases.append(("kayipli",vin,7.5,11/22.2))
    cases.append(("kayipli",26,0.75,11/22.2))
    rows=[]
    for mode,vin,io,duty in cases:
        print(f"Running {mode} Vin={vin} Iout={io} fixed={duty}")
        result=run_case(mode,vin,io,duty)
        rows.append({"mode":mode,"Vin_V":vin,"Iout_setting_A":io,"fixed_duty":duty,"measurements":result})
    path=ROOT/"ltspice-sonuc.json"
    path.write_text(json.dumps({
        "not":"GERCEK LTspice .asc batch sonucu; davranissal switch, gercek MOSFET gate surme/anahtarlama kaybi yok; fiziksel olcum degil",
        "kaynaklar":["buck-ideal.asc","buck-kayipli.asc"],"kosular":rows
    },indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("Wrote",path)
if __name__=="__main__":
    main()
