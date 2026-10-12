"""Invariants for the Texas SSI supplement for Medicaid-facility residents.

HHSC MEPD Handbook H-6000: "HHSC supplements the reduced SSI payment standard
by $45 per month to ensure SSI recipients also have a $75 personal needs
allowance." The supplement is the personal needs allowance (PNA) less the $30
reduced federal benefit, and a recipient's other income goes to the facility
co-payment rather than reducing it (H-6000, H-1200).

Checked for single residents of a Medicaid facility with generated pensions,
earnings and ages:

1. Income invariance: every eligible resident whose SSI countable income is
   at most the $30 reduced standard (an SSI recipient under H-6000) gets
   exactly PNA - $30 a month, whatever that income is.
2. Federal side of the identity: for those residents federal SSI plus
   countable income equals the $30 reduced standard.
3. Agreement with the "allowance less federal SSI less countable income"
   reading of SSA's description: PNA - SSI - countable income equals the
   supplement for those residents.
4. The supplement is never negative and never above PNA - $30.

And for every month from July 1988 to December 2026, the monthly amount for an
eligible resident matches the dated HHSC history: $0 before September 1999,
then $15, $30 (September 2001), $15 (September 2003), $30 (January 2006) and
$45 (January 2024).

Residents with countable income above $30 are not SSI recipients; whether they
are eligible is tested with the eligibility variable, not here.
"""

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation
from policyengine_us.system import system

PERIODS = ("2011-06", "2024-06", "2026-01")
TOLERANCE = 0.01
FACILITY_INPUTS = dict(
    is_in_medicaid_facility=True,
    ssi_lives_in_medical_treatment_facility=True,
    ssi_medicaid_pays_majority_of_care=True,
)
# (start month, monthly supplement): H-1500's PNA less the $30 reduced benefit.
HISTORY = (
    ("1988-07", 0),
    ("1999-09", 15),
    ("2001-09", 30),
    ("2003-09", 15),
    ("2006-01", 30),
    ("2024-01", 45),
)


def _situation(residents, years):
    situation = {
        group: {}
        for group in (
            "people",
            "tax_units",
            "marital_units",
            "spm_units",
            "families",
            "households",
        )
    }
    for index, (age, pension, earnings) in enumerate(residents):
        name = f"resident{index}"
        person = {
            "age": {year: age for year in years},
            "pension_income": {year: 12 * pension for year in years},
            "employment_income": {year: 12 * earnings for year in years},
        }
        for variable, value in FACILITY_INPUTS.items():
            person[variable] = {year: value for year in years}
        situation["people"][name] = person
        for group in ("tax_units", "marital_units", "spm_units", "families"):
            situation[group][f"{group}_{index}"] = {"members": [name]}
        situation["households"][f"household_{index}"] = {
            "members": [name],
            "state_code": {year: "TX" for year in years},
        }
    return situation


def _check(residents):
    years = sorted({int(period[:4]) for period in PERIODS})
    simulation = Simulation(situation=_situation(residents, years))
    for period in PERIODS:
        parameters = simulation.tax_benefit_system.parameters(period)
        pna = (
            parameters.gov.states.tx.hhsc.ssi_state_supplement.personal_needs_allowance
        )
        reduced = parameters.gov.ssa.ssi.amount.institutional.individual
        eligible = simulation.calculate("tx_ssi_state_supplement_eligible", period)
        supplement = simulation.calculate("tx_ssi_state_supplement", period)
        ssi = simulation.calculate("ssi", period)
        countable = simulation.calculate("ssi_countable_income", period)
        recipient = eligible & (countable <= reduced + TOLERANCE)

        # 4. Bounds.
        assert (supplement >= 0).all()
        assert (supplement <= pna - reduced + TOLERANCE).all()
        # 1. Income invariance.
        np.testing.assert_allclose(supplement[recipient], pna - reduced, atol=TOLERANCE)
        # 2. Federal SSI plus countable income is the reduced standard.
        np.testing.assert_allclose(
            (ssi + countable)[recipient], reduced, atol=TOLERANCE
        )
        # 3. Agreement with "allowance less federal SSI less countable income".
        np.testing.assert_allclose(
            supplement[recipient],
            (pna - ssi - countable)[recipient],
            atol=TOLERANCE,
        )
    return recipient, countable


residents = st.tuples(
    st.integers(min_value=65, max_value=95),
    # Monthly pension: $0-$150, so countable unearned income spans the $30
    # reduced standard.
    st.integers(min_value=0, max_value=150),
    # Monthly earnings: $0-$250.
    st.integers(min_value=0, max_value=250),
)

# A batch's cost is mostly per-variable overhead, so each example is a large
# batch and there are few examples.
SETTINGS = dict(
    max_examples=5,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)


@settings(**SETTINGS)
@given(st.lists(residents, min_size=10, max_size=30))
def test_generated_residents(population):
    _check(population)


def test_seeded_residents():
    # Pensions at and around the $50 that puts countable income at the $30
    # standard, earnings with and without a pension, and no income.
    population = [
        (age, pension, earnings)
        for age in (66, 85)
        for pension in (0, 20, 40, 49, 50, 51, 120)
        for earnings in (0, 100, 145, 200)
    ]
    recipient, countable = _check(population)
    # The grid reaches residents on both sides of the $30 standard.
    assert recipient.any()
    assert (countable > 30).any()


def _expected(month):
    return [amount for start, amount in HISTORY if start <= month][-1]


def test_dated_history_every_month():
    # Leaf parameter lookups are cheap, so check every month at that level.
    parameters = system.parameters
    pna = parameters.gov.states.tx.hhsc.ssi_state_supplement.personal_needs_allowance
    reduced = parameters.gov.ssa.ssi.amount.institutional.individual
    for year in range(1988, 2027):
        for month in range(1, 13):
            period = f"{year}-{month:02d}"
            if period < HISTORY[0][0]:
                continue
            instant = f"{period}-01"
            assert max(pna(instant) - reduced(instant), 0) == _expected(period), period


def test_dated_history():
    years = (1998, 1999, 2000, 2001, 2003, 2005, 2006, 2023, 2024)
    simulation = Simulation(
        situation={
            "people": {
                "resident": {
                    "tx_ssi_state_supplement_eligible": {year: True for year in years}
                }
            },
            "households": {
                "household": {
                    "members": ["resident"],
                    "state_code": {year: "TX" for year in years},
                }
            },
        }
    )

    def supplement(period):
        return simulation.calculate("tx_ssi_state_supplement", period)[0]

    # The month before and the month of each change, and the first month the
    # federal $30 reduced benefit applies.
    for start, _ in HISTORY:
        year, month = map(int, start.split("-"))
        before = f"{year - 1}-12" if month == 1 else f"{year}-{month - 1:02d}"
        months = (start,) if start == HISTORY[0][0] else (before, start)
        for period in months:
            assert supplement(period) == pytest.approx(_expected(period)), period
    # Annual totals sum the months in the years with a September change.
    for year in (1999, 2001, 2003):
        expected = sum(_expected(f"{year}-{month:02d}") for month in range(1, 13))
        assert supplement(str(year)) == pytest.approx(expected), year
