"""Benefit income flows read military_retirement_income, not the raw input.

`military_retirement_pay` is a military retiree's own pay. Military Survivor
Benefit Plan annuities are a separate input, `military_retirement_pay_survivors`
(#10182), and `military_retirement_income` adds the two. A benefit program
whose income list names only `military_retirement_pay` misses a survivor's
annuity. After the benefit lists moved to the total (#10317), open PRs still
added new lists that named the raw input, so this check fails on any new one.

Tax rules often treat a retiree's pay and a survivor's annuity differently, so
tax-side readers keep the raw input: parameter and variable files under
`gov/irs/` or under any `tax/` folder.

Checked outside the tax side:
- Parameter YAML: a block list entry `- military_retirement_pay` or a
  flow-style list containing it, unless the same file also lists
  `military_retirement_pay_survivors`. Comments are ignored, so commented-out
  entries and comments that name the input do not count.
- Python in the package (tests excluded): a string constant exactly equal to
  "military_retirement_pay". That covers source lists, `adds`, `add()` and
  direct entity reads. Longer variable names and comments are not that
  constant.

Allowed: the Python files in ALLOWED_PYTHON_FILES, which need the raw input
itself. The variable's own definition names it as a class, not a string, so it
needs no entry.

The check reads text and syntax trees without importing the model.
"""

import ast
import re
from pathlib import Path


PACKAGE = Path(__file__).resolve().parents[2]
PARAMETERS = PACKAGE / "parameters"
TESTS = PACKAGE / "tests"
RAW = "military_retirement_pay"
SURVIVORS = "military_retirement_pay_survivors"

ALLOWED_PYTHON_FILES = {
    # The total that benefit programs read.
    "variables/household/income/person/retirement/military_retirement_income.py": (
        "military_retirement_income adds the retiree pay and survivor annuities"
    ),
}


def list_entry_pattern(name: str) -> re.Pattern:
    """A block list entry (`- name`) or a flow list entry (`[a, name]`)."""
    return re.compile(r"(?:^\s*-\s*|[\[,]\s*)" + name + r"\s*(?:$|[\],])")


YAML_RAW_ENTRY = list_entry_pattern(RAW)
YAML_SURVIVORS_ENTRY = list_entry_pattern(SURVIVORS)


def is_tax_side(relative: Path) -> bool:
    """Whether a path under the package or parameter tree is a tax rule."""
    parts = relative.parts
    under_irs = any(parts[i : i + 2] == ("gov", "irs") for i in range(len(parts)))
    return under_irs or "tax" in parts[:-1]


def raw_yaml_lines(text: str) -> list[int]:
    """Uncommented raw entries in YAML text that lists no survivor annuities."""
    raw_lines = []
    lists_survivors = False
    for number, line in enumerate(text.splitlines(), start=1):
        code = line.split("#", 1)[0]
        if YAML_RAW_ENTRY.search(code):
            raw_lines.append(number)
        if YAML_SURVIVORS_ENTRY.search(code):
            lists_survivors = True
    return [] if lists_survivors else raw_lines


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
        "    - pension_income\n"
        "    - military_retirement_pay\n"
        "    - military_retirement_pay  # trailing comment\n"
        "  2026-01-01: [pension_income, military_retirement_pay]\n"
    ) == [4, 5, 6]
    assert (
        raw_yaml_lines(
            "values:\n"
            "  2025-01-01:\n"
            "    - military_retirement_income\n"
            "    # - military_retirement_pay\n"
            "    # military_retirement_pay is a separate input\n"
            "  2026-01-01: [pension_income, military_retirement_income]\n"
        )
        == []
    )
    assert (
        raw_yaml_lines(
            "values:\n"
            "  2025-01-01:\n"
            "    - military_retirement_pay\n"
            "    - military_retirement_pay_survivors\n"
        )
        == []
    )
    assert raw_yaml_lines(
        "values:\n"
        "  2025-01-01:\n"
        "    - military_retirement_pay\n"
        "    # - military_retirement_pay_survivors\n"
    ) == [3]
    assert raw_python_lines(
        'sources.append("military_retirement_pay")\n'
        'adds = ["pension_income", "military_retirement_pay"]\n'
        'pay = person("military_retirement_pay", period)\n'
    ) == [1, 2, 3]
    assert (
        raw_python_lines(
            "class military_retirement_pay(Variable):\n"
            '    label = "Military retirement pay"\n'
            "# military_retirement_pay in a comment\n"
            'pay = person("military_retirement_income", period)\n'
            'pay = person("military_retirement_pay_survivors", period)\n'
        )
        == []
    )
    assert is_tax_side(Path("gov/irs/gross_income/sources.yaml"))
    assert is_tax_side(Path("gov/states/mo/tax/income/subtractions/x.yaml"))
    assert is_tax_side(Path("variables/gov/states/vt/tax/income/x.py"))
    assert not is_tax_side(Path("gov/states/tx/tanf/income/sources/unearned.yaml"))
    assert not is_tax_side(Path("gov/states/ga/dfcs/liheap/income/tax.yaml"))


def test_benefit_source_lists_do_not_read_raw_military_retirement_pay():
    violations = []
    for path in sorted(PARAMETERS.rglob("*.yaml")):
        if is_tax_side(path.relative_to(PARAMETERS)):
            continue
        text = path.read_text(encoding="utf-8")
        if RAW not in text:
            continue
        for line in raw_yaml_lines(text):
            violations.append(f"{path.relative_to(PACKAGE).as_posix()}:{line}")
    assert not violations, (
        "List military_retirement_income, not the retiree-only "
        "military_retirement_pay input, so military Survivor Benefit Plan "
        "annuities count. Raw entries:\n" + "\n".join(violations)
    )


def test_benefit_python_does_not_read_raw_military_retirement_pay():
    violations = []
    for path in package_python_files():
        relative = path.relative_to(PACKAGE)
        if relative.as_posix() in ALLOWED_PYTHON_FILES or is_tax_side(relative):
            continue
        source = path.read_text(encoding="utf-8")
        if RAW not in source:
            continue
        for line in raw_python_lines(source, filename=str(path)):
            violations.append(f"{relative.as_posix()}:{line}")
    assert not violations, (
        "Read or add military_retirement_income, not the retiree-only "
        "military_retirement_pay input, so military Survivor Benefit Plan "
        "annuities count. If a reader truly needs the retiree's pay alone, "
        "add its file to ALLOWED_PYTHON_FILES with the reason. Raw reads:\n"
        + "\n".join(violations)
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
        "military_retirement_pay input; remove them:\n" + "\n".join(stale)
    )
