"""Structural guards for state-summing aggregate list parameters.

These lists sum implemented per-state variables into national aggregates.
Three failure modes have shipped before (see issues #9234 and #9080):
1. A list member that is not a defined variable (silent typo or rename).
2. A member without a state gate, leaking one state's program into every
   state (the dc_ctc bug).
3. A new year block silently dropping members of the previous block, since
   these lists are full-replacement rather than incremental.
"""

import re
from pathlib import Path

import pytest
import yaml

PARAMETERS = Path(__file__).parent.parent / "parameters"

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
