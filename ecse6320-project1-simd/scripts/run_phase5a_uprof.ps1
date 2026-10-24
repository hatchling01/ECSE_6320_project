param(
    [string]$OnlyCase
)

$ErrorActionPreference = 'Stop'
$repo = if ($PSScriptRoot) { Split-Path -Parent $PSScriptRoot } else { (Get-Location).Path }
$cmake = 'C:\Users\CHOUDN3\AppData\Local\Microsoft\WinGet\Packages\Kitware.CMake_Microsoft.Winget.Source_8wekyb3d8bbwe\cmake-4.4.4-windows-x86_64\bin\cmake.exe'
$uprof = 'C:\Program Files\AMD\AMDuProf\bin\AMDuProfCLI.exe'
$config = Get-Content (Join-Path $repo 'config\experiment_config.json') -Raw | ConvertFrom-Json
$experiment = $config.phase5a_uprof
$phaseRoot = Join-Path $repo $experiment.raw_directory
$manifestPath = Join-Path $phaseRoot 'command_manifest.csv'
$correctnessPath = Join-Path $phaseRoot 'correctness_preflight.csv'
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
$simdEvents = @{
    'gcc-scalar' = 'SCALAR_UOPS_RETIRED'
    'gcc-auto' = 'PACK_128_UOPS_RETIRED'
    'gcc-native' = 'PACK_512_UOPS_RETIRED'
}
$l1Event = 'L1_DC_ACCESSES_ALL'
$l2Event = 'L2_CACHE_ACCESS_FROM_L1_DC_MISS'
$tlbEvent = 'L1_DTLB_MISSES'
$runnerPaths = @{}
$profiles = [System.Collections.Generic.List[object]]::new()

foreach ($size in $experiment.profile_sizes) {
    foreach ($build in $experiment.builds) {
        $caseName = "$($size.name)_$build"
        if ($OnlyCase -and $OnlyCase -ne $caseName) { continue }
        $profiles.Add([pscustomobject]@{
            case_name = $caseName
            size_name = $size.name
            target_working_set_bytes = [int64]$size.target_working_set_bytes
            n = [int]$size.n
            batch = [int]$size.batch
            repetitions = [int]$size.profile_repetitions
            build = $build
        })
    }
}
if ($OnlyCase -and $profiles.Count -ne 1) {
    throw "Unknown Phase 5A case '$OnlyCase'. Valid values use <size_name>_<build>."
}

New-Item -ItemType Directory -Path $phaseRoot -Force | Out-Null
$allCases = $experiment.profile_sizes.Count * $experiment.builds.Count
if ($allCases -ne [int]$experiment.maximum_profile_runs) {
    throw "Configured Phase 5A matrix has $allCases cases, cap is $($experiment.maximum_profile_runs)."
}
Write-Output "Phase 5A planned profiles: $allCases maximum; this invocation selects $($profiles.Count)."
Write-Output "Counter bundle: cpi (cycles/instructions) + build SIMD uops + L1 accesses + L2 requests + L1 DTLB misses = 6 core PMCs."

try {
    Push-Location $repo
    foreach ($build in $experiment.builds) {
        & $cmake --build --preset $build --target benchmark_runner
        if ($LASTEXITCODE -ne 0) { throw "benchmark_runner build failed for $build." }
        $runnerPaths[$build] = Join-Path $repo "build-$build\benchmark_runner.exe"
    }

    $verificationRows = [System.Collections.Generic.List[object]]::new()
    foreach ($size in $experiment.profile_sizes) {
        foreach ($build in $experiment.builds) {
            $runner = Join-Path $repo "build-$build\benchmark_runner.exe"
            $verifyArgs = @(
                '--kernel', $experiment.kernel,
                '--datatype', $experiment.datatype,
                '--build', $build,
                '--compiler', "$compilerVersion",
                '--flags', $variantFlags[$build],
                '--n', "$($size.n)",
                '--target-working-set-bytes', "$($size.target_working_set_bytes)",
                '--warmups', '0',
                '--repetitions', '0',
                '--batch', '1',
                '--verify-only'
            )
            $verifyOutput = & $runner @verifyArgs
            if ($LASTEXITCODE -ne 0) { throw "Correctness preflight failed: $build $($size.name) N=$($size.n)." }
            $verifyText = $verifyOutput -join ' '
            if ($verifyText -notmatch 'status=PASS') { throw "Missing PASS in verification output: $verifyText" }
            $verificationRows.Add([pscustomobject]@{
                kernel = $experiment.kernel
                datatype = $experiment.datatype
                build = $build
                size_name = $size.name
                working_set_bytes = $size.target_working_set_bytes
                N = $size.n
                status = 'PASS'
                verification_output = $verifyText
            })
        }
    }
    $verificationRows | Export-Csv -Path $correctnessPath -NoTypeInformation -Encoding UTF8
    Write-Output "Correctness preflight passed: $($verificationRows.Count) configurations."

    $manifest = @()
    if (Test-Path $manifestPath) {
        $manifest = @(Import-Csv $manifestPath)
    }
    $completedCount = @($manifest | Where-Object collection_status -eq 'complete').Count
    foreach ($profileCase in $profiles) {
        $existing = @($manifest | Where-Object case_name -eq $profileCase.case_name)
        $existingSuccess = @($existing | Where-Object collection_status -eq 'complete')
        if ($existingSuccess.Count -gt 0) {
            Write-Output "Skipping already completed profile $($profileCase.case_name)."
            continue
        }
        $caseRoot = Join-Path $phaseRoot $profileCase.case_name
        $attemptNumber = $existing.Count + 1
        $caseDirectory = Join-Path $caseRoot ("attempt_{0:D2}" -f $attemptNumber)
        $completeMarker = Join-Path $caseDirectory 'phase5a_complete.txt'
        New-Item -ItemType Directory -Path $caseDirectory -Force | Out-Null
        $runner = $runnerPaths[$profileCase.build]
        $timingCsv = Join-Path $caseDirectory 'profiler_instrumented_timing.csv'
        $consoleLog = Join-Path $caseDirectory 'uprof_console.log'
        $reportCsv = Join-Path $caseDirectory 'uprof_report.csv'
        $eventArgs = @(
            '--event', "event=CYCLES_NOT_IN_HALT,interval=$($experiment.sampling_interval)",
            '--event', "event=RETIRED_INST,interval=$($experiment.sampling_interval)",
            '--event', "event=$($simdEvents[$profileCase.build]),interval=$($experiment.sampling_interval)",
            '--event', "event=$l1Event,interval=$($experiment.sampling_interval)",
            '--event', "event=$l2Event,interval=$($experiment.sampling_interval)",
            '--event', "event=$tlbEvent,interval=$($experiment.sampling_interval)"
        )
        $runnerArgs = @(
            '--kernel', $experiment.kernel,
            '--datatype', $experiment.datatype,
            '--build', $profileCase.build,
            '--compiler', 'GCC16.2.0',
            '--flags', $profileCase.build,
            '--n', "$($profileCase.n)",
            '--target-working-set-bytes', "$($profileCase.target_working_set_bytes)",
            '--warmups', '3',
            '--repetitions', "$($profileCase.repetitions)",
            '--batch', "$($profileCase.batch)",
            '--output', $timingCsv
        )
        $profileArgs = @(
            'profile'
        ) + $eventArgs + @(
            '--affinity', "$($experiment.cpu_affinity)",
            '--output-dir', $caseDirectory,
            '--show-event-count',
            '--stdout',
            '--report-output', $reportCsv,
            '--working-dir', $repo,
            $runner
        ) + $runnerArgs
        $commandLine = '"' + $uprof + '" ' + ($profileArgs -join ' ')
        Write-Output "Profiling $($profileCase.case_name) (completed case $($completedCount + 1)/$allCases)."
        $previousErrorActionPreference = $ErrorActionPreference
        $ErrorActionPreference = 'Continue'
        & $uprof @profileArgs *> $consoleLog
        $uprofExitCode = $LASTEXITCODE
        $ErrorActionPreference = $previousErrorActionPreference
        if ($uprofExitCode -ne 0) {
            throw "uProf profile failed for $($profileCase.case_name); inspect $consoleLog."
        }
        $rawProfileFiles = @(Get-ChildItem $caseDirectory -Recurse -File |
            Where-Object { $_.Extension -in @('.db', '.uprof') })
        $timingExists = Test-Path $timingCsv
        $reportExists = Test-Path $reportCsv
        $collectionStatus = if ($rawProfileFiles.Count -gt 0 -and $reportExists -and $timingExists) {
            'complete'
        } else {
            'incomplete_missing_raw_report_or_harness_csv'
        }
        if ($collectionStatus -eq 'complete') {
            Set-Content -Path $completeMarker -Value "completed $(Get-Date -Format o)" -Encoding UTF8
        }
        $row = [pscustomobject]@{
            attempt = $attemptNumber
            case_name = $profileCase.case_name
            kernel = $experiment.kernel
            datatype = $experiment.datatype
            build = $profileCase.build
            compiler = $compilerVersion
            compiler_flags = $variantFlags[$profileCase.build]
            uprof_version = '5.3.521.0'
            uprof_config = $experiment.uProf_config
            simd_event = $simdEvents[$profileCase.build]
            additional_events = "$l1Event;$l2Event;$tlbEvent"
            sampling_interval = $experiment.sampling_interval
            affinity_cpu = $experiment.cpu_affinity
            size_name = $profileCase.size_name
            target_working_set_bytes = $profileCase.target_working_set_bytes
            N = $profileCase.n
            batching_count = $profileCase.batch
            profiler_repetitions = $profileCase.repetitions
            correctness = 'PASS'
            command_line = $commandLine
            output_directory = $caseDirectory
            report_csv = $reportCsv
            console_log = $consoleLog
            collection_status = $collectionStatus
        }
        $manifest += $row
        $manifest | Export-Csv -Path $manifestPath -NoTypeInformation -Encoding UTF8
        if ($collectionStatus -ne 'complete') {
            throw "Profile did not produce all required outputs for $($profileCase.case_name); attempt preserved at $caseDirectory."
        }
        $completedCount++
    }
} finally {
    if ((Get-Location).Path -eq $repo) { Pop-Location }
    $env:Path = $oldPath
}
Write-Output "Phase 5A uProf run manifest: $manifestPath"
