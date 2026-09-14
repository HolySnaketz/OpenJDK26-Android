param([int]$TimeoutSec = 3600)
$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path $PSScriptRoot -Parent
$downloadDir = Join-Path $taskRoot 'downloads'
$sources = Get-Content -LiteralPath (Join-Path $downloadDir 'sources.lock.json') -Raw | ConvertFrom-Json
foreach ($source in $sources) {
    $destination = Join-Path $downloadDir $source.file
    if (-not (Test-Path -LiteralPath $destination)) {
        $partial = $destination + '.partial'
        Invoke-WebRequest -Uri $source.url -OutFile $partial -TimeoutSec $TimeoutSec
        if ((Get-FileHash -LiteralPath $partial -Algorithm SHA256).Hash.ToLowerInvariant() -ne $source.sha256) {
            throw "Checksum mismatch for $partial; lock file was not changed"
        }
        Move-Item -LiteralPath $partial -Destination $destination
    }
    if ((Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash.ToLowerInvariant() -ne $source.sha256) {
        throw "Checksum mismatch for $destination"
    }
    Write-Output "Verified $($source.file)"
}