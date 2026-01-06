from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import boto3
import pytest


class FakeS3:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []
        self.content: bytes = b"OK"  # default content to write on success
        self.raise_error: bool = False
        self.error_after_bytes: int | None = None  # if set and raise_error True, write partial then raise

    def download_fileobj(self, bucket: str, key: str, fileobj) -> None:  # noqa: ANN001 - file-like object
        self.calls.append((bucket, key))
        if self.raise_error:
            if self.error_after_bytes:
                fileobj.write(self.content[: self.error_after_bytes])
                fileobj.flush()
            # Raise a real ClientError like botocore would
            from botocore.exceptions import ClientError

            raise ClientError({"Error": {"Code": "500", "Message": "Simulated failure"}}, "Download")
        fileobj.write(self.content)
        fileobj.flush()


@pytest.fixture()
def fake_s3() -> FakeS3:
    return FakeS3()


@pytest.fixture()
def app_and_s3(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, fake_s3: FakeS3):
    """
    Load the target module under test with side-effects neutralized:
    - Work inside a temporary directory so relative paths don't pollute the repo
    - Pre-create data/tileList.txt to prevent tile list download on import
    - Monkeypatch boto3.client to return our FakeS3 so any import-time downloads use it
    - Import app.py from the project root under a stable module name
    """
    # Use isolated working directory
    monkeypatch.chdir(tmp_path)

    # Ensure the tile list exists so the import-time check doesn't attempt to download it
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "tileList.txt").write_text("dummy\n", encoding="utf-8")

    # Patch boto3.client BEFORE importing the target module
    monkeypatch.setattr(boto3, "client", lambda *args, **kwargs: fake_s3, raising=True)

    # Import app.py explicitly from the repository root
    project_root = Path(__file__).resolve().parents[1]
    app_path = project_root / "app.py"
    spec = importlib.util.spec_from_file_location("app_under_test", str(app_path))
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader, "Failed to load module spec for app.py"
    sys.modules["app_under_test"] = module
    spec.loader.exec_module(module)

    return module, fake_s3
