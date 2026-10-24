param(
    [Parameter(Mandatory = $true, Position = 0)]
    [ValidateSet('pilot', 'full')]
    [string]$Mode,
    [ValidateRange(0, 10)]
    [int]$Repetitions = 0
)

$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
$cmake = 'C:\Users\CHOUDN3\AppData\Local\Microsoft\WinGet\Packages\Kitware.CMake_Microsoft.Winget.Source_8wekyb3d8bbwe\cmake-4.4.4-windows-x86_64\bin\cmake.exe'
$ctest = 'C:\Users\CHOUDN3\AppData\Local\Microsoft\WinGet\Packages\Kitware.CMake_Microsoft.Winget.Source_8wekyb3d8bbwe\cmake-4.4.4-windows-x86_64\bin\ctest.exe'
$config = Get-Content (Join-Path $repo 'config\experiment_config.json') -Raw | ConvertFrom-Json

if ($Mode -eq 'pilot') {
    $output = Join-Path $repo (Join-Path 'data\raw' $config.pilot.raw_file)
    $workingSets = @($config.pilot.target_working_set_sizes_bytes)
    $kernels = @('elementwise_multiply')
    $datatypes = @($config.pilot.datatypes)
    $builds = @($config.pilot.build_variants)
    $warmups = [int]$config.pilot.initial_warmups
    if ($Repetitions -eq 0) { $Repetitions = [int]$config.pilot.initial_repetitions }
    if ($Repetitions -gt [int]$config.pilot.maximum_repetitions) {
        throw "Pilot repetitions cannot exceed $($config.pilot.maximum_repetitions)."
    }
} else {
    $output = Join-Path $repo (Join-Path 'data\raw' $config.full_matrix.raw_file)
    $workingSets = @($config.full_matrix.target_working_set_sizes_bytes)
    $kernels = @($config.kernels)
    $datatypes = @($config.datatypes)
    $builds = @('scalar', 'auto_vectorized', 'cpu_targeted')
    $warmups = [int]$config.full_matrix.warmups
    if ($Repetitions -eq 0) { $Repetitions = [int]$config.full_matrix.repetitions }
    if ($Repetitions -gt 10) {
        throw 'Phase 3 repetition count is capped at 10.'
    }
}

if (Test-Path $output) {
    throw "Refusing to overwrite raw measurements: $output"
}

$plannedSamples = $kernels.Count * $datatypes.Count * $builds.Count * $workingSets.Count * $Repetitions
Write-Output "Planned timed samples: $($kernels.Count) kernels x $($datatypes.Count) datatypes x $($builds.Count) builds x $($workingSets.Count) working-set sizes x $Repetitions repetitions = $plannedSamples"
if ($Mode -eq 'full' -and $plannedSamples -gt [int]$config.full_matrix.maximum_timed_samples) {
    throw "Planned sample count $plannedSamples exceeds the configured cap. Reduce the matrix before running."
}

$compilerPath = 'C:\msys64\ucrt64\bin\g++.exe'
$compilerVersion = (& $compilerPath --version | Select-Object -First 1)
$cmakeDirectory = Split-Path -Parent $cmake
$oldPath = $env:Path
$env:Path = 'C:\msys64\ucrt64\bin;' + $cmakeDirectory + ';' + $oldPath

$repoBuilds = @{
    scalar = 'gcc-scalar'
    auto_vectorized = 'gcc-auto'
    cpu_targeted = 'gcc-native'
}
$variantFlags = @{
    scalar = '-O3 -DNDEBUG -fno-tree-vectorize -fno-tree-loop-vectorize -fno-tree-slp-vectorize'
    auto_vectorized = '-O3 -DNDEBUG'
    cpu_targeted = '-O3 -DNDEBUG -march=native (resolves to znver5)'
}
$runnerPaths = @{}

try {
    Push-Location $repo
    foreach ($variant in $builds) {
        $preset = $repoBuilds[$variant]
        if (-not $runnerPaths.ContainsKey($variant)) {
            & $cmake --build --preset $preset --target benchmark_runner
            if ($LASTEXITCODE -ne 0) { throw "Build failed for $preset." }
            & $ctest --preset $preset
            if ($LASTEXITCODE -ne 0) { throw "Correctness tests failed for $preset." }
            $runnerPaths[$variant] = Join-Path $repo "build-$preset\benchmark_runner.exe"
        }
    }

    $createdOutput = $false
    foreach ($kernel in $kernels) {
        foreach ($datatype in $datatypes) {
            $elementBytes = if ($datatype -eq 'float32') { 4 } else { 8 }
            $arrayCount = if ($kernel -eq 'elementwise_multiply') { 3 } else { 2 }
            foreach ($build in $builds) {
                $runner = $runnerPaths[$build]
                $buildName = $repoBuilds[$build]
                $verifyN = 1003
                $verifyBytes = $verifyN * $elementBytes * $arrayCount
                $verifyArgs = @(
                    '--kernel', $kernel,
                    '--datatype', $datatype,
                    '--build', $buildName,
                    '--compiler', "$compilerVersion",
                    '--flags', $variantFlags[$build],
                    '--n', "$verifyN",
                    '--target-working-set-bytes', "$verifyBytes",
                    '--warmups', '0',
                    '--repetitions', '0',
                    '--batch', '1',
                    '--verify-only'
                )
                & $runner @verifyArgs
                if ($LASTEXITCODE -ne 0) {
                    throw "Representative correctness failed: $kernel $datatype $buildName N=$verifyN"
                }
            }
            foreach ($workingSet in $workingSets) {
                $n = [Math]::Max(1, [int][Math]::Floor([double]$workingSet / ($elementBytes * $arrayCount)))
                $batching = $config.pilot.batching
                if ($n -le [int]$batching.n_at_most) {
                    $batch = [int]$batching.batch_count
                } elseif ($n -le [int]$batching.n_at_most_next) {
                    $batch = [int]$batching.batch_count_next
                } else {
                    $batch = 1
                }

                foreach ($build in $builds) {
                    $runner = $runnerPaths[$build]
                    $buildName = $repoBuilds[$build]
                    $flags = $variantFlags[$build]
                    $common = @(
                        '--kernel', $kernel,
                        '--datatype', $datatype,
                        '--build', $buildName,
                        '--compiler', "$compilerVersion",
                        '--flags', $flags,
                        '--n', "$n",
                        '--target-working-set-bytes', "$workingSet",
                        '--warmups', "$warmups",
                        '--repetitions', "$Repetitions",
                        '--batch', "$batch"
                    )

                    $arguments = $common + @('--output', $output)
                    & $runner @arguments
                    if ($LASTEXITCODE -ne 0) {
                        throw "Measurement failed: $kernel $datatype $build N=$n"
                    }
                    $createdOutput = $true
                }
            }
        }
    }
    if (-not $createdOutput) { throw 'No benchmark samples were written.' }
} finally {
    if ((Get-Location).Path -eq $repo) { Pop-Location }
    $env:Path = $oldPath
}

if ($Mode -eq 'pilot') {
    $analysisArgs = @('--pilot', $output)
    foreach ($rerun in @('pilot_rerun_raw.csv', 'pilot_rerun2_raw.csv')) {
        $rerunPath = Join-Path $repo (Join-Path 'data\raw' $rerun)
        if (Test-Path $rerunPath) { $analysisArgs += @('--rerun', $rerunPath) }
    }
    & python (Join-Path $repo 'scripts\analyze_phase3.py') @analysisArgs
    if ($LASTEXITCODE -ne 0) { throw 'Pilot analysis failed.' }
} else {
    $analysisArgs = @('--full', $output)
    $rerunPath = Join-Path $repo (Join-Path 'data\raw' $config.full_matrix.targeted_rerun_file)
    if (Test-Path $rerunPath) { $analysisArgs += @('--rerun', $rerunPath) }
    & python (Join-Path $repo 'scripts\analyze_phase3.py') @analysisArgs
    if ($LASTEXITCODE -ne 0) { throw 'Full-matrix analysis failed.' }
}