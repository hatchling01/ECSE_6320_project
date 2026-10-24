param(
    [switch]$Reruns
)

$ErrorActionPreference = 'Stop'
$repo = if ($PSScriptRoot) { Split-Path -Parent $PSScriptRoot } else { (Get-Location).Path }
$cmake = 'C:\Users\CHOUDN3\AppData\Local\Microsoft\WinGet\Packages\Kitware.CMake_Microsoft.Winget.Source_8wekyb3d8bbwe\cmake-4.4.4-windows-x86_64\bin\cmake.exe'
$ctest = 'C:\Users\CHOUDN3\AppData\Local\Microsoft\WinGet\Packages\Kitware.CMake_Microsoft.Winget.Source_8wekyb3d8bbwe\cmake-4.4.4-windows-x86_64\bin\ctest.exe'
$config = Get-Content (Join-Path $repo 'config\experiment_config.json') -Raw | ConvertFrom-Json
$experiment = $config.phase4c_stride
$initialRaw = Join-Path $repo (Join-Path 'data\raw' $experiment.raw_file)
$initialCorrectness = Join-Path $repo 'data\processed\phase4c_stride_correctness.csv'
$selectionPath = Join-Path $repo 'data\metadata\phase4c_stride_rerun_selection.csv'
$rerunRaw = Join-Path $repo (Join-Path 'data\raw' $experiment.targeted_rerun_file)
$rerunCorrectness = Join-Path $repo 'data\processed\phase4c_stride_rerun_correctness.csv'

if ($Reruns) {
    if (-not (Test-Path $initialRaw) -or -not (Test-Path $initialCorrectness) -or -not (Test-Path $selectionPath)) {
        throw 'Run the initial Phase 4C stride matrix and analysis before targeted reruns.'
    }
    if ((Test-Path $rerunRaw) -or (Test-Path $rerunCorrectness)) {
        throw 'Refusing to overwrite existing Phase 4C targeted rerun files.'
    }
    $selection = @(Import-Csv $selectionPath | Where-Object { $_.build -and $_.selection_reason -eq 'initial_cv_gt_20_percent' })
    if ($selection.Count -eq 0) {
        Write-Output 'No initial Phase 4C configuration exceeded 20% CV; no rerun was needed.'
        return
    }
    $tests = [System.Collections.Generic.List[object]]::new()
    foreach ($row in $selection) {
        $tests.Add([pscustomobject]@{
            build = $row.build
            span_name = $row.span_name
            span_elements = [int]$row.span_elements
            allocated_total_bytes = [int64]$row.allocated_total_bytes
            stride = [int]$row.stride
            useful_n = [int]$row.useful_n
        })
    }
    $rawOutput = $rerunRaw
    $correctnessOutput = $rerunCorrectness
    $repetitions = [int]$experiment.rerun_repetitions
    if ($selection.Count * $repetitions -gt 180) {
        throw 'Targeted rerun sample count exceeds the 36-configuration matrix cap.'
    }
    Write-Output "Targeted rerun plan: $($selection.Count) initially unstable configurations x $repetitions samples."
} else {
    if (Test-Path $initialRaw) { throw "Refusing to overwrite initial raw data: $initialRaw" }
    if (Test-Path $initialCorrectness) { throw "Refusing to overwrite correctness manifest: $initialCorrectness" }
    $configurationCount = $experiment.spans.Count * $experiment.strides.Count * $experiment.builds.Count
    $repetitions = [int]$experiment.initial_repetitions
    $plannedSamples = $configurationCount * $repetitions
    if ($configurationCount -ne 36 -or $plannedSamples -ne 180) {
        throw "Configured Phase 4C matrix is unexpected: $configurationCount configurations, $plannedSamples samples."
    }
    Write-Output "Phase 4C plan: 3 fixed spans x 4 strides x 3 GCC builds = $configurationCount configurations; $plannedSamples initial timed samples."
    $tests = [System.Collections.Generic.List[object]]::new()
    $spanIndex = 0
    foreach ($span in $experiment.spans) {
        $strideIndex = 0
        foreach ($stride in $experiment.strides) {
            $buildStart = ($spanIndex + $strideIndex) % $experiment.builds.Count
            for ($buildStep = 0; $buildStep -lt $experiment.builds.Count; $buildStep++) {
                $buildIndex = ($buildStart + $buildStep) % $experiment.builds.Count
                $usefulN = [int]([int]$span.span_elements / [int]$stride)
                $tests.Add([pscustomobject]@{
                    build = $experiment.builds[$buildIndex]
                    span_name = $span.name
                    span_elements = [int]$span.span_elements
                    allocated_total_bytes = [int64]$span.allocated_total_bytes
                    stride = [int]$stride
                    useful_n = $usefulN
                })
            }
            $strideIndex++
        }
        $spanIndex++
    }
    $rawOutput = $initialRaw
    $correctnessOutput = $initialCorrectness
}

if ($Reruns -and ([int]$experiment.initial_repetitions + $repetitions -gt [int]$experiment.maximum_repetitions)) {
    throw 'Phase 4C reruns would exceed 10 observations/configuration.'
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

try {
    Push-Location $repo
    foreach ($build in $experiment.builds) {
        & $cmake --build --preset $build --target benchmark_runner
        if ($LASTEXITCODE -ne 0) { throw "Build failed for $build." }
        & $ctest --preset $build
        if ($LASTEXITCODE -ne 0) { throw "Correctness suite failed for $build." }
        $runnerPaths[$build] = Join-Path $repo "build-$build\benchmark_runner.exe"
    }

    $verificationRows = [System.Collections.Generic.List[object]]::new()
    foreach ($test in $tests) {
        $verifyArgs = @(
            '--kernel', $experiment.kernel,
            '--datatype', $experiment.datatype,
            '--build', $test.build,
            '--compiler', "$compilerVersion",
            '--flags', $variantFlags[$test.build],
            '--n', "$($test.useful_n)",
            '--span-elements', "$($test.span_elements)",
            '--stride', "$($test.stride)",
            '--target-working-set-bytes', "$($test.allocated_total_bytes)",
            '--warmups', '0',
            '--repetitions', '0',
            '--batch', '1',
            '--verify-only'
        )
        $verifyOutput = & $runnerPaths[$test.build] @verifyArgs
        if ($LASTEXITCODE -ne 0) {
            throw "Correctness preflight failed: $($test.build) $($test.span_name) stride=$($test.stride) N=$($test.useful_n)"
        }
        $verifyText = $verifyOutput -join ' '
        if ($verifyText -notmatch 'status=PASS') { throw "Missing PASS in verification output: $verifyText" }
        $absoluteMatch = [regex]::Match($verifyText, 'max_abs=([^ ]+)')
        $relativeMatch = [regex]::Match($verifyText, 'max_rel=([^ ]+)')
        $verificationRows.Add([pscustomobject]@{
            kernel = $experiment.kernel
            datatype = $experiment.datatype
            build = $test.build
            span_name = $test.span_name
            span_elements = $test.span_elements
            allocated_total_bytes = $test.allocated_total_bytes
            stride = $test.stride
            N = $test.useful_n
            max_absolute_error = $absoluteMatch.Groups[1].Value
            max_relative_error = $relativeMatch.Groups[1].Value
            status = 'PASS'
        })
    }
    $correctnessParent = Split-Path -Parent $correctnessOutput
    New-Item -ItemType Directory -Path $correctnessParent -Force | Out-Null
    $verificationRows | Export-Csv -Path $correctnessOutput -NoTypeInformation -Encoding UTF8
    Write-Output "Correctness preflight passed: $($verificationRows.Count) configurations."

    $batching = $experiment.batching
    foreach ($test in $tests) {
        if ($test.useful_n -le [int]$batching.n_at_most) {
            $batch = [int]$batching.batch_count
        } elseif ($test.useful_n -le [int]$batching.n_at_most_next) {
            $batch = [int]$batching.batch_count_next
        } else {
            $batch = 1
        }
        $arguments = @(
            '--kernel', $experiment.kernel,
            '--datatype', $experiment.datatype,
            '--build', $test.build,
            '--compiler', "$compilerVersion",
            '--flags', $variantFlags[$test.build],
            '--n', "$($test.useful_n)",
            '--span-elements', "$($test.span_elements)",
            '--stride', "$($test.stride)",
            '--target-working-set-bytes', "$($test.allocated_total_bytes)",
            '--warmups', "$($experiment.warmups)",
            '--repetitions', "$repetitions",
            '--batch', "$batch",
            '--output', $rawOutput
        )
        & $runnerPaths[$test.build] @arguments
        if ($LASTEXITCODE -ne 0) {
            throw "Measurement failed: $($test.build) $($test.span_name) stride=$($test.stride) N=$($test.useful_n)"
        }
    }
} finally {
    if ((Get-Location).Path -eq $repo) { Pop-Location }
    $env:Path = $oldPath
}

if ($Reruns) {
    & python (Join-Path $repo 'scripts\analyze_phase4c_stride.py') `
        --raw $initialRaw `
        --correctness $initialCorrectness `
        --expected-repetitions $($experiment.initial_repetitions) `
        --rerun $rerunRaw `
        --rerun-correctness $rerunCorrectness `
        --rerun-repetitions $repetitions
} else {
    & python (Join-Path $repo 'scripts\analyze_phase4c_stride.py') `
        --raw $initialRaw `
        --correctness $initialCorrectness `
        --expected-repetitions $repetitions
}
if ($LASTEXITCODE -ne 0) { throw 'Phase 4C stride analysis failed.' }
