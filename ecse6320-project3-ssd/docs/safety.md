# SSD Safety and Target Policy

The sole installed KIOXIA NVMe device is the Windows boot/system disk. Every raw disk, partition, volume, drive root, EFI/recovery target, and `C:` itself is **DO NOT BENCHMARK DIRECTLY**.

FIO may receive only a canonical regular-file path strictly below:

`ecse6320-project3-ssd\benchmark_data\`

The active Python validator rejects empty paths, roots, drive-only syntax, Windows device/volume syntax, `PhysicalDrive`/`HarddiskVolume` names, the benchmark directory itself, directories, and any path escaping the benchmark directory. Nonexistent candidates are accepted only when explicitly requested for safe file creation and their canonical destination remains inside the directory. PowerShell implementations remain reference-only because `.ps1` execution is restricted on this host.

The smoke wrapper validates first, prints `SAFE REGULAR-FILE TARGET VERIFIED`, logs all safety-critical parameters, creates only a tiny file through FIO, and deletes only that validated file after successful parsing. Raw JSON and logs are retained; the disposable payload is never committed.

Primary future tests use `windowsaio` and `direct=1`. The only planned buffered I/O is a separately authorized and labeled safe pitfall experiment. No disk/system settings are changed for this project.

