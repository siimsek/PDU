# PDU Konnect connection

Repaired 2026-10-19 without Computer Use.

- Installed Konnect: 0.13.0, commit6bbe3e4.
- Active settings: `C:\Users\SK\Documents\KiCad\10.0\3rdparty\plugins\com_github_mixelpixx_konnect\settings.json`.
- `eager_toolsets=true`: a fresh initial `tools/list` contains235 tools, including all228 grouped tools and7 router/meta tools.
- Codex `config.toml` explicitly passes `--config` to that settings file.
- The settings file's socket field is blank so KiCad-launched plugins can inherit their editor's `KICAD_API_SOCKET`.
- Codex supplies `KICAD_API_SOCKET=ipc://C:\Users\SK\AppData\Local\Temp\konnect-pdu-api\kicad\api.sock`.
- The PDU PCB editor runs with its own TEMP/TMP directory. This separates its IPC endpoint from Project Manager and other editors at the default address.

Use `start-pdu-api.ps1` in this folder if the private PDU editor has been closed. It does not overwrite a board, delete a lock, close another editor, or duplicate an existing endpoint. A pipe's existence alone does not prove which document is loaded: verify `open_project` and `get_editor_state` before writes.

Fresh-session results are recorded in `diagnostics/mcp-repair-final-results.json` and `diagnostics/pdu-api-results-3.json`. The latter proves exact PDU board identity, a successful live footprint inventory, and `short_count=0`. This is connection evidence, not circuit approval or a completed PCB transfer.

After the user restarted Codex, the current chat directly called the eagerly exposed tools successfully. Both dedicated endpoints answered exact-document queries: PDU on `konnect-pdu-api`, Pinmap on `konnect-pinmap-api`. Live scratch placement, pad readback, save and schematic-to-PCB transfer now work without Computer Use. Source changes made after connection repair are separately recorded in `diagnostics/pcb-transfer-evidence.json`.

If a stale PCB lock remains after a crash, `start-pdu-api.ps1 -RecoverLockedBoard` opens the native editor and leaves any lock/recovery decision to KiCad. It does not remove a lock or automate a recovery prompt. The default invocation refuses a lock when no endpoint is already running.

Original global settings/config backup: `C:\Users\SK\.konnect\backups\mcp-repair-20261019-112726`.
