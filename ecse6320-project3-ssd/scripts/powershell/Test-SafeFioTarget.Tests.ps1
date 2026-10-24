Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repoRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
. (Join-Path $PSScriptRoot 'Test-SafeFioTarget.ps1')

$unsafeCases = @(
    '',
    'C:',
    'C:\',
    '\\.\PhysicalDrive0',
    '\\?\Volume{00000000-0000-0000-0000-000000000000}\',
    '\Device\HarddiskVolume1',
    (Join-Path $repoRoot 'README.md'),
    (Split-Path $repoRoot -Parent),
    (Join-Path $repoRoot 'benchmark_data')
)

$failures = @()
foreach ($candidate in $unsafeCases) {
    try {
        Assert-SafeFioTarget -CandidatePath $candidate -RepositoryRoot $repoRoot -AllowNonexistent | Out-Null
        $failures += "Validator incorrectly accepted: '$candidate'"
    } catch {
        Write-Host "PASS rejected: '$candidate'"
    }
}

$safeCandidate = Join-Path $repoRoot 'benchmark_data\validator_future_file.bin'
try {
    $resolved = Assert-SafeFioTarget -CandidatePath $safeCandidate -RepositoryRoot $repoRoot -AllowNonexistent
    Write-Host "PASS accepted safe candidate: $resolved"
} catch {
    $failures += "Validator incorrectly rejected safe candidate: $($_.Exception.Message)"
}

if ($failures.Count -gt 0) {
    $failures | ForEach-Object { Write-Error $_ }
    throw "Safety validator tests failed: $($failures.Count)"
}

Write-Host 'ALL SAFETY VALIDATOR TESTS PASSED'

