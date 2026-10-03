"""Keep reference URLs that are known to be dead out of the package and docs.

This check is offline: it never requests a URL. Each TOML file in
known_dead_reference_urls/ lists URL prefixes that were dead when last
checked, and where their content lives now:

    [[dead]]
    prefix = "https://www.example.gov/forms/2021/instructions.pdf"
    verified = "2026-09-30"
    replacement = "https://web.archive.org/web/20220101000000/https://www.example.gov/forms/2021/instructions.pdf"

The files are TOML, not YAML, because pytest collects every YAML file in the
package as a policy test.

A prefix ending in "/" covers everything under it; any other prefix covers
that URL and anything after it except a longer file name (`.htm` does not
cover `.html`). Archived copies such as
https://web.archive.org/web/<timestamp>/https://www.tax.ny.gov/... remain
allowed, because the dead URL follows a slash inside them.

To add an entry, confirm the URL is dead with a GET request
(`curl -sL -o /dev/null -w '%{http_code}' -A "Mozilla/5.0" <url>`; treat
403 and 429 as unknown and recheck in a browser), replace every reference in
the repo, then list the prefix in the TOML file for its agency or host.
"""

import random
import re
import tomllib
from collections import defaultdict
from datetime import date
from pathlib import Path

import pytest

from policyengine_us.model_api import REPO


DATA_DIR = Path(__file__).resolve().parent / "known_dead_reference_urls"
ENTRY_KEYS = {"prefix", "verified", "replacement"}


def parse_entries(name: str, text: str) -> list[tuple[str, str, str]]:
    """Parse one data file into (prefix, verified, replacement) entries.

    Raises ValueError naming the file for anything but a non-empty [[dead]]
    array of entries with exactly the keys prefix, verified and replacement:
    a typo must fail loudly rather than load nothing."""
    try:
        data = tomllib.loads(text)
    except tomllib.TOMLDecodeError as error:
        raise ValueError(f"{name}: {error}") from error
    dead = data.get("dead")
    if set(data) != {"dead"} or not isinstance(dead, list) or not dead:
        raise ValueError(
            f"{name}: expected a non-empty [[dead]] array and nothing else"
        )
    entries = []
    for entry in dead:
        if not isinstance(entry, dict) or set(entry) != ENTRY_KEYS:
            raise ValueError(
                f"{name}: each [[dead]] entry needs exactly {sorted(ENTRY_KEYS)}"
            )
        prefix, verified, replacement = (
            entry[key] for key in ("prefix", "verified", "replacement")
        )
        head = isinstance(prefix, str) and re.fullmatch(
            r"(https?://[^/\s]+)/\S*", prefix
        )
        if not head:
            raise ValueError(f"{name}: not an http(s) URL with a path: {prefix!r}")
        if not head.group(1).isascii() or head.group(1) != head.group(1).lower():
            raise ValueError(
                f"{name}: write the scheme and host in lower-case ASCII: {prefix}"
            )
        try:
            date.fromisoformat(str(verified))
        except ValueError:
            raise ValueError(
                f"{name}: {prefix}: verified must be a YYYY-MM-DD date"
            ) from None
        if not isinstance(replacement, str) or not replacement.strip():
            raise ValueError(f"{name}: {prefix}: replacement must be non-empty text")
        entries.append((prefix, str(verified), replacement))
    return entries


def load_known_dead_url_prefixes(data_dir: Path = DATA_DIR) -> tuple:
    """Return (dead URL prefix, date verified dead, replacement) entries from
    every file in `data_dir`, which must all be .toml files."""
    entries = []
    for path in sorted(data_dir.iterdir()):
        if path.name.startswith(".") or path.name == "__pycache__":
            continue
        if path.suffix != ".toml" or not path.is_file():
            raise ValueError(f"{path.name}: files in {data_dir.name}/ must be .toml")
        entries.extend(parse_entries(path.name, path.read_text(encoding="utf-8")))
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


def build_index(entries) -> tuple[list, dict, dict]:
    """(patterns in list order, patterns grouped by host, prefix -> order)."""
    patterns = [
        (dead_url_pattern(prefix), prefix, replacement)
        for prefix, _, replacement in entries
    ]
    by_host = defaultdict(list)
    for pattern, prefix, replacement in patterns:
        by_host[url_host(prefix)].append((pattern, prefix, replacement))
    order = {prefix: index for index, (_, prefix, _) in enumerate(patterns)}
    return patterns, dict(by_host), order


PATTERNS, PATTERNS_BY_HOST, PATTERN_ORDER = build_index(KNOWN_DEAD_URL_PREFIXES)


def find_dead_urls_naive(text: str, patterns=None) -> list[tuple[int, str, str]]:
    """Reference implementation: every pattern against every line."""
    patterns = PATTERNS if patterns is None else patterns
    hits = []
    for number, line in enumerate(text.splitlines(), start=1):
        for pattern, prefix, replacement in patterns:
            if pattern.search(line):
                hits.append((number, prefix, replacement))
    return hits


def find_dead_urls(text: str, by_host=None, order=None) -> list[tuple[int, str, str]]:
    """Return (line number, dead prefix, replacement) for each match.

    Same result as `find_dead_urls_naive`, but only runs the patterns whose
    host appears in the line. Hosts are lower-case ASCII and every match
    contains its host in ASCII case, so lower-casing the line never hides
    one."""
    by_host = PATTERNS_BY_HOST if by_host is None else by_host
    order = PATTERN_ORDER if order is None else order
    lowered = text.lower()
    hosts = [host for host in by_host if host in lowered]
    if not hosts:
        return []
    hits = []
    for number, line in enumerate(text.splitlines(), start=1):
        lowered_line = line.lower()
        line_hits = [
            (number, prefix, replacement)
            for host in hosts
            if host in lowered_line
            for pattern, prefix, replacement in by_host[host]
            if pattern.search(line)
        ]
        hits.extend(sorted(line_hits, key=lambda hit: order[hit[1]]))
    return hits


def join_split_string_literals(text: str) -> str:
    """Apply Python's implicit concatenation to string literals that end
    one line and continue on the next, so a URL split across them reads
    whole on the first line. Consumed lines become empty, which keeps every
    later line number."""
    lines = text.split("\n")
    target = None
    for index, line in enumerate(lines):
        stripped = line.strip()
        if (
            target is not None
            and stripped[:1] in {'"', "'"}
            and lines[target].rstrip()[-1:] in {'"', "'"}
        ):
            lines[target] = lines[target].rstrip()[:-1] + stripped[1:]
            lines[index] = ""
        else:
            target = index
    return "\n".join(lines)


def find_dead_urls_in_file(
    text: str, suffix: str, by_host=None, order=None
) -> list[tuple[int, str, str]]:
    """`find_dead_urls`, plus, for Python, URLs split across literals."""
    hits = find_dead_urls(text, by_host, order)
    if suffix == ".py":
        hits += [
            hit
            for hit in find_dead_urls(join_split_string_literals(text), by_host, order)
            if hit not in hits
        ]
    return sorted(hits, key=lambda hit: hit[0])


def test_known_dead_url_entries_are_well_formed():
    prefixes = [prefix for prefix, _, _ in KNOWN_DEAD_URL_PREFIXES]
    assert prefixes, "no entries loaded from " + str(DATA_DIR)
    duplicates = sorted({p for p in prefixes if prefixes.count(p) > 1})
    assert not duplicates, f"Listed more than once: {duplicates}"
    for prefix, _, replacement in KNOWN_DEAD_URL_PREFIXES:
        assert "#" not in prefix, f"{prefix}: drop the fragment"
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


def random_texts(entries, count: int, seed: int = 0):
    """Lines built from listed prefixes, their hosts in mixed case, archive
    wrappers, characters that end or extend a URL, every kind of line break
    `str.splitlines` honours, and characters that fold to ASCII letters under
    Unicode case rules."""
    rng = random.Random(seed)
    pieces = [prefix for prefix, _, _ in entries]
    pieces += [url_host(prefix) for prefix in pieces]
    pieces += [
        "https://",
        "http://",
        "www.",
        "WWW.",
        "https://web.archive.org/web/20240101000000/",
    ]
    pieces += ["/", ".", "-", "_", "l", "x", "#page=3", "?a=1", " ", ")"]
    pieces += ["\n", "\r", "\r\n", "\x0b", "\x85", "\u2028"]
    # Long s, Kelvin sign, dotted capital I and dotless i.
    pieces += ["\u017f", "\u212a", "\u0130", "\u0131"]
    for _ in range(count):
        text = "".join(rng.choice(pieces) for _ in range(rng.randint(1, 12)))
        if rng.random() < 0.3:
            text = text.upper()
        yield text


def test_fast_scan_matches_naive_scan():
    for text in random_texts(KNOWN_DEAD_URL_PREFIXES, 3000):
        assert find_dead_urls(text) == find_dead_urls_naive(text), repr(text)


SYNTHETIC_ENTRIES = [
    (prefix, "2026-01-01", "https://example.org/")
    for prefix in (
        "https://ny.gov/a/",
        "https://www.tax.ny.gov/a/b.pdf",
        "https://sub.tax.ny.gov/a",
        "http://kansas.gov/ks/",
        "https://www.kansas.gov/ks/x.htm",
        "https://illinois.gov/i/doc.pdf",
        "https://example.gov:443/p/",
    )
]


def test_fast_scan_matches_naive_scan_across_hosts():
    """Overlapping hosts, several hosts per line and hosts that contain the
    letters with Unicode case-folding look-alikes (k, s, i)."""
    patterns, by_host, order = build_index(SYNTHETIC_ENTRIES)
    for text in random_texts(SYNTHETIC_ENTRIES, 3000, seed=1):
        assert find_dead_urls(text, by_host, order) == find_dead_urls_naive(
            text, patterns
        ), repr(text)


def test_urls_split_across_python_string_literals_are_flagged():
    _, by_host, order = build_index(SYNTHETIC_ENTRIES)
    source = (
        "reference = (\n"
        '    "https://www.tax.ny.gov/a/"\n'
        '    "b.pdf#page=3",\n'
        '    "https://www.tax.ny.gov/a/b.pdfx"\n'
        ")\n"
    )
    assert find_dead_urls(source, by_host, order) == []
    assert find_dead_urls_in_file(source, ".py", by_host, order) == [
        (2, "https://www.tax.ny.gov/a/b.pdf", "https://example.org/")
    ]
    # Other file types are scanned line by line only.
    assert find_dead_urls_in_file(source, ".yaml", by_host, order) == []


def test_joining_split_literals_keeps_line_numbers():
    source = 'x = (\n    "a"\n    "b"\n    \'c\'  \n\n    "d"\n)\ny = "e"\n'
    assert join_split_string_literals(source).split("\n") == [
        "x = (",
        "    \"abc'",
        "",
        "",
        "",
        '    "d"',
        ")",
        'y = "e"',
        "",
    ]


GOOD_ENTRY = (
    '[[dead]]\nprefix = "https://www.example.gov/a.pdf"\n'
    'verified = "2026-09-30"\nreplacement = "https://example.org/"\n'
)


@pytest.mark.parametrize(
    "text",
    [
        "",
        GOOD_ENTRY.replace("[[dead]]", "[[Dead]]"),
        GOOD_ENTRY.replace("[[dead]]", "[dead]"),
        GOOD_ENTRY.replace("prefix =", "prefx ="),
        GOOD_ENTRY.replace('replacement = "https://example.org/"\n', ""),
        GOOD_ENTRY + 'notes = "x"\n',
        GOOD_ENTRY.replace('"https://www.example.gov/a.pdf"', "5"),
        GOOD_ENTRY.replace("https://www.example.gov/a.pdf", "https://www.example.gov"),
        GOOD_ENTRY.replace(
            '"https://www.example.gov/a.pdf"', '"https://www.example.gov/a.pdf\\n"'
        ),
        GOOD_ENTRY.replace("https://www.example.gov", "https://WWW.Example.gov"),
        GOOD_ENTRY.replace("2026-09-30", "2026-13-45"),
        GOOD_ENTRY.replace('"https://example.org/"', '" "'),
        GOOD_ENTRY.replace('verified = "2026-09-30"', 'verified = "2026-09-30'),
    ],
)
def test_malformed_data_files_fail_naming_the_file(text):
    with pytest.raises(ValueError, match="^agency.toml: "):
        parse_entries("agency.toml", text)


def test_good_data_file_parses():
    assert parse_entries("agency.toml", GOOD_ENTRY) == [
        ("https://www.example.gov/a.pdf", "2026-09-30", "https://example.org/")
    ]


def test_data_folder_accepts_only_toml(tmp_path):
    (tmp_path / "agency.toml").write_text(GOOD_ENTRY)
    (tmp_path / ".DS_Store").write_text("")
    assert len(load_known_dead_url_prefixes(tmp_path)) == 1
    (tmp_path / "other.yaml").write_text("- prefix: x\n")
    with pytest.raises(ValueError, match="^other.yaml: "):
        load_known_dead_url_prefixes(tmp_path)


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
        for number, prefix, replacement in find_dead_urls_in_file(
            text, path.suffix.lower()
        ):
            violations.append(
                f"{path.relative_to(REPO.parent)}:{number} cites {prefix} "
                f"(dead); use {replacement}"
            )
    assert not violations, "Known-dead reference URLs:\n" + "\n".join(violations)
