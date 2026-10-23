"""Years in which the tips and overtime deductions apply (26 U.S.C. 224, 225).

Sections 224 and 225 apply to taxable years beginning after December 31, 2024
(Pub. L. 119-21, secs. 70201(j) and 70202(g)), and 224(h) and 225(g) say "No
deduction shall be allowed under this section for any taxable year beginning
after December 31, 2028."

The first test builds two simulations of many tax units (current law, and
both deductions switched on in every year); the second builds one. Inputs are
the same in every year. The tests check:

1. Outside 2025-2028 both deductions are zero for every return.
2. The year switch is the only thing that changes across years. With both
   deductions switched on in every year, each return gets in every year what
   it gets in 2025. Inside 2025-2028 that is also the current-law amount. This
   holds because the caps, thresholds and phase-out parameters each carry one
   value, dated 2025; if any is later indexed or amended, compare against
   that year's value instead.
3. South Carolina's add-back, Montana's Schedule 1-A subtraction and
   Arizona's subtractions pass the federal deductions through exactly. Giving
   a return its tips and overtime moves each by the federal tips and overtime
   deductions in 2026-2028, and not at all from 2029 (Hypothesis).
"""

import numpy as np
import pytest
from hypothesis import Phase, example, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation
from policyengine_us.system import system

YEARS = range(2015, 2036)
FIRST_YEAR, LAST_YEAR = 2025, 2028
STATUSES = ("SINGLE", "JOINT", "SEPARATE", "HEAD_OF_HOUSEHOLD", "SURVIVING_SPOUSE")
OUTPUTS = ("tip_income_deduction", "overtime_income_deduction")
SWITCHES = (
    "gov.irs.deductions.tip_income.in_effect",
    "gov.irs.deductions.overtime_income.in_effect",
)
# Each state's channel for the federal deductions, as a tax unit amount.
STATE_OUTPUTS = {
    "SC": "sc_obbba_addback",
    "MT": "mt_federal_obbba_subtraction",
    "AZ": "az_subtractions",
}
STATE_YEARS = (2026, 2027, 2028, 2029, 2030, 2035)


def _situation(units, years, state_of=None):
    """One tax unit per (status, magi, tips, overtime); joint units get a
    spouse with the same tips and overtime, others one person."""
    people, tax_units, marital_units, households = {}, {}, {}, {}
    for i, (status, magi, tips, overtime) in enumerate(units):
        members = [f"head{i}"] + ([f"spouse{i}"] if status == "JOINT" else [])
        for name in members:
            people[name] = {
                "age": {year: 40 for year in years},
                "ssn_card_type": {year: "CITIZEN" for year in years},
                "treasury_tipped_occupation_code": {year: 102 for year in years},
                "tip_income": {year: float(tips) for year in years},
                "fsla_overtime_premium": {year: float(overtime) for year in years},
            }
        tax_units[f"t{i}"] = {
            "members": members,
            "filing_status": {year: status for year in years},
            "adjusted_gross_income": {year: float(magi) for year in years},
            # Fixed, so that adding tips cannot change South Carolina's
            # standard deduction add-back through the itemizing choice.
            "tax_unit_itemizes": {year: False for year in years},
        }
        marital_units[f"m{i}"] = {"members": members}
        state = state_of[i] if state_of else "TX"
        households[f"h{i}"] = {
            "members": members,
            "state_code": {year: state for year in years},
        }
    return {
        "people": people,
        "tax_units": tax_units,
        "marital_units": marital_units,
        "households": households,
    }


def _draw(seed, n=120):
    rng = np.random.default_rng(seed)
    units = []
    for _ in range(n):
        status = STATUSES[int(rng.integers(len(STATUSES)))]
        magi = float(rng.choice([0, 60_000, 150_000, int(rng.integers(0, 500_001))]))
        tips = int(rng.choice([0, 25_000, int(rng.integers(0, 40_001))]))
        overtime = int(rng.choice([0, 12_500, int(rng.integers(0, 30_001))]))
        units.append((status, magi, tips, overtime))
    return units


@pytest.mark.parametrize("seed", [0, 1])
def test_deductions_apply_only_from_2025_through_2028(seed):
    units = _draw(seed)
    situation = _situation(units, YEARS)
    baseline = Simulation(tax_benefit_system=system, situation=situation)
    always = Simulation(
        situation=situation,
        reform={switch: {"2015-01-01.2100-12-31": True} for switch in SWITCHES},
    )
    for name in OUTPUTS:
        first_year = baseline.calculate(name, FIRST_YEAR)
        # Guard: the draw must hold returns with a positive deduction.
        assert np.any(first_year > 0), name
        for year in YEARS:
            current_law = baseline.calculate(name, year)
            switched_on = always.calculate(name, year)
            # 2. The switch alone changes the amount across years.
            np.testing.assert_array_equal(switched_on, first_year, (name, year))
            if FIRST_YEAR <= year <= LAST_YEAR:
                np.testing.assert_array_equal(current_law, first_year, (name, year))
            else:
                # 1. Nothing outside 2025-2028.
                assert np.all(current_law == 0), (name, year)


amounts = st.one_of(
    st.sampled_from([0, 12_500, 25_000]), st.integers(min_value=0, max_value=40_000)
)
cases = st.tuples(
    st.sampled_from(STATUSES),
    st.one_of(
        st.sampled_from([60_000, 150_000, 300_000]),
        st.integers(min_value=0, max_value=500_000),
    ),
    amounts,
    amounts,
)


# Shrinking a failure takes minutes on a simulation this size; the failing
# example is still reported.
@settings(
    max_examples=5,
    deadline=None,
    derandomize=True,
    phases=(Phase.explicit, Phase.generate),
)
@given(drawn=st.lists(cases, min_size=8, max_size=8))
# Generation starts from the minimal draw (no tips or overtime), so one
# explicit draw makes sure positive deductions reach every state.
@example(drawn=[(status, 60_000, 10_000, 5_000) for status in STATUSES] * 2)
def test_states_pass_the_federal_deductions_through_only_while_they_apply(drawn):
    # Each drawn return appears in each state twice: with its tips and
    # overtime, and with none.
    units, state_of = [], []
    for status, magi, tips, overtime in drawn:
        for state in STATE_OUTPUTS:
            units += [(status, magi, tips, overtime), (status, magi, 0, 0)]
            state_of += [state, state]
    simulation = Simulation(
        tax_benefit_system=system,
        situation=_situation(units, STATE_YEARS, state_of),
    )
    state_of = np.array(state_of)
    for year in STATE_YEARS:
        federal = sum(simulation.calculate(name, year) for name in OUTPUTS)
        for state, name in STATE_OUTPUTS.items():
            amount = simulation.calculate(name, year, map_to="tax_unit")
            rows = np.flatnonzero(state_of == state)
            with_pay, without_pay = rows[0::2], rows[1::2]
            moved = amount[with_pay] - amount[without_pay]
            # 3. Exactly the federal deductions while they apply, else nothing.
            expected = federal[with_pay] if year <= LAST_YEAR else 0
            np.testing.assert_allclose(moved, expected, atol=0.01, err_msg=(name, year))
            assert np.all(federal[without_pay] == 0), (name, year)
