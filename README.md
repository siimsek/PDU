# PDU — STM32 tabanlı dijital buck

20–26 V giriş, 24,6 V nominal, 11 V / 7,5 A çıkış ve 100 kHz anahtarlama. Ana güç katı, `ANA-GUC-DEVRESI` dalındaki `6879e87` sürümünden alınan 33 µH, 1000 µF ve 470 µF + 0,22 Ω seri sönüm dalına sahip asenkron buck devresidir.

![Dondurulmuş açık çevrim güç katı](buck/ltspice/buck_guc_kati.svg)

- [Yol haritası ve geçiş ölçütleri](YOL-HARITASI.md)
- [Tarihî LTspice güç katı sonuçları](buck/OPTIMIZASYON.md)
- [Güç katı parça hedefleri](buck/PARCA-HEDEFLERI.md)

Python ve PATH üzerinde ngspice ile repo kökünde `python -m control.spice` nominal açık çevrim koşusunu çalıştırır. `python buck/hesap.py` analitik güç katı hesabını üretir. LTspice ASC ve özgün LTspice betikleri referans olarak depoda bulunur.

## Windows 11 ve CachyOS

Her iki sistemde x64 Python 3.12, Git ve yerel C derleyicisi kullanılır. Windows’ta Visual Studio Build Tools 2022 veya 2026 içindeki **Desktop development with C++** iş yükü, Windows SDK ve 7-Zip gerekir. CachyOS’ta sistem paketleri için `sudo pacman -S --needed base-devel ngspice`. Depoda Python 3.12 yoksa örneğin `uv python install 3.12.12` ile yerel yorumlayıcı kurulabilir. Ubuntu CI, dağıtımın ngspice paketini kullanır.

Repo kökünde sanal ortam oluştur:

| Sistem | Ortamı oluştur | Ortamı etkinleştirmeden Python |
|---|---|---|
| Windows | `py -3.12 -m venv .venv` | `.venv\Scripts\python.exe` |
| CachyOS | `python3.12 -m venv .venv` | `.venv/bin/python` |

Aşağıdaki komutlarda `python` sanal ortamın Python’ıdır. `control.tools` Arm GNU Toolchain 14.3.Rel1, Windows’ta ayrıca ngspice 47’yi SHA256 karşılaştırmasından sonra `build/tools` altına açar. Kurulmuş yerel araçlar otomatik bulunur. Dış kurulum için `arm-none-eabi-gcc` PATH üzerinde ve gerekirse `NGSPICE` ortam değişkeni konsol çalıştırılabilir dosyasını göstermelidir.

```text
python -m pip install -r requirements.txt
python -m control.tools
python -m control.verify --firmware
```

- `python -m unittest discover -s control` katsayıları, güç katı kaynağını ve donanım eşik bütçelerini sınar.
- `python -m control.verify --quick --no-spice` hızlı yerel iterasyon içindir. Tam koşu ngspice açık çevrim ve PWM replay, çalışma zarfı, tolerans, arıza, grafik ve isteğe bağlı MCU derlemesini çalıştırır.
- `python -m control.design --optimize` CCM katsayı aramasını yeniden üretir. Sonrasında `control.verify` çalıştırılır.
- `python -m control.interface` ilk donanım eşiklerini ve tolerans bütçelerini hesaplar.
- `python -m control.verify --strict-stress --firmware` aynı ölçütleri birleşik yüksek ESR stres koşullarına da uygular. Bu koşullar sonuç dosyasında olağan doğrulamada da raporlanır.

Senaryo bazında sonuçlar `build/verify/results.json` dosyasındadır. Aynı klasörde Bode ve geçici rejim SVG’leri, ngspice logları ve `--firmware` ile `target/firmware/pdu_g474.{elf,bin,map}` oluşur. İki platformdan alınan JSON için `python -m control.verify --compare linux.json windows.json`. Workflow aynı komutları Ubuntu ve Windows Server 2025 x64 üzerinde çalıştırır. Windows 11 masaüstü ve fiziksel hedef kart ayrı doğrulama aşamalarıdır.

[Kontrol yöntemleri, model ve donanım arayüzü](control/TASARIM.md)
