"""Keep URLs in `reference` and `documentation` attributes separate.

Python joins adjacent string literals, so a missing comma in

    reference = (
        "https://www.ksrevenue.gov/pdf/ip21.pdf"
        "https://www.ksrevenue.gov/pdf/ip22.pdf"
    )

produces the single, broken reference
"https://www.ksrevenue.gov/pdf/ip21.pdfhttps://www.ksrevenue.gov/pdf/ip22.pdf".
This check parses every module in the package with `ast` (no simulation
import) and flags

- any string in a class's `reference` or `documentation` attribute in which a
  URL scheme is glued to the character before it, and
- any string in a class's `reference` attribute that contains a URL but is not
  exactly one bare URL: two URLs joined by " ; ", ", " or a space, stray
  leading or trailing spaces, or a note such as "(Line 3)" (put notes in a
  Python comment).

A scheme may follow whitespace, an opening bracket or quote, or "=" (a URL
passed as a query value, as in azleg.gov's viewdocument/?docName=https://...).
It may follow "/" only when that slash closes an archive.org wrapper such as
https://web.archive.org/web/<timestamp>/https://...
"""

import ast
import re
from pathlib import Path

import pytest


PACKAGE = Path(__file__).resolve().parents[2]
ATTRIBUTES = {"reference", "documentation"}
SCHEME = re.compile(r"https?://", re.IGNORECASE)
ALLOWED_BEFORE_SCHEME = set("([{<\"'`=")
BARE_URL = re.compile(r"https?://\S+", re.IGNORECASE)
ARCHIVE_WRAPPER = re.compile(
    r"(?:^|[\s(\[{<\"'`=])(?:https?://)?(?:web\.)?archive\.org/web/[^\s/]+/$",
    re.IGNORECASE,
)


def glued_url_offsets(text: str) -> list[int]:
    """Offsets in `text` of URL schemes glued to the character before them."""
    offsets = []
    for match in SCHEME.finditer(text):
        start = match.start()
        if start == 0:
            continue
        before = text[start - 1]
        if before.isspace() or before in ALLOWED_BEFORE_SCHEME:
            continue
        if before == "/" and ARCHIVE_WRAPPER.search(text, 0, start):
            continue
        offsets.append(start)
    return offsets


def class_attribute_strings(tree: ast.AST):
    """Yield (attribute, str constant) for each string in a class's
    `reference` or `documentation` attribute, at any depth (tuple and list
    elements, dict values)."""
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        for statement in node.body:
            if isinstance(statement, ast.Assign):
                targets = statement.targets
            elif isinstance(statement, ast.AnnAssign) and statement.value:
                targets = [statement.target]
            else:
                continue
            for target in targets:
                if isinstance(target, ast.Name) and target.id in ATTRIBUTES:
                    for child in ast.walk(statement.value):
                        if isinstance(child, ast.Constant) and isinstance(
                            child.value, str
                        ):
                            yield target.id, child


def is_wrapped_url(text: str, start: int) -> bool:
    """True if the URL scheme at `start` sits inside another URL: as a query
    value (`...?docName=https://...`) or after an archive.org wrapper."""
    before = text[start - 1]
    return before == "=" or (
        before == "/" and bool(ARCHIVE_WRAPPER.search(text, 0, start))
    )


def is_bare_url_or_has_none(text: str) -> bool:
    """True if `text` contains no URL, or is exactly one URL with nothing
    before or after it. A second scheme is allowed only inside the first URL,
    as a query value or after an archive.org wrapper."""
    starts = [match.start() for match in SCHEME.finditer(text)]
    if not starts:
        return True
    return bool(BARE_URL.fullmatch(text)) and all(
        is_wrapped_url(text, start) for start in starts[1:]
    )


def find_glued_urls(source: str, filename: str = "<string>") -> list[str]:
    violations = []
    for attribute, constant in class_attribute_strings(
        ast.parse(source, filename=filename)
    ):
        location = f"{filename}:{constant.lineno} {attribute}:"
        glued = glued_url_offsets(constant.value)
        for offset in glued:
            context = constant.value[max(offset - 40, 0) : offset + 40]
            violations.append(f"{location} glued URLs ...{context}...")
        if (
            attribute == "reference"
            and not glued
            and not is_bare_url_or_has_none(constant.value)
        ):
            violations.append(f"{location} not one bare URL {constant.value!r}")
    return violations


@pytest.mark.parametrize(
    "text",
    [
        "https://www.ksrevenue.gov/pdf/ip21.pdfhttps://www.ksrevenue.gov/pdf/ip22.pdf",
        "https://example.gov/a.pdf#page=3http://example.gov/b.pdf",
        "https://law.justia.com/codes/alabama/2022/title-40/section-40-18-15/"
        "https://www.revenue.alabama.gov/forms.pdf",
        "https://www.azleg.gov/viewdocument/?docName=https://www.azleg.gov/ars/43/01001.htm"
        "https://azdor.gov/forms/individual/form-140a",
        "Eligibility and Enrollmenthttps://www.cms.gov/medicare/enrollment",
        "https://example.gov/a)https://example.gov/b",
        "HTTPS://EXAMPLE.GOV/A.PDFHTTPS://EXAMPLE.GOV/B.PDF",
        "https://example.gov/web/2024/https://example.gov/b",
    ],
)
def test_glued_urls_are_flagged(text):
    assert len(glued_url_offsets(text)) == 1


@pytest.mark.parametrize(
    "text",
    [
        "https://www.ksrevenue.gov/pdf/ip21.pdf",
        "https://example.gov/a.pdf https://example.gov/b.pdf",
        "https://example.gov/a.pdf\nhttps://example.gov/b.pdf",
        "https://www.azleg.gov/viewdocument/?docName=https://www.azleg.gov/ars/43/01001.htm",
        "https://web.archive.org/web/20250720165524/https://www.mass.gov/doc/heap",
        "https://web.archive.org/web/20211208060516id_/https://dese.mo.gov/childhood",
        "web.archive.org/web/2025*/https://www.tax.ny.gov/pit/",
        "See the manual (https://example.gov/manual.pdf).",
        "[IT-201-I](https://www.tax.ny.gov/it201i.pdf)",
        '"https://example.gov/a"',
        "https://www.cbo.gov/system/files/2026-02/51138-2026-02-Revenue.xlsx",
    ],
)
def test_separated_and_wrapped_urls_are_not_flagged(text):
    assert glued_url_offsets(text) == []


@pytest.mark.parametrize(
    "text",
    [
        "https://example.gov/a ; https://example.gov/b",
        "https://example.gov/a, https://example.gov/b",
        "https://example.gov/a.pdf#page=27 https://example.gov/b.pdf",
        " https://example.gov/a.htm",
        "https://example.gov/a.htm ",
        "https://example.gov/a.pdf (Line 3)",
        "https://example.gov/a.pdf#page=1, 2",
        "See https://example.gov/a.pdf",
        'https://example.gov/a.pdf"https://example.gov/b.pdf"',
        "https://example.gov/a.pdf(https://example.gov/b.pdf)",
        "https://example.gov/a.pdf[https://example.gov/b.pdf]",
        "https://example.gov/web/2024/https://example.gov/b",
    ],
)
def test_reference_entries_that_are_not_one_bare_url_are_flagged(text):
    assert not is_bare_url_or_has_none(text)


@pytest.mark.parametrize(
    "text",
    [
        "https://example.gov/a.pdf#page=3",
        "https://www.azleg.gov/viewdocument/?docName=https://www.azleg.gov/ars/43/01001.htm",
        "https://web.archive.org/web/20250720165524/https://www.mass.gov/doc/heap",
        "https://web.archive.org/web/2021id_/https://example.gov/a?url=https://b.gov",
        "26 U.S.C. 32(b)",
        "IRS Publication 596, page 3",
        "",
    ],
)
def test_bare_urls_and_text_citations_pass(text):
    assert is_bare_url_or_has_none(text)


def test_implicit_concatenation_in_a_class_attribute_is_found():
    source = (
        "class v:\n"
        "    reference = (\n"
        '        "https://example.gov/a.pdf"\n'
        '        "https://example.gov/b.pdf",\n'
        '        {"href": "https://example.gov/c.pdfhttps://example.gov/d.pdf"},\n'
        "    )\n"
        '    documentation: str = "See https://example.gov/e.htmlhttps://f.gov"\n'
        '    label = "https://example.gov/g.pdfhttps://example.gov/h.pdf"\n'
        "class w:\n"
        '    reference = "https://example.gov/k.pdf ; https://example.gov/l.pdf"\n'
        '    documentation = "https://example.gov/m.pdf (Line 3)"\n'
        "def f():\n"
        '    reference = "https://example.gov/i.pdfhttps://example.gov/j.pdf"\n'
    )
    violations = find_glued_urls(source, "v.py")
    assert [v.split(" ")[:3] for v in violations] == [
        ["v.py:3", "reference:", "glued"],
        ["v.py:5", "reference:", "glued"],
        ["v.py:7", "documentation:", "glued"],
        ["v.py:10", "reference:", "not"],
    ]


def test_separated_class_attribute_urls_pass():
    source = (
        "class v:\n"
        "    reference = (\n"
        '        "https://example.gov/a.pdf",\n'
        '        "https://example.gov/b.pdf",\n'
        "    )\n"
        '    documentation = "https://example.gov/c.pdf\\nhttps://example.gov/d.pdf"\n'
        '    label = "Title, not a URL"\n'
        "class w:\n"
        '    reference = ({"title": "Form 1, line 3", "href": "https://x.gov/f.pdf"},)\n'
    )
    assert find_glued_urls(source) == []


def find_package_violations(root: Path) -> list[str]:
    violations = []
    for path in sorted(root.rglob("*.py")):
        source = path.read_text(encoding="utf-8")
        if "http" not in source.lower():
            continue
        violations.extend(find_glued_urls(source, str(path.relative_to(root))))
    return violations


def test_package_scan_reads_upper_case_urls(tmp_path):
    (tmp_path / "v.py").write_text(
        "class v:\n"
        "    reference = (\n"
        '        "HTTPS://EXAMPLE.GOV/A.PDF"\n'
        '        "HTTPS://EXAMPLE.GOV/B.PDF"\n'
        "    )\n"
    )
    assert [v.split(" ")[:3] for v in find_package_violations(tmp_path)] == [
        ["v.py:3", "reference:", "glued"],
    ]


def test_package_reference_urls_are_not_concatenated():
    violations = find_package_violations(PACKAGE)
    assert not violations, (
        "Malformed reference or documentation URLs. Put each reference URL "
        "in its own tuple element (with a comma after it), move notes into a "
        "Python comment, and separate URLs in documentation with a space or "
        "line break:\n" + "\n".join(violations)
    )
