"""Properties of the Medicaid income standard for aged, blind, and disabled
people who do not receive SSI, in states that set it at the SSI rate.

Seven states set that standard at the SSI federal benefit rate, a monthly
dollar amount for an individual or a couple, not a share of the poverty
guideline. They are flagged in the parameter
`gov.hhs.medicaid.eligibility.categories.senior_or_disabled.income.limit.uses_ssi_federal_benefit_rate`.
Six of them cover these people through the group of 42 CFR 435.210 and have
not elected the poverty-level group of 42 U.S.C. 1396a(m); Louisiana has
elected that group and pegs its level to the same rate. Montana's manual
(ABD 008) is the model case: its standards "are the benefit amounts paid by
the Social Security Administration to Supplemental Security Income (SSI)
cash recipients", applicants "with monthly countable income equal to or
less than these income standards are categorically needy Medicaid
eligible", and applicants "in excess of these income standards are not
categorically needy eligible".

The states' rules differ on income exactly at the standard. Oregon's
excludes it: an individual "must have adjusted income (see OAR
461-001-0000) below the standard in this section" (OAR 461-155-0250(3)).
The other six include it. Oregon is flagged in
`gov.hhs.medicaid.eligibility.categories.senior_or_disabled.income.limit.requires_income_below_limit`.

The state sets and comparisons below are written from those rules, not
read from the parameters, so the first two tests check the parameters
against them. Each later test evaluates a grid of households in one
vectorized simulation and checks, for every one of the seven states and
every year from 2018 to 2026:

- the limit equals twelve times the rate SSA published for that year, for an
  individual and for a couple (a differential check against SSA's table);
- income eligibility is true exactly when countable income meets the
  state's own comparison with that amount (at or below it, or below it in
  Oregon), so it never rises with income;
- for an aged person with no resources and only Social Security income, the
  pathway never covers anyone whose countable income is over the SSI rate,
  or at it in Oregon, and everyone under the rate receives SSI, so no band
  of income gets Medicaid without SSI at or above the rate.

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
# States whose own rules set the standard at the SSI rate (cited in
# uses_ssi_federal_benefit_rate.yaml).
SSI_RATE_STATES = sorted(["CO", "IA", "LA", "MT", "OH", "OR", "WA"])
# States whose rules require income below the standard rather than at or
# below it. Oregon: "must have adjusted income (see OAR 461-001-0000) below
# the standard in this section" (OAR 461-155-0250(3); every version since
# 1-01-14 says "below", in section (4) until April 2017). The other six
# include the standard: Montana "equal to or less than these income
# standards" (ABD 008); Louisiana "income equal to or less than the federal
# benefit rate (FBR)" (LAC 50:III.2305(B)); Ohio "countable income ... which
# does not exceed the income standard" (OAC 5160:1-3-02.4(B)(3));
# Washington "at or below the SSI-related WAH CN medical monthly standard"
# (WAC 182-512-0100(2)(a)); Colorado and Iowa cover people who meet SSI's
# income requirements (10 CCR 2505-10 § 8.100.3.F.1.d; 441 IAC 75.1(17)),
# and SSI covers income "at a rate of not more than" the benefit rate (42
# U.S.C. 1382(a)(1)(A) and (2)(A)): "If the CI is equal to or less than the
# FBR ... the individual, based on income, is eligible" (POMS SI
# 02005.001.C.3).
BELOW_ONLY_STATES = ["OR"]
# Annual dollars around the standard: far below, one month's dollar below,
# exactly at, one dollar above, and well above.
OFFSETS = [-6_000, -12, -1, 0, 1, 12, 42, 600, 6_000]

SYSTEM = CountryTaxBenefitSystem()


def limit_parameters(year):
    return SYSTEM.parameters(
        f"{year}-01-01"
    ).gov.hhs.medicaid.eligibility.categories.senior_or_disabled.income.limit


def states_where(flags):
    return sorted(state for state in STATES if flags[state])


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


@pytest.mark.parametrize("year", YEARS)
def test_ssi_rate_states_match_their_rules(year):
    flags = limit_parameters(year).uses_ssi_federal_benefit_rate
    assert states_where(flags) == SSI_RATE_STATES


@pytest.mark.parametrize("year", YEARS)
def test_below_only_states_match_their_rules(year):
    flags = limit_parameters(year).requires_income_below_limit
    assert states_where(flags) == BELOW_ONLY_STATES


@pytest.mark.parametrize("couple", [False, True])
@pytest.mark.parametrize("year", YEARS)
def test_limit_is_twelve_times_the_published_ssi_rate(year, couple):
    simulation = unit_simulation(year, SSI_RATE_STATES, couple)
    limit = simulation.calculate(
        "medicaid_optional_senior_or_disabled_income_limit", year
    )
    individual, couple_rate = SSA_MONTHLY_RATES[year]
    expected = 12 * (couple_rate if couple else individual)
    np.testing.assert_array_equal(limit, expected)


@pytest.mark.parametrize("couple", [False, True])
@pytest.mark.parametrize("year", YEARS)
def test_income_eligible_exactly_when_the_state_comparison_holds(year, couple):
    individual, couple_rate = SSA_MONTHLY_RATES[year]
    standard = 12 * (couple_rate if couple else individual)
    states = [state for state in SSI_RATE_STATES for _ in OFFSETS]
    incomes = np.array(
        [standard + offset for _ in SSI_RATE_STATES for offset in OFFSETS]
    )
    below_only = np.isin(states, BELOW_ONLY_STATES)
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
    expected = np.where(below_only, incomes < standard, incomes <= standard)
    np.testing.assert_array_equal(first_member, expected)
    # Never rises with income: within a state, incomes ascend with OFFSETS.
    by_state = first_member.reshape(len(SSI_RATE_STATES), len(OFFSETS)).astype(int)
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
    states = [state for state in SSI_RATE_STATES for _ in OFFSETS]
    countable = np.array(
        [standard + offset for _ in SSI_RATE_STATES for offset in OFFSETS]
    )
    below_only = np.isin(states, BELOW_ONLY_STATES)
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
    at_rate = countable == standard
    # Nobody over the SSI rate gets SSI or the pathway.
    assert not optional[over].any()
    np.testing.assert_array_equal(ssi[over], 0)
    # Everyone under the rate gets SSI; at the rate SSI is zero.
    assert (ssi[countable < standard] > 0).all()
    np.testing.assert_array_equal(ssi[at_rate], 0)
    # Under the rate the pathway's own tests pass, and at it they pass
    # except where the state requires income below the standard.
    covered = (countable < standard) | (at_rate & ~below_only)
    assert optional[covered].all()
    assert not optional[~covered].any()
    not_209b = np.array([not classification.section_209b[state] for state in states])
    receives = (countable < standard) & not_209b
    assert (category[receives] == "SSI_RECIPIENT").all()
    assert (category[at_rate & ~below_only & not_209b] == "SENIOR_OR_DISABLED").all()
    # In Oregon a person exactly at the rate gets neither SSI nor the pathway.
    assert not (category[at_rate & below_only] == "SENIOR_OR_DISABLED").any()


@pytest.mark.parametrize("couple", [False, True])
@pytest.mark.parametrize("year", YEARS)
def test_unflagged_states_keep_their_share_of_the_poverty_guideline(year, couple):
    p = limit_parameters(year)
    # Missouri publishes whole-dollar monthly standards and is tested in
    # medicaid_optional_senior_or_disabled_income_limit.yaml.
    states = [
        state for state in STATES if state not in SSI_RATE_STATES and state != "MO"
    ]
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
