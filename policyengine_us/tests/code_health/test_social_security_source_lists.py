"""Source lists name social_security or its components, not both.

`social_security` adds `social_security_dependents`, `_disability`,
`_retirement` and `_survivors`. A source list that names the total and one of
its components counts that component twice. Pennsylvania Child Care Works
listed `social_security`, `social_security_disability` and
`social_security_survivors`, so SSDI and survivor benefits counted twice
(#10408). Several lists name the components on their own, so adding
`- social_security` to one of them would bring the double count back with no
test failing.

Checked: each value block of a parameter YAML file (the entries under one
date key). A block fails when it has an uncommented entry for the total and
one for a component, as block list entries (`- social_security`) or in a
flow-style list. Comments are ignored, so a comment that names a component
does not count. A file may switch from the components to the total in a
later block.

Python readers are not checked: the ones that read both subtract a component
from the total (for example, to exclude SSDI) and do not add it twice.

The check reads text without importing the model.
"""

import re
from pathlib import Path


PACKAGE = Path(__file__).resolve().parents[2]
PARAMETERS = PACKAGE / "parameters"
TOTAL = "social_security"
COMPONENTS = [
    f"{TOTAL}_{kind}"
    for kind in ["dependents", "disability", "retirement", "survivors"]
]
DATE_KEY = re.compile(r"^\s*\d{4}-\d{2}-\d{2}\s*:")


def list_entry_pattern(names: list[str]) -> re.Pattern:
    """A block list entry (`- name`) or a flow list entry (`[a, name]`)."""
    alternatives = "|".join(re.escape(name) for name in names)
    return re.compile(r"(?:^\s*-\s*|[\[,]\s*)(?:" + alternatives + r")\s*(?:$|[\],])")


TOTAL_ENTRY = list_entry_pattern([TOTAL])
COMPONENT_ENTRY = list_entry_pattern(COMPONENTS)


def double_count_lines(text: str) -> list[int]:
    """Lines of total and component entries that share a value block."""
    flagged = set()
    total_lines = []
    component_lines = []

    def close_block():
        if total_lines and component_lines:
            flagged.update(total_lines + component_lines)
        total_lines.clear()
        component_lines.clear()

    for number, line in enumerate(text.splitlines(), start=1):
        code = line.split("#", 1)[0]
        if DATE_KEY.search(code):
            close_block()
        if TOTAL_ENTRY.search(code):
            total_lines.append(number)
        if COMPONENT_ENTRY.search(code):
            component_lines.append(number)
    close_block()
    return sorted(flagged)


def test_detector_flags_total_with_component_and_skips_everything_else():
    assert double_count_lines(
        "values:\n"
        "  2023-01-01:\n"
        "    - social_security\n"
        "    - social_security_disability\n"
        "    - social_security_survivors  # trailing comment\n"
        "  2024-01-01: [ssi, social_security, social_security_retirement]\n"
    ) == [3, 4, 5, 6]
    assert (
        double_count_lines(
            "values:\n"
            "  2023-01-01:\n"
            "    # social_security adds the disability and survivors benefits.\n"
            "    - social_security\n"
            "    # - social_security_disability\n"
            "    - ssi\n"
            "  2024-01-01:\n"
            "    - social_security_disability\n"
            "    - social_security_survivors\n"
        )
        == []
    )
    assert (
        double_count_lines(
            "values:\n"
            "  2023-01-01: [social_security_disability, social_security_dependents]\n"
            "  2024-01-01: [social_security, ssi]\n"
        )
        == []
    )
    assert (
        double_count_lines(
            "values:\n"
            "  2023-01-01:\n"
            "    - social_security\n"
            "    - taxable_social_security\n"
            "    - social_security_disability_insurance_premiums\n"
        )
        == []
    )


def test_source_lists_do_not_name_social_security_and_a_component():
    violations = []
    for path in sorted(PARAMETERS.rglob("*.yaml")):
        text = path.read_text(encoding="utf-8")
        if TOTAL not in text:
            continue
        for line in double_count_lines(text):
            violations.append(f"{path.relative_to(PACKAGE).as_posix()}:{line}")
    assert not violations, (
        "social_security already adds the dependents, disability, retirement "
        "and survivors benefits. List the total or the components, not both, "
        "so each benefit counts once. Entries:\n" + "\n".join(violations)
    )
