$ErrorActionPreference = 'Stop'
$repo = if ($PSScriptRoot) { Split-Path -Parent $PSScriptRoot } else { (Get-Location).Path }
$cmake = 'C:\Users\CHOUDN3\AppData\Local\Microsoft\WinGet\Packages\Kitware.CMake_Microsoft.Winget.Source_8wekyb3d8bbwe\cmake-4.4.4-windows-x86_64\bin\cmake.exe'
$ctest = 'C:\Users\CHOUDN3\AppData\Local\Microsoft\WinGet\Packages\Kitware.CMake_Microsoft.Winget.Source_8wekyb3d8bbwe\cmake-4.4.4-windows-x86_64\bin\ctest.exe'
$config = Get-Content (Join-Path $repo 'config\experiment_config.json') -Raw | ConvertFrom-Json
$phase4a = $config.phase4a_alignment
$initialRaw = Join-Path $repo (Join-Path 'data\raw' $phase4a.raw_file)
$selectionPath = Join-Path $repo 'data\metadata\phase4a_alignment_rerun_selection.csv'
$rerunRaw = Join-Path $repo 'data\raw\phase4a_alignment_targeted_reruns.csv'
$initialRepetitions = [int]$phase4a.initial_repetitions
$additionalRepetitions = [int]$phase4a.maximum_repetitions - $initialRepetitions

if (-not (Test-Path $initialRaw) -or -not (Test-Path $selectionPath)) {
    throw 'Run the initial Phase 4A experiment and analysis before targeted reruns.'
}
if (Test-Path $rerunRaw) {
    throw "Refusing to overwrite targeted rerun data: $rerunRaw"
}
if ($additionalRepetitions -le 0 -or $initialRepetitions + $additionalRepetitions -gt 10) {
    throw 'Targeted reruns would exceed the configured 10-sample cap.'
}
$selection = @(Import-Csv $selectionPath | Where-Object { $_.kernel -and $_.selection_reason -eq 'initial_cv_gt_20_percent' })
if ($selection.Count -eq 0) {
    Write-Output 'No initial configurations exceeded 20% CV; no rerun was needed.'
    exit 0
}
$plannedSamples = $selection.Count * $additionalRepetitions
Write-Output "Phase 4A targeted reruns: $($selection.Count) configurations with initial CV >20% x $additionalRepetitions additional samples = $plannedSamples samples."
Write-Output "Each selected configuration will have at most $($initialRepetitions + $additionalRepetitions) observations; initial and rerun raw files remain separate."

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

try {
    Push-Location $repo
    foreach ($build in $phase4a.builds) {
        & $cmake --build --preset $build --target alignment_benchmark
        if ($LASTEXITCODE -ne 0) { throw "Build failed for $build." }
        & $ctest --preset $build
        if ($LASTEXITCODE -ne 0) { throw "Correctness tests failed for $build." }
        $runnerPaths[$build] = Join-Path $repo "build-$build\alignment_benchmark.exe"
    }

    $conditionIndex = @{}
    foreach ($condition in $phase4a.conditions) { $conditionIndex[$condition.name] = $condition }
    $batching = $phase4a.batching
    foreach ($row in $selection) {
        $datatype = $row.datatype
        $elementBytes = if ($datatype -eq 'float32') { 4 } else { 8 }
        $kernel = $row.kernel
        $arrayCount = if ($kernel -eq 'axpy') { 2 } else { 3 }
        $workingSet = [int64]$row.target_working_set_bytes
        $n = [Math]::Max(1, [int][Math]::Floor([double]$workingSet / ($elementBytes * $arrayCount)))
        $condition = $conditionIndex[$row.alignment_condition]
        $offsetKey = if ($datatype -eq 'float32') { 'offset_float32_elements' } else { 'offset_float64_elements' }
        $offset = [int]$condition.$offsetKey
        $verifyArgs = @(
            '--kernel', $kernel,
            '--datatype', $datatype,
            '--build', $row.build,
            '--compiler', "$compilerVersion",
            '--flags', $variantFlags[$row.build],
            '--alignment-condition', $row.alignment_condition,
            '--offset-elements', "$offset",
            '--n', "$n",
            '--target-working-set-bytes', "$workingSet",
            '--warmups', '0',
            '--repetitions', '0',
            '--batch', '1',
            '--verify-only', 'true',
            '--output', $rerunRaw
        )
        & $runnerPaths[$row.build] @verifyArgs
        if ($LASTEXITCODE -ne 0) {
            throw "Targeted rerun preflight failed: $kernel $datatype $($row.build) $($row.alignment_condition) $workingSet"
        }
    }

    foreach ($row in $selection) {
        $datatype = $row.datatype
        $elementBytes = if ($datatype -eq 'float32') { 4 } else { 8 }
        $kernel = $row.kernel
        $arrayCount = if ($kernel -eq 'axpy') { 2 } else { 3 }
        $workingSet = [int64]$row.target_working_set_bytes
        $n = [Math]::Max(1, [int][Math]::Floor([double]$workingSet / ($elementBytes * $arrayCount)))
        $condition = $conditionIndex[$row.alignment_condition]
        $offsetKey = if ($datatype -eq 'float32') { 'offset_float32_elements' } else { 'offset_float64_elements' }
        $offset = [int]$condition.$offsetKey
        if ($n -le [int]$batching.n_at_most) {
            $batch = [int]$batching.batch_count
        } elseif ($n -le [int]$batching.n_at_most_next) {
            $batch = [int]$batching.batch_count_next
        } else {
            $batch = 1
        }
        $arguments = @(
            '--kernel', $kernel,
            '--datatype', $datatype,
            '--build', $row.build,
            '--compiler', "$compilerVersion",
            '--flags', $variantFlags[$row.build],
            '--alignment-condition', $row.alignment_condition,
            '--offset-elements', "$offset",
            '--n', "$n",
            '--target-working-set-bytes', "$workingSet",
            '--warmups', "$($phase4a.warmups)",
            '--repetitions', "$additionalRepetitions",
            '--batch', "$batch",
            '--output', $rerunRaw
        )
        & $runnerPaths[$row.build] @arguments
        if ($LASTEXITCODE -ne 0) {
            throw "Targeted rerun failed: $kernel $datatype $($row.build) $($row.alignment_condition) $workingSet"
        }
    }
} finally {
    if ((Get-Location).Path -eq $repo) { Pop-Location }
    $env:Path = $oldPath
}

& python (Join-Path $repo 'scripts\analyze_phase4a.py') `
    --raw $initialRaw `
    --expected-repetitions $initialRepetitions `
    --rerun $rerunRaw `
    --rerun-repetitions $additionalRepetitions
if ($LASTEXITCODE -ne 0) { throw 'Merged Phase 4A analysis failed.' }