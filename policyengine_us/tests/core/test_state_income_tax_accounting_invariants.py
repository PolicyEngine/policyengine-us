"""State income tax accounting invariants, for every state.

Household net income does not read each state's own final income tax. It
subtracts ``household_state_tax_before_refundable_credits`` and adds
``household_refundable_state_tax_credits``, which sum every state's tax before
refundable credits and every state's refundable credits from two cross-state
lists. A state whose final tax applies a rule that those two components do not
carry is then right in its own ``xx_income_tax`` and wrong in household net
income. Five cases shipped: the Wisconsin retirement income exclusion
election, the Vermont child care contribution, the Colorado alternative
minimum tax, Mississippi's nonrefundable credits, and the contributed Michigan
surtax.

Three properties guard against a sixth:

1. Structure, with no simulation. Where a state's ``xx_income_tax`` is a sum,
   it adds exactly that state's members of the before-refundable list and
   subtracts exactly its members of the refundable list.
2. ``state_income_tax`` equals the state's own ``xx_income_tax`` wherever the
   model defines one, and is zero in the states with no modelled income tax.
3. A household's state tax before refundable credits, less its refundable
   state credits, equals the ``state_income_tax`` of all its tax units plus
   their ``state_use_tax``. Use tax is the one intended difference: the
   household pays it to the state, but it is not an income tax
   (``state_income_tax_excludes_use_tax.yaml``).

Properties 2 and 3 must hold for every tax unit and household, so the tests
draw a seeded population in each of the 50 states and DC and run it as one
vectorized simulation. Where a state's ``xx_income_tax`` is a sum, property 1
already implies property 2, so Hypothesis draws further households only in the
states that compute it with a formula. YAML cases cannot express these
properties: each compares two computed totals on every row instead of one
total with a stated amount.
"""

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation
from policyengine_us.system import system

YEAR = 2025
SEED = 20261009
N_RANDOM_PER_STATE = 6
TOLERANCE = 0.05  # dollars; float32 sums of five- and six-figure amounts

STATES = (
    "AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS "
    "MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY"
).split()

# The model has no income tax for these states. The set is asserted against
# the variable registry, so a state cannot drop out of the properties unnoticed.
STATES_WITHOUT_INCOME_TAX = {"AK", "FL", "NV", "SD", "TN", "TX", "WY"}

# These states compute ``xx_income_tax`` with a formula, so property 1 cannot
# read its parts. Property 2 covers them.
STATES_WITH_FORMULA_INCOME_TAX = {
    # Lower of the joint return and separate returns on one form, each after
    # refundable credits.
    "MT",
    # No refundable credits: the before-refundable list holds nc_income_tax.
    "NC",
    # No tax at or below the filing threshold.
    "NJ",
    # Tax before refundable credits less refundable credits, both following
    # the retirement income exclusion election.
    "WI",
}


def _list_members(parameter):
    return set(parameter(f"{YEAR}-01-01"))


def _state_members(members, state):
    return {member for member in members if member.startswith(f"{state.lower()}_")}


@pytest.fixture(scope="module")
def before_refundable_list():
    return _list_members(
        system.parameters.gov.states.household.state_income_tax_before_refundable_credits
    )


@pytest.fixture(scope="module")
def refundable_list():
    return _list_members(
        system.parameters.gov.states.household.state_refundable_credits
    )


def test_states_without_an_income_tax_variable_are_the_expected_ones():
    without = {
        state
        for state in STATES
        if f"{state.lower()}_income_tax" not in system.variables
    }
    assert without == STATES_WITHOUT_INCOME_TAX


def test_states_with_a_formula_income_tax_are_the_expected_ones():
    with_formula = {
        state
        for state in STATES
        if state not in STATES_WITHOUT_INCOME_TAX
        and system.variables[f"{state.lower()}_income_tax"].adds is None
    }
    assert with_formula == STATES_WITH_FORMULA_INCOME_TAX


def test_list_members_are_defined_variables(before_refundable_list, refundable_list):
    undefined = (before_refundable_list | refundable_list) - set(system.variables)
    assert not undefined


def test_household_refundable_list_matches_the_state_refundable_list(refundable_list):
    household_list = _list_members(
        system.parameters.gov.household.household_refundable_state_credits
    )
    assert household_list == refundable_list


@pytest.mark.parametrize(
    "state",
    sorted(set(STATES) - STATES_WITHOUT_INCOME_TAX - STATES_WITH_FORMULA_INCOME_TAX),
)
def test_state_income_tax_parts_are_the_states_list_members(
    state, before_refundable_list, refundable_list
):
    own = system.variables[f"{state.lower()}_income_tax"]
    assert set(own.adds) == _state_members(before_refundable_list, state)
    assert set(own.subtracts or []) == _state_members(refundable_list, state)


# Each archetype is a list of tax units in one household. All inputs are leaf
# facts. A child is an age, or a dict of person inputs.
ARCHETYPES = [
    # Single worker.
    [{"adults": [{"age": 30, "employment_income": 30_000}]}],
    # Low-income single parent who rents: refundable state credits.
    [
        {
            "adults": [{"age": 32, "employment_income": 18_000, "rent": 9_000}],
            "children": [3, 7],
        }
    ],
    # Single parent who pays for child care: nonrefundable state credits.
    [
        {
            "adults": [{"age": 30, "employment_income": 30_000}],
            "children": [3, 5],
            "spm_unit": {"spm_unit_pre_subsidy_childcare_expenses": 6_000},
        }
    ],
    # Married couple with two children.
    [
        {
            "adults": [
                {"age": 40, "employment_income": 60_000},
                {"age": 38, "employment_income": 40_000},
            ],
            "children": [5, 9],
        }
    ],
    # Single retiree with a pension and Social Security.
    [
        {
            "adults": [
                {
                    "age": 70,
                    "taxable_private_pension_income": 40_000,
                    "social_security_retirement": 24_000,
                }
            ]
        }
    ],
    # Retired couple with pensions, Social Security and investment income.
    [
        {
            "adults": [
                {
                    "age": 68,
                    "taxable_private_pension_income": 30_000,
                    "social_security_retirement": 20_000,
                    "long_term_capital_gains": 10_000,
                    "taxable_interest_income": 3_000,
                },
                {
                    "age": 72,
                    "taxable_private_pension_income": 30_000,
                    "social_security_retirement": 20_000,
                },
            ]
        }
    ],
    # High earner with capital gains and dividends.
    [
        {
            "adults": [
                {
                    "age": 50,
                    "employment_income": 400_000,
                    "long_term_capital_gains": 100_000,
                    "qualified_dividend_income": 20_000,
                }
            ]
        }
    ],
    # Self-employed parent who rents.
    [
        {
            "adults": [{"age": 45, "self_employment_income": 50_000, "rent": 12_000}],
            "children": [10],
        }
    ],
    # Very low earner, below state filing thresholds.
    [{"adults": [{"age": 25, "employment_income": 5_000}]}],
    # Elderly renter living on Social Security.
    [{"adults": [{"age": 75, "social_security_retirement": 12_000, "rent": 7_000}]}],
    # Low-income retiree who rents: property tax and homestead credits.
    [
        {
            "adults": [
                {"age": 67, "taxable_private_pension_income": 16_313, "rent": 12_000}
            ]
        }
    ],
    # Two tax units in one household: parents and an adult child who works.
    [
        {
            "adults": [
                {"age": 58, "employment_income": 70_000},
                {"age": 57, "taxable_private_pension_income": 25_000},
            ]
        },
        {"adults": [{"age": 24, "employment_income": 28_000}]},
    ],
]


def _random_tax_unit(rng):
    adults = []
    for _ in range(int(rng.integers(1, 3))):
        age = int(rng.integers(19, 90))
        adults.append(
            {
                "age": age,
                "employment_income": float(
                    round(rng.choice([0, 0, rng.uniform(0, 150_000)]))
                ),
                "self_employment_income": float(
                    round(rng.choice([0, 0, 0, rng.uniform(-20_000, 80_000)]))
                ),
                "taxable_private_pension_income": float(
                    round(rng.choice([0, rng.uniform(0, 90_000)]) if age >= 55 else 0)
                ),
                "social_security_retirement": float(
                    round(
                        rng.choice([0, rng.uniform(5_000, 40_000)]) if age >= 62 else 0
                    )
                ),
                "long_term_capital_gains": float(
                    round(rng.choice([0, 0, rng.uniform(-5_000, 60_000)]))
                ),
                "taxable_interest_income": float(
                    round(rng.choice([0, rng.uniform(0, 8_000)]))
                ),
                "rent": float(round(rng.choice([0, rng.uniform(3_000, 24_000)]))),
                "real_estate_taxes": float(
                    round(rng.choice([0, 0, rng.uniform(500, 9_000)]))
                ),
            }
        )
    children = [
        int(rng.integers(0, 17)) for _ in range(int(rng.choice([0, 0, 1, 2, 3])))
    ]
    return {"adults": adults, "children": children}


def _situation(households, year):
    """Build a situation from (state, tax units) pairs, one per household."""
    people, tax_units, spm_units, household_entities = {}, {}, {}, {}

    def at_year(inputs):
        return {variable: {year: value} for variable, value in inputs.items()}

    for household_index, (state, household_tax_units) in enumerate(households):
        household_members = []
        spm_unit_inputs = {}
        for unit_index, unit in enumerate(household_tax_units):
            key = f"{household_index}_{unit_index}"
            members = []
            for adult_index, adult in enumerate(unit["adults"]):
                name = f"adult_{adult_index}_{key}"
                members.append(name)
                people[name] = at_year(adult)
            for child_index, child in enumerate(unit.get("children", [])):
                name = f"child_{child_index}_{key}"
                members.append(name)
                people[name] = at_year(
                    child if isinstance(child, dict) else {"age": child}
                )
            tax_units[f"tax_unit_{key}"] = {"members": members}
            spm_unit_inputs.update(unit.get("spm_unit", {}))
            household_members += members
        spm_units[f"spm_unit_{household_index}"] = {
            "members": household_members,
            **at_year(spm_unit_inputs),
        }
        household_entities[f"household_{household_index}"] = {
            "members": household_members,
            "state_code": {year: state},
        }
    return {
        "people": people,
        "tax_units": tax_units,
        "spm_units": spm_units,
        "households": household_entities,
    }


def _seeded_households():
    rng = np.random.default_rng(SEED)
    households = []
    for state in STATES:
        households += [(state, archetype) for archetype in ARCHETYPES]
        households += [
            (state, [_random_tax_unit(rng)]) for _ in range(N_RANDOM_PER_STATE)
        ]
    return households


def _tax_unit_state(simulation, year):
    tax_unit = simulation.populations["tax_unit"]
    return np.asarray(tax_unit.household("state_code", year).decode_to_str())


def _tax_unit(simulation, variable, year=YEAR):
    return np.asarray(simulation.calculate(variable, year), dtype=float)


def _household(simulation, variable, year=YEAR):
    return np.asarray(
        simulation.calculate(variable, year, map_to="household"), dtype=float
    )


def _check_state_income_tax_equals_own_income_tax(simulation, state, year=YEAR):
    in_state = _tax_unit_state(simulation, year) == state
    state_income_tax = _tax_unit(simulation, "state_income_tax", year)[in_state]
    if state in STATES_WITHOUT_INCOME_TAX:
        np.testing.assert_array_equal(state_income_tax, 0)
        return
    own_income_tax = _tax_unit(simulation, f"{state.lower()}_income_tax", year)
    np.testing.assert_allclose(
        state_income_tax, own_income_tax[in_state], atol=TOLERANCE, rtol=0
    )


def _check_household_totals(simulation, year=YEAR):
    before_refundable = _household(
        simulation, "household_state_tax_before_refundable_credits", year
    )
    refundable = _household(simulation, "household_refundable_state_tax_credits", year)
    state_income_tax = _household(simulation, "state_income_tax", year)
    use_tax = _household(simulation, "state_use_tax", year)
    np.testing.assert_allclose(
        before_refundable - refundable,
        state_income_tax + use_tax,
        atol=TOLERANCE,
        rtol=0,
    )


@pytest.fixture(scope="module")
def simulation():
    return Simulation(situation=_situation(_seeded_households(), YEAR))


@pytest.fixture(scope="module")
def tax_unit_state(simulation):
    return _tax_unit_state(simulation, YEAR)


def test_population_exercises_the_properties(simulation, tax_unit_state):
    state_income_tax = _tax_unit(simulation, "state_income_tax")
    for state in STATES:
        assert (tax_unit_state == state).sum() >= len(ARCHETYPES) + N_RANDOM_PER_STATE
    # Net refunds from refundable credits, in many states.
    assert len(set(tax_unit_state[state_income_tax < 0])) >= 10
    # Use tax, the labelled exception in property 3.
    assert (_household(simulation, "state_use_tax") > 0).sum() >= 10
    # Households with more than one tax unit.
    households = simulation.populations["household"].count
    assert simulation.populations["tax_unit"].count > households
    # Rules that were once missing from household net income. Leaf inputs
    # cannot produce a Colorado alternative minimum tax or the contributed
    # Michigan surtax; property 1 covers those.
    elected = np.asarray(
        simulation.calculate("wi_retirement_income_exclusion_elected", YEAR)
    )
    assert elected.sum() >= 2
    assert (_tax_unit(simulation, "vt_child_care_contributions") > 0).sum() >= 2
    assert (_tax_unit(simulation, "ms_non_refundable_credits") > 0).sum() >= 1


@pytest.mark.parametrize("state", STATES)
def test_state_income_tax_equals_the_states_own_income_tax(simulation, state):
    _check_state_income_tax_equals_own_income_tax(simulation, state)


def test_household_state_tax_totals_equal_state_income_tax_plus_use_tax(simulation):
    _check_household_totals(simulation)


# Whole-dollar amounts keep float32 sums exact. The fixed values sit on and
# beside Wisconsin's $24,000 exclusion cap and New Jersey's filing thresholds.
amounts = st.one_of(
    st.just(0.0),
    st.sampled_from([9_999.0, 10_000.0, 10_001.0, 20_000.0, 24_000.0, 24_001.0]),
    st.integers(1, 150_000).map(float),
)


@st.composite
def formula_state_households(draw):
    adults = []
    for _ in range(draw(st.integers(1, 2))):
        age = draw(st.one_of(st.sampled_from([64, 65, 66, 67]), st.integers(19, 90)))
        adults.append(
            {
                "age": age,
                "employment_income": draw(amounts),
                "self_employment_income": draw(
                    st.one_of(st.just(0.0), st.integers(-30_000, 80_000).map(float))
                ),
                "taxable_private_pension_income": draw(amounts) if age >= 55 else 0.0,
                "social_security_retirement": (
                    draw(st.integers(0, 40_000).map(float)) if age >= 62 else 0.0
                ),
                "long_term_capital_gains": draw(
                    st.one_of(st.just(0.0), st.integers(-8_000, 80_000).map(float))
                ),
                "rent": draw(
                    st.one_of(st.just(0.0), st.integers(1, 24_000).map(float))
                ),
            }
        )
    children = draw(st.lists(st.integers(0, 16), max_size=3))
    unit = {"adults": adults, "children": children}
    if children:
        unit["spm_unit"] = {
            "spm_unit_pre_subsidy_childcare_expenses": draw(
                st.one_of(st.just(0.0), st.integers(1, 12_000).map(float))
            )
        }
    state = draw(st.sampled_from(sorted(STATES_WITH_FORMULA_INCOME_TAX)))
    return state, [unit]


@settings(
    max_examples=4,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(
    st.lists(formula_state_households(), min_size=10, max_size=40),
    # Montana let spouses file separately on one form through 2023, and the
    # Wisconsin retirement income exclusion starts in 2025.
    st.sampled_from([2023, 2025]),
)
def test_formula_states_keep_the_properties(households, year):
    simulation = Simulation(situation=_situation(households, year))
    for state in sorted(STATES_WITH_FORMULA_INCOME_TAX):
        _check_state_income_tax_equals_own_income_tax(simulation, state, year)
    _check_household_totals(simulation, year)
