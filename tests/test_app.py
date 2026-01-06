from __future__ import annotations

import os
from pathlib import Path

import pytest
from botocore.exceptions import ClientError


def test_check_file_identifies_existing_files(app_and_s3, tmp_path: Path):
    app, _ = app_and_s3
    f = tmp_path / "exists.txt"
    f.write_text("hello", encoding="utf-8")

    assert app.CHECK_FILE(str(f)) is True


def test_check_file_identifies_missing_files(app_and_s3, tmp_path: Path):
    app, _ = app_and_s3
    missing = tmp_path / "missing.txt"

    assert app.CHECK_FILE(str(missing)) is False


def test_download_file_success(app_and_s3, tmp_path: Path):
    app, fake_s3 = app_and_s3
    fake_s3.content = b"downloaded-content"

    out_path = tmp_path / "file.bin"
    ok = app.DOWNLOAD_FILE("path/in/s3/object.bin", str(out_path))

    assert ok is True
    assert out_path.is_file()
    assert out_path.read_bytes() == b"downloaded-content"
    # Verify S3 call included the expected bucket and key
    assert fake_s3.calls[-1] == (app.S3_BUCKET_BASE, "path/in/s3/object.bin")


def test_download_file_cleans_up_partial_on_error(app_and_s3, tmp_path: Path):
    app, fake_s3 = app_and_s3
    fake_s3.content = b"partial-data"
    fake_s3.raise_error = True
    fake_s3.error_after_bytes = 3  # simulate a partial write then error

    out_path = tmp_path / "partial.bin"

    with pytest.raises(ClientError):
        app.DOWNLOAD_FILE("broken/object.bin", str(out_path))

    # File should have been removed by DOWNLOAD_FILE's error handler
    assert not out_path.exists()


def test_download_tile_generates_correct_paths(app_and_s3, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    app, _ = app_and_s3

    # Capture arguments passed to DOWNLOAD_FILE without performing any I/O
    captured: list[tuple[str, str]] = []

    def stub_download(object_name: str, file_name: str) -> bool:  # noqa: ANN001 - match target signature
        captured.append((object_name, file_name))
        return True

    monkeypatch.setattr(app, "DOWNLOAD_FILE", stub_download, raising=True)

    northing = "N47_00"
    easting = "E009_00"

    # Expected paths based on app.py logic
    expected_base = f"{app.BASE_DIR_1}_{northing}_{easting}_{app.BASE_DIR_2}"
    expected_s3 = f"{expected_base}/{expected_base}.tif"
    expected_local = os.path.join(app.TIF_LOCATION, f"{northing}_{easting}.tif")

    ok = app.DOWNLOAD_TILE(northing, easting)

    assert ok is True
    assert captured, "DOWNLOAD_FILE was not called"
    assert captured[0] == (expected_s3, expected_local)
