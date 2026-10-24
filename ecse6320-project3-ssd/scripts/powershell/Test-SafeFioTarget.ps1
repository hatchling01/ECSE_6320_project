Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Assert-SafeFioTarget {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [AllowEmptyString()]
        [string]$CandidatePath,

        [Parameter(Mandatory = $true)]
        [string]$RepositoryRoot,

        [switch]$AllowNonexistent
    )

    if ([string]::IsNullOrWhiteSpace($CandidatePath)) {
        throw 'Unsafe FIO target: path is empty.'
    }

    $raw = $CandidatePath.Trim()
    if ($raw -match '^[A-Za-z]:[\\/]?$') {
        throw 'Unsafe FIO target: drive roots and drive-only paths are forbidden.'
    }
    if ($raw -match '^(\\\\\.\\|\\\\\?\\(?:GLOBALROOT|Volume\{)|\\Device\\)' -or
        $raw -match '(?i)(PhysicalDrive|HarddiskVolume|Volume\{)') {
        throw 'Unsafe FIO target: device, physical-drive, partition, and volume paths are forbidden.'
    }

    $repoFull = [IO.Path]::GetFullPath($RepositoryRoot).TrimEnd([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar)
    $benchmarkRoot = [IO.Path]::GetFullPath((Join-Path $repoFull 'benchmark_data')).TrimEnd([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar)
    if (-not (Test-Path -LiteralPath $benchmarkRoot -PathType Container)) {
        throw "Benchmark-data directory does not exist: $benchmarkRoot"
    }

    $targetFull = [IO.Path]::GetFullPath($raw)
    $requiredPrefix = $benchmarkRoot + [IO.Path]::DirectorySeparatorChar
    if (-not $targetFull.StartsWith($requiredPrefix, [StringComparison]::OrdinalIgnoreCase)) {
        throw 'Unsafe FIO target: canonical path is not inside benchmark_data.'
    }
    if ($targetFull -eq $benchmarkRoot) {
        throw 'Unsafe FIO target: benchmark_data directory itself is not a file.'
    }
    if ([string]::IsNullOrWhiteSpace([IO.Path]::GetFileName($targetFull))) {
        throw 'Unsafe FIO target: no regular-file leaf name was supplied.'
    }

    if (Test-Path -LiteralPath $targetFull) {
        $item = Get-Item -LiteralPath $targetFull -Force
        if (-not ($item -is [IO.FileInfo])) {
            throw 'Unsafe FIO target: existing target is not a regular file.'
        }
    } elseif (-not $AllowNonexistent) {
        throw 'Target does not exist; pass -AllowNonexistent only for controlled file creation.'
    }

    return $targetFull
}

if ($MyInvocation.InvocationName -ne '.') {
    throw 'Dot-source this file and call Assert-SafeFioTarget with an explicit repository root.'
}

