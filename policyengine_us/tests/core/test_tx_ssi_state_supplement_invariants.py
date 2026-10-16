"""Income invariance of the Texas SSI supplement for Medicaid-facility residents.

1 TAC 358.381(c)(2): "For a person receiving the reduced SSI federal benefit
rate, HHSC issues a supplement to give the person a PNA at the minimum level
set by the HHSC executive commissioner." HHSC MEPD Handbook H-6000 states it as
a fixed amount: "HHSC supplements the reduced SSI payment standard by $45 per
month". No Texas source subtracts the recipient's own income from it.

Checked for single residents of a Medicaid facility who are paid SSI on the
reduced standard (a positive federal payment), with generated pensions,
earnings and ages, in June 2011 and June 2024:

1. Income invariance: each such eligible resident gets exactly PNA - $30 a
   month, whatever their income.
2. Federal identity: federal SSI plus countable income equals the $30 reduced
   standard.
3. Differential: PNA - SSI - countable income, the reading of SSA's
   description that subtracts the recipient's income, equals the supplement.
4. Bounds: 0 <= supplement <= PNA - $30 for every resident.

Residents with no federal payment (countable income at or above $30) are left
to the eligibility tests: the sources do not settle whether Texas pays one
whose countable income is exactly $30.

Why Python: YAML checks fixed expected outputs for listed households. These
properties compare three computed variables against each other for generated
residents, which YAML cannot express. The dated amounts are in
tx_ssi_state_supplement.yaml.
"""

import numpy as np
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

PERIODS = ("2011-06", "2024-06")
TOLERANCE = 0.01
FACILITY_INPUTS = dict(
    is_in_medicaid_facility=True,
    ssi_lives_in_medical_treatment_facility=True,
    ssi_medicaid_pays_majority_of_care=True,
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
    paid = []
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
        recipient = eligible & (ssi > 0)
        paid.append(recipient)

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
    return np.any(paid, axis=0)


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
    # Pensions below, at and above the $50 that puts countable income at the
    # $30 standard, earnings with and without a pension, and no income.
    population = [
        (age, pension, earnings)
        for age in (66, 85)
        for pension in (0, 20, 40, 49, 50, 51, 120)
        for earnings in (0, 100, 145, 200)
    ]
    paid = _check(population)
    # The grid reaches residents paid SSI with and without other income, and
    # residents with no federal payment.
    assert paid.sum() >= 10
    assert (~paid).any()
