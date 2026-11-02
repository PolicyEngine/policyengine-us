"""Properties of EITC eligibility for a filer whose qualifying child lacks a
valid SSN.

From 2021 (ARPA section 9622 struck former IRC 32(c)(1)(F)), such a filer is
an eligible individual with a qualifying child (32(c)(1)(A)(i)); the child is
left out only of the amount (32(c)(3)(D), (m)). So from 2021:

1. Adding a qualifying child without an SSN never lowers the EITC.
2. When the SSN-filtered child count is zero, the EITC never exceeds the
   zero-child maximum.

Before 2021 the model keeps the identification-filtered count, so:

3. A filer with only a child without an SSN gets the same EITC as the same
   filer alone.

Each example builds one simulation in which every filer appears twice: alone
and with a child without an SSN.
"""

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import CountryTaxBenefitSystem, Simulation

SYSTEM = CountryTaxBenefitSystem()

FILER = st.fixed_dictionaries(
    {
        "age": st.integers(min_value=16, max_value=80),
        "student": st.booleans(),
        "earnings": st.integers(min_value=0, max_value=30_000),
    }
)


def _simulate(year, filers):
    people, tax_units, households = {}, {}, {}
    for i, filer in enumerate(filers):
        for with_child in (False, True):
            name = f"u{i}_{int(with_child)}"
            members = [f"{name}_f"]
            people[f"{name}_f"] = {
                "age": {year: filer["age"]},
                "is_full_time_student": {year: filer["student"]},
                "is_eitc_qualifying_child": {year: False},
                "ssn_card_type": {year: "CITIZEN"},
                "employment_income": {year: filer["earnings"]},
            }
            if with_child:
                members.append(f"{name}_c")
                people[f"{name}_c"] = {
                    "age": {year: 2},
                    "is_tax_unit_dependent": {year: True},
                    "is_eitc_qualifying_child": {year: True},
                    "ssn_card_type": {year: "NONE"},
                }
            tax_units[name] = {
                "members": members,
                "filing_status": {year: "SINGLE"},
                "would_file_taxes_voluntarily": {year: True},
                "takes_up_eitc": {year: True},
            }
            households[name] = {"members": members, "state_code": {year: "TX"}}
    sim = Simulation(
        situation={
            "people": people,
            "tax_units": tax_units,
            "households": households,
        }
    )
    eitc = sim.calculate("eitc", year)
    count = sim.calculate("eitc_child_count", year)
    return eitc[0::2], eitc[1::2], count[1::2]


SETTINGS = settings(
    max_examples=8,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow],
)


@SETTINGS
@given(
    year=st.sampled_from([2021, 2022, 2023, 2024, 2025]),
    filers=st.lists(FILER, min_size=1, max_size=10),
)
def test_child_without_ssn_never_lowers_eitc_from_2021(year, filers):
    alone, with_child, count = _simulate(year, filers)
    zero_child_max = SYSTEM.parameters.gov.irs.credits.eitc.max(f"{year}-01-01").calc(0)
    assert (count == 0).all()
    assert (with_child >= alone - 0.01).all()
    assert (with_child <= zero_child_max + 0.01).all()


@SETTINGS
@given(
    year=st.sampled_from([2018, 2019, 2020]),
    filers=st.lists(FILER, min_size=1, max_size=10),
)
def test_child_without_ssn_changes_nothing_before_2021(year, filers):
    alone, with_child, _ = _simulate(year, filers)
    assert (abs(with_child - alone) < 0.01).all()
