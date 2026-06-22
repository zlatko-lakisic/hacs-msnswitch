# Install MSNSwitch integration into a Home Assistant config folder.
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File scripts/install-to-ha.ps1
#   powershell -ExecutionPolicy Bypass -File scripts/install-to-ha.ps1 -ConfigRoot '\\192.168.89.25\config'

param(
    [string]$ConfigRoot = '\\192.168.89.25\config'
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$src = Join-Path $repoRoot 'custom_components\msnswitch'
$dstRoot = Join-Path $ConfigRoot 'custom_components'
$dst = Join-Path $dstRoot 'msnswitch'

if (-not (Test-Path $src)) {
    throw "Integration source not found: $src"
}
if (-not (Test-Path $ConfigRoot)) {
    throw "Home Assistant config path not reachable: $ConfigRoot"
}

New-Item -ItemType Directory -Force -Path $dst | Out-Null
Copy-Item -Path (Join-Path $src '*') -Destination $dst -Recurse -Force

Write-Host "Installed MSNSwitch integration to $dst"
Write-Host "Restart Home Assistant, then: Settings -> Devices & services -> Add integration -> MSNSwitch"
