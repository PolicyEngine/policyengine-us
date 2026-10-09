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
5. In a reformed simulation with behavioral responses, the rates hold the
   responses at their simulated values: invariant 1 holds against fresh
   simulations that raise the pre-response input and keep every response.
6. A reformed simulation's baseline branch, and the baseline and reform
   branches that measure behavioral responses, equal fresh simulations of the
   baseline and of the reform without responses.
7. Inputs explicitly set on a measuring branch survive its raised branch,
   with only the raised earnings changed; calculated caches are recomputed.

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
from itertools import count

import numpy as np
import pandas as pd
import pytest
from hypothesis import HealthCheck, Phase, given, settings
from hypothesis import strategies as st
from policyengine_core.periods import period as make_period
from policyengine_core.reforms import Reform

from policyengine_us import Microsimulation, Simulation
from policyengine_us.data.dataset_schema import USSingleYearDataset
from policyengine_us.variables.gov.simulation.behavioral_response_measurements import (
    BEHAVIORAL_RESPONSE_CACHE_ATTR,
    PRE_RESPONSE_INPUTS,
)
from policyengine_us.variables.household.marginal_tax_rate_helpers import (
    HELD_BEHAVIORAL_RESPONSE_VARIABLES,
    create_perturbed_branch,
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
DATE_RANGE = "2020-01-01.2100-12-31"
# The reforms of tests/microsimulation/test_lsr_cg_interaction.py: a top
# rate 10 points higher, CBO's labor supply elasticities and a capital gains
# realization elasticity.
TOP_RATE = {"gov.irs.income.bracket.rates.7": {DATE_RANGE: 0.47}}
CBO_LABOR_SUPPLY = {
    "gov.simulation.labor_supply_responses.elasticities.income": {DATE_RANGE: -0.05},
    "gov.simulation.labor_supply_responses.elasticities.substitution.all": {
        DATE_RANGE: 0.25
    },
}
CAPITAL_GAINS_RESPONSE = {
    "gov.simulation.capital_gains_responses.elasticity": {DATE_RANGE: -0.62}
}


def reform(*parameter_changes):
    changes = {}
    for change in parameter_changes:
        changes.update(change)
    return Reform.from_dict(changes, country_id="us")


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


EARNINGS = (
    "employment_income",
    "self_employment_income",
    "sstb_self_employment_income",
)


def raise_earnings(base_situation, simulation, adult_index):
    """Raise the earnings of each household's ``adult_index``-th earner.

    Splits ``DELTA`` across wages, non-SSTB and SSTB self-employment income in
    proportion to the person's positive earnings, wages when there are none;
    the split the rates document. The situation's earnings are the
    pre-response inputs, so the raise goes on those.
    """
    ranks = simulation.calculate("adult_earnings_index", YEAR)
    positive = [np.maximum(simulation.calculate(x, YEAR), 0) for x in EARNINGS]
    total = sum(positive)
    pre_response = [
        simulation.calculate(PRE_RESPONSE_INPUTS[x], YEAR) for x in EARNINGS
    ]
    raised = copy.deepcopy(base_situation)
    for i, person in enumerate(base_situation["people"]):
        if ranks[i] != adult_index:
            continue
        shares = (
            [x[i] / total[i] for x in positive] if total[i] > 0 else [1.0, 0.0, 0.0]
        )
        for variable, base, share in zip(EARNINGS, pre_response, shares):
            raised["people"][person][variable] = {YEAR: float(base[i] + DELTA * share)}
    return raised, ranks == adult_index


def raise_long_term_gains(base_situation, simulation, adult_index):
    ranks = simulation.calculate("adult_index_cg", YEAR)
    gains = simulation.calculate(PRE_RESPONSE_INPUTS["long_term_capital_gains"], YEAR)
    raised = copy.deepcopy(base_situation)
    for i, person in enumerate(base_situation["people"]):
        if ranks[i] == adult_index:
            raised["people"][person]["long_term_capital_gains"] = {
                YEAR: float(gains[i] + DELTA)
            }
    return raised, ranks == adult_index


def hold_responses(raised_situation, simulation):
    """Give every person the behavioral responses they have in ``simulation``."""
    responses = {
        variable: simulation.calculate(variable, YEAR)
        for variable in HELD_BEHAVIORAL_RESPONSE_VARIABLES
    }
    for i, person in enumerate(raised_situation["people"]):
        for variable, values in responses.items():
            raised_situation["people"][person][variable] = {YEAR: float(values[i])}
    return raised_situation


def fresh_simulation(raised_situation, simulation, policy):
    """A fresh simulation of the raised households under ``policy``.

    Under a reform, the fresh simulation keeps the responses ``simulation``
    has, so the difference measures the rate at fixed behavior.
    """
    if policy is None:
        return Simulation(situation=raised_situation)
    return Simulation(
        situation=hold_responses(raised_situation, simulation), reform=policy
    )


def household_values(simulation, variable):
    return simulation.calculate(variable, YEAR, map_to="person")


def head_taxes(simulation, variable):
    """Tax-unit tax summed over each household's tax units, per person."""
    is_head = simulation.calculate("is_tax_unit_head", YEAR)
    person_tax = simulation.calculate(variable, YEAR, map_to="person") * is_head
    household = simulation.populations["household"]
    return household.project(household.sum(person_tax))


def fresh_earnings_rates(base_situation, simulation, policy=None):
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
        raised = fresh_simulation(raised_situation, simulation, policy)
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


def fresh_capital_gains_rate(base_situation, simulation, policy=None):
    base = household_values(simulation, "household_net_income")
    expected = np.zeros(len(base_situation["people"]))
    for adult_index in (1, 2):
        raised_situation, mask = raise_long_term_gains(
            base_situation, simulation, adult_index
        )
        alt = household_values(
            fresh_simulation(raised_situation, simulation, policy),
            "household_net_income",
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
# The Ohio Works First recipient of _ohio_parent_dataset(6_000).
OHIO_WORKS_FIRST_PARENT = (
    "OH",
    {
        "parent": {
            "age": 30,
            "employment_income": 6_000,
            "weekly_hours_worked": 30,
            "long_term_capital_gains": 500,
        }
    },
    [4, 8],
)
TEXAS_GAINS_FILER = (
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
BRANCH_NAMES = count()


@pytest.fixture(scope="module")
def branch_input_simulation():
    """A read-only source model; each case mutates only its own branches."""
    return Simulation(
        situation=situation(
            [("TX", {"parent": {"age": 30, "employment_income": 80_000}}, [4, 8])]
        )
    )


@pytest.fixture(scope="module")
def branch_identification_rates():
    """Fresh references share the same identification inputs at both wages."""
    base_situation = situation(
        [("TX", {"parent": {"age": 30, "employment_income": 80_000}}, [4, 8])]
    )
    for person, has_itin in zip(base_situation["people"].values(), [False, True, True]):
        person["has_itin"] = {YEAR: has_itin}
    raised_situation = copy.deepcopy(base_situation)
    raised_situation["people"]["h0_parent"]["employment_income"] = {YEAR: 81_000}
    base = Simulation(situation=base_situation)
    raised = Simulation(situation=raised_situation)
    # Identification denies the $4,400 CTC at both earnings levels.
    for reference in (base, raised):
        np.testing.assert_array_equal(reference.calculate("ctc", YEAR), [0])
    return {
        "federal_marginal_tax_rate": (
            raised.calculate("income_tax", YEAR)[0]
            - base.calculate("income_tax", YEAR)[0]
        )
        / DELTA,
        "marginal_tax_rate_including_health_benefits": 1
        - (
            raised.calculate("household_net_income_including_health_benefits", YEAR)[0]
            - base.calculate("household_net_income_including_health_benefits", YEAR)[0]
        )
        / DELTA,
    }


@pytest.mark.parametrize(
    "rate",
    ["federal_marginal_tax_rate", "marginal_tax_rate_including_health_benefits"],
)
def test_rates_keep_identification_inputs_set_on_the_measuring_branch(
    branch_input_simulation, branch_identification_rates, rate
):
    """A $1,000 raise cannot restore CTC denied by the parent's branch input.

    Core does not add branch set_input calls to input_variables. Keeping only
    that construction-time list erased has_itin from the raised branch, so
    the federal rate included a spurious $4,400 credit increase.
    """
    simulation = branch_input_simulation
    branch = simulation.get_branch(f"identification_{rate}")
    branch.set_input("has_itin", YEAR, [False, True, True])
    try:
        np.testing.assert_array_equal(branch.calculate("ctc", YEAR), [0])
        actual = branch.calculate(rate, YEAR)
        assert actual[0] == pytest.approx(
            branch_identification_rates[rate], abs=TOLERANCE
        )
        np.testing.assert_array_equal(actual[1:], [0, 0])
        raised = create_perturbed_branch(
            branch,
            make_period(YEAR),
            "identification_ctc_with_raise",
            {"employment_income": np.array([DELTA, 0, 0])},
        )
        np.testing.assert_array_equal(
            raised.get_array("has_itin", YEAR), [False, True, True]
        )
        np.testing.assert_array_equal(raised.calculate("ctc", YEAR), [0])
    finally:
        simulation.branches.pop(branch.branch_name)


@settings(
    max_examples=8,
    derandomize=True,
    database=None,
    deadline=None,
    # Cloning real-model branches makes failure shrinking expensive. The
    # retained-array assertion already identifies the lost input and value.
    phases=[Phase.generate],
    suppress_health_check=[HealthCheck.too_slow],
)
@given(
    tin=st.booleans(),
    state=st.sampled_from(["TX", "OH", "CA"]),
    zip_code=st.sampled_from(["77001", "44101", "90001"]),
    interest=st.integers(1, 20_000),
    incarcerated=st.booleans(),
    head=st.booleans(),
    earnings=st.integers(0, 100_000),
    increment=st.integers(1, 2_000),
    nested=st.booleans(),
)
def test_raised_branch_preserves_explicit_inputs_and_isolation(
    branch_input_simulation,
    tin,
    state,
    zip_code,
    interest,
    incarcerated,
    head,
    earnings,
    increment,
    nested,
):
    """Invariant 7 across input types, periods and one nested branch.

    All examples use branches of one read-only model, and calculate only the
    earnings aggregate; policy outputs are covered by the fresh references.
    """
    simulation = branch_input_simulation
    name = f"input_property_{next(BRANCH_NAMES)}"
    parent = simulation.get_branch(name)
    sibling = simulation.get_branch(f"{name}_sibling")
    original_inputs = list(simulation.input_variables)
    original_earnings = simulation.get_array(
        "employment_income_before_lsr", YEAR
    ).copy()
    parent.set_input("has_itin", YEAR, [tin, True, True])
    sibling.set_input("has_itin", YEAR, [not tin, True, True])
    measuring = parent.get_branch(f"{name}_nested") if nested else parent
    explicit = (
        ("has_itin", YEAR, [tin, True, True]),
        ("state_code", YEAR, [state]),
        ("zip_code", YEAR, [zip_code]),
        ("taxable_interest_income", YEAR, [interest, 0, 0]),
        ("is_incarcerated", f"{YEAR}-06", [incarcerated, False, False]),
        ("is_household_head", YEAR, [head, False, False]),
        ("employment_income_before_lsr", YEAR, [earnings, 0, 0]),
    )
    try:
        for variable, input_period, value in explicit[1:]:
            measuring.set_input(variable, input_period, value)
        expected = {
            (variable, input_period): measuring.get_array(variable, input_period).copy()
            for variable, input_period, _ in explicit
        }
        cached_earnings = measuring.calculate("employment_income", YEAR).copy()
        raised = create_perturbed_branch(
            measuring,
            make_period(YEAR),
            f"{name}_raised",
            {"employment_income": np.array([increment, 0, 0])},
        )

        # employment_income is calculated from the explicitly supplied
        # pre-response earnings, so the raised branch must clear its cache.
        assert raised.get_array("employment_income", YEAR) is None
        for (variable, input_period), value in expected.items():
            raised_value = (
                value + [increment, 0, 0]
                if variable == "employment_income_before_lsr"
                else value
            )
            np.testing.assert_array_equal(
                raised.get_array(variable, input_period),
                raised_value,
                err_msg=f"{variable} {input_period}",
            )
            np.testing.assert_array_equal(
                measuring.get_array(variable, input_period), value, err_msg=variable
            )
        np.testing.assert_array_equal(
            raised.calculate("employment_income", YEAR),
            cached_earnings + [increment, 0, 0],
        )
        np.testing.assert_array_equal(
            measuring.get_array("employment_income", YEAR), cached_earnings
        )
        # Eternal inputs retain their value when read through another year.
        np.testing.assert_array_equal(
            raised.get_array("is_household_head", YEAR - 1),
            expected[("is_household_head", YEAR)],
        )
        np.testing.assert_array_equal(
            sibling.get_array("has_itin", YEAR), [not tin, True, True]
        )
        np.testing.assert_array_equal(
            simulation.get_array("employment_income_before_lsr", YEAR),
            original_earnings,
        )
        assert simulation.get_array("has_itin", YEAR) is None
        assert simulation.input_variables == original_inputs
    finally:
        simulation.branches.pop(name)
        simulation.branches.pop(sibling.branch_name)


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
    base_situation = situation([TEXAS_GAINS_FILER])
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


# Households whose taxes 10-point higher 12% and 22% rates raise, so CBO's
# elasticities give them labor supply responses.
RESPONDING_HOUSEHOLDS = [
    ("TX", {"worker": {"age": 40, "employment_income": 50_000}}, []),
    (
        "CA",
        {
            "head": {
                "age": 45,
                "employment_income": 70_000,
                "self_employment_income": 20_000,
                "weekly_hours_worked": 40,
            },
            "spouse": {
                "age": 43,
                "sstb_self_employment_income": 30_000,
                "weekly_hours_worked": 25,
            },
        },
        [10],
    ),
    (
        "NY",
        {
            "retiree": {
                "age": 67,
                "employment_income": 35_000,
                "social_security_retirement": 18_000,
            }
        },
        [],
    ),
    OHIO_WORKS_FIRST_PARENT,
]
MIDDLE_RATES = {
    "gov.irs.income.bracket.rates.2": {DATE_RANGE: 0.22},
    "gov.irs.income.bracket.rates.3": {DATE_RANGE: 0.32},
}


def test_rates_in_a_dynamic_reform_hold_behavioral_responses():
    """Invariant 5 for the earnings rates.

    Under CBO's elasticities, 10-point higher 12% and 22% rates cut the Texas
    worker's earnings by $1,429 (substitution elasticity 0.25 times their
    after-tax wage change, times $50,000). Before the fix the branch
    recomputed that response on the raised pre-response earnings, so $1,000
    more earnings became about $971 of wages and their rate read 0.3166
    where fresh simulations at fixed behavior give 0.2965.
    """
    policy = reform(MIDDLE_RATES, CBO_LABOR_SUPPLY)
    base_situation = situation(RESPONDING_HOUSEHOLDS)
    simulation = Simulation(situation=base_situation, reform=policy)
    responses = simulation.calculate("labor_supply_behavioral_response", YEAR)
    assert (np.abs(responses) > 100).sum() >= 4

    assert_rates_match(
        simulation,
        fresh_earnings_rates(base_situation, simulation, policy),
        EARNINGS_RATES,
    )


def test_capital_gains_rate_in_a_dynamic_reform_holds_the_response():
    """Invariant 5 for the capital gains rate.

    A 20% rate on the Texas filer's gains (see
    test_capital_gains_rate_applies_preferential_rates) and a -0.62
    elasticity cut their $15,000 of gains by
    15,000 * (exp(-0.62 * ln(0.20 / 0.15)) - 1) = -$2,450. Before the fix
    the branch recomputed the response on $16,000, so $1,000 more gains
    became $837 and the rate read 0.3307 instead of 0.20.
    """
    policy = reform(
        {"gov.irs.capital_gains.rates.2": {DATE_RANGE: 0.20}},
        CAPITAL_GAINS_RESPONSE,
    )
    base_situation = situation([TEXAS_GAINS_FILER])
    simulation = Simulation(situation=base_situation, reform=policy)
    response = simulation.calculate("capital_gains_behavioral_response", YEAR)
    assert response[0] == pytest.approx(-2_450.4, abs=0.5)

    rate = simulation.calculate("marginal_tax_rate_on_capital_gains", YEAR)

    assert rate[0] == pytest.approx(0.20, abs=TOLERANCE)
    assert rate[0] == pytest.approx(
        fresh_capital_gains_rate(base_situation, simulation, policy)[0],
        abs=TOLERANCE,
    )


def values(simulation, variable):
    return np.asarray(simulation.calculate(variable, YEAR, map_to="person"))


@pytest.mark.parametrize("wrapper", [Simulation, Microsimulation])
def test_reformed_simulations_branch_the_baseline_after_moving_inputs(wrapper):
    """Invariant 6 for the baseline branch of either wrapper.

    Core branches the baseline while it constructs a reformed simulation,
    before the wrappers move inputs. The branch kept the Ohio Works First
    parent's wages on employment_income and none on
    employment_income_before_lsr, so its TANF counted no earnings ($7,474.60
    instead of $5,974.60) and its marginal tax rate read -0.2335 instead of
    0.1195.
    """
    policy = reform(TOP_RATE, CBO_LABOR_SUPPLY)
    if wrapper is Simulation:
        base_situation = situation([OHIO_WORKS_FIRST_PARENT])
        reformed = Simulation(situation=base_situation, reform=policy)
        fresh = Simulation(situation=base_situation)
    else:
        reformed = Microsimulation(dataset=_ohio_parent_dataset(6_000), reform=policy)
        fresh = Microsimulation(dataset=_ohio_parent_dataset(6_000))
    baseline = reformed.baseline

    assert baseline is reformed.branches["baseline"]
    assert baseline.baseline is None
    assert baseline.tax_benefit_system is not reformed.tax_benefit_system
    assert set(baseline.input_variables) == set(fresh.input_variables)
    for variable in (
        "employment_income_before_lsr",
        "weekly_hours_worked_before_lsr",
        "long_term_capital_gains",
        "tanf",
        "household_net_income",
        "marginal_tax_rate",
    ):
        np.testing.assert_allclose(
            values(baseline, variable),
            values(fresh, variable),
            atol=TOLERANCE,
            err_msg=variable,
        )


def test_behavioral_response_measurements_match_fresh_simulations():
    """Invariant 6 for the branches that measure behavioral responses.

    The top-rate reform changes no tax or benefit of these households, so
    none of them responds. Before the fix, the baseline measurement branch
    erased the Ohio Works First parent's pre-response wages in its rate
    branch. It measured a -0.2335 baseline rate against the reform's 0.1195
    and a $24,365 baseline net income against $23,318, so the parent
    responded to a reform that does not touch them with $416 less earnings.
    """
    policy = reform(TOP_RATE, CBO_LABOR_SUPPLY)
    base_situation = situation(RESPONDING_HOUSEHOLDS)
    simulation = Simulation(situation=base_situation, reform=policy)
    response = simulation.calculate("labor_supply_behavioral_response", YEAR)
    measurements = getattr(simulation, BEHAVIORAL_RESPONSE_CACHE_ATTR)[
        str(make_period(YEAR))
    ]
    fresh = {
        "baseline": Simulation(situation=base_situation),
        "reform": Simulation(situation=base_situation, reform=reform(TOP_RATE)),
    }

    for name, comparison in fresh.items():
        for measurement, variable in (
            ("mtr", "marginal_tax_rate"),
            ("capital_gains_mtr", "marginal_tax_rate_on_capital_gains"),
            ("net_income", "household_net_income"),
        ):
            np.testing.assert_allclose(
                measurements[f"{name}_{measurement}"],
                values(comparison, variable),
                atol=TOLERANCE,
                err_msg=f"{name}_{measurement}",
            )
    np.testing.assert_allclose(response, 0, atol=TOLERANCE)
