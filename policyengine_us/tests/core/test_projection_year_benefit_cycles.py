"""Guard against dependency cycles that only open in projection years.

Issue #9534: from 2027 Medicaid eligibility consults the community engagement
requirement, whose SNAP pass-through reads SNAP. Any SNAP input that reads
Medicaid enrollment then closes a loop that does not exist in 2026, so the
baseline computes today and raises ``CycleError`` for every household in the
affected state from 2027 on. Indiana and Kansas hit this when SNAP unearned
income began counting state SSI supplements whose eligibility reads Medicaid
enrollment.

policyengine-core detects cycles at run time, and a state formula only runs
when some entity is in its ``defined_for`` state. One simulation holding a
household in every state therefore exercises every state's formulas at once.
When it fails, the test reruns state by state to name the offenders.
"""

import pytest

from policyengine_us import Simulation

STATES = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL", "GA", "HI",
    "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN",
    "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH",
    "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA",
    "WV", "WI", "WY",
]  # fmt: skip

# The Medicaid community engagement requirement starts in 2027; 2030 checks
# that nothing else opens later in the projection window.
PROJECTION_YEARS = (2027, 2030)

# Outputs that sit on top of the SNAP, Medicaid and state supplement graphs.
OUTPUTS = ("snap", "medicaid", "spm_unit_benefits", "household_net_income")


def _situation(year: int, states: list[str]) -> dict:
    """One three-generation household per state.

    A working-age adult, a young child and an aged Social Security recipient
    put the expansion adult, child, and aged, blind or disabled pathways in
    the same simulation.
    """
    situation = {
        key: {}
        for key in (
            "people",
            "households",
            "tax_units",
            "spm_units",
            "families",
            "marital_units",
        )
    }
    for state in states:
        adult, child, elder = (f"{state}_adult", f"{state}_child", f"{state}_elder")
        situation["people"][adult] = {
            "age": {year: 40},
            "employment_income": {year: 5_000},
        }
        situation["people"][child] = {"age": {year: 4}}
        situation["people"][elder] = {
            "age": {year: 70},
            "social_security": {year: 6_000},
        }
        members = [adult, child, elder]
        situation["households"][state] = {
            "members": members,
            "state_code": {year: state},
        }
        for group in ("tax_units", "spm_units", "families"):
            situation[group][state] = {"members": members}
        for person in members:
            situation["marital_units"][person] = {"members": [person]}
    return situation


def _failure(year: int, states: list[str]) -> str | None:
    """Return a short description of the first failure, or None."""
    for output in OUTPUTS:
        try:
            # A fresh simulation per output: an earlier success would cache
            # part of the graph and could hide a cycle entered from here.
            Simulation(situation=_situation(year, states)).calculate(output, year)
        except Exception as error:  # noqa: BLE001 - report any failure type
            first_line = str(error).splitlines()[0] if str(error) else ""
            return f"{output}: {type(error).__name__}: {first_line}"
    return None


@pytest.mark.parametrize("year", PROJECTION_YEARS)
def test_benefits_compute_in_every_state_in_projection_years(year):
    if _failure(year, STATES) is None:
        return
    offenders = {
        state: failure
        for state in STATES
        if (failure := _failure(year, [state])) is not None
    }
    pytest.fail(
        f"Benefit outputs fail to compute for {year} in "
        f"{len(offenders)} state(s): {offenders}"
    )


BEFORE_WORK_REQUIREMENT_VARIABLES = (
    "is_medicaid_eligible_before_work_requirements",
    "medicaid_enrolled_before_work_requirements",
)

# The only formulas allowed to read Medicaid status before work requirements.
# Each pays people the community engagement requirement cannot reach (SSI
# recipients, or the aged, blind or disabled), which is what makes the
# substitution exact. Before adding a reader, confirm the same holds for it;
# an expansion adult read through these variables would silently skip the
# work requirement.
ALLOWED_READERS = {
    "gov/hhs/medicaid/eligibility/is_medicaid_eligible_before_work_requirements.py",
    "gov/hhs/medicaid/medicaid_enrolled_before_work_requirements.py",
    "gov/states/in/fssa/ssp/in_ssp_rcap_eligible.py",
    "gov/states/in/fssa/ssp/in_ssp_sapn_eligible.py",
    "gov/states/ks/kdhe/sspp/ks_sspp_eligible.py",
}


def test_before_work_requirements_readers_are_confined():
    from pathlib import Path

    import policyengine_us

    package = Path(policyengine_us.__file__).parent
    readers = set()
    for folder, pattern in (("variables", "*.py"), ("parameters", "*.yaml")):
        for path in (package / folder).rglob(pattern):
            text = path.read_text()
            if any(name in text for name in BEFORE_WORK_REQUIREMENT_VARIABLES):
                readers.add(path.relative_to(package / folder).as_posix())
    assert readers == ALLOWED_READERS, (
        "Medicaid status before work requirements is exact only for people "
        "the community engagement requirement cannot reach. Unexpected "
        f"readers: {sorted(readers - ALLOWED_READERS)}; missing: "
        f"{sorted(ALLOWED_READERS - readers)}"
    )


def test_before_work_requirements_matches_eligibility_without_a_requirement():
    """With no work requirement in effect the two concepts must agree.

    is_medicaid_eligible_before_work_requirements restates the categorical,
    immigration and state-funded tests of is_medicaid_eligible. This catches
    drift if one formula gains a condition the other lacks.
    """
    year = 2026
    simulation = Simulation(situation=_situation(year, STATES))
    before = simulation.calculate("is_medicaid_eligible_before_work_requirements", year)
    eligible = simulation.calculate("is_medicaid_eligible", year)
    assert (before == eligible).all()
    assert eligible.any() and not eligible.all()
