# Launch the saved PDU board with an isolated KiCad IPC endpoint.
# No UI automation, KiCad source edits, lock deletion, or other-process termination.
param([switch]$RecoverLockedBoard)
$ErrorActionPreference = 'Stop'
$pduApiRuntime = Join-Path $env:LOCALAPPDATA 'Temp\konnect-pdu-api'
$pduApiBoard = Join-Path (Split-Path $PSScriptRoot -Parent) 'PDU.kicad_pcb'
$pduApiPipe = '\\.\pipe\' + (Join-Path $pduApiRuntime 'kicad\api.sock')
if (-not (Test-Path -LiteralPath $pduApiBoard -PathType Leaf)) {
    throw "PDU board missing: $pduApiBoard"
}
$pduApiExistingPipes = [System.IO.Directory]::EnumerateFiles('\\.\pipe\')
if ($pduApiExistingPipes -contains $pduApiPipe) {
    Write-Output 'PDU API endpoint already exists; no second editor was launched. Verify its document identity with Konnect open_project.'
    exit 0
}
if ((Test-Path -LiteralPath (Join-Path (Split-Path $pduApiBoard) '~PDU.kicad_pcb.lck')) -and -not $RecoverLockedBoard) {
    throw 'PDU PCB lock exists. No editor was launched and no lock was deleted. Save/close the owning editor first.'
}
if ($RecoverLockedBoard) {
    Write-Output 'Opening the native editor for recovery. KiCad retains control of any existing lock/recovery prompt; no lock is removed or bypassed.'
}
New-Item -ItemType Directory -Force -Path $pduApiRuntime | Out-Null
$pduApiEditor = Start-Process -FilePath 'C:\Program Files\KiCad\10.0\bin\pcbnew.exe' `
    -ArgumentList $pduApiBoard -Environment @{ TEMP=$pduApiRuntime; TMP=$pduApiRuntime } `
    -WindowStyle Hidden -PassThru
Write-Output "PDU PCB editor started: PID $($pduApiEditor.Id)"
Write-Output ('API: ipc://' + (Join-Path $pduApiRuntime 'kicad\api.sock'))
Write-Output 'Wait for startup, then verify exact PDU document identity through Konnect before any mutation.'
