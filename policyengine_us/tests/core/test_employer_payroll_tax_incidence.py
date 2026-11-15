"""Fixed employer cost wage response to federal employer payroll tax reforms.

employer_payroll_tax_fixed_employer_cost_change moves wages so that payroll
wages plus federal employer payroll taxes stay at their baseline amount. For a
schedule of taxes ``rate * min(w, base)`` the cost ``w + tax(w)`` is
continuous, piecewise linear and increasing in payroll wages w, so:

1. Inverse: ``wages_at_employer_cost`` returns the one wage of zero or more
   whose cost under the schedule equals the target, for any target of zero or
   more; a brute-force bisection agrees; and an unchanged schedule returns the
   same wages, so a reform that leaves employer taxes alone moves no wages.
   It reproduces the after-offset wages in JCT's three worked examples.
2. Monotonicity: raising any rate weakly lowers the wage at a given cost.
3. Conservation: under a reform with the default employee share of 1, every
   worker's federal employer cost in the reformed simulation equals the
   baseline's, across the FUTA base and the Social Security cap, with and
   without FICA pre-tax deductions, and in a FUTA credit reduction state.
4. Share: with an employee share of one half, the model's change is half the
   change the inverse gives (a differential test of model against inverse).
5. No reform, no change: zero in a simulation without a reform and for anyone
   without payroll wages.
6. Marginal wedge: in a branch that raises earnings, wages rise by
   (1 + m_b) / (1 + m_r) per dollar, where m is the federal employer rate at
   the margin, so marginal tax rates measured in a reform carry the employer
   tax; the labor supply measurement branch applies the change.

The model stores values as float32, so model comparisons allow its rounding.
Each model test reuses one of two vectorized reform simulations.
"""

import numpy as np
import pytest
from hypothesis import HealthCheck, example, given, settings
from hypothesis import strategies as st
from policyengine_core.periods import period as make_period
from policyengine_core.reforms import Reform

from policyengine_us import Simulation
from policyengine_us.variables.gov.simulation.behavioral_response_measurements import (
    BEHAVIORAL_RESPONSE_MEASUREMENT_BRANCH,
)
from policyengine_us.variables.gov.simulation.employer_payroll_tax_incidence.employer_payroll_tax_fixed_employer_cost_change import (
    employer_payroll_tax_from_components,
    federal_employer_payroll_tax_components,
    wages_at_employer_cost,
)
from policyengine_us.variables.household.marginal_tax_rate_helpers import (
    create_perturbed_branch,
)

YEAR = 2026
DATES = "2020-01-01.2100-12-31"
PAYROLL = "gov.irs.payroll"
SHARE = "gov.simulation.employer_payroll_tax_incidence.employee_share"
CHANGE = "employer_payroll_tax_fixed_employer_cost_change"

PURE_SETTINGS = settings(max_examples=200, deadline=None, derandomize=True)

RATES = st.floats(min_value=0, max_value=0.6, allow_nan=False)
BASES = st.one_of(
    st.floats(min_value=0, max_value=1e6, allow_nan=False), st.just(np.inf)
)
COMPONENTS = st.lists(st.tuples(RATES, BASES), max_size=4)
COSTS = st.lists(
    st.floats(min_value=0, max_value=2e6, allow_nan=False), min_size=1, max_size=20
)


def employer_cost(wages, components):
    return np.asarray(wages, dtype=np.float64) + employer_payroll_tax_from_components(
        wages, components
    )


def bisect_wages(cost, components):
    """Wage at a cost by bisection, independent of the segment inversion."""
    low, high = 0.0, max(float(cost), 1.0)
    for _ in range(200):
        middle = (low + high) / 2
        if employer_cost([middle], components)[0] < cost:
            low = middle
        else:
            high = middle
    return (low + high) / 2


@PURE_SETTINGS
@given(COMPONENTS, COSTS)
@example([(0.062, 184_500.0), (0.0145, np.inf), (0.006, 7_000.0)], [0.0, 7_042.0])
def test_inverse_recovers_the_cost(components, costs):
    wages = wages_at_employer_cost(costs, components)
    assert np.all(wages >= 0)
    np.testing.assert_allclose(
        employer_cost(wages, components), costs, rtol=1e-12, atol=1e-6
    )


@PURE_SETTINGS
@given(COMPONENTS, COSTS)
def test_same_schedule_returns_the_same_wages(components, wages):
    """Without a change in the schedule there is no change in wages."""
    cost = employer_cost(wages, components)
    np.testing.assert_allclose(
        wages_at_employer_cost(cost, components), wages, rtol=1e-12, atol=1e-6
    )


@PURE_SETTINGS
@given(COMPONENTS, COSTS)
def test_inverse_matches_bisection(components, costs):
    wages = wages_at_employer_cost(costs, components)
    expected = [bisect_wages(cost, components) for cost in costs]
    np.testing.assert_allclose(wages, expected, rtol=1e-9, atol=1e-6)


@PURE_SETTINGS
@given(
    COMPONENTS.filter(len),
    st.data(),
    st.floats(min_value=0, max_value=0.5, allow_nan=False),
    COSTS,
)
def test_higher_rate_lowers_wages(components, data, increase, costs):
    index = data.draw(st.integers(min_value=0, max_value=len(components) - 1))
    rate, base = components[index]
    raised = list(components)
    raised[index] = (rate + increase, base)
    assert np.all(
        wages_at_employer_cost(costs, raised)
        <= wages_at_employer_cost(costs, components) + 1e-9
    )


@pytest.mark.parametrize(
    "wages, benefits, expected",
    [(10_000, 0, 9_954), (200_000, 10_000, 199_443), (1_000_000, 20_000, 999_427)],
)
def test_inverse_reproduces_jct_examples(wages, benefits, expected):
    """Differential against JCX-89-16's worked examples (pp. 10-11, Table 1).

    JCT raises the employer OASDI rate from 6.2% to 6.7% under 2016 law (a
    $118,500 cap, 1.45% HI, no FUTA) and keeps nontaxable benefits a fixed
    share of wages, so here they enter as an uncapped component at rate
    benefits / wages. The model itself leaves benefits out of the cost.
    https://www.jct.gov/getattachment/df6ad7a8-d3f8-4f39-b465-1cbe5b077d20/x-89-16-4962.pdf#page=12
    """
    benefits_rate = benefits / wages
    baseline = [(0.062, 118_500), (0.0145, np.inf), (benefits_rate, np.inf)]
    policy = [(0.067, 118_500), (0.0145, np.inf), (benefits_rate, np.inf)]
    cost = employer_cost([wages], baseline)
    assert wages_at_employer_cost(cost, policy)[0] == pytest.approx(expected, abs=0.5)


def test_inverse_takes_rates_that_vary_by_person():
    rates = np.array([0.006, 0.018])
    components = [(0.062, 184_500.0), (0.0145, np.inf), (rates, 7_000.0)]
    costs = np.array([5_000.0, 80_000.0])
    wages = wages_at_employer_cost(costs, components)
    np.testing.assert_allclose(employer_cost(wages, components), costs, rtol=1e-12)


def test_inverse_rejects_a_cost_that_falls_with_wages():
    with pytest.raises(ValueError):
        wages_at_employer_cost([1_000.0], [(-1.5, np.inf)])


# A worker at each side of the FUTA base and the Social Security cap, a worker
# whose FICA pre-tax deductions exceed pay, and workers with deductions, in
# Texas and in California, which has a FUTA credit reduction.
CAP = 184_500
PAY = [0, 1, 3_000, 6_999, 7_000, 7_001, 50_000, CAP - 1, CAP, CAP + 1, 250_000]
PAY += [1_000_000, 1_000, 60_000, 200_000]
PREMIUMS = [0] * 12 + [2_000, 5_000, 5_000]
STATES = ["TX", "CA"] * 7 + ["CA"]


def situation():
    people = {}
    for i, (pay, premium) in enumerate(zip(PAY, PREMIUMS)):
        people[f"p{i}"] = {
            "age": {YEAR: 40},
            "employment_income": {YEAR: pay},
            "pre_tax_health_insurance_premiums": {YEAR: premium},
        }
    units = {
        entity: {f"u{i}": {"members": [f"p{i}"]} for i in range(len(PAY))}
        for entity in ("tax_units", "spm_units", "families", "marital_units")
    }
    households = {
        f"h{i}": {"members": [f"p{i}"], "state_code": {YEAR: state}}
        for i, state in enumerate(STATES)
    }
    return {"people": people, **units, "households": households}


def simulate(changes):
    reform = Reform.from_dict(
        {name: {DATES: value} for name, value in changes.items()}, country_id="us"
    )
    return Simulation(situation=situation(), reform=reform)


def federal_employer_cost(simulation):
    return sum(
        simulation.calculate(variable, YEAR).astype(np.float64)
        for variable in (
            "payroll_tax_gross_wages",
            "employer_social_security_tax",
            "employer_medicare_tax",
            "employer_federal_unemployment_tax",
        )
    )


# Reform A raises every federal employer tax and moves both bases, at the
# default employee share of 1. Reform B removes the Social Security cap, cuts
# the employer rates and passes half the change to wages.
RAISE = {
    f"{PAYROLL}.social_security.rate.employer": 0.162,
    f"{PAYROLL}.social_security.cap": 400_000,
    f"{PAYROLL}.medicare.rate.employer": 0.2145,
    f"{PAYROLL}.federal_unemployment.effective_rate": 0.01,
    f"{PAYROLL}.federal_unemployment.taxable_wage_base": 15_000,
}
HALF_CUT_NO_CAP = {
    f"{PAYROLL}.social_security.rate.employer": 0.031,
    f"{PAYROLL}.social_security.cap": np.inf,
    f"{PAYROLL}.medicare.rate.employer": 0.01,
    SHARE: 0.5,
}


@pytest.fixture(scope="module")
def raised():
    return simulate(RAISE)


@pytest.fixture(scope="module")
def half_cut():
    return simulate(HALF_CUT_NO_CAP)


def test_reform_holds_federal_employer_cost(raised):
    baseline = raised.baseline
    has_wages = baseline.calculate("payroll_tax_gross_wages", YEAR) > 0
    change = raised.calculate(CHANGE, YEAR)
    # float32 storage: about 7 significant digits of each stored term.
    np.testing.assert_allclose(
        federal_employer_cost(raised)[has_wages],
        federal_employer_cost(baseline)[has_wages],
        rtol=1e-6,
        atol=0.02,
    )
    np.testing.assert_array_equal(change[~has_wages], 0)
    assert np.all(change[has_wages] < 0)
    np.testing.assert_allclose(
        raised.calculate("employment_income", YEAR),
        baseline.calculate("employment_income", YEAR) + change,
        rtol=1e-6,
    )
    np.testing.assert_array_equal(baseline.calculate(CHANGE, YEAR), 0)


def test_change_is_the_share_of_the_fixed_cost_change(half_cut):
    """Differential: the model's change equals half the pure inverse's."""
    baseline = half_cut.baseline
    wages = baseline.calculate("payroll_tax_gross_wages", YEAR).astype(np.float64)
    state_code = baseline.populations["household"]("state_code", YEAR)
    state_code = baseline.populations["person"].household.project(state_code)
    components = {}
    for name, current in (("baseline", baseline), ("reform", half_cut)):
        components[name] = federal_employer_payroll_tax_components(
            current.tax_benefit_system.parameters(YEAR).gov.irs.payroll,
            state_code,
        )
    cost = wages + employer_payroll_tax_from_components(wages, components["baseline"])
    expected = 0.5 * (wages_at_employer_cost(cost, components["reform"]) - wages)
    np.testing.assert_allclose(
        half_cut.calculate(CHANGE, YEAR), expected, rtol=1e-6, atol=0.02
    )
    # The cuts raise pay below the old cap; with no cap, the top earner's
    # employer Social Security tax rises, so their pay falls.
    change = half_cut.calculate(CHANGE, YEAR)
    assert change[PAY.index(50_000)] > 0 and change[PAY.index(1_000_000)] < 0


def test_raised_earnings_carry_the_employer_wedge(raised):
    """Rate branches see (1 + m_b) / (1 + m_r) of each added dollar.

    Worker p6 earns $50,000 in Texas, above the FUTA bases and below both caps,
    so the marginal federal employer rate is the Social Security rate plus the
    Medicare rate.
    """

    def margin(simulation):
        payroll = simulation.tax_benefit_system.parameters(YEAR).gov.irs.payroll
        return payroll.social_security.rate.employer + payroll.medicare.rate.employer

    worker = PAY.index(50_000)
    delta = 100.0
    increments = np.zeros(len(PAY))
    increments[worker] = delta
    expected_gain = (1 + margin(raised.baseline)) / (1 + margin(raised))
    for current, expected in ((raised, expected_gain), (raised.baseline, 1.0)):
        base = current.calculate("employment_income", YEAR)[worker]
        branch = create_perturbed_branch(
            current,
            make_period(YEAR),
            "employer_wedge",
            {"employment_income": increments},
        )
        try:
            gain = branch.calculate("employment_income", YEAR)[worker] - base
        finally:
            del current.branches["employer_wedge"]
        assert gain / delta == pytest.approx(expected, rel=1e-4)


def test_reform_measurement_branch_applies_the_change(raised):
    """The labor supply measurement branch keeps the reform's baseline.

    get_behavioral_response_measurements measures the reformed net income and
    marginal tax rate in this branch, so it must apply the wage change. Its
    baseline counterpart has no baseline of its own, so the formula returns 0
    there.
    """
    branch = raised.get_branch(
        BEHAVIORAL_RESPONSE_MEASUREMENT_BRANCH, clone_system=True
    )
    try:
        np.testing.assert_allclose(
            branch.calculate(CHANGE, YEAR), raised.calculate(CHANGE, YEAR), rtol=1e-6
        )
    finally:
        del raised.branches[BEHAVIORAL_RESPONSE_MEASUREMENT_BRANCH]
