param(
    [ValidateRange(1, 10)]
    [int]$Repetitions = 5
)

$ErrorActionPreference = 'Stop'
$repo = if ($PSScriptRoot) { Split-Path -Parent $PSScriptRoot } else { (Get-Location).Path }
$cmake = 'C:\Users\CHOUDN3\AppData\Local\Microsoft\WinGet\Packages\Kitware.CMake_Microsoft.Winget.Source_8wekyb3d8bbwe\cmake-4.4.4-windows-x86_64\bin\cmake.exe'
$ctest = 'C:\Users\CHOUDN3\AppData\Local\Microsoft\WinGet\Packages\Kitware.CMake_Microsoft.Winget.Source_8wekyb3d8bbwe\cmake-4.4.4-windows-x86_64\bin\ctest.exe'
$config = Get-Content (Join-Path $repo 'config\experiment_config.json') -Raw | ConvertFrom-Json
$phase4a = $config.phase4a_alignment
$output = Join-Path $repo (Join-Path 'data\raw' $phase4a.raw_file)

if ($Repetitions -gt [int]$phase4a.maximum_repetitions) {
    throw "Phase 4A repetitions cannot exceed $($phase4a.maximum_repetitions)."
}
if (Test-Path $output) {
    throw "Refusing to overwrite raw measurements: $output"
}

$kernels = @($phase4a.kernels)
$datatypes = @($phase4a.datatypes)
$builds = @($phase4a.builds)
$workingSets = @($phase4a.target_working_set_sizes_bytes)
$conditions = @($phase4a.conditions)
$configurationCount = $kernels.Count * $datatypes.Count * $builds.Count * $workingSets.Count * $conditions.Count
$plannedSamples = $configurationCount * $Repetitions
Write-Output "Phase 4A plan: $($kernels.Count) kernels x $($datatypes.Count) datatypes x $($builds.Count) GCC builds x $($workingSets.Count) Phase 3 sizes x $($conditions.Count) alignments = $configurationCount configurations."
Write-Output "Planned timed samples: $configurationCount x $Repetitions repetitions = $plannedSamples (maximum repetitions: $($phase4a.maximum_repetitions))."

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
    foreach ($build in $builds) {
        & $cmake --build --preset $build --target alignment_benchmark
        if ($LASTEXITCODE -ne 0) { throw "Build failed for $build." }
        & $ctest --preset $build
        if ($LASTEXITCODE -ne 0) { throw "Correctness tests failed for $build." }
        $runnerPaths[$build] = Join-Path $repo "build-$build\alignment_benchmark.exe"
    }

    $batching = $phase4a.batching
    $warmups = [int]$phase4a.warmups
    $kernelIndex = 0
    foreach ($kernel in $kernels) {
        $datatypeIndex = 0
        foreach ($datatype in $datatypes) {
            $elementBytes = if ($datatype -eq 'float32') { 4 } else { 8 }
            $arrayCount = if ($kernel -eq 'axpy') { 2 } else { 3 }
            $sizeIndex = 0
            foreach ($workingSet in $workingSets) {
                $n = [Math]::Max(1, [int][Math]::Floor([double]$workingSet / ($elementBytes * $arrayCount)))
                foreach ($condition in $conditions) {
                    $offsetKey = if ($datatype -eq 'float32') { 'offset_float32_elements' } else { 'offset_float64_elements' }
                    $offset = [int]$condition.$offsetKey
                    foreach ($build in $builds) {
                        $runner = $runnerPaths[$build]
                        $verifyArgs = @(
                            '--kernel', $kernel,
                            '--datatype', $datatype,
                            '--build', $build,
                            '--compiler', "$compilerVersion",
                            '--flags', $variantFlags[$build],
                            '--alignment-condition', $condition.name,
                            '--offset-elements', "$offset",
                            '--n', "$n",
                            '--target-working-set-bytes', "$workingSet",
                            '--warmups', '0',
                            '--repetitions', '0',
                            '--batch', '1',
                            '--verify-only', 'true',
                            '--output', $output
                        )
                        & $runner @verifyArgs
                        if ($LASTEXITCODE -ne 0) {
                            throw "Preflight correctness/alignment failed: $kernel $datatype $build $condition $workingSet"
                        }
                    }
                }
                $sizeIndex++
            }
            $datatypeIndex++
        }
        $kernelIndex++
    }

    $createdOutput = $false
    $kernelIndex = 0
    foreach ($kernel in $kernels) {
        $datatypeIndex = 0
        foreach ($datatype in $datatypes) {
            $elementBytes = if ($datatype -eq 'float32') { 4 } else { 8 }
            $arrayCount = if ($kernel -eq 'axpy') { 2 } else { 3 }
            $sizeIndex = 0
            foreach ($workingSet in $workingSets) {
                $n = [Math]::Max(1, [int][Math]::Floor([double]$workingSet / ($elementBytes * $arrayCount)))
                if ($n -le [int]$batching.n_at_most) {
                    $batch = [int]$batching.batch_count
                } elseif ($n -le [int]$batching.n_at_most_next) {
                    $batch = [int]$batching.batch_count_next
                } else {
                    $batch = 1
                }
                $conditionIndex = 0
                foreach ($condition in $conditions) {
                    $offsetKey = if ($datatype -eq 'float32') { 'offset_float32_elements' } else { 'offset_float64_elements' }
                    $offset = [int]$condition.$offsetKey
                    $buildStart = ($kernelIndex + $datatypeIndex + $sizeIndex + $conditionIndex) % $builds.Count
                    for ($buildStep = 0; $buildStep -lt $builds.Count; $buildStep++) {
                        $buildIndex = ($buildStart + $buildStep) % $builds.Count
                        $build = $builds[$buildIndex]
                        $arguments = @(
                            '--kernel', $kernel,
                            '--datatype', $datatype,
                            '--build', $build,
                            '--compiler', "$compilerVersion",
                            '--flags', $variantFlags[$build],
                            '--alignment-condition', $condition.name,
                            '--offset-elements', "$offset",
                            '--n', "$n",
                            '--target-working-set-bytes', "$workingSet",
                            '--warmups', "$warmups",
                            '--repetitions', "$Repetitions",
                            '--batch', "$batch",
                            '--output', $output
                        )
                        & $runnerPaths[$build] @arguments
                        if ($LASTEXITCODE -ne 0) {
                            throw "Measurement failed: $kernel $datatype $build $condition $workingSet"
                        }
                        $createdOutput = $true
                    }
                    $conditionIndex++
                }
                $sizeIndex++
            }
            $datatypeIndex++
        }
        $kernelIndex++
    }
    if (-not $createdOutput) { throw 'No Phase 4A samples were written.' }
} finally {
    if ((Get-Location).Path -eq $repo) { Pop-Location }
    $env:Path = $oldPath
}

& python (Join-Path $repo 'scripts\analyze_phase4a.py') --raw $output --expected-repetitions $Repetitions
if ($LASTEXITCODE -ne 0) { throw 'Phase 4A analysis failed.' }