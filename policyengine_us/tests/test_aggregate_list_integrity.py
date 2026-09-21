"""Structural guards for benefit aggregate lists.

The first half covers the state-summing aggregate list parameters, which sum
implemented per-state variables into national aggregates. Three failure modes
have shipped before (see issues #9234 and #9080):
1. A list member that is not a defined variable (silent typo or rename).
2. A member without a state gate, leaking one state's program into every
   state (the dc_ctc bug).
3. A new year block silently dropping members of the previous block, since
   these lists are full-replacement rather than incremental.

The second half covers the benefit aggregates themselves. Several structural
reforms replace household_benefits or spm_unit_benefits with their own
hardcoded list, so a contributed program added to the baseline aggregates is
silently dropped under those reforms unless it is added to every copy. That
shipped with the Trump dividend, which #9430 added to the baseline lists only.
"""

import ast
import re
from pathlib import Path

import pytest
import yaml

PACKAGE = Path(__file__).parent.parent
PARAMETERS = PACKAGE / "parameters"

AGGREGATE_LISTS = [
    "gov/states/household/state_ctcs.yaml",
    "gov/states/household/state_eitcs.yaml",
    "gov/states/household/state_cdccs.yaml",
    "gov/hhs/ccdf/child_care_subsidy_programs.yaml",
    "gov/household/household_state_benefits.yaml",
]

# Gates that restrict a variable geographically without a StateCode
# defined_for (locality booleans).
GEOGRAPHIC_GATES = {"in_la", "in_nyc"}

# Members intentionally removed in a year block, keyed by (list, block date).
# Add an entry here when a credit genuinely ends; do not silently drop
# members when copying a block forward.
ALLOWED_REMOVALS = {
    # NY additional Empire State Child Credit was a supplemental payment
    # in 2021 and 2023 only.
    ("gov/states/household/state_ctcs.yaml", "2022-01-01"): {"ny_additional_ctc"},
    ("gov/states/household/state_ctcs.yaml", "2024-01-01"): {"ny_additional_ctc"},
    # VT restructured its CDCC into a single vt_cdcc in 2022.
    ("gov/states/household/state_cdccs.yaml", "2022-01-01"): {
        "vt_low_income_cdcc",
        "vt_nonrefundable_cdcc",
    },
}


@pytest.fixture(scope="module")
def variables():
    from policyengine_us.system import system

    return system.variables


def blocks_of(list_path):
    raw = yaml.load((PARAMETERS / list_path).read_text(), Loader=yaml.BaseLoader)
    return sorted(
        (date, members)
        for date, members in raw["values"].items()
        if isinstance(members, list)
    )


def members_of(list_path):
    return {m for _, members in blocks_of(list_path) for m in members}


@pytest.mark.parametrize("list_path", AGGREGATE_LISTS)
def test_members_are_defined_variables(list_path, variables):
    undefined = sorted(members_of(list_path) - set(variables))
    assert not undefined, (
        f"{list_path} references variables that do not exist: {undefined}"
    )


@pytest.mark.parametrize("list_path", AGGREGATE_LISTS)
def test_members_are_state_gated(list_path, variables):
    ungated = []
    for member in sorted(members_of(list_path)):
        gate = variables[member].defined_for
        for _ in range(10):
            if gate is None:
                break
            if re.fullmatch(r"[A-Z]{2}", str(gate)):
                break  # StateCode gate found
            if gate in GEOGRAPHIC_GATES:
                break
            gate = variables[gate].defined_for if gate in variables else None
        else:
            gate = None
        if gate is None:
            ungated.append(member)
    assert not ungated, (
        f"{list_path} members without a StateCode gate in their "
        f"defined_for chain (dc_ctc-style leak risk): {ungated}"
    )


@pytest.mark.parametrize("list_path", AGGREGATE_LISTS)
def test_no_silent_removals_between_year_blocks(list_path):
    blocks = blocks_of(list_path)
    for (_, prev), (date, curr) in zip(blocks, blocks[1:]):
        removed = set(prev) - set(curr)
        allowed = ALLOWED_REMOVALS.get((list_path, date), set())
        unexpected = sorted(removed - allowed)
        assert not unexpected, (
            f"{list_path} block {date} drops {unexpected} from the "
            "previous block. These lists are full replacements: copy all "
            "prior members forward, or record an intentional removal in "
            "ALLOWED_REMOVALS in this test."
        )


# --- Reform-side copies of the benefit aggregates -------------------------

AGGREGATE_VARIABLES = ("household_benefits", "spm_unit_benefits")

BASELINE_SPM_BENEFITS_SOURCE = (
    PACKAGE / "variables/household/income/spm_unit/spm_unit_benefits.py"
)
BASELINE_HOUSEHOLD_BENEFITS_LIST = "gov/household/household_benefits.yaml"

# Contributed programs that a reform may legitimately leave out of its own
# copy of an aggregate, keyed by (reform source path, variable name).
ALLOWED_REFORM_OMISSIONS: dict[tuple[str, str], set[str]] = {}


def contrib_variable_names():
    """Variables defined under variables/contrib, by source-file location."""
    names = set()
    for source in (PACKAGE / "variables/contrib").rglob("*.py"):
        names.update(re.findall(r"^class (\w+)\(Variable\)", source.read_text(), re.M))
    return names


def benefits_lists_in(source_path):
    """(variable name, members) for each literal BENEFITS list in a file.

    Only plain list literals are returned. A reform that rebuilds its list
    from the parameter (or filters an existing one) has no literal to check.
    """
    tree = ast.parse(source_path.read_text())
    found = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef) or node.name not in AGGREGATE_VARIABLES:
            continue
        for statement in ast.walk(node):
            if not isinstance(statement, ast.Assign):
                continue
            targets = [t.id for t in statement.targets if isinstance(t, ast.Name)]
            if "BENEFITS" not in targets:
                continue
            if not isinstance(statement.value, ast.List):
                continue
            found.append(
                (
                    node.name,
                    [
                        element.value
                        for element in statement.value.elts
                        if isinstance(element, ast.Constant)
                    ],
                )
            )
    return found


def reform_aggregate_overrides():
    cases = []
    for source in sorted((PACKAGE / "reforms").rglob("*.py")):
        for variable_name, members in benefits_lists_in(source):
            cases.append(
                (str(source.relative_to(PACKAGE)), variable_name, tuple(members))
            )
    return cases


REFORM_AGGREGATE_OVERRIDES = reform_aggregate_overrides()


def baseline_members(variable_name):
    if variable_name == "spm_unit_benefits":
        lists = benefits_lists_in(BASELINE_SPM_BENEFITS_SOURCE)
        assert len(lists) == 1, "baseline spm_unit_benefits changed shape"
        return set(lists[0][1])
    return members_of(BASELINE_HOUSEHOLD_BENEFITS_LIST)


def test_reform_aggregate_overrides_are_discovered():
    """The scan below is only a guard while it still finds the copies."""
    found = {(path, variable) for path, variable, _ in REFORM_AGGREGATE_OVERRIDES}
    assert len(found) >= 6, (
        f"expected the reform-side benefit aggregate copies, found {sorted(found)}"
    )


@pytest.mark.parametrize(
    "source_path,variable_name,members",
    REFORM_AGGREGATE_OVERRIDES,
    ids=[f"{path}::{variable}" for path, variable, _ in REFORM_AGGREGATE_OVERRIDES],
)
def test_reform_aggregates_keep_baseline_contrib_entries(
    source_path, variable_name, members
):
    contrib = contrib_variable_names()
    expected = baseline_members(variable_name) & contrib
    allowed = ALLOWED_REFORM_OMISSIONS.get((source_path, variable_name), set())
    missing = sorted(expected - set(members) - allowed)
    assert not missing, (
        f"{source_path} redefines {variable_name} with its own list and drops "
        f"{missing}, which the baseline {variable_name} counts. Add the entry "
        "here too, or record a deliberate omission in "
        "ALLOWED_REFORM_OMISSIONS in this test."
    )
