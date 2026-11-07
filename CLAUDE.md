# CLAUDE.md

Kurallar, kanıt etiketleri ve yasaklar için **[`AGENTS.md`](AGENTS.md)**; proje durumu için **[`docs/START-HERE.md`](docs/START-HERE.md)**. Burada yalnız Claude Code'a özgü notlar var.

- `.claude/settings.json` `archive/**`, `reports/*/sim/**` ve büyük JSON/log dosyalarını okumadan önce onay ister (`ask`). Bunlar kanıt arşividir; özetler `archive/INDEX.md` ve `reports/g2/SIM-RESULTS.md` içindedir.
- Uzun koşular: `python analysis/run_all.py` (~5 dk) arka planda çalıştırılabilir; ngspice yolu `PDU_NGSPICE` veya `F:\Spice64\bin\ngspice_con.exe`.
- kicad-cli PATH'te değil: `C:\Program Files\KiCad\10.0\bin\kicad-cli.exe`. ERC/DRC çıktısını yalnız `reports/g4/baseline/` gibi rapor klasörüne yaz; KiCad dosyalarını kaydetme.
- Windows'ta Python dosya yazarken `newline="\n"` kullan (repo LF; `.gitattributes`).
- Türkçe raporlarda sayıların kaynağı JSON/hesap dosyasıdır; elle sayı yazma, üretici betiği çalıştır.
