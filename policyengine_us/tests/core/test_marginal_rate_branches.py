"""Branch-measured marginal rates must equal fresh re-simulation.

``marginal_tax_rate`` raises one adult's earnings by ``delta`` in a branch of
the simulation and compares household net income. The branch must reproduce
an independent simulation of the same household with the raised earnings, so
for every household and every adult the rate measures:

1. ``marginal_tax_rate == 1 - (net income at earnings + delta - net income)
   / delta``, with net income from two fresh simulations; the same holds for
   ``marginal_tax_rate_including_health_benefits`` with health benefits
   counted, for ``federal_``, ``state_`` and ``fica_marginal_tax_rate`` as
   ``(tax at earnings + delta - tax) / delta``, and for
   ``marginal_tax_rate_on_capital_gains`` with long-term gains raised instead.
2. People the rate does not measure (children, adults past the cap) get 0.
3. Measuring a rate leaves the simulation's own results and branches as they
   were.
4. Right after construction, ``input_variables`` lists exactly the variables
   that hold values.

Invariant 4 is what the branches rely on. The ``Simulation`` and
``Microsimulation`` wrappers move ``employment_income`` and similar inputs onto
pre-response variables (``employment_income_before_lsr`` ...) and backfill
``state_code`` from ``state_code_str`` after policyengine-core records
``input_variables``. The branches keep only listed variables, so a stale list
erased the moved inputs: an Ohio parent's branch counted no earnings for Ohio
Works First and reported a marginal tax rate of -4.70 where fresh simulations
give 0.527.

These tests use the Python wrappers because the YAML runner skips the moves.
"""

import copy

import numpy as np
import pandas as pd
import pytest

from policyengine_us import Microsimulation, Simulation
from policyengine_us.data.dataset_schema import USSingleYearDataset
from policyengine_us.variables.gov.simulation.behavioral_response_measurements import (
    PRE_RESPONSE_INPUTS,
)

YEAR = 2026
DELTA = 1_000
TOLERANCE = 1e-3
STATES = (
    "AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS "
    "MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY"
).split()
EARNINGS_RATES = (
    "marginal_tax_rate",
    "marginal_tax_rate_including_health_benefits",
    "federal_marginal_tax_rate",
    "state_marginal_tax_rate",
    "fica_marginal_tax_rate",
)
COMPONENT_TAXES = {
    "federal_marginal_tax_rate": "income_tax",
    "state_marginal_tax_rate": "state_income_tax",
    "fica_marginal_tax_rate": "employee_payroll_tax",
}


def situation(households, geography="state_code"):
    """Build one situation holding several independent households.

    Each household is ``(state, adults, children)``: ``adults`` maps person
    names to their yearly inputs and ``children`` lists ages. Two adults form a
    married couple filing one return.
    """
    result = {
        key: {}
        for key in (
            "people",
            "tax_units",
            "spm_units",
            "families",
            "marital_units",
            "households",
        )
    }
    for h, (state, adults, children) in enumerate(households):
        members = []
        adult_ids = []
        for name, inputs in adults.items():
            person = f"h{h}_{name}"
            members.append(person)
            adult_ids.append(person)
            result["people"][person] = {
                variable: {YEAR: value} for variable, value in inputs.items()
            }
        for i, age in enumerate(children):
            person = f"h{h}_child{i}"
            members.append(person)
            result["people"][person] = {
                "age": {YEAR: age},
                "is_tax_unit_dependent": {YEAR: True},
            }
            result["marital_units"][f"{person}_marital_unit"] = {"members": [person]}
        if len(adult_ids) == 2:
            result["marital_units"][f"h{h}_couple"] = {"members": adult_ids}
        else:
            for person in adult_ids:
                result["marital_units"][f"{person}_marital_unit"] = {
                    "members": [person]
                }
        for group in ("tax_units", "spm_units", "families"):
            result[group][f"h{h}_{group}"] = {"members": members}
        result["households"][f"h{h}"] = {
            "members": members,
            geography: {YEAR: state},
        }
    return result


def raise_earnings(base_situation, simulation, adult_index):
    """Raise the earnings of each household's ``adult_index``-th earner.

    Splits ``DELTA`` across wages, non-SSTB and SSTB self-employment income in
    proportion to the person's positive earnings, wages when there are none;
    the split the rates document.
    """
    ranks = simulation.calculate("adult_earnings_index", YEAR)
    wages = simulation.calculate("employment_income", YEAR)
    self_employment = simulation.calculate("self_employment_income", YEAR)
    sstb = simulation.calculate("sstb_self_employment_income", YEAR)
    positive = [np.maximum(x, 0) for x in (wages, self_employment, sstb)]
    total = sum(positive)
    raised = copy.deepcopy(base_situation)
    for i, person in enumerate(base_situation["people"]):
        if ranks[i] != adult_index:
            continue
        shares = (
            [x[i] / total[i] for x in positive] if total[i] > 0 else [1.0, 0.0, 0.0]
        )
        for variable, base, share in zip(
            (
                "employment_income",
                "self_employment_income",
                "sstb_self_employment_income",
            ),
            (wages, self_employment, sstb),
            shares,
        ):
            raised["people"][person][variable] = {YEAR: float(base[i] + DELTA * share)}
    return raised, ranks == adult_index


def raise_long_term_gains(base_situation, simulation, adult_index):
    ranks = simulation.calculate("adult_index_cg", YEAR)
    gains = simulation.calculate("long_term_capital_gains", YEAR)
    raised = copy.deepcopy(base_situation)
    for i, person in enumerate(base_situation["people"]):
        if ranks[i] == adult_index:
            raised["people"][person]["long_term_capital_gains"] = {
                YEAR: float(gains[i] + DELTA)
            }
    return raised, ranks == adult_index


def household_values(simulation, variable):
    return simulation.calculate(variable, YEAR, map_to="person")


def head_taxes(simulation, variable):
    """Tax-unit tax summed over each household's tax units, per person."""
    is_head = simulation.calculate("is_tax_unit_head", YEAR)
    person_tax = simulation.calculate(variable, YEAR, map_to="person") * is_head
    household = simulation.populations["household"]
    return household.project(household.sum(person_tax))


def fresh_earnings_rates(base_situation, simulation):
    """Each earnings rate as a difference between fresh simulations."""
    adult_count = simulation.tax_benefit_system.parameters(
        YEAR
    ).simulation.marginal_tax_rate_adults
    base = {
        "marginal_tax_rate": household_values(simulation, "household_net_income"),
        "marginal_tax_rate_including_health_benefits": household_values(
            simulation, "household_net_income_including_health_benefits"
        ),
        **{rate: head_taxes(simulation, tax) for rate, tax in COMPONENT_TAXES.items()},
    }
    expected = {rate: np.zeros(len(base_situation["people"])) for rate in base}
    for adult_index in range(1, adult_count + 1):
        raised_situation, mask = raise_earnings(base_situation, simulation, adult_index)
        raised = Simulation(situation=raised_situation)
        alt = {
            "marginal_tax_rate": household_values(raised, "household_net_income"),
            "marginal_tax_rate_including_health_benefits": household_values(
                raised, "household_net_income_including_health_benefits"
            ),
            **{rate: head_taxes(raised, tax) for rate, tax in COMPONENT_TAXES.items()},
        }
        for rate in expected:
            change = (alt[rate] - base[rate]) / DELTA
            if rate in COMPONENT_TAXES:
                value = change
            else:
                value = 1 - change
            expected[rate] = np.where(mask, value, expected[rate])
    return expected


def fresh_capital_gains_rate(base_situation, simulation):
    base = household_values(simulation, "household_net_income")
    expected = np.zeros(len(base_situation["people"]))
    for adult_index in (1, 2):
        raised_situation, mask = raise_long_term_gains(
            base_situation, simulation, adult_index
        )
        alt = household_values(
            Simulation(situation=raised_situation), "household_net_income"
        )
        expected = np.where(mask, 1 - (alt - base) / DELTA, expected)
    return expected


def assert_rates_match(simulation, expected, rates):
    for rate in rates:
        np.testing.assert_allclose(
            simulation.calculate(rate, YEAR),
            expected[rate],
            atol=TOLERANCE,
            err_msg=rate,
        )


OHIO_PARENT = (
    "OH",
    {"parent": {"age": 30, "employment_income": 28_000}},
    [4, 8],
)


def test_ohio_parent_marginal_tax_rate_matches_fresh_simulations():
    """The reported case: fresh simulations give 0.527, the branch gave -4.70."""
    base_situation = situation([OHIO_PARENT])
    simulation = Simulation(situation=base_situation)
    raised_situation = copy.deepcopy(base_situation)
    raised_situation["people"]["h0_parent"]["employment_income"] = {YEAR: 29_000}
    base = simulation.calculate("household_net_income", YEAR)[0]
    raised = Simulation(situation=raised_situation).calculate(
        "household_net_income", YEAR
    )[0]

    rate = simulation.calculate("marginal_tax_rate", YEAR)

    assert rate[0] == pytest.approx(1 - (raised - base) / DELTA, abs=TOLERANCE)
    assert rate[0] == pytest.approx(0.5271, abs=TOLERANCE)
    assert list(rate[1:]) == [0, 0]


def test_simulation_lists_the_variables_holding_inputs():
    """Invariant 4 for household simulations, across every moved input."""
    base_situation = situation(
        [
            (
                "OH",
                {
                    "worker": {
                        "age": 45,
                        "employment_income": 30_000,
                        "self_employment_income": 5_000,
                        "sstb_self_employment_income": 2_000,
                        "weekly_hours_worked": 35,
                        "long_term_capital_gains": 4_000,
                    }
                },
                [],
            )
        ],
        geography="state_code_str",
    )
    simulation = Simulation(situation=base_situation)
    holding_values = {
        variable
        for variable in simulation.tax_benefit_system.variables
        if simulation.get_holder(variable).get_known_periods()
    }

    assert set(simulation.input_variables) == holding_values
    assert set(PRE_RESPONSE_INPUTS.values()) | {"state_code"} <= holding_values
    assert not (set(PRE_RESPONSE_INPUTS) | {"state_code_str"}) & holding_values


def _ohio_parent_dataset(wages):
    """One Ohio parent of two children, as an entity-level dataset."""
    person = pd.DataFrame(
        {
            "person_id": [1, 2, 3],
            "person_household_id": [1, 1, 1],
            "person_tax_unit_id": [1, 1, 1],
            "person_spm_unit_id": [1, 1, 1],
            "person_family_id": [1, 1, 1],
            "person_marital_unit_id": [1, 2, 3],
            "age": [30.0, 4.0, 8.0],
            "employment_income": [float(wages), 0.0, 0.0],
            "weekly_hours_worked": [30.0, 0.0, 0.0],
            "long_term_capital_gains": [500.0, 0.0, 0.0],
        }
    )
    household = pd.DataFrame(
        {
            "household_id": [1],
            "state_fips": np.asarray([39], dtype="int64"),
            "household_weight": [1.0],
        }
    )
    return USSingleYearDataset(
        person=person,
        household=household,
        tax_unit=pd.DataFrame({"tax_unit_id": [1]}),
        spm_unit=pd.DataFrame({"spm_unit_id": [1]}),
        family=pd.DataFrame({"family_id": [1]}),
        marital_unit=pd.DataFrame({"marital_unit_id": [1, 2, 3]}),
        time_period=YEAR,
    )


def test_microsimulation_marginal_tax_rate_matches_fresh_microsimulations():
    """Invariants 1 and 4 for dataset-backed simulations.

    Before the fix, ``Microsimulation`` listed the moved inputs, so its branch
    kept the parent's pre-response wages and raised only the
    ``employment_income`` aggregate: Ohio Works First, which counts
    pre-response wages, never saw the raise.
    """
    simulation = Microsimulation(dataset=_ohio_parent_dataset(6_000))
    raised = Microsimulation(dataset=_ohio_parent_dataset(7_000))
    holding_values = {
        variable
        for variable in simulation.tax_benefit_system.variables
        if simulation.get_holder(variable).get_known_periods()
    }
    assert set(simulation.input_variables) == holding_values
    assert "long_term_capital_gains" not in simulation.input_variables

    base = simulation.calculate("household_net_income", YEAR).values[0]
    alt = raised.calculate("household_net_income", YEAR).values[0]
    assert (
        simulation.calculate("tanf", YEAR).values[0]
        > raised.calculate("tanf", YEAR).values[0]
    )

    rate = simulation.calculate("marginal_tax_rate", YEAR).values

    assert rate[0] == pytest.approx(1 - (alt - base) / DELTA, abs=TOLERANCE)


def test_marginal_rates_leave_the_simulation_unchanged():
    """Invariant 3: branches neither leak into nor linger on the simulation."""
    simulation = Simulation(situation=situation([OHIO_PARENT]))
    watched = (
        ("household_net_income", YEAR),
        ("tanf", f"{YEAR}-06"),
        ("employment_income_before_lsr", f"{YEAR}-06"),
    )
    before = [simulation.calculate(*key).copy() for key in watched]
    branches = set(simulation.branches)

    for rate in (*EARNINGS_RATES, "marginal_tax_rate_on_capital_gains"):
        simulation.calculate(rate, YEAR)

    # The model keeps its own branches, such as itemizing; rates add none.
    assert set(simulation.branches) == branches
    for key, value in zip(watched, before):
        np.testing.assert_array_equal(simulation.calculate(*key), value)


def test_state_code_str_household_keeps_its_state_in_the_branch():
    """A household located only by state_code_str keeps that state."""
    base_situation = situation([OHIO_PARENT], geography="state_code_str")
    simulation = Simulation(situation=base_situation)

    assert_rates_match(
        simulation,
        fresh_earnings_rates(base_situation, simulation),
        ("marginal_tax_rate", "marginal_tax_rate_including_health_benefits"),
    )


def test_capital_gains_rate_applies_preferential_rates():
    """The capital gains rate raises long-term gains, which are taxed at 15%.

    A Texas filer with $60,000 of wages and $15,000 of long-term gains has
    $43,900 of ordinary taxable income after the $16,100 standard deduction,
    so the gains fill the 0% bracket to $49,450 and the rest is taxed at 15%.
    Texas has no income tax and the filer is below the net investment income
    tax threshold, so an extra dollar of gains costs 15 cents.
    """
    base_situation = situation(
        [
            (
                "TX",
                {
                    "filer": {
                        "age": 45,
                        "employment_income": 60_000,
                        "long_term_capital_gains": 15_000,
                    }
                },
                [],
            )
        ]
    )
    simulation = Simulation(situation=base_situation)

    rate = simulation.calculate("marginal_tax_rate_on_capital_gains", YEAR)

    assert rate[0] == pytest.approx(0.15, abs=TOLERANCE)
    assert rate[0] == pytest.approx(
        fresh_capital_gains_rate(base_situation, simulation)[0], abs=TOLERANCE
    )


def random_households(seed, count):
    """Households drawn to reach every moved input and many programs."""
    rng = np.random.default_rng(seed)
    households = []
    for _ in range(count):
        adults = {}
        for name in ("head", "spouse")[: rng.integers(1, 3)]:
            age = int(rng.integers(19, 80))
            inputs = {"age": age}
            wage_band = rng.choice([0, 12_000, 35_000, 120_000])
            if wage_band:
                inputs["employment_income"] = float(rng.uniform(0.2, 1.0) * wage_band)
                if rng.random() < 0.7:
                    inputs["weekly_hours_worked"] = float(rng.uniform(5, 50))
            if rng.random() < 0.25:
                inputs["self_employment_income"] = float(rng.uniform(-5_000, 40_000))
            if rng.random() < 0.1:
                inputs["sstb_self_employment_income"] = float(rng.uniform(0, 60_000))
            if rng.random() < 0.2:
                inputs["long_term_capital_gains"] = float(rng.uniform(0, 50_000))
            if age >= 62 and rng.random() < 0.7:
                inputs["social_security_retirement"] = float(rng.uniform(5_000, 30_000))
            adults[name] = inputs
        children = [int(age) for age in rng.integers(0, 18, rng.integers(0, 4))]
        households.append((str(rng.choice(STATES)), adults, children))
    return households


@pytest.mark.parametrize("seed", [20260928])
def test_marginal_rates_match_fresh_simulations_for_random_households(seed):
    """Invariants 1 and 2 over randomly drawn households in every state."""
    base_situation = situation(random_households(seed, 24))
    simulation = Simulation(situation=base_situation)
    expected = fresh_earnings_rates(base_situation, simulation)
    expected["marginal_tax_rate_on_capital_gains"] = fresh_capital_gains_rate(
        base_situation, simulation
    )

    assert_rates_match(simulation, expected, expected)
