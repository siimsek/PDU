# T-002 — KiCad şema düzenleme aracı kararı

Tarih 2026-11-07. Kanıt: [`tooling/roundtrip.json`](tooling/roundtrip.json) (üretici `python scripts/sch_roundtrip_proof.py`), testler `scripts/test_kicad_sexpr.py`.

## Seçenekler

| Seçenek | Erişilebilir mi (kanıt) | Risk | Geri alma | Röle moduna uygun mu |
|---|---|---|---|---|
| (1) Konnect MCP (README'deki eski kural, `b5fd926`; G4 README yeniden yazımında düştü) | **Hayır.** Bu oturumda Konnect MCP sunucusu tanımlı değil (`.mcp.json` yok, `konnect` komutu ve Python paketi yok); yalnız `%LOCALAPPDATA%\konnect\` veri klasörü var. Konnect KiCad IPC API'sine bağlanır (`.konnect/diagnostics/default-api-config.json`: `ipc_socket_path`), bu da **açık bir KiCad GUI** ister; IPC soket dizini yok. `.konnect/MCP-API.md` repoda yok. İki kontrol, ikisi de olumsuz. | GUI oturumu ve kullanıcı etkileşimi gerektirir | KiCad geri al / git | **Hayır** — kullanıcıdan GUI açması istenemez |
| (2) **Kayıpsız S-ifade betiği** `scripts/kicad_sexpr.py` | **Evet.** `PDU.kicad_sch`, `PDU.kicad_pcb` ve 5 özel `.kicad_mod` parse→dump **baytça aynı** (7/7). Geçici kopyada yuvarlak-gezi sonrası kicad-cli 10.0.7 ERC ihlalleri aynı (0 = 0) ve dışa aktarılan netlist aynı (7036 satır, tarih/yol satırları hariç). Deneme düzenlemesi (RFB2 Value → 9.76k) kicad-cli'de yükleniyor, ERC 0 kalıyor, netliste yansıyor. | Yeni sembol/tel yerleşimi koordinat hesabı ister (UUID, ızgara 1,27 mm); hatalı düzenleme ERC/netlist ile yakalanır | `git checkout -- PDU.kicad_sch` (blok başı commit) | **Evet** — tamamen betik + kicad-cli |
| (3) GUI talimatı (kullanıcı KiCad'de elle düzenler) | Evet | İnsan hatası; izlenebilirlik düşük | KiCad geri al | **Hayır** — kullanıcı manuel iş istemiyor |

## Seçim: (2) kayıpsız S-ifade betiği + kicad-cli doğrulaması

Gerekçe: tek seçenek ki hem bu ortamda çalışıyor hem de kullanıcı eylemi gerektirmiyor; dokunulmayan metin KiCad'in kendi biçiminde kaldığı için git farkı yalnız düzenlenen satırları gösterir. Her şema kartı (T-006…T-012) için kural:

1. Blok öncesi commit.
2. Düzenleme yalnız `scripts/kicad_sexpr.py` (ve onun üzerine kurulan, testli yardımcılar) ile; elle metin düzenleme yok.
3. Blok sonrası `kicad-cli sch erc` (yeni ihlal 0) + `kicad-cli sch export netlist` → `analysis/check_consistency.py --schematic` (T-006'da eklenecek) fark 0.
4. Bozulursa `git checkout -- PDU.kicad_sch`.
5. Görsel kontrol: `kicad-cli sch export svg/pdf` → R-002 (THINKER) inceler.

Sınır: betik bugün özellik (property) değiştirmeyi ve alt liste ekleme/çıkarmayı destekler; yeni sembol örneği ve tel üretimi T-006'da yardımcı fonksiyonlarla (lib_symbols kopyası, UUID, ızgara hizası) eklenecek ve aynı yuvarlak-gezi + ERC kanıtıyla test edilecek.
