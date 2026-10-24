"""Harmless unit tests for the active Python FIO target validator."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from safe_target import UnsafeTargetError, repository_root, validate_fio_target


class SafeTargetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.repo = repository_root()
        cls.benchmark_root = cls.repo / "benchmark_data"

    def assert_rejected(self, candidate: str | Path | None) -> None:
        with self.assertRaises(UnsafeTargetError, msg=f"incorrectly accepted {candidate!r}"):
            validate_fio_target(candidate, self.repo, allow_nonexistent=True)

    def test_rejects_empty(self) -> None:
        self.assert_rejected("")
        self.assert_rejected("   ")
        self.assert_rejected(None)

    def test_rejects_drive_and_filesystem_roots(self) -> None:
        self.assert_rejected("C:")
        self.assert_rejected("C:\\")
        self.assert_rejected(Path(self.repo.anchor))

    def test_rejects_devices_and_volumes(self) -> None:
        self.assert_rejected(r"\\.\PhysicalDrive0")
        self.assert_rejected("\\\\?\\Volume{00000000-0000-0000-0000-000000000000}\\")
        self.assert_rejected(r"\Device\HarddiskVolume1")

    def test_rejects_alternate_data_stream_leaf(self) -> None:
        self.assert_rejected(self.benchmark_root / "file.bin:stream")

    def test_rejects_outside_repository_and_repo_root(self) -> None:
        self.assert_rejected(self.repo.parent / "outside.bin")
        self.assert_rejected(self.repo)
        with tempfile.TemporaryDirectory() as temporary:
            self.assert_rejected(Path(temporary) / "outside.bin")

    def test_rejects_benchmark_directory_itself(self) -> None:
        self.assert_rejected(self.benchmark_root)

    def test_accepts_intended_regular_file_path(self) -> None:
        expected = (self.benchmark_root / "fio_smoke_test.bin").resolve()
        actual = validate_fio_target(expected, self.repo, allow_nonexistent=True)
        self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main(verbosity=2)

