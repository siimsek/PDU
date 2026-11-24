"""Install pinned standalone CI tools on native x64 Linux or Windows."""
import argparse
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
from urllib.request import Request, urlopen
import zipfile

ARM_BASE = "https://developer.arm.com/-/media/Files/downloads/gnu/14.3.rel1/binrel/"
ARM_WIN = "arm-gnu-toolchain-14.3.rel1-mingw-w64-i686-arm-none-eabi.zip"
ARM_LINUX = "arm-gnu-toolchain-14.3.rel1-x86_64-arm-none-eabi.tar.xz"
NG_WIN = "ngspice-47_64.7z"
NG_BASE = "https://downloads.sourceforge.net/project/ngspice/ng-spice-rework/old-releases/47/"
HASHES = {
    ARM_WIN: "836ebe51fd71b6542dd7884c8fb2011192464b16c28e4b38fddc9350daba5ee8",
    ARM_LINUX: "8f6903f8ceb084d9227b9ef991490413014d991874a1e34074443c2a72b14dbd",
    NG_WIN: "59225971bd68cdd1199443649aa4615a9e6d684933f205ab49006a3942518f5a",
}


def digest(path):
    with path.open("rb") as file:
        return hashlib.file_digest(file, "sha256").hexdigest()


def download(work, base, name):
    target = work / name
    if target.is_file() and digest(target) == HASHES[name]:
        return target
    incoming = work / (name + ".download")
    request = Request(base + name, headers={"User-Agent": "PDU verification tool"})
    with urlopen(request, timeout=120) as source, incoming.open("wb") as dest:
        shutil.copyfileobj(source, dest)
    if digest(incoming) != HASHES[name]:
        incoming.unlink()
        raise RuntimeError(f"Unexpected SHA256 for {name}")
    incoming.replace(target)
    return target


def install(work):
    work = Path(work).resolve()
    work.mkdir(parents=True, exist_ok=True)
    windows = os.name == "nt"
    name = ARM_WIN if windows else ARM_LINUX
    archive = download(work, ARM_BASE, name)
    if windows:
        arm = work / "arm-windows" / "bin"
        if not (arm / "arm-none-eabi-gcc.exe").is_file():
            with zipfile.ZipFile(archive) as package:
                package.extractall(arm.parent)
        spice = work / "Spice64" / "bin" / "ngspice_con.exe"
        if not spice.is_file():
            sevenzip = shutil.which("7z") or shutil.which("7za")
            if sevenzip is None and "ProgramFiles" in os.environ:
                candidate = Path(os.environ["ProgramFiles"]) / "7-Zip" / "7z.exe"
                sevenzip = str(candidate) if candidate.is_file() else None
            if sevenzip is None:
                raise RuntimeError("Add 7-Zip (7z.exe) to PATH for the Windows ngspice archive")
            subprocess.run([sevenzip, "x", "-y", f"-o{work}", str(download(work, NG_BASE, NG_WIN))],
                           check=True, stdout=subprocess.DEVNULL)
    else:
        arm = work / name.removesuffix(".tar.xz") / "bin"
        if not (arm / "arm-none-eabi-gcc").is_file():
            with tarfile.open(archive) as package:
                package.extractall(work, filter="data")
        spice = None
    return arm, spice


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", default="build/tools")
    args = parser.parse_args()
    arm, spice = install(args.path)
    print(f"GNU Arm bin = {arm}")
    if spice:
        print(f"NGSPICE = {spice}")
    if "GITHUB_PATH" in os.environ:
        with open(os.environ["GITHUB_PATH"], "a", encoding="utf-8") as out:
            print(arm, file=out)
        if spice:
            with open(os.environ["GITHUB_ENV"], "a", encoding="utf-8") as out:
                print(f"NGSPICE={spice}", file=out)


if __name__ == "__main__":
    main()
