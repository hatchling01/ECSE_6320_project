# Pre-test Environment Snapshot

Captured 2026-10-23 before the smoke validation. Values are directly reported by Windows/tool queries unless marked unavailable. No setting was changed.

## Host

- System: ASUS System Product Name.
- OS: Microsoft Windows 11 Enterprise, version/build 10.0.26200 / 26200, 64-bit.
- CPU: AMD Ryzen 9 9950X 16-Core Processor; 16 physical cores, 32 logical processors; reported maximum 4300 MHz.
- RAM: 66,199,183,360 bytes (61.65 GiB) installed; Windows reported 64,647,640 KiB visible.
- Hypervisor present: yes.
- Virtualization-based security status: 2 (running); configured services `{2}`, running services `{1,2}` as reported by `Win32_DeviceGuard`.
- Active power plan: Balanced (`381b4222-f694-41f0-9685-ff5bb260df2e`). It was observed, not changed.

## Storage

- SSD: KXG80ZNV1T02 REV2 KIOXIA.
- Firmware: APGA4102.
- Media/bus: SSD / NVMe.
- Physical capacity: 1,024,209,543,168 bytes (approximately 1.024 TB / 953.87 GiB).
- Disk 0: GPT, online, boot and system disk.
- `C:`: NTFS, 1,023,154,319,360 bytes total; 602,981,761,024 bytes free (approximately 602.98 GB / 561.57 GiB at capture).
- Health: Healthy / OK.
- Detailed reliability counters/temperature/wear: unavailable; the Windows storage provider returned access unavailable/denied.
- NVMe controller driver: Microsoft Standard NVM Express Controller, `stornvme.inf`, version 10.0.26100.9549.

## Toolchain

| Component | Version | Path/evidence |
|---|---:|---|
| FIO | 3.43 | `C:\Program Files\fio\fio.exe` |
| FIO engine | windowsaio | Listed by the installed build |
| Conda | 25.11.0 | `C:\Users\CHOUDN3\AppData\Local\anaconda3\Scripts\conda.exe` |
| Python | 3.13.9 | `C:\Users\CHOUDN3\AppData\Local\anaconda3\python.exe` |
| pip | 25.3 | Existing Anaconda base environment |
| numpy | 2.3.5 | Import verified |
| pandas | 2.3.3 | Import verified |
| matplotlib | 3.10.6 | Import verified |
| PowerShell | 5.1.26100.9711 | Windows PowerShell Desktop |
| Git | 2.54.0.windows.1 | `C:\Program Files\Git\cmd\git.exe` |

## Minimal toolchain validation

The corrected Phase 1 smoke check validated the regular-file workflow, FIO 3.43 `windowsaio`, `direct=1`, QD=1 configuration, JSON percentile fields, and the Python parser. This smoke output is not a performance measurement; see `smoke_validation.md`.

