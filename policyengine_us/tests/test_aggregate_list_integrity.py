"""Structural guards for benefit aggregate lists.

The first half covers the state-summing aggregate list parameters, which sum
implemented per-state variables into national aggregates. Three failure modes
have shipped before (see issues #9234 and #9080):
1. A list member that is not a defined variable (silent typo or rename).
2. A member without a state gate, leaking one state's program into every
   state (the dc_ctc bug).
3. A new year block silently dropping members of the previous block, since
   these lists are full-replacement rather than incremental.

The second half covers the benefit aggregates themselves. Structural reforms
used to replace household_benefits or spm_unit_benefits with their own
hardcoded copy of the list, and every copy fell behind: the Trump dividend
(#9430) and dozens of state SSI supplements reached the baseline lists only, so
those reforms dropped them for every household (#10226). Both lists are now
parameters, and a reform adds its own programs to them with
add_to_list_parameter. These tests keep it that way.
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
GEOGRAPHIC_GATES = {"in_la", "in_nyc", "in_riv"}

# Variables that cap an aggregate and add nothing of their own.
CAPPED_AGGREGATES = {"household_child_care_subsidies": {"child_care_subsidies"}}

# Members intentionally removed in a year block, keyed by (list, block date).
# Add an entry here when a credit genuinely ends; do not silently drop
# members when copying a block forward.
ALLOWED_REMOVALS = {
    # NY additional Empire State Child Credit was a supplemental payment
    # in 2021 and 2023 only.
    ("gov/states/household/state_ctcs.yaml", "2022-01-01"): {"ny_additional_ctc"},
    ("gov/states/household/state_ctcs.yaml", "2024-01-01"): {"ny_additional_ctc"},
    # Idaho's child tax credit expires after 2025.
    ("gov/states/household/state_ctcs.yaml", "2026-01-01"): {"id_ctc"},
    # From 2023 MN phases its working family credit down jointly with a new
    # child tax credit (Minn. Stat. 290.0661, subd. 4); mn_wfc models only the
    # pre-2023 working family credit formula.
    ("gov/states/household/state_eitcs.yaml", "2023-01-01"): {"mn_wfc"},
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


def has_state_gate(variables, member):
    """True when a StateCode (or locality) gate appears in the defined_for chain."""
    gate = variables[member].defined_for
    for _ in range(10):
        if gate is None:
            return False
        if re.fullmatch(r"[A-Z]{2}", str(gate)):
            return True  # StateCode gate found
        if gate in GEOGRAPHIC_GATES:
            return True
        gate = variables[gate].defined_for if gate in variables else None
    return False


def aggregate_members(variables, member):
    """The variables an aggregate member sums, or None if it is not an aggregate.

    `adds` is either a list of variable names or a dotted parameter path
    (e.g. gov.hhs.ccdf.child_care_subsidy_programs). A variable in
    CAPPED_AGGREGATES caps the aggregates it names, so those are its members.
    """
    if member in CAPPED_AGGREGATES:
        return CAPPED_AGGREGATES[member]
    adds = getattr(variables[member], "adds", None)
    if not adds:
        return None
    if isinstance(adds, str):
        list_path = adds.replace(".", "/") + ".yaml"
        if not (PARAMETERS / list_path).exists():
            return None
        return members_of(list_path)
    return set(adds)


def is_state_gated(variables, member, depth=0):
    if has_state_gate(variables, member):
        return True
    # An aggregate whose every summed member is state-gated cannot leak one
    # state's program into other states: each addend is zero outside its gate.
    if depth < 3:
        members = aggregate_members(variables, member)
        if members is not None:
            return all(is_state_gated(variables, m, depth + 1) for m in members)
    return False


@pytest.mark.parametrize("list_path", AGGREGATE_LISTS)
def test_members_are_state_gated(list_path, variables):
    ungated = [
        member
        for member in sorted(members_of(list_path))
        if not is_state_gated(variables, member)
    ]
    assert not ungated, (
        f"{list_path} members without a StateCode gate in their "
        f"defined_for chain (dc_ctc-style leak risk): {ungated}"
    )


# household_benefits and spm_unit_benefits need no state gate, because most
# members are national.
BENEFIT_LISTS = [
    "gov/household/household_benefits.yaml",
    "gov/household/spm_unit_benefits.yaml",
]


@pytest.mark.parametrize("list_path", [*AGGREGATE_LISTS, *BENEFIT_LISTS])
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


@pytest.mark.parametrize("list_path", BENEFIT_LISTS)
def test_benefit_list_members_are_defined_variables(list_path, variables):
    undefined = sorted(members_of(list_path) - set(variables))
    assert not undefined, (
        f"{list_path} references variables that do not exist: {undefined}"
    )


@pytest.mark.parametrize("list_path", BENEFIT_LISTS)
def test_benefit_lists_hold_each_member_once(list_path):
    for date, members in blocks_of(list_path):
        repeated = sorted(m for m in set(members) if members.count(m) > 1)
        assert not repeated, f"{list_path} block {date} repeats {repeated}"


# --- Reforms extend the benefit lists rather than copy them ----------------

AGGREGATE_VARIABLES = ("household_benefits", "spm_unit_benefits")


def aggregate_redefinitions(source_text):
    """Names of the benefit aggregates that a module defines a class for.

    Reform modules define their variables inside a create_* function, so the
    walk covers nested classes too.
    """
    return sorted(
        node.name
        for node in ast.walk(ast.parse(source_text))
        if isinstance(node, ast.ClassDef) and node.name in AGGREGATE_VARIABLES
    )


def test_aggregate_redefinitions_finds_a_nested_copy():
    """The scan below is only a guard while it would find a copy."""
    source = (
        "def create_reform():\n"
        "    class spm_unit_benefits(Variable):\n"
        "        pass\n"
        "    class household_benefits(Variable):\n"
        "        pass\n"
        "    class spm_unit_net_income(Variable):\n"
        "        pass\n"
    )
    assert aggregate_redefinitions(source) == [
        "household_benefits",
        "spm_unit_benefits",
    ]


def test_reforms_extend_benefit_lists_rather_than_copy_them():
    copies = [
        f"{source.relative_to(PACKAGE)}::{name}"
        for source in sorted((PACKAGE / "reforms").rglob("*.py"))
        for name in aggregate_redefinitions(source.read_text())
    ]
    assert not copies, (
        f"These reforms redefine a benefit aggregate: {copies}. A copy of the "
        "list falls behind the baseline, and every program it misses drops "
        "out of income for every household the reform applies to (#10226). "
        "Add the reform's own programs to gov.household.household_benefits or "
        "gov.household.spm_unit_benefits with add_to_list_parameter "
        "(policyengine_us/tools/parameters.py) in its modify_parameters."
    )
