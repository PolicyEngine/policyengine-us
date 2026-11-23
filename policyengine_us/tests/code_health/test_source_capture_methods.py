"""Check extraction limits that affect quotations from captured amendments."""

from pathlib import Path


def test_act_155_discloses_lost_amendment_marks():
    capture = (
        Path(__file__).resolve().parents[3]
        / "source_conflicts/sources/us-ar/act-155-2017-p9-10.txt"
    )
    header, body = capture.read_text().split("\n\n", 1)

    # A verbatim match alone accepts this year even though the PDF strikes it.
    assert "as in effect on January 1, 2015" in " ".join(body.split())
    assert "pdftotext drops strike-through and underline marks" in header
    assert "the PDF strikes 2015 and underlines 2017" in header
    assert (
        "On PDF page 9, section 21 underlines text from "
        '"including without limitation gambling losses" through '
        '"itemized deductions".'
    ) in header
