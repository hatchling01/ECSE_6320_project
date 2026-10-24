param(
    [switch]$Reruns
)

$ErrorActionPreference = 'Stop'
$repo = if ($PSScriptRoot) { Split-Path -Parent $PSScriptRoot } else { (Get-Location).Path }
$cmake = 'C:\Users\CHOUDN3\AppData\Local\Microsoft\WinGet\Packages\Kitware.CMake_Microsoft.Winget.Source_8wekyb3d8bbwe\cmake-4.4.4-windows-x86_64\bin\cmake.exe'
$ctest = 'C:\Users\CHOUDN3\AppData\Local\Microsoft\WinGet\Packages\Kitware.CMake_Microsoft.Winget.Source_8wekyb3d8bbwe\cmake-4.4.4-windows-x86_64\bin\ctest.exe'
$config = Get-Content (Join-Path $repo 'config\experiment_config.json') -Raw | ConvertFrom-Json
$experiment = $config.phase4b_tail
$initialRaw = Join-Path $repo (Join-Path 'data\raw' $experiment.raw_file)
$initialCorrectness = Join-Path $repo 'data\processed\phase4b_tail_correctness.csv'
$selectionPath = Join-Path $repo 'data\metadata\phase4b_tail_rerun_selection.csv'
$rerunRaw = Join-Path $repo (Join-Path 'data\raw' $experiment.targeted_rerun_file)
$rerunCorrectness = Join-Path $repo 'data\processed\phase4b_tail_rerun_correctness.csv'

if ($Reruns) {
    if (-not (Test-Path $initialRaw) -or -not (Test-Path $initialCorrectness) -or -not (Test-Path $selectionPath)) {
        throw 'Run the initial Phase 4B tail matrix and analysis before targeted reruns.'
    }
    if ((Test-Path $rerunRaw) -or (Test-Path $rerunCorrectness)) {
        throw 'Refusing to overwrite existing Phase 4B targeted rerun files.'
    }
    $selection = @(Import-Csv $selectionPath | Where-Object { $_.build -and $_.selection_reason -eq 'initial_cv_gt_20_percent' })
    if ($selection.Count -eq 0) {
        Write-Output 'No initial Phase 4B configuration exceeded 20% CV; no rerun was needed.'
        return
    }
    $output = $rerunRaw
    $correctnessOutput = $rerunCorrectness
    $repetitions = [int]$experiment.rerun_repetitions
    $outputPath = $rerunRaw
    Write-Output "Targeted rerun plan: $($selection.Count) configurations x $repetitions additional observations = $($selection.Count * $repetitions) samples. Maximum observations/configuration: $($experiment.maximum_repetitions)."
} else {
    if (Test-Path $initialRaw) { throw "Refusing to overwrite raw measurements: $initialRaw" }
    if (Test-Path $initialCorrectness) { throw "Refusing to overwrite correctness manifest: $initialCorrectness" }
    $output = $initialRaw
    $correctnessOutput = $initialCorrectness
    $repetitions = [int]$experiment.initial_repetitions
    $outputPath = $initialRaw
    $selection = @()
    $configurationCount = $experiment.base_sizes.Count * $experiment.remainders.Count * $experiment.builds.Count
    $plannedSamples = $configurationCount * $repetitions
    if ($configurationCount -ne 96 -or $plannedSamples -ne 480) {
        throw "Configured Phase 4B matrix is unexpected: $configurationCount configurations, $plannedSamples initial samples."
    }
    Write-Output "Phase 4B tail-only plan: 2 bases x 16 remainders x 3 builds = $configurationCount configurations; $plannedSamples initial timed samples."
}

if (($Reruns -and ($repetitions + [int]$experiment.initial_repetitions -gt [int]$experiment.maximum_repetitions)) -or
    (-not $Reruns -and $repetitions -gt [int]$experiment.maximum_repetitions)) {
    throw 'Phase 4B repetition cap exceeded.'
}

$compilerPath = 'C:\msys64\ucrt64\bin\g++.exe'
$compilerVersion = (& $compilerPath --version | Select-Object -First 1)
$cmakeDirectory = Split-Path -Parent $cmake
$oldPath = $env:Path
$env:Path = 'C:\msys64\ucrt64\bin;' + $cmakeDirectory + ';' + $oldPath
$variantFlags = @{
    'gcc-scalar' = '-O3 -DNDEBUG -fno-tree-vectorize -fno-tree-loop-vectorize -fno-tree-slp-vectorize'
    'gcc-auto' = '-O3 -DNDEBUG'
    'gcc-native' = '-O3 -DNDEBUG -march=native (resolves to znver5)'
}
$runnerPaths = @{}
$tests = [System.Collections.Generic.List[object]]::new()

if ($Reruns) {
    foreach ($row in $selection) {
        $tests.Add([pscustomobject]@{
            build = $row.build
            base_name = $row.base_name
            base_n = [int]$row.base_n
            remainder = [int]$row.remainder
            N = [int]$row.N
        })
    }
} else {
    foreach ($base in $experiment.base_sizes) {
        foreach ($remainder in $experiment.remainders) {
            foreach ($build in $experiment.builds) {
                $tests.Add([pscustomobject]@{
                    build = $build
                    base_name = $base.name
                    base_n = [int]$base.base_n
                    remainder = [int]$remainder
                    N = [int]$base.base_n + [int]$remainder
                })
            }
        }
    }
}

try {
    Push-Location $repo
    foreach ($build in $experiment.builds) {
        & $cmake --build --preset $build --target benchmark_runner
        if ($LASTEXITCODE -ne 0) { throw "Build failed for $build." }
        & $ctest --preset $build
        if ($LASTEXITCODE -ne 0) { throw "Correctness tests failed for $build." }
        $runnerPaths[$build] = Join-Path $repo "build-$build\benchmark_runner.exe"
    }

    $verificationRows = [System.Collections.Generic.List[object]]::new()
    foreach ($test in $tests) {
        $verifyArgs = @(
            '--kernel', 'axpy',
            '--datatype', 'float32',
            '--build', $test.build,
            '--compiler', "$compilerVersion",
            '--flags', $variantFlags[$test.build],
            '--n', "$($test.N)",
            '--target-working-set-bytes', "$([int64]$test.N * 8)",
            '--warmups', '0',
            '--repetitions', '0',
            '--batch', '1',
            '--verify-only'
        )
        $verifyOutput = & $runnerPaths[$test.build] @verifyArgs
        if ($LASTEXITCODE -ne 0) { throw "Correctness preflight failed: $($test.build) base=$($test.base_n) r=$($test.remainder) N=$($test.N)" }
        $verifyText = $verifyOutput -join ' '
        if ($verifyText -notmatch 'status=PASS') { throw "Missing PASS in correctness output: $verifyText" }
        $absoluteMatch = [regex]::Match($verifyText, 'max_abs=([^ ]+)')
        $relativeMatch = [regex]::Match($verifyText, 'max_rel=([^ ]+)')
        $verificationRows.Add([pscustomobject]@{
            kernel = 'axpy'
            datatype = 'float32'
            build = $test.build
            base_name = $test.base_name
            base_n = $test.base_n
            remainder = $test.remainder
            N = $test.N
            max_absolute_error = $absoluteMatch.Groups[1].Value
            max_relative_error = $relativeMatch.Groups[1].Value
            status = 'PASS'
        })
    }
    $correctnessOutputParent = Split-Path -Parent $correctnessOutput
    New-Item -ItemType Directory -Path $correctnessOutputParent -Force | Out-Null
    $verificationRows | Export-Csv -Path $correctnessOutput -NoTypeInformation -Encoding UTF8
    Write-Output "Correctness preflight passed for $($verificationRows.Count) configurations."

    $batching = $experiment.batching
    $testIndex = 0
    foreach ($test in $tests) {
        if ($test.N -le [int]$batching.n_at_most) {
            $batch = [int]$batching.batch_count
        } elseif ($test.N -le [int]$batching.n_at_most_next) {
            $batch = [int]$batching.batch_count_next
        } else {
            $batch = 1
        }
        $arguments = @(
            '--kernel', 'axpy',
            '--datatype', 'float32',
            '--build', $test.build,
            '--compiler', "$compilerVersion",
            '--flags', $variantFlags[$test.build],
            '--n', "$($test.N)",
            '--target-working-set-bytes', "$([int64]$test.N * 8)",
            '--warmups', "$($experiment.warmups)",
            '--repetitions', "$repetitions",
            '--batch', "$batch",
            '--output', $outputPath
        )
        & $runnerPaths[$test.build] @arguments
        if ($LASTEXITCODE -ne 0) { throw "Timing failed: $($test.build) base=$($test.base_n) r=$($test.remainder) N=$($test.N)" }
        $testIndex++
    }
} finally {
    if ((Get-Location).Path -eq $repo) { Pop-Location }
    $env:Path = $oldPath
}

if ($Reruns) {
    & python .\scripts\analyze_phase4b_tail.py `
        --raw $initialRaw `
        --correctness $initialCorrectness `
        --expected-repetitions $($experiment.initial_repetitions) `
        --rerun $rerunRaw `
        --rerun-correctness $rerunCorrectness `
        --rerun-repetitions $repetitions
} else {
    & python .\scripts\analyze_phase4b_tail.py `
        --raw $initialRaw `
        --correctness $initialCorrectness `
        --expected-repetitions $repetitions
}
if ($LASTEXITCODE -ne 0) { throw 'Phase 4B tail analysis failed.' }