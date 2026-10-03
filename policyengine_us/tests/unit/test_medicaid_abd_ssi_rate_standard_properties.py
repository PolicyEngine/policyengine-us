"""Properties of the Medicaid income standard for aged, blind, and disabled
people who do not receive SSI, in states that set it at the SSI rate.

States that have not elected the poverty-level group of 42 U.S.C. 1396a(m)
are flagged in the parameter
`gov.hhs.medicaid.eligibility.categories.senior_or_disabled.income.limit.uses_ssi_federal_benefit_rate`.
In those states the standard is the SSI federal benefit rate, a monthly
dollar amount for an individual or a couple, not a share of the poverty
guideline. Montana's manual (ABD 008) is the model case: its standards "are
the benefit amounts paid by the Social Security Administration to
Supplemental Security Income (SSI) cash recipients", applicants "with monthly
countable income equal to or less than these income standards are
categorically needy Medicaid eligible", and applicants "in excess of these
income standards are not categorically needy eligible".

Each test evaluates a grid of households in one vectorized simulation and
checks, for every flagged state and every year from 2018 to 2026:

- the limit equals twelve times the rate SSA published for that year, for an
  individual and for a couple (a differential check against SSA's table);
- income eligibility is true exactly when countable income is at or below
  that amount, so it never rises with income;
- for an aged person with no resources and only Social Security income, the
  pathway never covers anyone whose countable income is over the SSI rate,
  and everyone under the rate receives SSI, so no band of income gets
  Medicaid without SSI just above the rate.

A last test checks that states which are not flagged keep the share of the
poverty guideline that their parameter gives.
"""

import numpy as np
import pytest

from policyengine_us import CountryTaxBenefitSystem, Simulation
from policyengine_us.variables.household.demographic.geographic.state_code import (
    StateCode,
)

# SSA, "SSI Federal Payment Amounts" (https://www.ssa.gov/oact/cola/SSIamts.html):
# monthly maximum for an eligible individual and an eligible couple.
SSA_MONTHLY_RATES = {
    2018: (750, 1_125),
    2019: (771, 1_157),
    2020: (783, 1_175),
    2021: (794, 1_191),
    2022: (841, 1_261),
    2023: (914, 1_371),
    2024: (943, 1_415),
    2025: (967, 1_450),
    2026: (994, 1_491),
}
YEARS = sorted(SSA_MONTHLY_RATES)
# The 50 states and the District of Columbia.
STATES = [
    state.name
    for state in StateCode
    if state.name not in ("AA", "AE", "AP", "GU", "MP", "PR", "PW", "VI")
]
# Annual dollars around the standard: far below, one month's dollar below,
# exactly at, one dollar above, and well above.
OFFSETS = [-6_000, -12, -1, 0, 1, 12, 42, 600, 6_000]

SYSTEM = CountryTaxBenefitSystem()


def limit_parameters(year):
    return SYSTEM.parameters(
        f"{year}-01-01"
    ).gov.hhs.medicaid.eligibility.categories.senior_or_disabled.income.limit


def flagged_states(year):
    flags = limit_parameters(year).uses_ssi_federal_benefit_rate
    return [state for state in STATES if flags[state]]


def unit_simulation(year, states, couple, per_person_inputs=None):
    """One marital unit per entry of `states`; two spouses when `couple`."""
    per_person_inputs = per_person_inputs or {}
    situation = {
        "people": {},
        "tax_units": {},
        "marital_units": {},
        "spm_units": {},
        "families": {},
        "households": {},
    }
    for i, state in enumerate(states):
        members = [f"p{i}_1"] + ([f"p{i}_2"] if couple else [])
        for member in members:
            situation["people"][member] = {"age": {year: 70}}
        for name, values in per_person_inputs.items():
            situation["people"][members[0]][name] = {year: float(values[i])}
        for entity in ("tax_units", "marital_units", "spm_units", "families"):
            situation[entity][f"{entity}_{i}"] = {"members": members}
        situation["households"][f"household_{i}"] = {
            "members": members,
            "state_code": {year: state},
        }
    return Simulation(situation=situation)


def test_some_state_is_flagged():
    assert "MT" in flagged_states(2026)


@pytest.mark.parametrize("couple", [False, True])
@pytest.mark.parametrize("year", YEARS)
def test_limit_is_twelve_times_the_published_ssi_rate(year, couple):
    states = flagged_states(year)
    simulation = unit_simulation(year, states, couple)
    limit = simulation.calculate(
        "medicaid_optional_senior_or_disabled_income_limit", year
    )
    individual, couple_rate = SSA_MONTHLY_RATES[year]
    expected = 12 * (couple_rate if couple else individual)
    np.testing.assert_array_equal(limit, expected)


@pytest.mark.parametrize("couple", [False, True])
@pytest.mark.parametrize("year", YEARS)
def test_income_eligible_exactly_when_at_or_below_the_ssi_rate(year, couple):
    individual, couple_rate = SSA_MONTHLY_RATES[year]
    standard = 12 * (couple_rate if couple else individual)
    flagged = flagged_states(year)
    states = [state for state in flagged for _ in OFFSETS]
    incomes = np.array([standard + offset for _ in flagged for offset in OFFSETS])
    simulation = unit_simulation(
        year,
        states,
        couple,
        {"medicaid_optional_senior_or_disabled_countable_income": incomes},
    )
    eligible = simulation.calculate(
        "is_optional_senior_or_disabled_income_eligible", year
    )
    # Each unit's first member carries the unit's whole countable income.
    first_member = eligible[:: 2 if couple else 1]
    np.testing.assert_array_equal(first_member, incomes <= standard)
    # Never rises with income: within a state, incomes ascend with OFFSETS.
    by_state = first_member.reshape(len(flagged), len(OFFSETS)).astype(int)
    assert (np.diff(by_state, axis=1) <= 0).all()


@pytest.mark.parametrize("year", YEARS)
def test_no_medicaid_without_ssi_above_the_ssi_rate(year):
    individual, _ = SSA_MONTHLY_RATES[year]
    standard = 12 * individual
    # Section 209(b) states test SSI recipients against their own criteria,
    # so the SSI-receipt half of this property is stated for the others.
    classification = SYSTEM.parameters(
        f"{year}-01-01"
    ).gov.hhs.medicaid.eligibility.categories.ssi_recipient.classification
    flagged = flagged_states(year)
    states = [state for state in flagged for _ in OFFSETS]
    countable = np.array([standard + offset for _ in flagged for offset in OFFSETS])
    # SSI excludes the first $20 a month of unearned income.
    social_security = countable + 240
    simulation = unit_simulation(
        year,
        states,
        False,
        {"social_security_retirement": social_security},
    )
    ssi = simulation.calculate("ssi", year)
    optional = simulation.calculate("is_optional_senior_or_disabled_for_medicaid", year)
    category = simulation.calculate("medicaid_category", year).decode_to_str()
    over = countable > standard
    # Nobody over the SSI rate gets SSI or the pathway.
    assert not optional[over].any()
    np.testing.assert_array_equal(ssi[over], 0)
    # Everyone under the rate gets SSI; at the rate SSI is zero.
    assert (ssi[countable < standard] > 0).all()
    np.testing.assert_array_equal(ssi[countable == standard], 0)
    # At or under the rate the pathway's own tests pass.
    assert optional[~over].all()
    not_209b = np.array([not classification.section_209b[state] for state in states])
    receives = (countable < standard) & not_209b
    assert (category[receives] == "SSI_RECIPIENT").all()
    at_rate = (countable == standard) & not_209b
    assert (category[at_rate] == "SENIOR_OR_DISABLED").all()


@pytest.mark.parametrize("couple", [False, True])
@pytest.mark.parametrize("year", YEARS)
def test_unflagged_states_keep_their_share_of_the_poverty_guideline(year, couple):
    p = limit_parameters(year)
    flagged = set(flagged_states(year))
    # Missouri publishes whole-dollar monthly standards and is tested in
    # medicaid_optional_senior_or_disabled_income_limit.yaml.
    states = [state for state in STATES if state not in flagged and state != "MO"]
    simulation = unit_simulation(year, states, couple)
    limit = simulation.calculate(
        "medicaid_optional_senior_or_disabled_income_limit", year
    )[:: 2 if couple else 1]
    fpg = SYSTEM.parameters(f"{year}-01-01").gov.hhs.fpg
    group = {"AK": "AK", "HI": "HI"}
    expected = np.array(
        [
            (p.couple if couple else p.individual)[state]
            * (
                fpg.first_person[group.get(state, "CONTIGUOUS_US")]
                + couple * fpg.additional_person[group.get(state, "CONTIGUOUS_US")]
            )
            for state in states
        ]
    )
    np.testing.assert_allclose(limit, expected, rtol=1e-6)
