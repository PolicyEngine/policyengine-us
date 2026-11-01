"""Every reference entry must link to exactly one URL.

Python joins adjacent string literals, so a ``reference`` tuple written
without commas between its URLs collapses into one string. policyengine-core
wraps that string as a one-element list, and it renders as a single dead link.

A variable's ``documentation`` is prose. Any URL it cites must also be listed
in ``reference``, and documentation that is nothing but URLs is a citation
filed in the wrong attribute.
"""

import ast
import re

import pytest

from policyengine_us.model_api import REPO

URL = re.compile(r"https?://")
# A URL may embed another URL as a Wayback Machine snapshot target
# (web.archive.org/web/<timestamp>/https://...) or as the value of a query
# parameter (viewdocument/?docName=https://... or ?a=1&url=https://...). The
# parameter must sit in the query, before any "#": an "=" inside a fragment,
# as in x.pdf#page=https://..., marks two URLs fused together.
EMBEDDED_URL_PREFIX = re.compile(
    r"(?:web\.archive\.org/web/\d+[a-z_]*/|\?(?:[^#\s]*&)?[^?&#=\s]*=)$"
)
# Punctuation that ends a sentence rather than a URL cited in prose.
TRAILING_PUNCTUATION = ".,;:!?'\""


def top_level_url_starts(text):
    """Offsets of the URLs in ``text`` that are not embedded in another URL."""
    return [
        match.start()
        for match in URL.finditer(text)
        if not EMBEDDED_URL_PREFIX.search(text[: match.start()])
    ]


def reference_url_problem(href):
    """Describe what is wrong with one reference string, or return None.

    Strings without a URL (plain-text citations) are accepted. A string with a
    URL must be exactly one bare URL: no second URL fused onto it, no
    surrounding whitespace, and no trailing annotation text or separators.
    """
    if not isinstance(href, str):
        return None
    if not URL.search(href):
        return None
    if len(top_level_url_starts(href)) > 1:
        return "contains more than one URL (missing comma between literals?)"
    if not re.fullmatch(r"https?://\S+", href) or href.endswith((",", ";")):
        return "is not a single bare URL"
    return None


def _entries(reference):
    if not reference:
        return []
    if isinstance(reference, (str, dict)):
        reference = [reference]
    return [
        entry.get("href") if isinstance(entry, dict) else entry for entry in reference
    ]


def _cited_urls(token):
    """The URLs in a whitespace-free ``token`` of prose, each cut at the next
    URL fused onto it and stripped of the punctuation or closing bracket that
    ends the sentence."""
    starts = top_level_url_starts(token)
    ends = [*starts[1:], len(token)]
    return [_strip_prose(token[start:end]) for start, end in zip(starts, ends)]


def _strip_prose(url):
    url = url.rstrip(TRAILING_PUNCTUATION)
    while url.endswith(")") and url.count(")") > url.count("("):
        url = url[:-1].rstrip(TRAILING_PUNCTUATION)
    return url


def documentation_url_problems(documentation, reference):
    """Describe what is wrong with the URLs in a variable's documentation."""
    if not isinstance(documentation, str) or not URL.search(documentation):
        return []
    problems = []
    tokens = documentation.split()
    if all(URL.match(token) for token in tokens):
        problems.append("is only URLs: move them into reference")
    cited = []
    for token in tokens:
        urls = _cited_urls(token)
        if len(urls) > 1:
            problems.append(f"{token!r} contains more than one URL")
        cited.extend(urls)
    listed = set(_entries(reference))
    problems.extend(
        f"cites {url!r}, which reference does not list"
        for url in dict.fromkeys(cited)
        if url not in listed
    )
    return problems


@pytest.mark.parametrize(
    "href",
    [
        "https://www.dfa.arkansas.gov/wp-content/uploads/a.pdf#page=3",
        "26 U.S. Code § 1(h)(3)",
        "placeholder",
        "http://web.archive.org/web/20091202182220/http://www.mass.gov/g.pdf",
        "https://www.azleg.gov/viewdocument/?docName=https://www.azleg.gov/ars/43/01072.htm",
        "https://a.gov/view?a=1&url=https://b.gov/2.pdf",
        "https://web.archive.org/web/2021id_/https://a.gov/view?url=https://b.gov",
    ],
)
def test_reference_url_problem_accepts(href):
    assert reference_url_problem(href) is None


@pytest.mark.parametrize(
    "href",
    [
        # Adjacent literals joined by Python.
        "https://a.gov/1.pdf#page=2https://a.gov/2.pdf",
        "https://a.gov/section-1/https://a.gov/2.pdf",
        "https://a.gov/1.pdf ; https://a.gov/2.pdf",
        " https://a.gov/1.pdf",
        "https://a.gov/1.pdf ",
        "https://a.gov/1.pdf, ",
        "https://a.gov/1.pdf, # Line 7",
        "https://a.gov/1.pdf (Line 3)",
        # A fragment truncated before two literals were joined: "=" ends a
        # fragment here, not a query parameter.
        "https://a.gov/1.pdf#page=https://b.gov/2.pdf",
        "https://a.gov/1.pdf#page=2&view=https://b.gov/2.pdf",
        "https://a.gov/view?a=1#page=https://b.gov/2.pdf",
    ],
)
def test_reference_url_problem_rejects(href):
    assert reference_url_problem(href) is not None


@pytest.mark.parametrize(
    "documentation, reference",
    [
        (None, None),
        ("Prose without a link.", None),
        (
            "See the list at https://a.gov/1202#e_3_A.",
            "https://a.gov/1202#e_3_A",
        ),
        (
            "Explained in the manual (https://a.gov/manual.pdf), section 2.",
            [dict(title="Manual", href="https://a.gov/manual.pdf")],
        ),
        (
            "Wikipedia: https://en.wikipedia.org/wiki/Tax_(disambiguation).",
            ("https://en.wikipedia.org/wiki/Tax_(disambiguation)",),
        ),
    ],
)
def test_documentation_url_problems_accepts(documentation, reference):
    assert documentation_url_problems(documentation, reference) == []


@pytest.mark.parametrize(
    "documentation, reference, expected",
    [
        # az_taxable_income before this check: one URL written twice and no
        # reference. The URL is reported once.
        (
            "https://a.gov/140.pdf#page=8\nhttps://a.gov/140.pdf#page=8",
            None,
            [
                "is only URLs: move them into reference",
                "cites 'https://a.gov/140.pdf#page=8', which reference does not list",
            ],
        ),
        # Listing the URL in reference too does not make the documentation
        # prose.
        (
            "https://a.gov/140.pdf#page=8\nhttps://a.gov/140.pdf#page=8",
            "https://a.gov/140.pdf#page=8",
            ["is only URLs: move them into reference"],
        ),
        (
            "https://a.gov/statute.htm",
            "A.R.S. 43-1022",
            [
                "is only URLs: move them into reference",
                "cites 'https://a.gov/statute.htm', which reference does not list",
            ],
        ),
        (
            "See https://a.gov/1.pdf.",
            None,
            ["cites 'https://a.gov/1.pdf', which reference does not list"],
        ),
        (
            "See https://a.gov/1.pdf#page=2https://b.gov/2.pdf",
            ("https://a.gov/1.pdf#page=2", "https://b.gov/2.pdf"),
            [
                "'https://a.gov/1.pdf#page=2https://b.gov/2.pdf' contains more than one URL"
            ],
        ),
    ],
)
def test_documentation_url_problems_rejects(documentation, reference, expected):
    assert documentation_url_problems(documentation, reference) == expected


def test_variable_references_are_single_urls():
    from policyengine_us.system import system

    errors = [
        f"{name}: {href!r} {problem}"
        for name, variable in sorted(system.variables.items())
        for href in _entries(variable.reference)
        if (problem := reference_url_problem(href))
    ]
    assert not errors, "\n".join(errors)


def _module_constants(tree):
    constants = {}
    for statement in tree.body:
        if not isinstance(statement, ast.Assign):
            continue
        try:
            value = ast.literal_eval(statement.value)
        except (ValueError, TypeError, SyntaxError):
            continue
        for target in statement.targets:
            if isinstance(target, ast.Name):
                constants[target.id] = value
    return constants


def _evaluate_reference(node, constants):
    """Evaluate a reference expression built from literals, module-level
    literal constants and dict(title=..., href=...) calls."""
    if isinstance(node, ast.Name):
        return constants[node.id]
    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "dict"
        and not node.args
    ):
        return {
            keyword.arg: _evaluate_reference(keyword.value, constants)
            for keyword in node.keywords
        }
    if isinstance(node, (ast.List, ast.Tuple)):
        return [_evaluate_reference(element, constants) for element in node.elts]
    return ast.literal_eval(node)


def test_variable_documentation_urls_are_references():
    from policyengine_us.system import system

    errors = [
        f"{name}: documentation {problem}"
        for name, variable in sorted(system.variables.items())
        for problem in documentation_url_problems(
            variable.documentation, variable.reference
        )
    ]
    assert not errors, "\n".join(errors)


def _class_attributes(node, constants, names, location, errors):
    """Evaluate the class attributes in ``names`` that ``node`` assigns."""
    attributes = {}
    for statement in node.body:
        if not isinstance(statement, ast.Assign):
            continue
        for target in statement.targets:
            if not (isinstance(target, ast.Name) and target.id in names):
                continue
            try:
                attributes[target.id] = _evaluate_reference(statement.value, constants)
            except (KeyError, ValueError, TypeError, SyntaxError):
                errors.append(
                    f"{location}: {target.id} is not built from literals, so "
                    "this test cannot check it"
                )
    return attributes


def test_reform_variable_references_are_single_urls():
    # Reform variables are defined inside reform factories, so they are not in
    # the baseline system; check their reference and documentation
    # assignments in source instead.
    errors = []
    for path in sorted((REPO / "reforms").rglob("*.py")):
        tree = ast.parse(path.read_text())
        constants = _module_constants(tree)
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            location = f"{path.relative_to(REPO)}::{node.name}"
            attributes = _class_attributes(
                node, constants, {"reference", "documentation"}, location, errors
            )
            for href in _entries(attributes.get("reference")):
                if problem := reference_url_problem(href):
                    errors.append(f"{location}: {href!r} {problem}")
            for problem in documentation_url_problems(
                attributes.get("documentation"), attributes.get("reference")
            ):
                errors.append(f"{location}: documentation {problem}")
    assert not errors, "\n".join(errors)


def test_parameter_reference_hrefs_are_single_urls():
    from policyengine_us.system import system

    errors = set()
    for parameter in system.parameters.get_descendants():
        # References under a dated value's own metadata
        # (values: {<date>: {value, metadata: {reference}}}) live on the
        # parameter's values_list entries, not on the parameter itself.
        sources = [parameter, *(getattr(parameter, "values_list", None) or [])]
        for source in sources:
            metadata = getattr(source, "metadata", None) or {}
            for href in _entries(metadata.get("reference")):
                if problem := reference_url_problem(href):
                    errors.add(f"{parameter.name}: {href!r} {problem}")
    assert not errors, "\n".join(sorted(errors))
