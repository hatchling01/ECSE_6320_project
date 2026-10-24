[CmdletBinding()]
param(
    [string]$FioPath = 'C:\Program Files\fio\fio.exe',
    [string]$PythonPath = 'C:\Users\CHOUDN3\AppData\Local\anaconda3\python.exe',
    [string]$Target,
    [switch]$KeepTarget
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repoRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
if ([string]::IsNullOrWhiteSpace($Target)) {
    $Target = Join-Path $repoRoot 'benchmark_data\fio_smoke_test.bin'
}

. (Join-Path $PSScriptRoot 'Test-SafeFioTarget.ps1')
$targetFull = Assert-SafeFioTarget -CandidatePath $Target -RepositoryRoot $repoRoot -AllowNonexistent

if (Test-Path -LiteralPath $targetFull) {
    throw "Smoke target already exists; refusing to overwrite it: $targetFull"
}
if (-not (Test-Path -LiteralPath $FioPath -PathType Leaf)) {
    throw "FIO executable not found: $FioPath"
}
if (-not (Test-Path -LiteralPath $PythonPath -PathType Leaf)) {
    throw "Python executable not found: $PythonPath"
}

$configPath = Join-Path $repoRoot 'configs\fio\smoke.fio'
$rawDir = Join-Path $repoRoot 'data\raw\smoke'
$parsedDir = Join-Path $repoRoot 'data\parsed\smoke'
$metadataDir = Join-Path $repoRoot 'data\metadata\smoke'
$logDir = Join-Path $repoRoot 'logs\smoke'
foreach ($dir in @($rawDir, $parsedDir, $metadataDir, $logDir)) {
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
}

$stamp = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssfffZ')
$jsonPath = Join-Path $rawDir "smoke_$stamp.json"
$csvPath = Join-Path $parsedDir "smoke_$stamp.csv"
$metadataPath = Join-Path $metadataDir "smoke_$stamp.json"
$logPath = Join-Path $logDir "smoke_$stamp.log"

$parameters = [ordered]@{
    classification = 'NOT FOR PERFORMANCE ANALYSIS'
    resolved_target = $targetFull
    file_size_bytes = 16MB
    measured_io_bytes = 4MB
    ioengine = 'windowsaio'
    direct = 1
    rw = 'randrw'
    rwmixread = 50
    block_size_bytes = 4KB
    iodepth = 1
    numjobs = 1
    fio_path = $FioPath
    fio_config = $configPath
    timestamp_utc = $stamp
}

Write-Host 'SAFE REGULAR-FILE TARGET VERIFIED'
$parameters.GetEnumerator() | ForEach-Object { Write-Host ("{0}={1}" -f $_.Key, $_.Value) }
$parameters.GetEnumerator() | ForEach-Object { "{0}={1}" -f $_.Key, $_.Value } | Set-Content -LiteralPath $logPath -Encoding UTF8

$fioArgs = @(
    "--output=$jsonPath",
    '--output-format=json',
    "--filename=$targetFull",
    $configPath
)
Add-Content -LiteralPath $logPath -Value ('command="{0}" {1}' -f $FioPath, ($fioArgs -join ' '))

$fioVersion = (& $FioPath --version).Trim()
$parameters.fio_version = $fioVersion

try {
    & $FioPath @fioArgs
    if ($LASTEXITCODE -ne 0) {
        throw "FIO smoke validation failed with exit code $LASTEXITCODE"
    }

    & $PythonPath (Join-Path $repoRoot 'scripts\python\parse_fio.py') --input $jsonPath --output $csvPath --expect-smoke
    if ($LASTEXITCODE -ne 0) {
        throw "FIO JSON parser validation failed with exit code $LASTEXITCODE"
    }

    $parameters.fio_exit_code = 0
    $parameters.parser_status = 'validated'
    $parameters.target_cleanup = $(if ($KeepTarget) { 'retained by explicit switch' } else { 'deleted after validation' })
    $parameters | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $metadataPath -Encoding UTF8
    Add-Content -LiteralPath $logPath -Value 'SMOKE VALIDATION PASSED'
    Write-Host "Raw JSON: $jsonPath"
    Write-Host "Parsed CSV: $csvPath"
    Write-Host 'SMOKE VALIDATION PASSED — NOT FOR PERFORMANCE ANALYSIS'
} finally {
    if (-not $KeepTarget -and (Test-Path -LiteralPath $targetFull -PathType Leaf)) {
        $validatedAgain = Assert-SafeFioTarget -CandidatePath $targetFull -RepositoryRoot $repoRoot
        Remove-Item -LiteralPath $validatedAgain -Force
        Write-Host "Deleted validated disposable smoke file: $validatedAgain"
    }
}

