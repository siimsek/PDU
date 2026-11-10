#!/usr/bin/env python3
"""Asama 1: tek faz acik cevrim buck icin matematiksel degerler (LTspice DEGIL)."""
from __future__ import annotations
import json, math
from pathlib import Path

VO, IO, F = 11.0, 7.5, 100e3
VIN = (20.0, 22.2, 26.0)
L, CIN, COUT = 33e-6, 440e-6, 1360e-6
ESR_IN, ESR_OUT, DCR = 25e-3, 20e-3, 20e-3
RSRC, RSW, RDIO, VF = 50e-3, 30e-3, 33e-3, 0.6
L_TOL = 0.20
RIPPLE_LIMIT = 0.30
P_OUT = VO * IO

def duty_loss(vin: float, iout: float = IO) -> float:
    # Sabit duty deneyi icin tahmini baslangic ayari; geri besleme DEGiL.
    return (VO + VF + iout * DCR) / (vin - RSRC * VO*iout/(0.94*vin) - iout*RSW + VF)

def data():
    rows = []
    for vin in VIN:
        d = VO / vin
        di = (vin - VO) * d / (F*L)
        i_peak = IO + di/2
        d_loss = duty_loss(vin)
        # Basit kayip modeli: sadece karsilastirma icin, gercek komponent veya anahtarlama modeli degil.
        p_sw = IO**2 * RSW * d_loss
        p_d = (VF*IO + RDIO*IO**2) * (1-d_loss)
        p_l = IO**2 * DCR
        i_in_est = P_OUT/(0.94*vin)
        p_src = RSRC * i_in_est**2
        p_other = p_sw+p_d+p_l+p_src
        rows.append({
            "Vin_V": vin, "Duty_ideal": d, "Duty_kayipli_tahmin": d_loss,
            "I_L_dalgalanma_pp_A": di, "I_L_tepe_A": i_peak,
            "Cout_dalgalanma_yaklasik_mV": 1e3*(di/(8*F*COUT)+di*ESR_OUT),
            "Cin_Irms_A_ideal": IO*math.sqrt(d*(1-d)),
            "iletim_ve_bakir_kayiplari_yaklasik_W": p_other,
            "anahtarlama_haric_verim_yaklasik_pct": 100*P_OUT/(P_OUT+p_other),
        })
    worst_di = VO*(1-VO/VIN[-1])/(L*F)
    di_tol = worst_di/(1-L_TOL)
    return {
        "sinif": "HESAP / VARSAYIM; ne LTspice sonucu ne fiziksel olcum",
        "topoloji": "tek faz asenkron acik cevrim",
        "parametreler": {
            "Vin_V": list(VIN), "Vo_hedef_V": VO, "Iout_tasarim_A": IO,
            "Pout_hedef_W": P_OUT, "f_Hz": F,
            "L_uH": L*1e6, "Cin_uF": CIN*1e6, "Cout_uF": COUT*1e6,
            "Rsrc_mOhm": RSRC*1e3, "Rsw_mOhm": RSW*1e3,
            "Rdiode_mOhm": RDIO*1e3, "Vf_diode_V": VF,
            "DCR_mOhm": DCR*1e3,
            "ESRin_mOhm": ESR_IN*1e3, "ESRout_mOhm": ESR_OUT*1e3,
        },
        "L_min_uH_yuzde30": VO*(1-VO/VIN[-1])/(RIPPLE_LIMIT*IO*F)*1e6,
        "L_tolerans_eksi20_dalgalanma_A": di_tol,
        "L_tolerans_eksi20_Ipk_A": IO+di_tol/2,
        "Isat_sadece_kararli_min_A_30pct_marj": (IO+di_tol/2)*1.3,
        "not": "Kalkis akimi kararlidan fazla olabilir; Isat buna gore kontrol edilir. Gercek yuk baglanmaz.",
        "sonuclar": rows,
    }
if __name__=="__main__":
    p=Path(__file__).with_name("hesap-sonuc.json")
    p.write_text(json.dumps(data(),indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(p)
