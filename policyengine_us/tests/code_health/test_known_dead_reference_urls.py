"""Keep reference URLs that are known to be dead out of the package and docs.

This check is offline: it never requests a URL. Each entry below records a URL
prefix that returned HTTP 404 when last checked, and where its content lives
now. Archived copies such as
https://web.archive.org/web/<timestamp>/https://www.tax.ny.gov/... remain
allowed, because the dead URL follows a slash inside them.

To add an entry, confirm the 404 with a GET request
(`curl -sL -o /dev/null -w '%{http_code}' -A "Mozilla/5.0" <url>`), replace
every reference in the repo, then list the prefix here.
"""

import re
from pathlib import Path

import pytest

from policyengine_us.model_api import REPO


# (dead URL prefix, date verified dead, where its content lives now)
KNOWN_DEAD_URL_PREFIXES = (
    (
        "https://www.tax.ny.gov/pdf/2023/printable-pdfs/",
        "2026-09-28",
        "The 2023 HTML instructions at "
        "https://www.tax.ny.gov/forms/html-instructions/2023/it/<form>i-2023.htm "
        "(use a section anchor such as #step-8), or an archived copy of the "
        "same PDF with the same #page.",
    ),
    (
        "https://www.tax.ny.gov/pit/inflation-refund-checks.htm",
        "2026-09-28",
        "https://web.archive.org/web/20260617073750/"
        "https://www.tax.ny.gov/pit/inflation-refund-checks.htm",
    ),
    (
        "https://www.tax.ny.gov/pit/child-earned-payments.htm",
        "2026-09-28",
        "https://web.archive.org/web/20221020033542/"
        "https://www.tax.ny.gov/pit/child-earned-payments.htm",
    ),
    (
        "https://www.tax.ny.gov/pdf/current_forms/it/it558i.pdf",
        "2026-09-28",
        "https://www.tax.ny.gov/pdf/2022/inc/it558i_2022.pdf",
    ),
)
SCANNED_ROOTS = (REPO, REPO.parent / "docs")
SCANNED_SUFFIXES = {".ipynb", ".md", ".py", ".yaml", ".yml"}
THIS_FILE = Path(__file__).resolve()


def dead_url_pattern(prefix: str) -> re.Pattern:
    """Match `prefix` over http or https, with or without `www.`, in any case
    for the scheme and host, unless a slash, dot or word character precedes it
    (as in an archived copy). A prefix naming a file does not match a longer
    file name (`.htm` does not match `.html`)."""
    host, path = re.match(r"https?://(?:www\.)?([^/]+)(/.*)", prefix).groups()
    end = "" if path.endswith("/") else r"(?![\w-])"
    return re.compile(
        r"(?<![/\w.])(?i:(?:https?://)?(?:www\.)?"
        + re.escape(host)
        + ")"
        + re.escape(path)
        + end
    )


PATTERNS = [
    (dead_url_pattern(prefix), prefix, replacement)
    for prefix, _, replacement in KNOWN_DEAD_URL_PREFIXES
]


def find_dead_urls(text: str) -> list[tuple[int, str, str]]:
    """Return (line number, dead prefix, replacement) for each match."""
    hits = []
    for number, line in enumerate(text.splitlines(), start=1):
        for pattern, prefix, replacement in PATTERNS:
            if pattern.search(line):
                hits.append((number, prefix, replacement))
    return hits


@pytest.mark.parametrize(
    "text",
    [
        "href: https://www.tax.ny.gov/pdf/2023/printable-pdfs/inc/it201i-2023.pdf#page=26",
        "href: http://tax.ny.gov/pdf/2023/printable-pdfs/inc/it196i-2023.pdf",
        "# see www.tax.ny.gov/pit/child-earned-payments.htm",
        "href: https://www.tax.ny.gov/pit/inflation-refund-checks.htm?utm=x",
        "# https://www.tax.ny.gov/pdf/current_forms/it/it558i.pdf",
        "href: HTTPS://WWW.TAX.NY.GOV/pit/child-earned-payments.htm#amount",
        '"[IT-201-I](https://www.tax.ny.gov/pdf/2023/printable-pdfs/inc/it201i-2023.pdf)"',
    ],
)
def test_dead_urls_are_flagged(text):
    assert len(find_dead_urls(text)) == 1


@pytest.mark.parametrize(
    "text",
    [
        "href: https://web.archive.org/web/20240317205657/https://www.tax.ny.gov/pdf/2023/printable-pdfs/inc/it201i-2023.pdf#page=18",
        "href: https://web.archive.org/web/2025id_/https://www.tax.ny.gov/pit/inflation-refund-checks.htm",
        "href: https://www.tax.ny.gov/forms/html-instructions/2023/it/it201i-2023.htm#step-8",
        "href: https://www.tax.ny.gov/pdf/2022/printable-pdfs/inc/it201i-2022.pdf#page=27",
        "href: https://www.tax.ny.gov/pdf/current_forms/it/it201i.pdf#page=25",
        "href: https://www.tax.ny.gov/pdf/current_forms/it/it558i.pdfx",
        "href: https://www.tax.ny.gov/pit/inflation-refund-checks-faq.htm",
    ],
)
def test_archived_and_live_urls_are_not_flagged(text):
    assert find_dead_urls(text) == []


def test_package_and_docs_have_no_known_dead_reference_urls():
    violations = []
    for root in SCANNED_ROOTS:
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*")):
            if (
                path.suffix.lower() not in SCANNED_SUFFIXES
                or not path.is_file()
                or path.resolve() == THIS_FILE
            ):
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            for number, prefix, replacement in find_dead_urls(text):
                violations.append(
                    f"{path.relative_to(REPO.parent)}:{number} cites {prefix} "
                    f"(dead); use {replacement}"
                )
    assert not violations, "Known-dead reference URLs:\n" + "\n".join(violations)
