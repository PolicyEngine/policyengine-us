import zipfile
from pathlib import Path

import pytest

from policyengine_us.tools.geography.download_50_state_census_block_data import (
    MAX_ARCHIVE_DOWNLOAD_BYTES,
    MAX_ARCHIVE_UNCOMPRESSED_BYTES,
    _download_with_limits,
    _safe_extract,
)


def test_safe_extract_rejects_zip_slip(tmp_path):
    archive_path = tmp_path / "malicious.zip"
    extract_dir = tmp_path / "extract"

    with zipfile.ZipFile(archive_path, "w") as zip_ref:
        zip_ref.writestr("../evil.txt", "pwned")

    with zipfile.ZipFile(archive_path, "r") as zip_ref:
        with pytest.raises(ValueError, match="Unsafe path"):
            _safe_extract(zip_ref, extract_dir)

    assert not (tmp_path / "evil.txt").exists()
    assert not (extract_dir / "evil.txt").exists()


def test_safe_extract_rejects_oversized_archives(tmp_path):
    class FakeMember:
        def __init__(self, filename: str, file_size: int):
            self.filename = filename
            self.file_size = file_size

    class FakeZipFile:
        def __init__(self):
            self.extracted = False

        def infolist(self):
            return [FakeMember("data.txt", MAX_ARCHIVE_UNCOMPRESSED_BYTES + 1)]

        def extractall(self, destination):
            self.extracted = True

    extract_dir = tmp_path / "extract"
    fake_zip = FakeZipFile()

    with pytest.raises(ValueError, match="uncompressed size limit"):
        _safe_extract(fake_zip, extract_dir)

    assert fake_zip.extracted is False


def test_download_with_limits_rejects_oversized_responses(tmp_path, monkeypatch):
    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def raise_for_status(self):
            return None

        def iter_content(self, chunk_size):
            yield b"x" * MAX_ARCHIVE_DOWNLOAD_BYTES
            yield b"x"

    monkeypatch.setattr(
        "requests.get",
        lambda *args, **kwargs: FakeResponse(),
    )

    destination = Path(tmp_path) / "archive.zip"

    with pytest.raises(ValueError, match="exceeds"):
        _download_with_limits("https://example.com/archive.zip", destination)

    assert not destination.exists()
