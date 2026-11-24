"""Build and validate the PDU on a native host. Results are written as JSON."""
import argparse
import hashlib
from itertools import product
from dataclasses import replace
import json
import math
import os
from pathlib import Path
import platform
import shutil
import struct
import subprocess
import sys

import numpy as np

from . import spice
from .configure import (ADC_CLOCK_HZ, ADC_FRAME_S, ADC_TRIGGER_S, CURRENT_APERTURE_S,
                        EXECUTION_BUDGET_S, METHODS, UPDATE_DEADLINE_S, VOUT_APERTURE_S)
from .design import corners, evaluate, FREQUENCY, responses, sampled, loops
from .interface import Interface
from .plant import ROOT, VIN_POINTS
from .tools import ARM_LINUX
from .simulate import (
    ADC_RAIL, ADC_STUCK_LOW, BACKUP_OCP, BAD_SAMPLE, CBC, CC, CP, CR, DCM, DISABLED,
    ISOLATED, LOAD_UV_LATCH, OVP, OVERLOAD_LATCH, SHORTED_S1, STALE_ADC,
    WATCHDOG, host_library, mask, metrics, model, run,
)

METHOD = "type_iii"
LATCHES = OVP | WATCHDOG | LOAD_UV_LATCH | OVERLOAD_LATCH | BACKUP_OCP
SPICE_LIMITS = {"mean_v": .02, "ripple_v": .002, "peak_i": .05, "min_i": .05}
LTSPICE_BASELINE = {"mean_v": 11.000, "ripple_v": .0557, "peak_i": 8.44, "min_i": 6.56}


def command(*args):
    subprocess.run([str(arg) for arg in args], cwd=ROOT, check=True)


def need(condition, description):
    if not condition:
        raise RuntimeError(description)


def compare(actual, expected, tolerance):
    for key, limit in tolerance.items():
        value = actual[key]
        need(math.isfinite(value) and abs(value - expected[key]) <= limit,
             f"{key}: {value} vs {expected[key]}, allowed delta {limit}")


def windows_generator():
    installation_root = os.environ.get("ProgramFiles(x86)", os.environ.get("ProgramFiles", ""))
    vswhere = Path(installation_root) / "Microsoft Visual Studio" / "Installer" / "vswhere.exe"
    need(vswhere.is_file(), "Install Visual Studio Build Tools with Desktop development with C++")
    installed = subprocess.check_output(
        [str(vswhere), "-latest", "-products", "*", "-requires",
         "Microsoft.VisualStudio.Component.VC.Tools.x86.x64", "-property", "installationVersion"],
        text=True, timeout=20).strip()
    generators = {"17": "Visual Studio 17 2022", "18": "Visual Studio 18 2026"}
    major = installed.partition(".")[0]
    need(major in generators, f"Supported Visual Studio C++ compiler missing (found {installed!r})")
    return generators[major]


def build(destination, firmware=False, scope=False):
    cmake = shutil.which("cmake")
    need(cmake is not None, "Install the pinned Python requirements and activate the environment")
    flags = ["-DCMAKE_BUILD_TYPE=Release", f"-DPython3_EXECUTABLE={sys.executable}"]
    if firmware:
        flags.extend(("-G", "Ninja", f"-DPDU_SCOPE_PWM={'ON' if scope else 'OFF'}",
                      f"-DFETCHCONTENT_BASE_DIR={destination.parent / 'target_deps'}"))
        if not (destination / "CMakeCache.txt").exists():
            flags.append("-DCMAKE_TOOLCHAIN_FILE=firmware/arm-none-eabi.cmake")
    elif platform.system() == "Windows":
        flags.extend(("-G", windows_generator(), "-A", "x64"))
    else:
        flags.extend(("-G", "Ninja"))
    command(cmake, "-S", ROOT, "-B", destination, *flags)
    command(cmake, "--build", destination, "--config", "Release")


def firmware_metrics(directory):
    image = (directory / "firmware/pdu_g474.bin").read_bytes()
    words = struct.unpack_from("<85I", image)
    stack, reset = words[:2]
    dma, adc, timer = (words[16 + irq] for irq in (11, 18, 68))
    need(stack == 0x20018000, f"Invalid SRAM vector {stack:#x}")
    need(len(image) < 32768, f"Unexpected bench image footprint {len(image)} bytes")
    need(len({reset, dma, adc, timer}) == 4, "Reset, DMA, ADC and HRTIM need separate handlers")
    for handler in (reset, dma, adc, timer):
        need(handler & 1 and 0x08000000 < handler < 0x08000000 + len(image),
             f"Invalid Thumb vector {handler:#x}")
    return {"bytes": len(image), "arm_gcc": version("arm-none-eabi-gcc"),
            "sha256": hashlib.sha256(image).hexdigest()}


def version(executable):
    result = subprocess.run([executable, "--version"], check=True, capture_output=True, text=True,
                            errors="replace", timeout=20)
    return next((line for line in result.stdout.splitlines() if line.strip("* ")), "unknown")


def stage_results(data, stages):
    counts = [round(stage[0] / 1e-5) for stage in stages]
    need(all(count > 0 for count in counts) and len(data) == sum(counts),
         "Trace length does not match its PWM stages")
    for field in ("low_v", "high_v", "mean_v", "high_i", "rms_i", "pout", "loss"):
        need(np.isfinite(data[field]).all(), f"Non-finite waveform field {field}")
    offset = 0
    for number, (stage, count) in enumerate(zip(stages, counts)):
        chunk = data[offset:offset + count]
        offset += count
        summary = metrics(chunk, min(200, len(chunk)))
        if number:
            need(9 <= summary["min_v"] and summary["max_v"] <= 11.75,
                 f"stage {number} transient {summary}")
        else:
            need(summary["max_v"] <= 11.75, f"startup overvoltage {summary}")
        need(summary["peak_i"] <= 10.65, f"stage {number} coil peak {summary}")
        need(summary["fault_cycles"] == 0, f"stage {number} latched during regulation {summary}")
        if stage[0] >= .010:
            need(abs(summary["mean_v"] - 11) <= .11, f"stage {number} steady state {summary}")
            need(summary["ripple_v"] <= .165, f"stage {number} steady PWM ripple {summary}")
        else:
            summary["max_cycle_excursion_v"] = summary.pop("ripple_v")
        yield summary


def electrical(library, full):
    cases = {}
    for name, plant in corners().items():
        for vin in VIN_POINTS if full else (20, 26):
            for kind in (CR, CC, CP):
                label = f"{name}/{vin:g}/{kind}"
                stages = [(0.042, vin, .2, kind, 0), (.02, vin, 7.5, kind, 0),
                          (.035, vin, 0, kind, 0), (.02, vin, 2., kind, 0)]
                try:
                    cases[label] = list(stage_results(run(library, model(METHOD, plant), stages), stages))
                except RuntimeError as error:
                    cases[label] = {"failure": str(error)}
    return cases


def startups(library):
    results = {}
    for name, p in corners().items():
        for vin in (20., 26.):
            for load, amps in ((CR, 0.), (CR, 7.5), (CC, 7.5)):
                stages = [(.042, vin, amps, load, 0)]
                if amps == 0:
                    stages.append((.016, vin, 7.5, CP, 0))
                name_load = f"{name}/{vin:g}/{load}/{amps:g}"
                results[name_load] = list(stage_results(run(library, model(METHOD, p), stages), stages))
    return results


def additional(library, full, stress=False):
    results = {}
    nominal = corners()["nominal"]
    interface = Interface()
    configurations = []
    if not stress:
        configurations.extend([
            ("sense_shunt", model(METHOD, replace(nominal, dcr=nominal.dcr + interface.current_shunt_ohm))),
            ("noise", model(METHOD, jitter=120e-9, noise_v=.008, noise_i=.05)),
        ])
        for v_sign, i_sign in product((-1, 1), repeat=2):
            configurations.append((f"measurement-{v_sign:+d}-{i_sign:+d}", model(
                METHOD, vin_gain=1 + v_sign * .01, vout_gain=1 + v_sign * .004,
                vout_offset=v_sign * .008, current_gain=1 + i_sign * .015,
                current_offset=i_sign * .03, jitter=120e-9, noise_v=.008, noise_i=.05)))
    rng = np.random.default_rng(474)
    for index in range(48 if full else 8):
        base = corners()["nominal"]
        plant = replace(base, inductance=base.inductance * rng.uniform(.7, 1.2),
                        cout=base.cout * rng.uniform(.8, 1.2), cd=base.cd * rng.uniform(.8, 1.2),
                        esr=rng.uniform(.01, .12 if stress else .055), rd=rng.uniform(.15, .60),
                        dcr=rng.uniform(.0065, .015), ron=rng.uniform(.0047, .010),
                        vf=rng.uniform(.265, .415), diode_r=rng.uniform(.004, .008))
        configurations.append((f"mc-{index:02}", model(METHOD, plant, limit_i=rng.uniform(9.55, 10.05),
            limit_v=rng.uniform(11.75, 11.95), noise_v=.008, noise_i=.04, jitter=70e-9, seed=474 + index)))

    for label, config in configurations:
        stages = [(.041, 24.6, 4., CP, 0), (.012, 20, 4., CP, 0),
                  (.012, 26, 4., CP, 0), (.001, 26, 7.5, CP, 0),
                  (.012, 26, 4., CP, 0), (.200, 26, 7.5, CP, 0), (.025, 26, .6, CP, 0)]
        # Start CPL at regulation. The load's cold-start demand is evaluated separately.
        stages[0] = (.041, 24.6, 4., CR, 0)
        try:
            results[label] = list(stage_results(run(library, config, stages), stages))
        except RuntimeError as error:
            results[label] = {"failure": str(error)}
    return results



def component_endpoints(library, full):
    """Check coupled tolerance limits, not only independently named and random corners."""
    nominal = corners()["nominal"]
    combinations = (product((.7, 1.2), (.8, 1.2), (.8, 1.2), (.15, .60), (.010, .055))
                    if full else ((.7, .8, .8, .60, .055), (1.2, .8, .8, .60, .010)))
    cases = {}
    for lf, co, cd, rd, esr in combinations:
        corner = replace(nominal, inductance=nominal.inductance * lf, cout=nominal.cout * co,
                         cd=nominal.cd * cd, rd=rd, esr=esr)
        config = model(METHOD, corner, noise_v=.008, noise_i=.04, jitter=70e-9,
                       limit_i=9.55, limit_v=11.75)
        for vin in (20, 26):
            label = f"{lf:g}/{co:g}/{cd:g}/{rd:g}/{esr:g}/{vin:g}"
            stages = [(.042, vin, .2, CP, 0), (.021, vin, 7.5, CP, 0),
                      (.035, vin, 0., CP, 0), (.025, vin, 2., CP, 0)]
            try:
                result = list(stage_results(run(library, config, stages), stages))
                worst = max(row["window_pp_v"] for row in result)
                need(worst <= .165, f"2 ms window ripple {worst:.6f} V")
                cases[label] = result
            except RuntimeError as error:
                cases[label] = {"failure": str(error)}
    return cases

def protections(library):
    data = {}
    plant = corners()["low_lc"]
    start = (.042, 26., 2., CR, 0)
    skip = round(start[0] / 1e-5)
    for limit in (9.55, 10.05):
        config = model(METHOD, plant, limit_i=limit, ocp_delay=.35e-6)
        fault = run(library, config, [start, (.008, 26., 500., CR, 0)])[skip:]
        latched = np.flatnonzero(mask(fault, LOAD_UV_LATCH | OVERLOAD_LATCH))
        need(mask(fault, CBC).any() and len(latched) > 0 and latched[0] <= 220,
             "Short needs CBC and a sustained-fault latch within 2.2 ms")
        need(max(fault["high_i"]) < 11 and max(fault["ocp_latency"]) <= .65e-6,
             "Short exceeded 11 A or the behavioral OCP timing budget")
        need(not fault["duty"][-20:].any(), "Short restarted without a reset")
        data[f"short_{limit:g}"] = {"peak_i": float(max(fault["high_i"])),
                                    "latency_us": float(max(fault["ocp_latency"]) * 1e6),
                                    "latch_ms": int(latched[0]) * .01}

    for flag in (STALE_ADC, ADC_RAIL, ADC_STUCK_LOW):
        fault = run(library, model(METHOD), [start, (.01, 26., 2., CR, flag)])[skip:]
        expected = {STALE_ADC: WATCHDOG, ADC_RAIL: BAD_SAMPLE, ADC_STUCK_LOW: OVP}[flag]
        indices = np.flatnonzero(mask(fault, expected))
        need(len(indices) and not fault["duty"][-20:].any(), f"ADC fault {flag} failed to stop PWM")
        need(max(fault["high_v"]) < 12, f"ADC fault {flag} exceeded 12 V")
        data[f"adc_{flag}"] = {"stop_ms": int(indices[0]) * .01, "max_v": float(max(fault["high_v"]))}

    restart = [start, (.018, 17., 2., CR, 0), (.04, 20, 2., CR, 0),
               (.018, 20., 2., CR, DISABLED), (.04, 20., 2., CR, 0)]
    waveform = run(library, model(METHOD), restart)
    for k in (skip, skip + 1800 + 4000):
        need(not waveform["duty"][k:k + 1800].any(), "UVLO or shutdown retained PWM")
    need(abs(waveform["mean_v"][-200:].mean() - 11.) < .11, "Failed to restart from a prebiased state")

    late = run(library, model(METHOD, execute_time=1.60e-6), [start])
    need(mask(late, WATCHDOG).any() and not late["duty"].any(), "Late ADC frame escaped timing protection")

    for isolation in (1e9, 2e-6, 10e-6):
        cfg = model(METHOD, plant, isolate_delay=isolation)
        fault = run(library, cfg, [start, (.002, 26., 2., CR, SHORTED_S1)])[skip:]
        need(mask(fault, OVP).any(), "Stuck S1 did not trigger OVP")
        if isolation < 1:
            need(mask(fault, ISOLATED).any(), "OVP failed to request energy cutoff")
        data[f"stuck_s1_{isolation:g}"] = {
            "max_v": float(max(fault["high_v"])), "peak_i": float(max(fault["high_i"])),
            "ovp_delay_us": float(max(fault["ovp_latency"]) * 1e6)}

    backup_cases = {}
    for name, corner in corners().items():
        for amps, after in ((0., 0.), (2., 2.), (7.5, 7.5), (7.5, 0.)):
            for phase_us in (0., 2.5, 5., 7.5):
                label = f"{name}/{amps:g}-{after:g}/{phase_us:g}"
                cfg = model(METHOD, corner, backup_limit_i=11.5, backup_delay=.65e-6,
                            limit_v=11.95, isolate_delay=.6e-6, short_phase=phase_us * 1e-6)
                settled = (.042, 26., amps, CR, 0)
                fault = run(library, cfg, [settled, (.002, 26., after, CR, SHORTED_S1)])[skip:]
                need(mask(fault, ISOLATED).any() and mask(fault, OVP | BACKUP_OCP).any(),
                     f"Independent cutoff missed stuck S1: {label}")
                max_v = float(max(fault["high_v"]))
                peak_i = float(max(fault["high_i"]))
                need(max_v < 12 and peak_i < 12.5,
                     f"Stuck S1 backup exceeded its budget in {label}: {max_v:.5f} V, {peak_i:.4f} A")
                backup_cases[label] = {"max_v": max_v, "peak_i": peak_i,
                                       "trigger": "OCP" if mask(fault, BACKUP_OCP).any() else "OVP"}
    data["stuck_s1_backup_trip"] = backup_cases

    cold_cpl = run(library, model(METHOD), [(.055, 20., 7.5, CP, 0)])
    data["cpl_cold_start"] = metrics(cold_cpl)
    need(mask(cold_cpl, LATCHES).any() and not cold_cpl["duty"][-20:].any(),
         "CPL with an above-rated startup demand did not shut down safely")
    return data


def switch_reference(library, directory, skip_spice):
    p = corners()["nominal"]
    config = model(METHOD)
    data = run(library, config, [(.034, p.vin, .2, CR, 0), (.010, p.vin, 7.5, CR, 0)])
    tail = data[-100:]
    host = {"mean_v": float(tail["mean_v"].mean()),
            "ripple_v": float(max(tail["high_v"]) - min(tail["low_v"])),
            "peak_i": float(max(tail["high_i"])), "min_i": float(min(tail["low_i"]))}
    fine = run(library, model(METHOD, max_step=50e-9),
               [(.034, p.vin, .2, CR, 0), (.010, p.vin, 7.5, CR, 0)])
    need(np.max(np.abs(fine["mean_v"][-100:] - tail["mean_v"])) < .002,
         "Switched-model timestep regression exceeded 2 mV")
    need(mask(data[:3400], DCM).any() and not mask(data[-100:], DCM).any(),
         "The switched model missed the DCM/CCM transition")
    output = {"host": host}
    if skip_spice:
        return output
    baseline = spice.run(directory / "baseline")
    compare(baseline, LTSPICE_BASELINE, SPICE_LIMITS)
    output["ngspice"] = version(os.environ.get("NGSPICE", "ngspice"))
    output["baseline"] = baseline
    output["replay"] = spice.replay(directory / "replay", data["duty"], config.turn_on,
                                   config.turn_off, .2, 7.5, .034)
    compare(output["replay"], host, {**SPICE_LIMITS, "ripple_v": .004})
    output["cutoff"] = cutoff_reference(library, directory / "cutoff")
    output["hotplug"] = spice.hotplug(directory / "hotplug")
    peak = {k: item["peak_v"] for k, item in output["hotplug"].items()}
    # The overdamped trace approaches the source voltage from below.
    # A finite observation window and SPICE rounding must not require it to cross 26 V.
    compare({"damped_peak_v": peak["damped"]}, {"damped_peak_v": 26.}, {"damped_peak_v": .002})
    need(peak["inductive"] > 39., f"Expected cable ringing in the high-Q case, got {peak['inductive']} V")
    return output



def cutoff_reference(library, directory):
    result = {}
    for name, amps, initial_i in (("nominal", 2., 2.), ("low_lc", 7.5, 8.9), ("cold_esr", 0., 0.)):
        corner = corners()[name]
        config = model(METHOD, corner, initial_v=11., initial_i=initial_i, backup_limit_i=11.5,
                       backup_delay=.65e-6, limit_v=11.95, isolate_delay=.60e-6, max_step=25e-9)
        fault = run(library, config, [(.0003, 26., amps, CR, DISABLED | SHORTED_S1)])
        times = fault["cutoff_s"][fault["cutoff_s"] >= 0]
        need(len(times) > 0, f"C model did not cut input in {name}")
        expected = {"peak_v": float(max(fault["high_v"])), "peak_i": float(max(fault["high_i"])),
                    "cutoff_s": float(min(times))}
        actual = spice.cutoff_reference(directory / name, corner, 26., amps, initial_i)
        compare(actual, expected, {"peak_v": .005, "peak_i": .035, "cutoff_s": .10e-6})
        need(actual["peak_v"] < 12., f"ngspice reached 12 V before independent cutoff in {name}")
        result[name] = {"spice": actual, "host": expected}
    return result

def comparison(library):
    gains = json.loads((ROOT / "control/gains.json").read_text(encoding="ascii"))
    result = {}
    cases = [(.042, 24.6, .2, CR, 0), (.020, 24.6, 7.5, CP, 0), (.025, 26., 0., CR, 0)]
    for method in METHODS:
        value = run(library, model(method), cases)
        result[method] = dict(linear=evaluate(method, gains[method]),
                              switched=metrics(value[4200:]))
    return result


def plots(directory, library):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    gains = json.loads((ROOT / "control/gains.json").read_text(encoding="ascii"))
    p = corners()["nominal"]
    _, channels = responses([("nominal", p.vin, "cp", 7.5, *sampled(p, p.vin, 7.5, "cp"))], FREQUENCY)
    fig, axes = plt.subplots(2, 1, sharex=True, figsize=(8, 6), layout="constrained")
    for method in METHODS:
        voltage = loops(method, gains[method], channels[0, 0], channels[0, 1], p.vin)["voltage"]
        axes[0].semilogx(FREQUENCY, 20 * np.log10(abs(voltage)), label=method)
        axes[1].semilogx(FREQUENCY, np.unwrap(np.angle(voltage)) * (180 / np.pi))
    axes[0].axhline(0, color="0.5", linewidth=.8)
    axes[1].axhline(-180, color="0.5", linewidth=.8)
    axes[0].set(ylabel="Çevrim kazancı (dB)", title="24,6 V giriş, 82,5 W CPL, CCM")
    axes[1].set(xlabel="Frekans (Hz)", ylabel="Faz (°)")
    axes[0].legend()
    for ax in axes:
        ax.grid(alpha=.25, which="both")
    fig.savefig(directory / "bode.svg")
    plt.close(fig)

    fig, axes = plt.subplots(2, 1, sharex=True, figsize=(8, 6), layout="constrained")
    for method in METHODS:
        value = run(library, model(method), [(.042, 24.6, .2, CR, 0),
                      (.020, 24.6, 7.5, CP, 0), (.025, 26., 0., CR, 0)])[3700:]
        t = np.arange(len(value)) * .01 - 5
        axes[0].plot(t, value["mean_v"], label=method, linewidth=1.15)
        axes[1].plot(t, value["high_i"], linewidth=1.15)
    axes[0].set(ylabel="Çıkış gerilimi (V)", title="0,2 A → 82,5 W CPL → yüksüz")
    axes[1].set(xlabel="İlk yük adımına göre zaman (ms)", ylabel="Bobin tepe akımı (A)")
    axes[0].legend()
    for ax in axes:
        ax.grid(alpha=.25)
    fig.savefig(directory / "load-step.svg")
    plt.close(fig)


def cross_platform(paths):
    first, second = (json.loads(Path(name).read_text(encoding="utf-8")) for name in paths)
    need({first["system"], second["system"]} == {"Linux", "Windows"}, "A Windows and a Linux run are required")
    for key in ("baseline", "host", "replay"):
        compare(first["reference"][key], second["reference"][key], SPICE_LIMITS)
    for key, value in first["reference"]["cutoff"].items():
        for solver in ("spice", "host"):
            compare(value[solver], second["reference"]["cutoff"][key][solver],
                    {"peak_v": .003, "peak_i": .025, "cutoff_s": .10e-6})
    for key, value in first["reference"]["hotplug"].items():
        compare(value, second["reference"]["hotplug"][key], {"peak_v": .05, "peak_i": 1.})
    for group in ("matrix", "startups", "additional", "component_endpoints", "extended_stress"):
        need(first[group].keys() == second[group].keys(), f"Mismatched scenario set in {group}")
        for label in first[group]:
            one, two = first[group][label], second[group][label]
            if group == "extended_stress" and isinstance(one, dict) and isinstance(two, dict):
                need("failure" in one and "failure" in two, f"Invalid stress result for {label}")
                continue
            need(isinstance(one, list) and isinstance(two, list), f"Different platform outcomes for {group}/{label}")
            for a, b in zip(one, two, strict=True):
                ripple = "ripple_v" if "ripple_v" in a else "max_cycle_excursion_v"
                compare(a, b, {"mean_v": .012, "min_v": .04, "max_v": .04, ripple: .010,
                               "window_pp_v": .015, "peak_i": .16})
    for key, a in first["protections"]["stuck_s1_backup_trip"].items():
        b = second["protections"]["stuck_s1_backup_trip"][key]
        need(a["trigger"] == b["trigger"], f"Protection trigger changed in {key}")
        compare(a, b, {"max_v": .020, "peak_i": .08})
    for key in ("firmware", "scope_firmware"):
        need(key in first and key in second, f"Both hosts need a valid {key} image")
        need(first[key]["sha256"] == second[key]["sha256"], f"Mismatched {key} ARM binary hashes")
    print(f"Equivalent matched results from {first['system']} and {second['system']}")


def select_tools():
    local_tools = ROOT / "build/tools"
    arm = local_tools / ("arm-windows" if os.name == "nt" else ARM_LINUX.removesuffix(".tar.xz")) / "bin"
    os.environ["PATH"] = os.pathsep.join((str(arm), str(Path(sys.executable).parent), os.environ.get("PATH", "")))
    local_spice = local_tools / "Spice64/bin/ngspice_con.exe"
    if os.name == "nt" and local_spice.is_file():
        os.environ.setdefault("NGSPICE", str(local_spice))


def main():
    select_tools()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", default="build/verify")
    parser.add_argument("--firmware", action="store_true")
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--no-spice", action="store_true")
    parser.add_argument("--strict-stress", action="store_true",
                        help="Apply the same limits to combined high-ESR stress scenarios")
    parser.add_argument("--compare", nargs=2, metavar=("RESULT1", "RESULT2"))
    args = parser.parse_args()
    if args.compare:
        cross_platform(args.compare)
        return
    directory = Path(args.directory).resolve()
    build(directory / "host")
    command(sys.executable, "-m", "unittest", "discover", "-s", "control")
    library = host_library(directory / "host")
    result = {"system": platform.system(), "system_release": platform.release(),
              "python": platform.python_version()}
    if result["system"] == "Linux":
        result["distribution"] = platform.freedesktop_os_release().get("PRETTY_NAME", "Linux")
    result["interface_budgets"] = Interface().calculate()
    result["adc_timing"] = {
        "clock_hz": ADC_CLOCK_HZ, "trigger_s": ADC_TRIGGER_S,
        "current_sample_s": ADC_TRIGGER_S + CURRENT_APERTURE_S,
        "voltage_sample_s": ADC_TRIGGER_S + VOUT_APERTURE_S,
        "conversion_s": ADC_FRAME_S, "execution_budget_s": EXECUTION_BUDGET_S,
        "update_deadline_s": UPDATE_DEADLINE_S,
    }
    result["reference"] = switch_reference(library, directory, args.no_spice)
    result["comparison"] = comparison(library)
    result["protections"] = protections(library)
    result["matrix"] = electrical(library, not args.quick)
    result["startups"] = startups(library)
    result["additional"] = additional(library, not args.quick)
    result["extended_stress"] = additional(library, not args.quick, stress=True)
    result["component_endpoints"] = component_endpoints(library, not args.quick)
    if args.firmware:
        build(directory / "target", firmware=True)
        result["firmware"] = firmware_metrics(directory / "target")
        build(directory / "target_scope", firmware=True, scope=True)
        result["scope_firmware"] = firmware_metrics(directory / "target_scope")
        need(result["firmware"]["sha256"] != result["scope_firmware"]["sha256"],
             "Safe and scope images must have different content")
    plots(directory, library)
    (directory / "results.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    def failures(group):
        return [key for key, outcome in result[group].items() if isinstance(outcome, dict) and "failure" in outcome]

    rejected = [*failures("matrix"), *failures("additional"), *failures("component_endpoints")]
    stress_failures = failures("extended_stress")
    if args.strict_stress:
        rejected.extend(stress_failures)
    print(f"Results: {directory / 'results.json'} ({len(result['matrix'])} matrix, "
          f"{len(result['startups'])} startups, {len(result['additional'])} timing/tolerance cases, "
          f"{len(result['component_endpoints'])} coupled endpoints)")
    print(f"Extended high-ESR stress failures: {len(stress_failures)} of {len(result['extended_stress'])}")
    need(not rejected, "Electrical test failures: " + ", ".join(rejected))


if __name__ == "__main__":
    main()
