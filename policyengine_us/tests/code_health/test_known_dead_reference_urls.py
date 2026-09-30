"""Keep reference URLs that are known to be dead out of the package and docs.

This check is offline: it never requests a URL. Each YAML file in
known_dead_reference_urls/ lists URL prefixes that were dead when last
checked, and where their content lives now:

    - prefix: https://www.example.gov/forms/2021/instructions.pdf
      verified: "2026-09-30"
      replacement: https://web.archive.org/web/20220101000000/https://www.example.gov/forms/2021/instructions.pdf

A prefix ending in "/" covers everything under it; any other prefix covers
that URL and anything after it except a longer file name (`.htm` does not
cover `.html`). Archived copies such as
https://web.archive.org/web/<timestamp>/https://www.tax.ny.gov/... remain
allowed, because the dead URL follows a slash inside them.

To add an entry, confirm the URL is dead with a GET request
(`curl -sL -o /dev/null -w '%{http_code}' -A "Mozilla/5.0" <url>`; treat
403 and 429 as unknown and recheck in a browser), replace every reference in
the repo, then list the prefix in the YAML file for its agency or host.
"""

import random
import re
from collections import defaultdict
from pathlib import Path

import pytest
import yaml

from policyengine_us.model_api import REPO


DATA_DIR = Path(__file__).resolve().parent / "known_dead_reference_urls"


def load_known_dead_url_prefixes() -> tuple:
    """Return (dead URL prefix, date verified dead, replacement) entries."""
    entries = []
    for path in sorted(DATA_DIR.glob("*.yaml")):
        for entry in yaml.safe_load(path.read_text(encoding="utf-8")) or []:
            prefix = entry["prefix"]
            if not re.match(r"https?://[^/\s]+/", prefix):
                raise ValueError(
                    f"{path.name}: not an http(s) URL with a path: {prefix}"
                )
            entries.append((prefix, entry["verified"], entry["replacement"]))
    return tuple(entries)


# (dead URL prefix, date verified dead, where its content lives now)
KNOWN_DEAD_URL_PREFIXES = load_known_dead_url_prefixes()
SCANNED_ROOTS = (REPO, REPO.parent / "docs")
SCANNED_SUFFIXES = {".ipynb", ".md", ".py", ".yaml", ".yml"}
THIS_FILE = Path(__file__).resolve()


def url_host(prefix: str) -> str:
    return re.match(r"https?://(?:www\.)?([^/]+)", prefix).group(1).lower()


def dead_url_pattern(prefix: str) -> re.Pattern:
    """Match `prefix` over http or https, with or without `www.`, in any
    (ASCII) case for the scheme and host, unless a slash, dot or word
    character precedes it (as in an archived copy). A prefix naming a file
    does not match a longer file name (`.htm` does not match `.html`)."""
    host, path = re.match(r"https?://(?:www\.)?([^/]+)(/.*)", prefix).groups()
    end = "" if path.endswith("/") else r"(?![\w-])"
    return re.compile(
        r"(?<![/\w.])(?ai:(?:https?://)?(?:www\.)?"
        + re.escape(host)
        + ")"
        + re.escape(path)
        + end
    )


PATTERNS = [
    (dead_url_pattern(prefix), prefix, replacement)
    for prefix, _, replacement in KNOWN_DEAD_URL_PREFIXES
]
PATTERN_ORDER = {prefix: index for index, (_, prefix, _) in enumerate(PATTERNS)}
PATTERNS_BY_HOST = defaultdict(list)
for pattern, prefix, replacement in PATTERNS:
    PATTERNS_BY_HOST[url_host(prefix)].append((pattern, prefix, replacement))


def find_dead_urls_naive(text: str) -> list[tuple[int, str, str]]:
    """Reference implementation: every pattern against every line."""
    hits = []
    for number, line in enumerate(text.splitlines(), start=1):
        for pattern, prefix, replacement in PATTERNS:
            if pattern.search(line):
                hits.append((number, prefix, replacement))
    return hits


def find_dead_urls(text: str) -> list[tuple[int, str, str]]:
    """Return (line number, dead prefix, replacement) for each match.

    Same result as `find_dead_urls_naive`, but only runs the patterns whose
    host appears in the line. Every match contains its host in ASCII case,
    so lower-casing the line never hides one."""
    lowered = text.lower()
    hosts = [host for host in PATTERNS_BY_HOST if host in lowered]
    if not hosts:
        return []
    hits = []
    for number, line in enumerate(text.splitlines(), start=1):
        lowered_line = line.lower()
        line_hits = [
            (number, prefix, replacement)
            for host in hosts
            if host in lowered_line
            for pattern, prefix, replacement in PATTERNS_BY_HOST[host]
            if pattern.search(line)
        ]
        hits.extend(sorted(line_hits, key=lambda hit: PATTERN_ORDER[hit[1]]))
    return hits


def test_known_dead_url_entries_are_well_formed():
    prefixes = [prefix for prefix, _, _ in KNOWN_DEAD_URL_PREFIXES]
    assert prefixes, "no entries loaded from " + str(DATA_DIR)
    duplicates = sorted({p for p in prefixes if prefixes.count(p) > 1})
    assert not duplicates, f"Listed more than once: {duplicates}"
    for prefix, verified, replacement in KNOWN_DEAD_URL_PREFIXES:
        assert re.match(r"https?://[^/\s]+/\S*$", prefix), prefix
        assert "#" not in prefix, f"{prefix}: drop the fragment"
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(verified)), prefix
        assert isinstance(replacement, str) and replacement.strip(), prefix
        # A replacement that is itself listed dead would send readers in circles.
        assert not find_dead_urls_naive(replacement), prefix


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
    assert find_dead_urls(text) == find_dead_urls_naive(text)


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
    assert find_dead_urls_naive(text) == []


def random_texts(count: int, seed: int = 0):
    """Lines built from listed prefixes, their hosts in mixed case, archive
    wrappers and characters that end or extend a URL."""
    rng = random.Random(seed)
    pieces = [prefix for prefix, _, _ in KNOWN_DEAD_URL_PREFIXES]
    pieces += [url_host(prefix) for prefix in pieces]
    pieces += [
        "https://",
        "http://",
        "www.",
        "WWW.",
        "https://web.archive.org/web/20240101000000/",
        "/",
        ".",
        "-",
        "l",
        "x",
        "#page=3",
        "?a=1",
        " ",
        ")",
        "\n",
        "ſ",  # LATIN SMALL LETTER LONG S: matches "s" under Unicode case folding
        "K",  # KELVIN SIGN: matches "k" under Unicode case folding
    ]
    for _ in range(count):
        text = "".join(rng.choice(pieces) for _ in range(rng.randint(1, 12)))
        if rng.random() < 0.3:
            text = text.upper()
        yield text


def test_fast_scan_matches_naive_scan():
    for text in random_texts(3000):
        assert find_dead_urls(text) == find_dead_urls_naive(text), repr(text)


def scanned_files():
    for root in SCANNED_ROOTS:
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*")):
            if (
                path.suffix.lower() not in SCANNED_SUFFIXES
                or not path.is_file()
                or path.resolve() == THIS_FILE
                or DATA_DIR in path.resolve().parents
            ):
                continue
            yield path


def test_package_and_docs_have_no_known_dead_reference_urls():
    violations = []
    for path in scanned_files():
        text = path.read_text(encoding="utf-8", errors="replace")
        for number, prefix, replacement in find_dead_urls(text):
            violations.append(
                f"{path.relative_to(REPO.parent)}:{number} cites {prefix} "
                f"(dead); use {replacement}"
            )
    assert not violations, "Known-dead reference URLs:\n" + "\n".join(violations)
