"""Every reference entry must link to exactly one URL.

Python joins adjacent string literals, so a ``reference`` tuple written
without commas between its URLs collapses into one string. policyengine-core
wraps that string as a one-element list, and it renders as a single dead link.
"""

import ast
import re

import pytest

from policyengine_us.model_api import REPO

URL = re.compile(r"https?://")
# A URL may embed another URL as a Wayback Machine snapshot target
# (web.archive.org/web/<timestamp>/https://...) or as a query value
# (viewdocument/?docName=https://...).
EMBEDDED_URL_PREFIX = re.compile(r"(?:web\.archive\.org/web/\d+[a-z_]*/|=)$")


def reference_url_problem(href):
    """Describe what is wrong with one reference string, or return None.

    Strings without a URL (plain-text citations) are accepted. A string with a
    URL must be exactly one bare URL: no second URL fused onto it, no
    surrounding whitespace, and no trailing annotation text or separators.
    """
    if not isinstance(href, str):
        return None
    starts = [match.start() for match in URL.finditer(href)]
    if not starts:
        return None
    top_level = [i for i in starts if not EMBEDDED_URL_PREFIX.search(href[:i])]
    if len(top_level) > 1:
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


@pytest.mark.parametrize(
    "href",
    [
        "https://www.dfa.arkansas.gov/wp-content/uploads/a.pdf#page=3",
        "26 U.S. Code § 1(h)(3)",
        "placeholder",
        "http://web.archive.org/web/20091202182220/http://www.mass.gov/g.pdf",
        "https://www.azleg.gov/viewdocument/?docName=https://www.azleg.gov/ars/43/01072.htm",
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
    ],
)
def test_reference_url_problem_rejects(href):
    assert reference_url_problem(href) is not None


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


def test_reform_variable_references_are_single_urls():
    # Reform variables are defined inside reform factories, so they are not in
    # the baseline system; check their reference assignments in source instead.
    errors = []
    for path in sorted((REPO / "reforms").rglob("*.py")):
        tree = ast.parse(path.read_text())
        constants = _module_constants(tree)
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            for statement in node.body:
                if not (
                    isinstance(statement, ast.Assign)
                    and any(
                        isinstance(target, ast.Name) and target.id == "reference"
                        for target in statement.targets
                    )
                ):
                    continue
                location = f"{path.relative_to(REPO)}::{node.name}"
                try:
                    reference = _evaluate_reference(statement.value, constants)
                except (KeyError, ValueError, TypeError, SyntaxError):
                    errors.append(
                        f"{location}: reference is not built from literals, so "
                        "this test cannot check it"
                    )
                    continue
                for href in _entries(reference):
                    if problem := reference_url_problem(href):
                        errors.append(f"{location}: {href!r} {problem}")
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
