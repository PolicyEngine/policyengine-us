"""Fixed employer cost wage response to federal employer payroll tax reforms.

employer_payroll_tax_fixed_employer_cost_change moves wages so that payroll
wages plus federal employer payroll taxes stay at their baseline amount. For a
schedule of taxes ``rate * min(w, base)`` the cost ``w + tax(w)`` is
continuous, piecewise linear and increasing in payroll wages w, so:

1. Inverse: ``wages_at_employer_cost`` returns the one wage of zero or more
   whose cost under the schedule equals the target, for any target of zero or
   more; a brute-force bisection agrees; and an unchanged schedule returns the
   same wages, so a reform that leaves employer taxes alone moves no wages.
   Schedules are drawn free-form and in the model's own shapes, including
   CBO's negative component. It reproduces the after-offset wages in JCT's
   three worked examples.
2. Monotonicity: raising any rate weakly lowers the wage at a given cost.
3. Conservation: under a reform with the default employee share of 1, every
   worker's federal employer cost in the reformed simulation equals the
   baseline's, across the FUTA base, the Social Security cap and CBO's
   secondary earnings threshold, with and without FICA pre-tax deductions,
   and in a FUTA credit reduction state.
4. Share: with an employee share of one half, the model's change is half the
   change the inverse gives (a differential test of model against inverse).
5. No reform, no change: zero in a simulation without a reform, for anyone
   without payroll wages, and under a scenario that only extends current law
   (the Trustees' economic assumptions move the taxable maximum in both the
   baseline cost and the reform). The tax components the formula compares
   stay equal under employee-side reforms and before a reform starts. The
   payroll wage exclusions it compares are each simulation's own
   fica_pre_tax_contributions, so a supplied total counts in both, and
   neutralizing or abolishing it moves pay with the components unchanged,
   as do reforms that keep the list but limit the total to children or give
   a listed contribution a formula. A branch that was subsampled matches its
   ancestor's baseline by person ID, among the IDs the baseline has once, so
   a person whose ID axes repeated raises by name, and a formula for the
   total that reads employment income is refused with core's CycleError.
6. Marginal wedge: in a branch that raises earnings, wages rise by
   (1 + m_b) / (1 + m_r) per dollar, where m is the federal employer rate at
   the margin, so marginal tax rates measured in a reform carry the employer
   tax; the labor supply measurement branch recalculates the change from its
   own inputs, and its baseline counterpart returns zero.
7. Payroll wage definitions: when a reform changes which pay counts as
   payroll wages (the tax-exempt reform's tips), the employer's outlay of pay
   plus federal employer tax still holds, after the labor supply response,
   with CBO's secondary threshold below the taxable maximum, for a worker whose
   exempt tips exceed pay and for negative pay. Pure properties of the change:
   conservation at a share of 1, proportionality for shares up to 1, and a
   floor that keeps reform payroll wages from going negative above 1.

The model stores values as float32, so model comparisons allow its rounding.
Each reform simulation is built once for the tests that use it and dropped
after them, so at most one is held at a time.
"""

import gc
from types import SimpleNamespace

import numpy as np
import pytest
from hypothesis import example, given, settings
from hypothesis import strategies as st
from policyengine_core.errors import CycleError
from policyengine_core.periods import YEAR as YEAR_PERIOD
from policyengine_core.periods import period as make_period
from policyengine_core.reforms import Reform
from policyengine_core.variables import Variable

from policyengine_us import Simulation
from policyengine_us.entities import Person
from policyengine_us.reforms.ssa.trustees_2026 import (
    trustees_2026_economic_assumptions_reform,
)
from policyengine_us.system import system
from policyengine_us.variables.gov.simulation.behavioral_response_measurements import (
    _baseline_measurement_branch,
    _copy_behavioral_response_inputs,
    _neutralize_behavioral_responses,
)
from policyengine_us.variables.gov.simulation.employer_payroll_tax_incidence.employer_payroll_tax_fixed_employer_cost_change import (
    DEFAULT_WAGE_RULE,
    FICA_PRE_TAX_ABOLISHED,
    FICA_PRE_TAX_LIST,
    TAX_EXEMPT_WAGE_RULE,
    components_match,
    employer_cost_schedules,
    employer_payroll_tax_from_components,
    federal_employer_payroll_tax_components,
    fica_pre_tax_list,
    fixed_employer_cost_wage_change,
    for_each_person,
    payroll_wage_rule,
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


# CBO's secondary threshold: Social Security tax below the cap and above
# $250,000, so a negative component cancels the uncapped one in the donut.
DONUT = [(0.062, 184_500.0), (0.0145, np.inf), (0.062, np.inf), (-0.062, 250_000.0)]
DONUT_COSTS = [0.0, 100_000.0, 210_000.0, 260_000.0, 300_000.0, 2e6]


@st.composite
def model_schedules(draw):
    """Schedules shaped like federal_employer_payroll_tax_components builds.

    Social Security to the cap, uncapped Medicare, federal unemployment to its
    base and, when CBO's threshold or the cap is finite, Social Security again
    above max(threshold, cap): an uncapped component and a negative one. A
    threshold below the cap leaves Social Security uncapped; one drawn as a
    gap above the cap leaves a donut between them.
    """
    social_security = draw(st.floats(min_value=0.01, max_value=0.6))
    cap = draw(BASES)
    components = [
        (social_security, cap),
        (draw(RATES), np.inf),
        (draw(RATES), draw(BASES)),
    ]
    threshold = draw(
        st.one_of(
            BASES,
            st.floats(min_value=1, max_value=1e6).map(lambda gap: cap + gap),
        )
    )
    secondary = max(threshold, cap)
    if np.isfinite(secondary):
        components += [(social_security, np.inf), (-social_security, secondary)]
    return components


# Free-form schedules of nonnegative rates, and the model's own shapes, which
# have a negative rate under CBO's option.
SCHEDULES = st.one_of(COMPONENTS, model_schedules())


@PURE_SETTINGS
@given(SCHEDULES, COSTS)
# 7,577.50 is the cost of wages at the federal unemployment base, a kink.
@example([(0.062, 184_500.0), (0.0145, np.inf), (0.006, 7_000.0)], [0.0, 7_577.5])
@example(DONUT, DONUT_COSTS)
def test_inverse_recovers_the_cost(components, costs):
    wages = wages_at_employer_cost(costs, components)
    assert np.all(wages >= 0)
    np.testing.assert_allclose(
        employer_cost(wages, components), costs, rtol=1e-12, atol=1e-6
    )


@PURE_SETTINGS
@given(SCHEDULES, COSTS)
def test_same_schedule_returns_the_same_wages(components, wages):
    """Without a change in the schedule there is no change in wages."""
    cost = employer_cost(wages, components)
    np.testing.assert_allclose(
        wages_at_employer_cost(cost, components), wages, rtol=1e-12, atol=1e-6
    )


@PURE_SETTINGS
@given(SCHEDULES, COSTS)
@example(DONUT, DONUT_COSTS)
def test_inverse_matches_bisection(components, costs):
    wages = wages_at_employer_cost(costs, components)
    expected = [bisect_wages(cost, components) for cost in costs]
    np.testing.assert_allclose(wages, expected, rtol=1e-9, atol=1e-6)


@PURE_SETTINGS
@given(
    SCHEDULES.filter(len),
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
    """Differential against JCX-89-16's worked examples (PDF pages 12-14).

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


@pytest.mark.parametrize("rate", [-1.5, -1.0])
def test_inverse_rejects_a_cost_that_does_not_rise_with_wages(rate):
    with pytest.raises(ValueError):
        wages_at_employer_cost([1_000.0], [(rate, np.inf)])


PAYS = st.lists(
    st.floats(min_value=-1e5, max_value=2e6, allow_nan=False), min_size=1, max_size=10
)
EXCLUSIONS = st.floats(min_value=0, max_value=1e5, allow_nan=False)


def outlay(pay, exclusions, components):
    """Pay plus federal employer tax on payroll wages max(0, pay - exclusions)."""
    pay = np.asarray(pay, dtype=np.float64)
    wages = np.maximum(pay - exclusions, 0)
    return pay + employer_payroll_tax_from_components(wages, components)


@PURE_SETTINGS
@given(PAYS, EXCLUSIONS, EXCLUSIONS, SCHEDULES, SCHEDULES)
@example([30_000.0, -5_000.0], 0.0, 45_000.0, DONUT, DONUT)
def test_change_holds_the_outlay(pay, baseline_x, reform_x, baseline, reform):
    """At a share of 1 the reform's outlay equals the baseline's, for any pay.

    Exclusions above pay (exempt tips above reported pay) and negative pay
    leave the reform taxing none of the pay; the employer then pays out the
    whole baseline tax.
    """
    change = fixed_employer_cost_wage_change(
        pay, baseline_x, reform_x, baseline, reform, 1
    )
    np.testing.assert_allclose(
        outlay(np.asarray(pay) + change, reform_x, reform),
        outlay(pay, baseline_x, baseline),
        rtol=1e-12,
        atol=1e-6,
    )


@PURE_SETTINGS
@given(
    PAYS,
    EXCLUSIONS,
    EXCLUSIONS,
    SCHEDULES,
    SCHEDULES,
    st.floats(min_value=0, max_value=5, allow_nan=False),
)
def test_share_scales_the_change_and_the_floor_binds_only_above_1(
    pay, baseline_x, reform_x, baseline, reform, share
):
    full = fixed_employer_cost_wage_change(
        pay, baseline_x, reform_x, baseline, reform, 1
    )
    change = fixed_employer_cost_wage_change(
        pay, baseline_x, reform_x, baseline, reform, share
    )
    reform_wages = np.asarray(pay) - reform_x
    np.testing.assert_allclose(
        change,
        np.maximum(share * full, -np.maximum(reform_wages, 0)),
        rtol=1e-12,
        atol=1e-6,
    )
    if share <= 1:
        np.testing.assert_allclose(change, share * full, rtol=1e-12, atol=1e-6)
    # Positive reform payroll wages never go below zero.
    assert np.all(reform_wages + change >= np.minimum(reform_wages, 0) - 1e-6)


@PURE_SETTINGS
@given(PAYS, EXCLUSIONS, SCHEDULES)
def test_same_schedule_and_definition_change_nothing(pay, exclusions, components):
    np.testing.assert_allclose(
        fixed_employer_cost_wage_change(
            pay, exclusions, exclusions, components, components, 1
        ),
        0,
        atol=1e-6,
    )


def test_unknown_payroll_wage_definition_raises():
    """A structural reform this model has no exclusions for is refused."""

    class Formula:
        def get_formula(self, period):
            return lambda person, period, parameters: 0

    class System:
        def get_variable(self, name):
            return Formula()

    with pytest.raises(NotImplementedError):
        payroll_wage_rule(System(), YEAR)


@pytest.mark.parametrize("year", [2026, 2035, 2060])
def test_current_law_cap_copy_matches_the_cap(year):
    """The baseline cost reads its copy, so it must equal the live cap."""
    gov = system.parameters(year).gov
    assert gov.simulation.employer_payroll_tax_incidence.current_law_cap == (
        pytest.approx(gov.irs.payroll.social_security.cap)
    )
    assert payroll_wage_rule(system, year) == DEFAULT_WAGE_RULE


def test_schedules_differ_only_when_the_employer_cost_does():
    """The zero shortcut in the formula compares the employer tax components.

    In 2026 the reform edits only the owners' draw copy of the current-law
    cap, which is not the copy the baseline cost reads. From 2027, employee
    Social Security and Medicare rates, the Additional Medicare Tax and the
    employee share change; none is an employer tax, so the components stay
    equal. Dropping premiums from the FICA pre-tax list (2028 only) or
    abolishing the total (2029 only) changes payroll wages without moving a
    rate or a base, so the components match and the payroll wage rule stays
    the default: the formula sees these changes in each simulation's
    exclusions instead (test_abolitions_and_deduction_lists_hold_the_outlay,
    test_removing_the_fica_total_lowers_pay). Raising the employer Medicare
    rate (from 2030) changes a component.
    """
    later = "2027-01-01.2100-12-31"
    current_list = system.parameters(
        2028
    ).gov.irs.gross_income.fica_pre_tax_contributions
    reform = Reform.from_dict(
        {
            "gov.contrib.ssa.owners_draw.current_law_cap": {
                "2026-01-01.2026-12-31": 250_000
            },
            f"{PAYROLL}.social_security.rate.employee": {later: 0.072},
            f"{PAYROLL}.medicare.rate.employee": {later: 0.0245},
            f"{PAYROLL}.medicare.additional.rate": {later: 0.019},
            SHARE: {later: 0.5},
            "gov.irs.gross_income.fica_pre_tax_contributions": {
                "2028-01-01.2028-12-31": [
                    item
                    for item in current_list
                    if item != "pre_tax_health_insurance_premiums"
                ]
            },
            "gov.abolitions.fica_pre_tax_contributions": {
                "2029-01-01.2029-12-31": True
            },
            f"{PAYROLL}.medicare.rate.employer": {"2030-01-01.2100-12-31": 0.0245},
        },
        country_id="us",
    )
    reformed = reform(system)
    states = np.array(["TX", "CA"])
    # Year: whether the tax components match.
    expected = {2026: True, 2027: True, 2028: True, 2029: True, 2030: False}
    for year, same_components in expected.items():
        baseline, policy = employer_cost_schedules(system, reformed, year, states)
        assert baseline.wage_rule == policy.wage_rule == DEFAULT_WAGE_RULE
        assert (
            components_match(baseline.components, policy.components) is same_components
        )


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


# Reform A raises every federal employer tax, moves both bases and turns on
# CBO's secondary threshold above the new cap, at the default employee share
# of 1. Reform B removes the Social Security cap, cuts the employer rates and
# passes half the change to wages.
SECONDARY_THRESHOLD = "gov.contrib.cbo.payroll.secondary_earnings_threshold"
RAISE = {
    f"{PAYROLL}.social_security.rate.employer": 0.162,
    f"{PAYROLL}.social_security.cap": 200_000,
    SECONDARY_THRESHOLD: 300_000,
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


class TestRaisedReform:
    """Reform A, built once for these tests and dropped after them."""

    @pytest.fixture(scope="class")
    def raised(self):
        simulation = simulate(RAISE)
        yield simulation
        del simulation
        gc.collect()

    def test_reform_holds_federal_employer_cost(self, raised):
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
        # CBO's option is live: the top earner's new wages stay above the
        # secondary threshold and pay Social Security tax there, so their cost
        # crosses the donut between the cap and the threshold.
        taxable = raised.calculate("taxable_earnings_for_social_security", YEAR)
        wages = raised.calculate("payroll_tax_gross_wages", YEAR)
        top = PAY.index(1_000_000)
        assert taxable[top] == pytest.approx(200_000 + wages[top] - 300_000, rel=1e-6)

    def test_raised_earnings_carry_the_employer_wedge(self, raised):
        """Rate branches see (1 + m_b) / (1 + m_r) of each added dollar.

        Worker p6 earns $50,000 in Texas, above the FUTA bases and below both caps,
        so the marginal federal employer rate is the Social Security rate plus the
        Medicare rate.
        """

        def margin(simulation):
            payroll = simulation.tax_benefit_system.parameters(YEAR).gov.irs.payroll
            return (
                payroll.social_security.rate.employer + payroll.medicare.rate.employer
            )

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


@pytest.fixture
def half_cut():
    simulation = simulate(HALF_CUT_NO_CAP)
    yield simulation
    del simulation
    gc.collect()


def test_change_is_the_share_of_the_fixed_cost_change(half_cut):
    """Differential: the model's change equals half the pure inverse's."""
    baseline = half_cut.baseline
    wages = baseline.calculate("payroll_tax_gross_wages", YEAR).astype(np.float64)
    state_code = baseline.populations["household"]("state_code", YEAR)
    state_code = baseline.populations["person"].household.project(state_code)
    components = {}
    for name, current in (("baseline", baseline), ("reform", half_cut)):
        components[name] = federal_employer_payroll_tax_components(
            current.tax_benefit_system.parameters(YEAR).gov, state_code
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


def small_situation(year, people, states):
    """One-person households from {variable: value} dicts."""
    members = {
        f"p{i}": {"age": {year: 40}, **{k: {year: v} for k, v in person.items()}}
        for i, person in enumerate(people)
    }
    units = {
        entity: {f"u{i}": {"members": [f"p{i}"]} for i in range(len(people))}
        for entity in ("tax_units", "spm_units", "families", "marital_units")
    }
    households = {
        f"h{i}": {"members": [f"p{i}"], "state_code": {year: state}}
        for i, state in enumerate(states)
    }
    return {"people": members, **units, "households": households}


def current_law_federal_employer_tax(wages, year, states):
    """Current-law employer OASDI, HI and FUTA, written out from parameters."""
    payroll = system.parameters(year).gov.irs.payroll
    futa = payroll.federal_unemployment
    futa_rate = futa.effective_rate + futa.credit_reduction_rate[np.array(states)]
    return (
        payroll.social_security.rate.employer
        * np.minimum(wages, payroll.social_security.cap)
        + payroll.medicare.rate.employer * wages
        + futa_rate * np.minimum(wages, futa.taxable_wage_base)
    )


def assert_outlay_held(simulation, year, states, pay):
    """Reform pay plus reform federal employer tax equals the baseline outlay.

    ``pay`` is pay before the wage change (after any labor supply response),
    whose baseline payroll wages are ``max(0, pay - FICA pre-tax deductions)``,
    with the deductions on current law's list.
    """
    current_law_list = system.parameters(
        year
    ).gov.irs.gross_income.fica_pre_tax_contributions
    deductions = sum(
        simulation.calculate(variable, year) for variable in current_law_list
    )
    baseline_wages = np.maximum(pay - deductions, 0)
    baseline_outlay = pay + current_law_federal_employer_tax(
        baseline_wages, year, states
    )
    reform_outlay = simulation.calculate("employment_income", year).astype(
        np.float64
    ) + sum(
        simulation.calculate(variable, year).astype(np.float64)
        for variable in (
            "employer_social_security_tax",
            "employer_medicare_tax",
            "employer_federal_unemployment_tax",
        )
    )
    np.testing.assert_allclose(reform_outlay, baseline_outlay, rtol=1e-6, atol=0.05)


def test_trustees_assumptions_alone_change_no_wages():
    """A scenario that extends current law is not a tax change.

    The 2026 Trustees' wage path raises the 2035 taxable maximum from $252,000
    to $270,000 in the reform system, and in its current-law copy, which the
    baseline cost reads.
    """
    year = 2035
    pays = [250_000, 260_000, 280_000, 1_000_000]
    simulation = Simulation(
        situation=small_situation(
            year, [{"employment_income": pay} for pay in pays], ["TX"] * len(pays)
        ),
        reform=trustees_2026_economic_assumptions_reform,
    )
    try:
        gov = simulation.tax_benefit_system.parameters(year).gov
        assert gov.irs.payroll.social_security.cap > 252_000
        np.testing.assert_array_equal(simulation.calculate(CHANGE, year), 0)
        np.testing.assert_array_equal(
            simulation.calculate("employment_income", year), pays
        )
    finally:
        del simulation
        gc.collect()


TAX_EXEMPT_TIPS = {
    "gov.contrib.tax_exempt.in_effect": True,
    "gov.contrib.tax_exempt.tip_income.payroll_tax_exempt": True,
}


def test_abolitions_and_deduction_lists_hold_the_outlay():
    """Changes to employer taxes outside their rates and bases are covered.

    Abolishing employer_medicare_tax zeroes it, and dropping health insurance
    premiums from the FICA pre-tax list makes them payroll wages. Neither moves
    a rate or a base. The first worker pays premiums, so their payroll wages
    rise under the reform while their baseline wages keep the deduction.
    """
    states = ["TX", "CA", "TX"]
    people = [
        {"employment_income": 60_000, "pre_tax_health_insurance_premiums": 6_000},
        {"employment_income": 30_000},
        {"employment_income": 0},
    ]
    current_list = system.parameters(
        YEAR
    ).gov.irs.gross_income.fica_pre_tax_contributions
    reform = Reform.from_dict(
        {
            "gov.abolitions.employer_medicare_tax": {DATES: True},
            "gov.irs.gross_income.fica_pre_tax_contributions": {
                DATES: [
                    item
                    for item in current_list
                    if item != "pre_tax_health_insurance_premiums"
                ]
            },
        },
        country_id="us",
    )
    simulation = Simulation(
        situation=small_situation(YEAR, people, states), reform=reform
    )
    try:
        np.testing.assert_array_equal(
            simulation.calculate("employer_medicare_tax", YEAR), 0
        )
        change = simulation.calculate(CHANGE, YEAR)
        assert change[1] > 0 and change[2] == 0
        pay = np.array([person["employment_income"] for person in people], float)
        assert_outlay_held(simulation, YEAR, states, pay)
    finally:
        del simulation
        gc.collect()


EMPLOYER_TAXES = (
    "employer_social_security_tax",
    "employer_medicare_tax",
    "employer_federal_unemployment_tax",
)


def simulated_outlay(simulation, year):
    """Pay plus federal employer tax, as ``simulation`` calculates them.

    A reform simulation without a labor supply response starts its change
    from the pay its baseline has, so the baseline's own value of this is the
    outlay the change holds.
    """
    return sum(
        simulation.calculate(variable, year).astype(np.float64)
        for variable in ("employment_income", *EMPLOYER_TAXES)
    )


def test_a_supplied_fica_total_sets_payroll_wages():
    """Payroll wages leave out fica_pre_tax_contributions as supplied.

    The first worker supplies a $6,000 total. A situation that supplies the
    total for one person supplies it for everyone, so the second worker's is
    zero. With employer Medicare at 11.45%, the first keeps the $64,173
    baseline outlay ($54,000 of payroll wages) at pay of
    (64,173 - 42 + 0.1765 * 6,000) / 1.1765 = $55,410.11, and the second
    keeps $64,632 at (64,632 - 42) / 1.1765 = $54,900.13.
    """
    states = ["TX"] * 2
    people = [
        {"employment_income": 60_000, "fica_pre_tax_contributions": 6_000},
        {"employment_income": 60_000},
    ]
    reform = Reform.from_dict(
        {f"{PAYROLL}.medicare.rate.employer": {DATES: 0.1145}}, country_id="us"
    )
    simulation = Simulation(
        situation=small_situation(YEAR, people, states), reform=reform
    )
    try:
        baseline_outlay = simulated_outlay(simulation.baseline, YEAR)
        np.testing.assert_allclose(baseline_outlay, [64_173, 64_632])
        np.testing.assert_allclose(
            simulation.calculate("employment_income", YEAR),
            [55_410.11, 54_900.13],
            atol=0.02,
        )
        np.testing.assert_allclose(
            simulated_outlay(simulation, YEAR), baseline_outlay, rtol=1e-6, atol=0.05
        )
    finally:
        del simulation
        gc.collect()


class NeutralizeFicaTotal(Reform):
    def apply(self):
        self.neutralize_variable("fica_pre_tax_contributions")


@pytest.mark.parametrize("removal", ["neutralized", "abolished"])
def test_removing_the_fica_total_lowers_pay(removal):
    """No FICA pre-tax deductions, with every employer rate and base unchanged.

    Neutralizing fica_pre_tax_contributions (a structural reform) or
    abolishing it leaves the tax components equal, so only the exclusions
    show the employer's cost changed. The premium payer's payroll wages
    become all of pay, which falls from $60,000 to keep the $64,173 outlay:
    (64,173 - 42) / 1.0765 = $59,573.62. The other worker's pay stays.
    """
    states = ["TX", "TX"]
    people = [
        {"employment_income": 60_000, "pre_tax_health_insurance_premiums": 6_000},
        {"employment_income": 60_000},
    ]
    if removal == "neutralized":
        reform = NeutralizeFicaTotal
    else:
        reform = Reform.from_dict(
            {"gov.abolitions.fica_pre_tax_contributions": {DATES: True}},
            country_id="us",
        )
    simulation = Simulation(
        situation=small_situation(YEAR, people, states), reform=reform
    )
    try:
        baseline, policy = employer_cost_schedules(
            simulation.baseline.tax_benefit_system,
            simulation.tax_benefit_system,
            YEAR,
            np.array(states),
        )
        assert components_match(baseline.components, policy.components)
        np.testing.assert_array_equal(
            simulation.baseline.calculate("fica_pre_tax_contributions", YEAR),
            [6_000, 0],
        )
        np.testing.assert_array_equal(
            simulation.calculate("fica_pre_tax_contributions", YEAR), [0, 0]
        )
        np.testing.assert_allclose(
            simulation.calculate("employment_income", YEAR),
            [59_573.62, 60_000],
            atol=0.02,
        )
        np.testing.assert_allclose(
            simulated_outlay(simulation, YEAR),
            simulated_outlay(simulation.baseline, YEAR),
            rtol=1e-6,
            atol=0.05,
        )
    finally:
        del simulation
        gc.collect()


# Core names a variable after its class, and this module already has a class
# named fica_pre_tax_contributions (ProportionalFicaTotal's, below), so these
# reforms define theirs inside apply.
class ChildOnlyFicaTotal(Reform):
    """Keeps the FICA pre-tax list, but counts the total for children only."""

    def apply(self):
        class fica_pre_tax_contributions(Variable):
            value_type = float
            entity = Person
            definition_period = YEAR_PERIOD
            adds = FICA_PRE_TAX_LIST
            defined_for = "is_child"

        self.update_variable(fica_pre_tax_contributions)


class PremiumFormula(Reform):
    """Keeps the FICA pre-tax list, but gives a listed contribution a formula."""

    def apply(self):
        class pre_tax_health_insurance_premiums(Variable):
            value_type = float
            entity = Person
            definition_period = YEAR_PERIOD

            def formula(person, period, parameters):
                return 0.1 * person("employment_income_before_lsr", period)

        self.update_variable(pre_tax_health_insurance_premiums)


# A Texas adult with $60,000 of pay. Limiting the total to children drops
# their $6,000 of premiums from it, so pay falls to keep the $64,173 outlay:
# (64,173 - 42) / 1.0765 = $59,573.62. The formula gives them $6,000 of
# premiums where the baseline has none, so pay rises to keep $64,632:
# (64,632 - 42 + 0.0765 * 6,000) / 1.0765 = $60,426.38.
SAME_LIST_CASES = {
    "child_only_total": (
        ChildOnlyFicaTotal,
        {
            "employment_income_before_lsr": 60_000,
            "pre_tax_health_insurance_premiums": 6_000,
        },
        (6_000, 0),
        64_173,
        59_573.62,
    ),
    "premium_formula": (
        PremiumFormula,
        {"employment_income_before_lsr": 60_000},
        (0, 6_000),
        64_632,
        60_426.38,
    ),
}


@pytest.mark.parametrize("case", SAME_LIST_CASES)
def test_same_list_reforms_that_change_the_total_hold_the_outlay(case):
    """Equal FICA pre-tax lists don't make equal totals.

    Each reform adds the list the baseline adds, yet calculates another total
    for this worker, so the baseline side reads the baseline simulation's
    own total and pay moves to keep the outlay.
    """
    reform, person, (baseline_total, reform_total), outlay, pay = SAME_LIST_CASES[case]
    simulation = Simulation(
        situation=small_situation(YEAR, [person], ["TX"]), reform=reform
    )
    try:
        assert fica_pre_tax_list(simulation.tax_benefit_system, YEAR) == (
            fica_pre_tax_list(simulation.baseline.tax_benefit_system, YEAR)
        )
        np.testing.assert_array_equal(
            simulation.baseline.calculate("fica_pre_tax_contributions", YEAR),
            [baseline_total],
        )
        np.testing.assert_array_equal(
            simulation.calculate("fica_pre_tax_contributions", YEAR), [reform_total]
        )
        np.testing.assert_allclose(
            simulated_outlay(simulation.baseline, YEAR), [outlay]
        )
        np.testing.assert_allclose(
            simulation.calculate("employment_income", YEAR), [pay], atol=0.02
        )
        np.testing.assert_allclose(
            simulated_outlay(simulation, YEAR), [outlay], rtol=1e-6, atol=0.05
        )
    finally:
        del simulation
        gc.collect()


class fica_pre_tax_contributions(Variable):
    """A total that reads employment income, which the response can't solve."""

    value_type = float
    entity = Person
    definition_period = YEAR_PERIOD

    def formula(person, period, parameters):
        return 0.1 * person("employment_income", period)


class ProportionalFicaTotal(Reform):
    def apply(self):
        self.update_variable(fica_pre_tax_contributions)


def test_fica_pre_tax_list_says_how_a_system_defines_the_total():
    """The list, a marker for abolition, or None for another definition."""
    current_list = tuple(
        system.parameters(YEAR).gov.irs.gross_income.fica_pre_tax_contributions
    )
    assert "pre_tax_health_insurance_premiums" in current_list
    assert fica_pre_tax_list(system, YEAR) == current_list
    abolished = Reform.from_dict(
        {"gov.abolitions.fica_pre_tax_contributions": {DATES: True}},
        country_id="us",
    )(system)
    assert fica_pre_tax_list(abolished, YEAR) == FICA_PRE_TAX_ABOLISHED
    assert fica_pre_tax_list(NeutralizeFicaTotal(system), YEAR) is None
    assert fica_pre_tax_list(ProportionalFicaTotal(system), YEAR) is None


def test_a_total_that_reads_employment_income_is_refused():
    """The total would depend on the wage this variable sets: a cycle."""
    simulation = Simulation(
        situation=small_situation(YEAR, [{"employment_income": 60_000}], ["TX"]),
        reform=ProportionalFicaTotal,
    )
    try:
        with pytest.raises(CycleError):
            simulation.calculate("employment_income", YEAR)
    finally:
        del simulation
        gc.collect()


def numbered_situation(year, people, states):
    """small_situation with numeric IDs, which subsample's rebuild needs."""
    members = {
        str(i): {"age": {year: 40}, **{k: {year: v} for k, v in person.items()}}
        for i, person in enumerate(people)
    }
    units = {
        entity: {str(i): {"members": [str(i)]} for i in range(len(people))}
        for entity in ("tax_units", "spm_units", "families", "marital_units")
    }
    households = {
        str(i): {"members": [str(i)], "state_code": {year: state}}
        for i, state in enumerate(states)
    }
    return {"people": members, **units, "households": households}


# Pay after the change for each worker below, by person ID, when the total
# is neutralized: (pay * 1.0765 - 0.0765 * premiums) / 1.0765.
SAMPLED_PEOPLE = [
    {"employment_income": 60_000, "pre_tax_health_insurance_premiums": 6_000},
    {"employment_income": 80_000, "pre_tax_health_insurance_premiums": 12_000},
]
NEUTRALIZED_PAY = {"0": 59_573.62, "1": 79_147.24}


@pytest.mark.parametrize("removal", ["employee_rate", "neutralized"])
def test_a_subsampled_branch_matches_its_baseline_by_person(removal):
    """A branch keeps its ancestor's baseline, with all of its people.

    Subsampling the branch to one of two households leaves that baseline at
    two people, so the baseline's FICA pre-tax total is read for the person
    the sample kept, matched by ID. Under an employee-only reform the two
    totals are equal and the change is zero; with the total neutralized,
    pay falls by the employer tax on the kept worker's premiums.
    """
    if removal == "employee_rate":
        reform = Reform.from_dict(
            {f"{PAYROLL}.medicare.rate.employee": {DATES: 0.0245}}, country_id="us"
        )
    else:
        reform = NeutralizeFicaTotal
    simulation = Simulation(
        situation=numbered_situation(YEAR, SAMPLED_PEOPLE, ["TX", "TX"]),
        reform=reform,
    )
    try:
        # What a household simulation lacks for subsample: array IDs and the
        # dataset's period and name.
        for current in (simulation, simulation.baseline):
            for population in current.populations.values():
                population.ids = np.asarray(population.ids)
        simulation.dataset = SimpleNamespace(time_period=YEAR, name="sampled")
        simulation.set_input("household_weight", YEAR, [1.0, 1.0])
        branch = simulation.get_branch("sampled")
        branch.subsample(n=1, seed="sampled", time_period=YEAR)
        assert branch.persons.count == 1
        assert branch.baseline.persons.count == 2
        kept = str(branch.persons.ids[0])
        pay = branch.calculate("employment_income", YEAR)
        if removal == "employee_rate":
            np.testing.assert_array_equal(branch.calculate(CHANGE, YEAR), 0)
            np.testing.assert_array_equal(
                pay, [SAMPLED_PEOPLE[int(kept)]["employment_income"]]
            )
        else:
            np.testing.assert_allclose(pay, [NEUTRALIZED_PAY[kept]], atol=0.02)
    finally:
        del simulation
        gc.collect()


# Core's axes append each cell's index to every person ID, so over 11 cells
# person "1" in cell 10 and person "11" in cell 0 share the ID "110".
AXIS_PERSON_IDS = [pid + str(cell) for cell in range(11) for pid in ("1", "11")]


def axes_situation(person_ids):
    """One worker per household, the first with pay from $60,000 to $80,000."""
    people = {
        pid: {
            "age": {YEAR: 40},
            "employment_income": {YEAR: 60_000},
            "pre_tax_health_insurance_premiums": {YEAR: 6_000 * (i + 1)},
        }
        for i, pid in enumerate(person_ids)
    }
    units = {
        entity: {str(i + 2): {"members": [pid]} for i, pid in enumerate(person_ids)}
        for entity in ("tax_units", "spm_units", "families", "marital_units")
    }
    households = {
        str(i + 2): {"members": [pid], "state_code": {YEAR: "TX"}}
        for i, pid in enumerate(person_ids)
    }
    return {
        "people": people,
        **units,
        "households": households,
        "axes": [
            [
                {
                    "name": "employment_income",
                    "period": YEAR,
                    "index": 0,
                    "count": 11,
                    "min": 60_000,
                    "max": 80_000,
                }
            ]
        ],
    }


def test_a_subsampled_branch_finds_its_person_among_repeated_axis_ids():
    """Axes can give two people one ID; a subsampled branch matches by ID.

    With the FICA pre-tax total neutralized, each worker's pay falls by the
    employer tax on their premiums: (pay * 1.0765 - 0.0765 * premiums) /
    1.0765. Before the subsample both simulations list the same IDs, so the
    repeated "110" aligns by position. A branch subsampled to one household
    reads the baseline's total for the person it kept, by an ID the baseline
    has once, or raises naming an ID the baseline repeats.
    """
    simulation = Simulation(
        situation=axes_situation(["1", "11"]), reform=NeutralizeFicaTotal
    )
    try:
        ids = [str(pid) for pid in simulation.persons.ids]
        assert ids == AXIS_PERSON_IDS
        pay = simulation.calculate("employment_income", YEAR)
        before = simulation.calculate("employment_income_before_lsr", YEAR)
        premiums = simulation.calculate("pre_tax_health_insurance_premiums", YEAR)
        np.testing.assert_allclose(pay, before - 0.0765 * premiums / 1.0765, atol=0.02)
        # What a household simulation lacks for subsample, as in
        # test_a_subsampled_branch_matches_its_baseline_by_person.
        for current in (simulation, simulation.baseline):
            for population in current.populations.values():
                population.ids = np.asarray(population.ids)
        simulation.dataset = SimpleNamespace(time_period=YEAR, name="axes-collision")
        simulation.set_input(
            "household_weight", YEAR, np.ones(simulation.household.count)
        )
        branch = simulation.get_branch("sampled")
        branch.subsample(n=1, seed="axes-collision", time_period=YEAR)
        assert branch.baseline.persons.count == len(ids)
        kept = [str(pid) for pid in branch.persons.ids]
        repeated = [pid for pid in kept if ids.count(pid) > 1]
        if repeated:
            with pytest.raises(
                NotImplementedError,
                match=f"more than one person with ID '{repeated[0]}'",
            ):
                branch.calculate("employment_income", YEAR)
        else:
            np.testing.assert_allclose(
                branch.calculate("employment_income", YEAR),
                [pay[ids.index(pid)] for pid in kept],
                atol=0.02,
            )
    finally:
        del simulation
        gc.collect()


def test_people_match_by_position_or_by_an_id_the_baseline_has_once():
    """for_each_person, with the IDs axes give people "1" and "11".

    Identical ID lists align by position, the repeated "110" included.
    Otherwise each person is found by an ID the baseline has once, and an ID
    the baseline repeats or lacks raises, naming it.
    """
    baseline = SimpleNamespace(ids=np.array(AXIS_PERSON_IDS))
    values = np.arange(len(AXIS_PERSON_IDS))

    def match(ids):
        return for_each_person(SimpleNamespace(ids=ids), baseline, values)

    np.testing.assert_array_equal(match(np.array(AXIS_PERSON_IDS)), values)
    np.testing.assert_array_equal(match(["19", "1110", "10"]), [18, 21, 0])
    with pytest.raises(NotImplementedError, match="more than one person with ID '110'"):
        match(["19", "110"])
    with pytest.raises(NotImplementedError, match="no person with ID '3'"):
        match(["19", "3"])


def test_exempting_tips_from_payroll_tax_raises_tipped_pay():
    """With rates unchanged, exempt tips save the employer its tax on them.

    The tax components match, so the change comes from the payroll wage
    exclusions alone: tipped workers' pay rises by the employer's saving, and
    others' does not move.
    """
    states = ["TX", "TX", "CA"]
    people = [
        {"employment_income": 40_000, "tip_income": 10_000},
        {"employment_income": 60_000},
        {"employment_income": 30_000, "tip_income": 30_000},
    ]
    reform = Reform.from_dict(
        {name: {DATES: value} for name, value in TAX_EXEMPT_TIPS.items()},
        country_id="us",
    )
    simulation = Simulation(
        situation=small_situation(YEAR, people, states), reform=reform
    )
    try:
        assert payroll_wage_rule(simulation.tax_benefit_system, YEAR) == (
            TAX_EXEMPT_WAGE_RULE
        )
        change = simulation.calculate(CHANGE, YEAR)
        assert change[0] > 0 and change[1] == 0 and change[2] > 0
        pay = np.array([person["employment_income"] for person in people], float)
        assert_outlay_held(simulation, YEAR, states, pay)
    finally:
        del simulation
        gc.collect()


# A 2035 reform that combines a rate rise, CBO's secondary threshold at
# $250,000 (below that year's $252,000 taxable maximum, so the threshold is the
# cap), a federal unemployment base above the cap, and payroll-tax-exempt tips.
# Some workers have a labor supply response, given as an input: calculating it
# from elasticities would add about 3 GB of measurement branches to this file,
# and the change reads the response the same way either way.
MIXED_YEAR = 2035
MIXED = {
    **TAX_EXEMPT_TIPS,
    f"{PAYROLL}.medicare.rate.employer": 0.0245,
    SECONDARY_THRESHOLD: 250_000,
    f"{PAYROLL}.federal_unemployment.taxable_wage_base": 300_000,
}
RESPONSE = "employment_income_behavioral_response"
MIXED_PEOPLE = [
    {"employment_income": 50_000, RESPONSE: -1_500},
    {"employment_income": 40_000, "tip_income": 12_000, RESPONSE: 800},
    # Exempt tips above reported pay: the reform taxes none of the pay.
    {"employment_income": 30_000, "tip_income": 45_000},
    {"employment_income": -5_000},
    {"employment_income": 0},
    # The response takes this worker from above the threshold to below it.
    {"employment_income": 251_000, RESPONSE: -2_000},
    {"employment_income": 300_000},
    {"employment_income": 1_000_000, RESPONSE: -20_000},
    {
        "employment_income": 100_000,
        "tip_income": 10_000,
        "pre_tax_health_insurance_premiums": 5_000,
    },
]
MIXED_STATES = ["TX", "TX", "CA", "TX", "TX", "TX", "CA", "TX", "CA"]


class TestMixedReform:
    """The 2035 mixed reform, built once for these tests and dropped after them."""

    @pytest.fixture(scope="class")
    def mixed(self):
        reform = Reform.from_dict(
            {name: {DATES: value} for name, value in MIXED.items()}, country_id="us"
        )
        simulation = Simulation(
            situation=small_situation(MIXED_YEAR, MIXED_PEOPLE, MIXED_STATES),
            reform=reform,
        )
        yield simulation
        del simulation
        gc.collect()

    def test_outlay_holds_after_the_labor_supply_response(self, mixed):
        year = MIXED_YEAR
        assert payroll_wage_rule(mixed.tax_benefit_system, year) == TAX_EXEMPT_WAGE_RULE
        assert payroll_wage_rule(mixed.baseline.tax_benefit_system, year) == (
            DEFAULT_WAGE_RULE
        )
        response = mixed.calculate(RESPONSE, year)
        assert np.any(response != 0)
        pay = mixed.calculate("employment_income_before_lsr", year).astype(
            np.float64
        ) + response.astype(np.float64)
        change = mixed.calculate(CHANGE, year)
        np.testing.assert_allclose(
            mixed.calculate("employment_income", year),
            pay + change,
            rtol=1e-6,
            atol=0.05,
        )
        assert_outlay_held(mixed, year, MIXED_STATES, pay)
        # Negative pay and no pay: nothing to tax in either system.
        assert change[3] == 0 and change[4] == 0
        # Tips above pay: the reform taxes none of it, so pay rises by the whole
        # baseline tax.
        assert change[2] > 0

    def test_measurement_branches_calculate_the_change_from_their_own_inputs(
        self, mixed
    ):
        """The labor supply measurements see the change, without the response.

        Built as get_behavioral_response_measurements builds them: the reform
        branch neutralizes the responses and copies the pre-response inputs, so it
        calculates the change on pay before the response, which differs from the
        simulation's own change wherever the response is not zero. The baseline
        branch has no baseline, so its change is zero.

        get_behavioral_response_measurements branches while the simulation is
        calculating the response, which the change reads, so the simulation has
        no change for the period yet. This simulation already has one, and a
        branch keeps its parent's values when only its system changes, so the
        test drops them, as core advises for a branch with a changed system.
        """
        year = MIXED_YEAR
        person = mixed.populations["person"]
        response = mixed.calculate(RESPONSE, year)
        branch = mixed.get_branch("employer_incidence_measurement", clone_system=True)
        try:
            _neutralize_behavioral_responses(branch)
            _copy_behavioral_response_inputs(branch, person, year)
            branch.drop_computed_arrays()
            np.testing.assert_array_equal(branch.calculate(RESPONSE, year), 0)
            pay = branch.calculate("employment_income_before_lsr", year).astype(
                np.float64
            )
            branch_change = branch.calculate(CHANGE, year)
            assert_outlay_held(branch, year, MIXED_STATES, pay)
            moved = response != 0
            assert np.all(branch_change[moved] != mixed.calculate(CHANGE, year)[moved])
        finally:
            del mixed.branches["employer_incidence_measurement"]
        baseline_branch = _baseline_measurement_branch(mixed)
        assert payroll_wage_rule(baseline_branch.tax_benefit_system, year) == (
            DEFAULT_WAGE_RULE
        )
        np.testing.assert_array_equal(baseline_branch.calculate(CHANGE, year), 0)
