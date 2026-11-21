"""Keep Louisiana's source captures separate from interpretive notes."""

import hashlib
from pathlib import Path
import re

import pytest


CAPTURES = Path(__file__).resolve().parents[3] / "source_conflicts/sources/us-la"
# Hash each complete page's unedited pdftotext output from the official PDFs.
# Each capture records the PDF's URL, page and SHA256 separately in its header.
PAGE_SHA256 = {
    "rr18-001-p2.txt": "a43f13d365031ab018df1a1ce943e667a8c32c308b652b09c4c6d8292dfdd186",
    "it540-instructions-2021-p3.txt": "ccfb814f1fb72db6ac7edb8816fe1fba7497c380618710ecfbe78e837189c217",
    "it540-instructions-2022-p2.txt": "3b42f352f733e59c1dabc4183b5c095b5e73802ee123bbe64138d49331ae07d0",
    "it540-instructions-2023-p3.txt": "2f7cddefbcf3b9689669e2adfb8fec2377091302ecd20f99ef5244459cac8ba7",
    "it540-instructions-2024-p3.txt": "13bd6a7c7ff96fe43055fc97db3ed74e55606eae24d1f9cef8fdf06b4fd84a56",
    "it540-instructions-2024-p18.txt": "9c82e330bdcd2d453ea1f288c54c333e3fbab8e71013be4d50ef486c1af6a52e",
    "it540-tax-table-2022-p1.txt": "8161e8611736a9518c905742c812f9e4d9722ea2fa7c032b8cb5a11bf732741b",
    "it540-tax-table-2023-p1.txt": "a65515fe9e1a8c11a2567577b67d449a5b750a5140a0861476af7cba56d55edc",
}


def test_la_captures_record_page_extraction():
    for name in PAGE_SHA256:
        path = CAPTURES / name
        header = path.read_bytes().split(b"\n\n", 1)[0].decode()
        assert re.fullmatch(
            r"Source: https://dam\.ldr\.la\.gov/[^\n]+#page=(\d+)\n"
            r"Pages \1-\1, text extracted with pdftotext \(poppler\), reading order\.\n"
            r"PDF SHA256: [0-9a-f]{64}",
            header,
        ), f"{path.name} must identify one official document page and its extraction"


@pytest.mark.parametrize("name, expected_sha256", PAGE_SHA256.items())
def test_la_captures_contain_complete_official_pages(name, expected_sha256):
    _, body = (CAPTURES / name).read_bytes().split(b"\n\n", 1)
    assert hashlib.sha256(body).hexdigest() == expected_sha256
