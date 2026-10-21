"""Income flows read total_unemployment_compensation, not the raw input.

`unemployment_compensation` is the reported (uprated) input.
`total_unemployment_compensation` uses that amount when it is nonzero and
otherwise falls back to the modeled state unemployment insurance programs, so
a formula or parameter source list that reads the raw input misses modeled UI.
After the readers moved to the total, later merges of main brought in 13 new
raw readers, so this check fails on any new one.

Checked:
- Parameter YAML: a block list entry `- unemployment_compensation` or a
  flow-style list containing it. Comments are ignored, so commented-out
  entries do not count.
- Python in the package (tests excluded): a string constant exactly equal to
  "unemployment_compensation". That covers gross-income-source appends,
  source lists, `adds`, `add()` and direct entity reads. Dotted parameter
  paths, longer variable names and comments are not that constant.

Allowed: the Python files in ALLOWED_PYTHON_FILES, which need the raw input
itself. The variable's own definition names it as a class, not a string, so it
needs no entry. To add a reader that truly needs the reported-only amount, list
its file there with the reason.

The check reads text and syntax trees without importing the model.
"""

import ast
import re
from pathlib import Path


PACKAGE = Path(__file__).resolve().parents[2]
PARAMETERS = PACKAGE / "parameters"
TESTS = PACKAGE / "tests"
RAW = "unemployment_compensation"

ALLOWED_PYTHON_FILES = {
    # Input uprating keeps the raw input on the SOI series.
    "reforms/ssa/trustees_2025.py": "uprating under the 2025 Trustees reform",
    "tools/default_uprating.py": "default input uprating",
    # TAXSIM supplies reported unemployment compensation as an input.
    "tools/taxsim/generate_taxsim_tests.py": "TAXSIM test generator input",
    # The adapter that reads the reported amount and falls back to modeled UI.
    "variables/household/income/person/total_unemployment_compensation.py": (
        "total_unemployment_compensation formula"
    ),
}

# A raw entry in a block list (`- unemployment_compensation`) or a flow list
# (`[a, unemployment_compensation]`), after the comment is removed.
YAML_RAW_ENTRY = re.compile(
    r"(?:^\s*-\s*|[\[,]\s*)" + RAW + r"\s*(?:$|[\],])",
)


def raw_yaml_lines(text: str) -> list[int]:
    """Line numbers of uncommented raw list entries in parameter YAML text."""
    lines = []
    for number, line in enumerate(text.splitlines(), start=1):
        code = line.split("#", 1)[0]
        if YAML_RAW_ENTRY.search(code):
            lines.append(number)
    return lines


def raw_python_lines(source: str, filename: str = "<string>") -> list[int]:
    """Line numbers of string constants equal to the raw input name."""
    tree = ast.parse(source, filename=filename)
    return sorted(
        node.lineno
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and node.value == RAW
    )


def package_python_files():
    for path in sorted(PACKAGE.rglob("*.py")):
        if TESTS in path.parents:
            continue
        yield path


def test_detectors_flag_raw_readers_and_skip_everything_else():
    assert raw_yaml_lines(
        "values:\n"
        "  2025-01-01:\n"
        "    - ssi\n"
        "    - unemployment_compensation\n"
        "    - unemployment_compensation  # trailing comment\n"
        "  2026-01-01: [ssi, unemployment_compensation]\n"
    ) == [4, 5, 6]
    assert (
        raw_yaml_lines(
            "values:\n"
            "  2025-01-01:\n"
            "    - total_unemployment_compensation\n"
            "    # - unemployment_compensation\n"
            "    # unemployment_compensation is excluded\n"
            "    - taxable_unemployment_compensation\n"
            "  2026-01-01: [ssi, total_unemployment_compensation]\n"
            "metadata:\n"
            "  parameter: calibration.gov.cbo.unemployment_compensation\n"
        )
        == []
    )
    assert raw_python_lines(
        'sources.append("unemployment_compensation")\n'
        'adds = ["employment_income", "unemployment_compensation"]\n'
        'uc = person("unemployment_compensation", period)\n'
    ) == [1, 2, 3]
    assert (
        raw_python_lines(
            "class unemployment_compensation(Variable):\n"
            '    uprating = "calibration.gov.irs.soi.unemployment_compensation"\n'
            "# unemployment_compensation in a comment\n"
            'uc = person("total_unemployment_compensation", period)\n'
            "x = p.unemployment_compensation.agi_reduction\n"
        )
        == []
    )


def test_parameter_source_lists_do_not_read_raw_unemployment_compensation():
    violations = []
    for path in sorted(PARAMETERS.rglob("*.yaml")):
        text = path.read_text(encoding="utf-8")
        if RAW not in text:
            continue
        for line in raw_yaml_lines(text):
            violations.append(f"{path.relative_to(PACKAGE).as_posix()}:{line}")
    assert not violations, (
        "List total_unemployment_compensation, not the reported-only "
        "unemployment_compensation input, so modeled state unemployment "
        "insurance counts. Raw entries:\n" + "\n".join(violations)
    )


def test_python_does_not_read_raw_unemployment_compensation():
    violations = []
    for path in package_python_files():
        relative = path.relative_to(PACKAGE).as_posix()
        if relative in ALLOWED_PYTHON_FILES:
            continue
        source = path.read_text(encoding="utf-8")
        if RAW not in source:
            continue
        for line in raw_python_lines(source, filename=str(path)):
            violations.append(f"{relative}:{line}")
    assert not violations, (
        "Read or append total_unemployment_compensation, not the "
        "reported-only unemployment_compensation input, so modeled state "
        "unemployment insurance counts. If a reader truly needs the reported "
        "amount, add its file to ALLOWED_PYTHON_FILES with the reason. Raw "
        "reads:\n" + "\n".join(violations)
    )


def test_allowed_python_files_still_read_the_raw_input():
    stale = [
        relative
        for relative in ALLOWED_PYTHON_FILES
        if not (PACKAGE / relative).exists()
        or not raw_python_lines((PACKAGE / relative).read_text(encoding="utf-8"))
    ]
    assert not stale, (
        "These ALLOWED_PYTHON_FILES entries no longer read the raw "
        "unemployment_compensation input; remove them:\n" + "\n".join(stale)
    )
