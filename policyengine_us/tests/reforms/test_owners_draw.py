"""Structural activation, isolation, and vector invariants for owners' draw.

Dollar examples live in owners_draw.yaml. These tests capture the installed
formula classes for fast deterministic and shrinking generated vectors. Public
Simulation tests batch households under one private policy per test to exercise
constructor activation, baseline equality, cap preservation and AIME history.
"""

import gc
from itertools import chain
from types import SimpleNamespace

import numpy as np
import pytest
from hypothesis import HealthCheck, example, given, settings
from hypothesis import strategies as st
from policyengine_core.periods import period
from policyengine_core.reforms import Reform

from policyengine_us import Simulation
from policyengine_us.reforms.ssa.owners_draw import (
    create_owners_draw,
    create_owners_draw_reform,
)
from policyengine_us.system import system
from policyengine_us.variables.gov.contrib.congress.s770.s770_active_business_income import (
    s770_active_business_income,
)
from policyengine_us.variables.gov.irs.income.taxable_income.adjusted_gross_income.above_the_line_deductions.self_employment_tax_ald_person import (
    self_employment_tax_ald_person,
)
from policyengine_us.variables.gov.irs.tax.payroll.social_security.taxable_earnings_for_social_security import (
    taxable_earnings_for_social_security,
)
from policyengine_us.variables.gov.irs.tax.self_employment.self_employment_medicare_tax import (
    self_employment_medicare_tax,
)
from policyengine_us.variables.gov.irs.tax.self_employment.self_employment_social_security_tax import (
    self_employment_social_security_tax,
)
from policyengine_us.variables.gov.irs.tax.self_employment.self_employment_tax import (
    self_employment_tax,
)
from policyengine_us.variables.gov.irs.tax.self_employment.social_security_taxable_self_employment_income import (
    social_security_taxable_self_employment_income,
)
from policyengine_us.variables.gov.irs.tax.self_employment.taxable_self_employment_income import (
    taxable_self_employment_income,
)


BASELINE_VARIABLES = {
    variable.__name__: variable
    for variable in (
        taxable_earnings_for_social_security,
        taxable_self_employment_income,
        social_security_taxable_self_employment_income,
        self_employment_social_security_tax,
        self_employment_medicare_tax,
        self_employment_tax,
        self_employment_tax_ald_person,
    )
}
PERIOD = period("2027")
CAP = 200_000


@pytest.fixture(scope="module")
def reform_variables():
    installed = []
    create_owners_draw().apply(SimpleNamespace(update_variable=installed.append))
    return BASELINE_VARIABLES | {
        variable.__name__: variable
        for variable in installed
        if variable.__name__ != "ss_aime"
    }


def _parameters(
    *,
    oasdi_rate=0.124,
    hi_rate=0.029,
    employer_share=0.5,
    cap=CAP,
    deductible_share=0.5,
    **overrides,
):
    draw = SimpleNamespace(
        in_effect=True,
        start_year=2027,
        phase_in_years=10,
        phase_in_share=1,
        material_participation_only=True,
        net_earnings_factor=0,
        include_hi=False,
        half_seca_deduction=True,
        benefit_credit=True,
        room_cap_basis=0,
        current_law_cap=cap,
    )
    for name, value in overrides.items():
        setattr(draw, name, value)
    root = SimpleNamespace(
        gov=SimpleNamespace(
            contrib=SimpleNamespace(
                ssa=SimpleNamespace(owners_draw=draw),
                ubi_center=SimpleNamespace(
                    flat_tax=SimpleNamespace(abolish_self_emp_tax=False)
                ),
            ),
            irs=SimpleNamespace(
                payroll=SimpleNamespace(social_security=SimpleNamespace(cap=cap)),
                self_employment=SimpleNamespace(
                    rate=SimpleNamespace(social_security=oasdi_rate, medicare=hi_rate),
                    net_earnings_exemption=400,
                ),
                ald=SimpleNamespace(
                    misc=SimpleNamespace(employer_share=employer_share),
                    self_employment_tax=SimpleNamespace(
                        percent_deductible=deductible_share
                    ),
                ),
            ),
        )
    )
    return lambda instant: root


def _calculate(variables, parameters, inputs, outputs=None):
    values = {
        "s_corp_income": 0,
        "partnership_income": 0,
        "passive_partnership_s_corp_income": 0,
        "partnership_self_employment_net_earnings": 0,
        "owners_draw_subsets_are_disjoint": True,
        "owners_draw_passive_se_overlap": np.nan,
        "self_employment_income": 0,
        "sstb_self_employment_income": 0,
        "farm_operations_income": 0,
        "payroll_tax_gross_wages": 0,
        **inputs,
    }

    values = {name: np.asarray(value) for name, value in values.items()}

    def person(name, instant, options=None):
        if name not in values:
            values[name] = variables[name].formula(person, instant, parameters)
        return values[name]

    # Core's add() checks entity metadata before summing Person variables.
    person.entity = SimpleNamespace(is_person=True, key="person")
    person.entity.get_variable = lambda name: SimpleNamespace(entity=person.entity)

    for name in outputs or variables:
        if name not in (
            "owners_draw_subsets_are_disjoint",
            "owners_draw_passive_se_overlap",
        ):
            person(name, PERIOD)
    return values


VECTOR_INPUTS = {
    "payroll_tax_gross_wages": np.array(
        [0, 100_000, 200_000, 300_000, 0, 90_000, 199_999, 0], dtype=float
    ),
    "s_corp_income": np.array(
        [150_000, 200_000, 300_000, 150_000, -50_000, 100_000, 500_000, 433],
        dtype=float,
    ),
    "self_employment_income": np.array(
        [0, 50_000, 0, 50_000, 80_000, 100_000, 1_000, 0], dtype=float
    ),
    "partnership_income": np.array(
        [0, 30_000, 40_000, 0, 20_000, 20_000, 0, 0], dtype=float
    ),
    "partnership_self_employment_net_earnings": np.array(
        [0, 30_000, 0, 0, 0, 20_000, 0, 0], dtype=float
    ),
}


def test_vector_invariants_and_phase_monotonicity(reform_variables):
    prior_base = np.zeros(8)
    prior_tax = np.zeros(8)
    for share in (0, 0.1, 0.3, 0.7, 1):
        values = _calculate(
            reform_variables, _parameters(phase_in_share=share), VECTOR_INPUTS
        )
        base = values["owners_draw_oasdi_base"]
        gross = values["owners_draw_gross"]
        room = values["owners_draw_oasdi_room"]
        tax = values["owners_draw_oasdi_tax"]
        assert np.all(base >= 0)
        assert np.all(base <= room)
        assert np.all(base <= gross)
        assert np.all(base >= prior_base)
        assert np.all(tax >= prior_tax)
        total_earnings = (
            values["taxable_earnings_for_social_security"]
            + values["social_security_taxable_self_employment_income"]
            + base
        )
        assert np.all(total_earnings <= CAP)
        # M7 cannot exclude untaxed or undrawn profits from the active base.
        exclusion = values["owners_draw_niit_exclusion"]
        assert np.all(exclusion >= 0)
        assert np.all(exclusion <= gross + 1e-8)
        np.testing.assert_allclose(exclusion * 0.9235, base)
        prior_base, prior_tax = base, tax


def test_disabled_formulas_equal_baseline_on_the_same_vectors(reform_variables):
    parameters = _parameters(in_effect=False)
    baseline = _calculate(BASELINE_VARIABLES, parameters, VECTOR_INPUTS)
    reformed = _calculate(reform_variables, parameters, VECTOR_INPUTS)
    for name in BASELINE_VARIABLES:
        np.testing.assert_array_equal(reformed[name], baseline[name], err_msg=name)
    for name in reform_variables.keys() - BASELINE_VARIABLES.keys():
        if name not in (
            "owners_draw_subsets_are_disjoint",
            "owners_draw_passive_se_overlap",
        ):
            assert np.all(np.asarray(reformed[name]) == 0), name


def test_already_se_partnership_income_cannot_add_a_second_draw(reform_variables):
    already_se = np.array([0, 399, 1_000, 100_000, 500_000], dtype=float)
    inputs = {
        "partnership_income": already_se,
        "partnership_self_employment_net_earnings": already_se,
    }
    parameters = _parameters()
    baseline = _calculate(BASELINE_VARIABLES, parameters, inputs)
    reformed = _calculate(reform_variables, parameters, inputs)
    assert np.all(reformed["owners_draw_gross"] == 0)
    assert np.all(reformed["owners_draw_oasdi_base"] == 0)
    for name in BASELINE_VARIABLES:
        np.testing.assert_array_equal(reformed[name], baseline[name], err_msg=name)


@pytest.mark.parametrize(
    "inputs, message",
    [
        (
            {
                "owners_draw_subsets_are_disjoint": False,
                "owners_draw_passive_se_overlap": np.nan,
            },
            "validated disjoint",
        ),
        (
            {
                "owners_draw_subsets_are_disjoint": True,
                "owners_draw_passive_se_overlap": 1_000,
            },
            "contradicts",
        ),
    ],
)
def test_ambiguous_or_contradictory_classification_is_rejected(
    reform_variables, inputs, message
):
    with pytest.raises(ValueError, match=message):
        _calculate(
            reform_variables,
            _parameters(),
            {
                "partnership_income": np.array([100_000, 50_000]),
                "partnership_self_employment_net_earnings": np.array([40_000, 0]),
                "passive_partnership_s_corp_income": np.array([20_000, 0]),
                **inputs,
            },
            outputs=["owners_draw_active_income"],
        )


@pytest.mark.parametrize(
    "overrides, output, message",
    [
        ({"phase_in_years": 0}, "owners_draw_gross", "positive integer"),
        ({"phase_in_years": 1.5}, "owners_draw_gross", "positive integer"),
        ({"phase_in_share": 1.01}, "owners_draw_gross", "phase_in_share"),
        ({"phase_in_share": -0.1}, "owners_draw_gross", "phase_in_share"),
        ({"net_earnings_factor": 1.1}, "owners_draw_gross", "net earnings factor"),
        ({"net_earnings_factor": -0.1}, "owners_draw_gross", "net earnings factor"),
        ({"room_cap_basis": 2}, "owners_draw_oasdi_room", "room_cap_basis"),
    ],
)
def test_invalid_policy_settings_fail_explicitly(
    reform_variables, overrides, output, message
):
    with pytest.raises(ValueError, match=message):
        _calculate(
            reform_variables,
            _parameters(**overrides),
            {"s_corp_income": 100_000},
            outputs=[output],
        )


def test_future_parameter_activation_captures_cap_and_preserves_baseline():
    years = (2026, 2036, 2037)
    situation = {
        "people": {
            "owner": {
                "age": {year: 45 for year in years},
                "payroll_tax_gross_wages": {year: 150_000 for year in years},
                "self_employment_income": {year: 50_000 for year in years},
                "s_corp_income": {year: 400_000 for year in years},
            },
            "past_owner": {
                "age": {year: year - 1975 for year in years},
                "s_corp_income": {2026: 0, 2036: 150_000, 2037: 0},
            },
        }
    }
    parameter_reform = Reform.from_dict(
        {
            "gov.contrib.ssa.owners_draw.in_effect": {
                "2036-01-01.2036-12-31": True,
                "2037-01-01.2100-12-31": False,
            },
            "gov.irs.payroll.social_security.cap": {"2036-01-01.2100-12-31": np.inf},
            "gov.simulation.aime_lookback_years": {"2026-01-01.2100-12-31": 1},
        },
        country_id="us",
    )
    baseline = Simulation(tax_benefit_system=system, situation=situation)
    reformed = Simulation(
        tax_benefit_system=system, situation=situation, reform=parameter_reform
    )

    # Parameter-only activation must discover a finite active interval twelve
    # years beyond the default 2024 factory start, including its later end.
    assert create_owners_draw_reform(system.parameters, "2024-01-01") is None
    unaffected_outputs = (
        *BASELINE_VARIABLES,
        "irs_gross_income",
        "adjusted_gross_income",
        "niit_magi",
        "net_investment_income_tax",
        "income_tax",
    )
    for year in (2026, 2037):
        for name in unaffected_outputs:
            np.testing.assert_array_equal(
                reformed.calculate(name, year),
                baseline.calculate(name, year),
                err_msg=f"{name} in inactive {year}",
            )
        assert reformed.calculate("owners_draw_gross", year)[0] == 0

    cap = system.parameters("2036-01-01").gov.irs.payroll.social_security.cap
    reformed_parameters = reformed.tax_benefit_system.parameters("2036-01-01")
    assert np.isinf(reformed_parameters.gov.irs.payroll.social_security.cap)
    assert reformed_parameters.gov.contrib.ssa.owners_draw.current_law_cap == cap
    expected_room = max(0, cap - 150_000 - 46_175)
    assert reformed.calculate("owners_draw_oasdi_room", 2036)[0] == pytest.approx(
        expected_room
    )
    assert reformed.calculate("owners_draw_oasdi_base", 2036)[0] == pytest.approx(
        min(369_400, expected_room)
    )

    # Covered earnings retain the earning year's classification when the
    # calculation/payment year is inactive. The 62-year-old's sole draw was
    # earned at age 61, after the age-60 indexing year, so no wage indexing
    # applies: 138,525 / (35 * 12) = 329.8214286.
    assert reformed.calculate("owners_draw_credited_earnings", 2036)[
        1
    ] == pytest.approx(138_525)
    assert reformed.calculate("owners_draw_credited_earnings", 2037)[1] == 0
    assert reformed.calculate("ss_aime", 2037)[1] == pytest.approx(138_525 / 420)

    # Neither the captured current-law path nor the shared baseline was mutated
    # by removing the tax ceiling in the reformed simulation.
    assert system.parameters("2036-01-01").gov.irs.payroll.social_security.cap == cap
    assert not system.parameters("2036-01-01").gov.contrib.ssa.owners_draw.in_effect


# Formula-level generators keep shrinking cheap: all owners in an example
# share one policy and are calculated together as NumPy arrays.
SETTINGS = dict(
    max_examples=40,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)

_RATE_POLICY = st.tuples(
    st.integers(1, 250), st.integers(1, 100), st.integers(0, 1_000)
)
_SIGNED_OWNER_BATCH = st.lists(
    st.tuples(
        st.integers(0, 1_000_000),  # wages
        st.integers(-500_000, 500_000),  # other existing SE income
        st.integers(-500_000, 500_000),  # active income outside SE
        st.integers(-500_000, 500_000),  # passive-only income
        st.integers(-500_000, 500_000),  # SE-only partnership income
        st.integers(-500_000, 500_000),  # passive/SE intersection
        st.integers(-500_000, 500_000),  # allocation to S corporations
    ),
    min_size=1,
    max_size=12,
)


def _policy_rates(rates):
    oasdi, hi, employer = rates
    return dict(
        oasdi_rate=oasdi / 1_000,
        hi_rate=hi / 1_000,
        employer_share=employer / 1_000,
    )


def _signed_owner_inputs(rows):
    wages, other_se, active, passive_only, se_only, overlap, s_corp = np.asarray(
        rows, dtype=float
    ).T
    # Four signed atoms supply an independent inclusion/exclusion oracle:
    # T = A + Q_only + K_only + Q_intersect_K, Q = Q_only + overlap,
    # K = K_only + overlap, so T - Q - K + overlap = A.
    total = active + passive_only + se_only + overlap
    return {
        "payroll_tax_gross_wages": wages,
        "self_employment_income": other_se,
        "s_corp_income": s_corp,
        "partnership_income": total - s_corp,
        "passive_partnership_s_corp_income": passive_only + overlap,
        "partnership_self_employment_net_earnings": se_only + overlap,
        "owners_draw_subsets_are_disjoint": False,
        "owners_draw_passive_se_overlap": overlap,
    }, active


@settings(**SETTINGS)
@given(
    rows=_SIGNED_OWNER_BATCH,
    rates=_RATE_POLICY,
    cap=st.integers(1_000, 1_000_000),
    preserved_cap=st.integers(1_000, 1_000_000),
    share=st.integers(0, 1_000),
    override_factor=st.sampled_from([0, 0.5, 0.8, 1]),
)
@example(
    rows=[
        (0, 0, 500, 0, 0, 0, 500),  # adjusted draw exactly $400
        (0, 0, 1_000, 0, 0, 0, 1_000),  # exactly the cap room
        (1_000, 0, 2_000, 0, 0, 0, 2_000),  # no room
        (2_000, 0, 2_000, 0, 0, 0, 2_000),  # above the preserved cap
    ],
    rates=(124, 29, 500),
    cap=1_000,
    preserved_cap=800,
    share=1_000,
    override_factor=0.8,
)
def test_generated_draw_bounds_and_adjustment(
    reform_variables, rows, rates, cap, preserved_cap, share, override_factor
):
    inputs, _ = _signed_owner_inputs(rows)
    policy = _policy_rates(rates)
    parameters = _parameters(
        **policy,
        cap=cap,
        current_law_cap=preserved_cap,
        phase_in_share=share / 1_000,
        net_earnings_factor=override_factor,
    )
    baseline = _calculate(BASELINE_VARIABLES, parameters, inputs)
    values = _calculate(reform_variables, parameters, inputs)
    q = override_factor or 1 - policy["employer_share"] * (
        policy["oasdi_rate"] + policy["hi_rate"]
    )
    expected_room = np.maximum(
        0,
        preserved_cap
        - baseline["taxable_earnings_for_social_security"]
        - baseline["social_security_taxable_self_employment_income"],
    )
    gross = values["owners_draw_gross"]
    net = values["owners_draw_net_earnings"]
    base = values["owners_draw_oasdi_base"]
    assert np.all(gross >= 0)
    np.testing.assert_allclose(net, gross * q)
    np.testing.assert_allclose(values["owners_draw_oasdi_room"], expected_room)
    assert np.all(base >= 0)
    assert np.all(base <= expected_room)
    assert np.all(base <= gross)
    np.testing.assert_allclose(base, np.minimum(net, expected_room))


@settings(**SETTINGS)
@given(
    rows=_SIGNED_OWNER_BATCH,
    rates=_RATE_POLICY,
    cap=st.integers(1_000, 1_000_000),
    shares=st.tuples(st.integers(0, 1_000), st.integers(0, 1_000)),
)
@example(
    rows=[(0, 0, 100_000, 0, 0, 0, 100_000)],
    rates=(124, 29, 500),
    cap=200_000,
    shares=(200, 300),  # an annual phase-in step
)
@example(
    rows=[(0, 0, 800, 0, 0, 0, 800)],
    rates=(124, 29, 500),
    cap=200_000,
    shares=(0, 1_000),
)
def test_generated_phase_in_tax_is_monotone(reform_variables, rows, rates, cap, shares):
    inputs, _ = _signed_owner_inputs(rows)
    lower, upper = sorted(shares)
    taxes = [
        _calculate(
            reform_variables,
            _parameters(**_policy_rates(rates), cap=cap, phase_in_share=share / 1_000),
            inputs,
        )["owners_draw_oasdi_tax"]
        for share in (lower, upper)
    ]
    assert np.all(taxes[0] <= taxes[1])


@settings(**SETTINGS)
@given(
    rows=_SIGNED_OWNER_BATCH,
    rates=_RATE_POLICY,
    share=st.integers(0, 1_000),
)
@example(
    rows=[
        (0, 0, 0, 0, 50_000, 0, 0),  # all income already SE
        (0, 0, 0, -20_000, 30_000, -10_000, -20_000),  # signed net zero
        (0, 10_000, 5_000, -5_000, 10_000, -2_000, 15_000),
    ],
    rates=(124, 29, 500),
    share=1_000,
)
def test_generated_signed_residual_never_double_counts_se(
    reform_variables, rows, rates, share
):
    inputs, active_not_se = _signed_owner_inputs(rows)
    parameters = _parameters(**_policy_rates(rates), phase_in_share=share / 1_000)
    baseline = _calculate(BASELINE_VARIABLES, parameters, inputs)
    values = _calculate(reform_variables, parameters, inputs)
    np.testing.assert_array_equal(values["owners_draw_active_income"], active_not_se)
    planned = np.maximum(0, active_not_se) * share / 1_000
    np.testing.assert_allclose(values["owners_draw_planned_gross"], planned)
    assert np.all(values["owners_draw_gross"] <= planned + 1e-8)
    for name in (
        "payroll_tax_gross_wages",
        "self_employment_income",
        "partnership_self_employment_net_earnings",
        "taxable_earnings_for_social_security",
        "taxable_self_employment_income",
        "social_security_taxable_self_employment_income",
    ):
        np.testing.assert_array_equal(values[name], baseline[name], err_msg=name)


@settings(**SETTINGS)
@given(
    rows=st.lists(
        st.tuples(
            st.one_of(
                st.sampled_from([0, 399, 399.99, 400, 400.01, 401]),
                st.integers(0, 10_000),
            ),
            st.integers(-100_000, 100_000),
        ),
        min_size=1,
        max_size=12,
    ),
    factor=st.sampled_from([0.5, 1]),
)
@example(rows=[(399.99, 100_000), (400, 0), (400.01, 100_000)], factor=0.5)
@example(rows=[(399, 0), (400, 399), (401, -100_000)], factor=1)
def test_generated_reporting_floor_is_separate_from_existing_se(
    reform_variables, rows, factor
):
    adjusted, existing_se = np.asarray(rows, dtype=float).T
    planned = adjusted / factor
    values = _calculate(
        reform_variables,
        _parameters(net_earnings_factor=factor),
        {"s_corp_income": planned, "self_employment_income": existing_se},
    )
    expected_gross = np.where(adjusted >= 400, planned, 0)
    np.testing.assert_array_equal(values["owners_draw_gross"], expected_gross)
    np.testing.assert_array_equal(
        values["owners_draw_net_earnings"], expected_gross * factor
    )


@settings(**SETTINGS)
@given(
    rows=_SIGNED_OWNER_BATCH,
    rates=_RATE_POLICY,
    cap=st.integers(1_000, 1_000_000),
)
@example(
    rows=[
        (200_000, 0, 500_000, 0, 0, 0, 500_000),  # no OASDI room
        (0, 0, 500_000, 0, 0, 0, 500_000),  # draw exceeds the cap
    ],
    rates=(124, 29, 500),
    cap=100_000,
)
def test_generated_hi_defaults_off_and_is_uncapped_when_enabled(
    reform_variables, rows, rates, cap
):
    inputs, _ = _signed_owner_inputs(rows)
    policy = dict(**_policy_rates(rates), cap=cap)
    baseline = _calculate(BASELINE_VARIABLES, _parameters(**policy), inputs)
    default = _calculate(reform_variables, _parameters(**policy), inputs)
    assert np.all(np.asarray(default["owners_draw_hi_tax"]) == 0)
    np.testing.assert_array_equal(
        default["self_employment_medicare_tax"],
        baseline["self_employment_medicare_tax"],
    )
    enabled = _calculate(
        reform_variables, _parameters(**policy, include_hi=True), inputs
    )
    added_hi = policy["hi_rate"] * enabled["owners_draw_net_earnings"]
    np.testing.assert_allclose(enabled["owners_draw_hi_tax"], added_hi)
    np.testing.assert_allclose(
        enabled["self_employment_medicare_tax"],
        baseline["self_employment_medicare_tax"] + added_hi,
    )


@settings(**SETTINGS)
@given(
    rows=_SIGNED_OWNER_BATCH,
    rates=_RATE_POLICY,
    deductible=st.integers(0, 1_000),
    include_hi=st.booleans(),
)
@example(
    rows=[(0, 50_000, 100_000, 0, 0, 0, 100_000)],
    rates=(124, 29, 500),
    deductible=250,
    include_hi=True,
)
@example(
    rows=[(0, 0, 100_000, 0, 0, 0, 100_000)],
    rates=(124, 29, 500),
    deductible=1_000,
    include_hi=False,
)
def test_generated_deduction_tracks_existing_deductible_share(
    reform_variables, rows, rates, deductible, include_hi
):
    inputs, _ = _signed_owner_inputs(rows)
    policy = dict(
        **_policy_rates(rates),
        deductible_share=deductible / 1_000,
        include_hi=include_hi,
    )
    baseline = _calculate(BASELINE_VARIABLES, _parameters(**policy), inputs)
    enabled = _calculate(reform_variables, _parameters(**policy), inputs)
    added_seca = enabled["owners_draw_oasdi_tax"] + enabled["owners_draw_hi_tax"]
    np.testing.assert_allclose(
        enabled["self_employment_tax"] - baseline["self_employment_tax"], added_seca
    )
    np.testing.assert_allclose(
        enabled["self_employment_tax_ald_person"],
        baseline["self_employment_tax_ald_person"]
        + policy["deductible_share"] * added_seca,
    )
    disabled = _calculate(
        reform_variables,
        _parameters(**policy, half_seca_deduction=False),
        inputs,
    )
    np.testing.assert_allclose(
        disabled["self_employment_tax_ald_person"],
        baseline["self_employment_tax_ald_person"],
    )


@pytest.fixture
def private_draw_system():
    """Keep one independent registry/parameter tree for a complete property.

    Hypothesis reuses a function fixture across examples intentionally: policy
    stays fixed, while every example gets new Simulation holders.
    A mutable owner releases even pytest's fixture reference after the test.
    """
    gc.collect()
    owner = SimpleNamespace(system=None)
    try:
        yield owner
    finally:
        if owner.system is not None:
            owner.system.simulation = None
        owner.system = None
        gc.collect()


SIMULATION_SETTINGS = {
    **SETTINGS,
    "max_examples": 2,
    "suppress_health_check": [
        *SETTINGS["suppress_health_check"],
        HealthCheck.function_scoped_fixture,
    ],
}
SIMULATION_YEAR = 2027
SIMULATION_WINDOW = "2027-01-01.2100-12-31"
SIMULATION_DRAW = "gov.contrib.ssa.owners_draw."
SIMULATION_CAP = "gov.irs.payroll.social_security.cap"
simulation_amount = st.integers(0, 600_000)
simulation_person = st.tuples(
    st.integers(20, 85),
    simulation_amount,
    st.integers(-40_000, 250_000),
    st.integers(-100_000, 600_000),
    st.integers(-100_000, 300_000),
    st.integers(0, 80_000),
    st.integers(0, 80_000),
)


def _simulation_situation(batch, year=SIMULATION_YEAR, supplied=None):
    """Build separate single-person tax units in one vectorized simulation."""
    result = {
        entity: {}
        for entity in (
            "people",
            "tax_units",
            "families",
            "spm_units",
            "marital_units",
            "households",
        )
    }
    input_names = (
        "age",
        "employment_income",
        "self_employment_income",
        "s_corp_income",
        "partnership_income",
        "partnership_self_employment_net_earnings",
        "passive_partnership_s_corp_income",
    )
    years = (year,) if isinstance(year, int) else year
    for i, inputs in enumerate(batch):
        name = f"owner_{i}"
        result["people"][name] = {
            key: {year: value for year in years}
            for key, value in zip(input_names, inputs)
        }
        if supplied is not None:
            result["people"][name]["ss_aime_input"] = {
                year: supplied[i] for year in years
            }
        for entity in result.keys() - {"people"}:
            result[entity][f"unit_{i}"] = {"members": [name]}
        result["households"][f"unit_{i}"]["state_code"] = {year: "TX" for year in years}
    return result


def _private_simulation(owner, situation, reform=None):
    # The public US constructor clones a supplied system when given a reform.
    # Adopt that one private clone, then share its unchanged policy across new
    # holders for every generated batch. Repeated constructors with a reform
    # would copy the entire country tree on every example.
    if owner.system is None:
        simulation = Simulation(
            tax_benefit_system=system, situation=situation, reform=reform
        )
        owner.system = simulation.tax_benefit_system
        return simulation
    return Simulation(tax_benefit_system=owner.system, situation=situation)


def _zero_earlier_earnings(simulation, year):
    # Supply a complete zero history through the public API after construction.
    # This keeps the default lookback and isolates draw history from historical
    # labor-response parameter coverage in the ordinary earnings formulas.
    zeros = np.zeros(simulation.populations["person"].count)
    for historic_year in range(year - 45, year):
        simulation.set_input("employment_income", historic_year, zeros)
        simulation.set_input("total_self_employment_income", historic_year, zeros)


def _release_simulation_caches(simulation):
    """Release derived history caches without changing policy or input values."""
    policy = simulation.tax_benefit_system
    if getattr(policy, "simulation", None) is simulation:
        policy.simulation = None
    policy._parameters_at_instant_cache.clear()
    root = policy.parameters
    # Core eagerly materializes each full parameter tree at every instant.
    # Children retain their own caches, so clearing only the root is not enough.
    for node in chain((root,), root.get_descendants()):
        cache = getattr(node, "_at_instant_cache", None)
        if cache is not None:
            cache.clear()


@pytest.mark.parametrize("route", ["parametric", "class"])
@settings(**SIMULATION_SETTINGS)
@given(batch=st.lists(simulation_person, min_size=3, max_size=8))
@example(
    batch=[
        (62, 0, 0, 600_000, 0, 0, 0),
        (62, 200_000, 0, 600_000, 0, 0, 0),
        (62, 600_000, 250_000, 600_000, 0, 0, 0),
    ],
)
def test_generated_raised_cap_paths_preserve_current_law_room(
    private_draw_system, reform_variables, route, batch
):
    """Property 2: current-law, parameter and class cap paths share ordering."""
    # The same invariant is checked cheaply first, so a source mutant can be
    # rejected under the mutation runner's 2 GiB cap before cloning a system.
    raised_cap = 400_000
    probe = _calculate(
        reform_variables,
        _parameters(cap=raised_cap, current_law_cap=200_000),
        {"s_corp_income": 1_000_000},
    )
    assert probe["owners_draw_oasdi_base"] == 200_000
    # These subsets can be arbitrary in the off differential below. Here they
    # are explicitly disjoint, so install that classification only in the
    # private reformed simulation (the baseline has no such input variable).
    situation = _simulation_situation(batch, (2027, 2028))
    policy = {
        SIMULATION_DRAW + "in_effect": {SIMULATION_WINDOW: True},
        SIMULATION_DRAW + "phase_in_share": {SIMULATION_WINDOW: 1},
        SIMULATION_CAP: {"2027-01-01.2027-12-31": raised_cap},
    }

    class RaisedCap(Reform):
        def apply(self):
            activation = Reform.from_dict(
                {key: value for key, value in policy.items() if key != SIMULATION_CAP},
                country_id="us",
            )
            activation.apply(self)
            self.parameters.gov.irs.payroll.social_security.cap.update(
                start=PERIOD.start, stop=PERIOD.stop, value=raised_cap
            )

    simulation = _private_simulation(
        private_draw_system, situation, policy if route == "parametric" else RaisedCap
    )
    for year in (2027, 2028):
        simulation.set_input(
            "owners_draw_subsets_are_disjoint", year, np.ones(len(batch), bool)
        )
        cap = system.parameters(f"{year}-01-01").gov.irs.payroll.social_security.cap
        active_cap = raised_cap if year == 2027 else cap
        p = simulation.tax_benefit_system.parameters(f"{year}-01-01")
        assert p.gov.irs.payroll.social_security.cap == active_cap
        assert p.gov.contrib.ssa.owners_draw.current_law_cap == cap
        wages = simulation.calculate("taxable_earnings_for_social_security", year)
        existing = simulation.calculate(
            "social_security_taxable_self_employment_income", year
        )
        room = np.maximum(0, cap - wages - existing)
        draw = simulation.calculate("owners_draw_oasdi_base", year)
        np.testing.assert_allclose(
            simulation.calculate("owners_draw_oasdi_room", year), room, atol=0.02
        )
        adjusted = simulation.calculate("owners_draw_net_earnings", year)
        np.testing.assert_allclose(draw, np.minimum(adjusted, room), atol=0.02)
        assert np.all(wages + existing + draw <= active_cap + 0.02)
        assert (
            system.parameters(f"{year}-01-01").gov.irs.payroll.social_security.cap
            == cap
        )


@settings(**SIMULATION_SETTINGS)
@given(batch=st.lists(simulation_person, min_size=3, max_size=8))
@example(
    batch=[
        (62, 0, 0, 150_000, 0, 0, 0),
        (45, 300_000, 50_000, -50_000, 50_000, 0, 0),
        (85, 100_000, -20_000, 0, 100_000, 40_000, 20_000),
    ]
)
def test_generated_disabled_reform_matches_public_baseline(
    private_draw_system, reform_variables, batch
):
    """Property 3: disabled formulas agree through complete public tax paths."""
    probe_inputs = {"s_corp_income": 150_000, "self_employment_income": 50_000}
    parameters = _parameters(in_effect=False)
    probe = _calculate(reform_variables, parameters, probe_inputs)
    reference = _calculate(BASELINE_VARIABLES, parameters, probe_inputs)
    for output in BASELINE_VARIABLES:
        np.testing.assert_array_equal(probe[output], reference[output], err_msg=output)
    situation = _simulation_situation(batch)
    outputs = (
        *BASELINE_VARIABLES,
        "payroll_tax_gross_wages",
        "total_self_employment_income",
        "irs_gross_income",
        "adjusted_gross_income",
        "income_tax",
        "ss_aime",
        "niit_magi",
        "net_investment_income_tax",
    )
    # Calculate the real baseline first, then release its 45-year parameter
    # caches before the independent disabled policy builds its own history.
    # Keeping both full histories resident can exceed the file's memory cap.
    baseline = Simulation(tax_benefit_system=system, situation=situation)
    try:
        _zero_earlier_earnings(baseline, 2027)
        assert (
            baseline.tax_benefit_system.parameters(
                "2027-01-01"
            ).gov.simulation.aime_lookback_years
            == 45
        )
        baseline_outputs = {
            output: baseline.calculate(output, 2027).copy() for output in outputs
        }
    finally:
        _release_simulation_caches(baseline)
        del baseline
        gc.collect()

    disabled = _private_simulation(private_draw_system, situation, create_owners_draw())
    try:
        _zero_earlier_earnings(disabled, 2027)
        assert (
            disabled.tax_benefit_system.parameters(
                "2027-01-01"
            ).gov.simulation.aime_lookback_years
            == 45
        )
        for output in outputs:
            np.testing.assert_array_equal(
                disabled.calculate(output, 2027),
                baseline_outputs[output],
                err_msg=output,
            )
    finally:
        _release_simulation_caches(disabled)
        del disabled
        gc.collect()


@settings(**SIMULATION_SETTINGS)
@given(
    amounts=st.lists(
        st.tuples(simulation_amount, st.integers(0, 250_000), simulation_amount),
        min_size=3,
        max_size=8,
    ),
    year=st.sampled_from([2027, 2036]),
)
@example(
    amounts=[(0, 0, 600_000), (600_000, 0, 600_000), (0, 0, 433)],
    year=2027,
)
@example(amounts=[(0, 0, 0), (0, 0, 100_000), (100_000, 50_000, 100_000)], year=2036)
def test_generated_benefit_credit_cap_override_and_historical_lookback(
    private_draw_system, reform_variables, amounts, year
):
    """Property 9 and regression: default 45-year histories are always valid."""
    probe = _calculate(
        reform_variables,
        _parameters(benefit_credit=False),
        {"s_corp_income": 150_000},
    )
    assert probe["owners_draw_credited_earnings"] == 0
    historical_parameters = _parameters(in_effect=False)
    # Historical disabled years may lack the modern reporting-floor node.
    del historical_parameters(PERIOD).gov.irs.self_employment.net_earnings_exemption
    historical = _calculate(
        reform_variables,
        historical_parameters,
        {"s_corp_income": 150_000},
        outputs=["owners_draw_gross"],
    )
    assert historical["owners_draw_gross"] == 0
    batch = [(62, wages, se, draw, 0, 0, 0) for wages, se, draw in amounts]
    # Both supplied and computed AIMEs occur in every generated batch.
    supplied = np.array(
        [
            123.45 if i % 4 == 1 else 1_234.5 if i % 4 == 3 else 0
            for i in range(len(batch))
        ]
    )
    situation = _simulation_situation(batch, year, supplied)
    policy = {
        SIMULATION_DRAW + "in_effect": {SIMULATION_WINDOW: True},
        SIMULATION_DRAW + "phase_in_share": {SIMULATION_WINDOW: 1},
        SIMULATION_DRAW + "benefit_credit": {
            "2027-01-01.2027-12-31": True,
            "2028-01-01.2028-12-31": False,
            "2036-01-01.2036-12-31": True,
            "2037-01-01.2037-12-31": False,
        },
    }
    credited = _private_simulation(private_draw_system, situation, policy)
    _zero_earlier_earnings(credited, year)
    p = credited.tax_benefit_system.parameters(f"{year}-01-01")
    assert p.gov.simulation.aime_lookback_years == 45
    wages, se, gross = np.array(amounts, dtype=float).T
    q = 1 - p.gov.irs.ald.misc.employer_share * (
        p.gov.irs.self_employment.rate.social_security
        + p.gov.irs.self_employment.rate.medicare
    )
    adjusted = gross * q
    adjusted = np.where(
        adjusted >= p.gov.irs.self_employment.net_earnings_exemption, adjusted, 0
    )
    np.testing.assert_allclose(
        credited.calculate("owners_draw_credited_earnings", year), adjusted, atol=0.02
    )
    annual_cap = p.gov.ssa.social_security.wage_base
    # At age 62 the current year's earnings are after the indexing year. All
    # earlier supplied earnings default to zero, so the annual ledger gives a
    # hand-computable AIME with no projection or wage-indexing dependency.
    covered = np.minimum(wages + se + adjusted, annual_cap)
    expected = np.where(supplied > 0, supplied, covered / 420)
    np.testing.assert_allclose(credited.calculate("ss_aime", year), expected, atol=0.02)
    assert np.all(covered <= annual_cap)
    # Calling every lookback year explicitly catches a disabled-year formula
    # reading the net-earnings floor before its first defined year (2013).
    for historic_year in range(year - 45, year + 1):
        value = credited.calculate("owners_draw_gross", historic_year)
        assert np.isfinite(value).all()
        if historic_year < 2027:
            np.testing.assert_array_equal(value, np.zeros(len(batch)))

    # A separate batch in a configured credit-off year avoids copying the
    # parameter tree to toggle a flag between examples. It is compared with
    # the public baseline for that same year and exactly those earnings.
    off_year = year + 1
    off_situation = _simulation_situation(batch, off_year, supplied)
    no_credit = _private_simulation(private_draw_system, off_situation)
    _zero_earlier_earnings(no_credit, off_year)
    # Every owner is 62 in this separate scoring-year fixture, with zero
    # earnings in all 45 prior years. Main's baseline AIME therefore uses
    # only current wages plus gross SE earnings, capped at that year's wage
    # base, divided by 35 * 12; a positive supplied AIME still takes priority.
    # This independent baseline oracle avoids a third simulation. The
    # disabled-reform differential above also checks main's public helper.
    off_cap = no_credit.tax_benefit_system.parameters(
        f"{off_year}-01-01"
    ).gov.ssa.social_security.wage_base
    expected_off = np.where(
        supplied > 0, supplied, np.minimum(wages + se, off_cap) / 420
    )
    actual_off = no_credit.calculate("ss_aime", off_year)
    np.testing.assert_array_equal(actual_off, expected_off.astype(actual_off.dtype))
    np.testing.assert_array_equal(
        no_credit.calculate("owners_draw_credited_earnings", off_year),
        np.zeros(len(batch)),
    )


@settings(**SETTINGS)
@given(
    rows=st.lists(
        st.tuples(
            st.integers(0, 1_000_000),
            st.integers(-100_000, 1_000_000),
            st.integers(0, 100_000),
            st.integers(0, 100_000),
            st.integers(-100_000, 100_000),
        ),
        min_size=1,
        max_size=12,
    ),
    rates=_RATE_POLICY,
    cap=st.integers(1_000, 1_000_000),
    share=st.integers(0, 1_000),
    override_factor=st.sampled_from([0, 0.5, 0.8, 1]),
    include_hi=st.booleans(),
)
@example(
    rows=[(250_000, 400_000, 0, 0, 0), (100_000, 400_000, 0, 0, 0), (0, 0, 0, 0, 0)],
    rates=(124, 29, 500),
    cap=200_000,
    share=1_000,
    override_factor=0,
    include_hi=False,
)
@example(
    rows=[
        (0, 499.99, 0, 0, 0),
        (0, 500, 0, 0, 0),
        (0, 500.01, 0, 0, 0),
        (100_000, 400_000, 0, 0, 0),
    ],
    rates=(124, 29, 500),
    cap=200_000,
    share=1_000,
    override_factor=0.8,
    include_hi=False,
)
@example(
    rows=[(250_000, 400_000, 0, 0, 0), (100_000, 400_000, 0, 0, 0), (0, -100, 0, 0, 0)],
    rates=(124, 29, 500),
    cap=200_000,
    share=1_000,
    override_factor=0,
    include_hi=True,
)
@example(
    rows=[(100_000, 400_000, 50_000, 30_000, 20_000)],
    rates=(124, 29, 500),
    cap=200_000,
    share=300,
    override_factor=0,
    include_hi=False,
)
def test_generated_s770_excludes_actual_owners_draw(
    reform_variables, rows, rates, cap, share, override_factor, include_hi
):
    """The active NIIT residual consumes the draw's actual M7 classification."""
    wages, active, passive, already_se, other_se = np.asarray(rows, dtype=float).T
    inputs = {
        "payroll_tax_gross_wages": wages,
        "s_corp_income": active,
        "partnership_income": passive + already_se,
        "passive_partnership_s_corp_income": passive,
        "partnership_self_employment_net_earnings": already_se,
        "self_employment_income": other_se,
    }
    policy = dict(
        **_policy_rates(rates),
        cap=cap,
        phase_in_share=share / 1_000,
        net_earnings_factor=override_factor,
        include_hi=include_hi,
    )
    values = _calculate(reform_variables, _parameters(**policy), inputs)
    member_values = {
        **values,
        "partnership_s_corp_income": active + passive + already_se,
        "s770_passive_se_income": 0,
        "s770_draw_gross": 0,
        "s770_draw_oasdi_base": 0,
        "s770_draw_hi_in_effect": False,
        "s770_active_fica_income": 0,
        "is_tax_unit_dependent": False,
    }

    def person(name, instant):
        return np.asarray(member_values[name])

    registry = {"owners_draw_niit_exclusion": object()}
    person.simulation = SimpleNamespace(
        tax_benefit_system=SimpleNamespace(variables=registry)
    )
    # One tax unit per owner preserves the vector batch without a model clone.
    tax_unit = SimpleNamespace(members=person, sum=lambda array: array)
    result = s770_active_business_income.formula(
        tax_unit, PERIOD, _parameters(**policy)
    )
    np.testing.assert_allclose(result, active - values["owners_draw_niit_exclusion"])

    # Installed-but-disabled, pre-start, and uninstalled draws retain the
    # independent manual integration hooks, including their ordinary factor.
    member_values["s770_draw_oasdi_base"] = 1_234.5
    q = 1 - policy["employer_share"] * (policy["oasdi_rate"] + policy["hi_rate"])
    for installed, enabled, start_year in (
        (True, False, 2027),
        (True, True, 2028),
        (False, True, 2027),
    ):
        person.simulation.tax_benefit_system.variables = registry if installed else {}
        result = s770_active_business_income.formula(
            tax_unit,
            PERIOD,
            _parameters(**policy, in_effect=enabled, start_year=start_year),
        )
        np.testing.assert_allclose(result, active - 1_234.5 / q)


@settings(**SETTINGS)
@given(
    rows=st.lists(
        st.tuples(
            st.integers(-1_000_000, 1_000_000),  # total pass-through income
            st.integers(-1_000_000, 1_000_000),  # passive subset
            st.integers(-1_000_000, 1_000_000),  # already-SE subset
            st.integers(-1_000_000, 1_000_000),  # passive/SE intersection
            st.integers(-1_000_000, 1_000_000),  # manual actual gross draw
            st.integers(-1_000_000, 1_000_000),  # manual taxed OASDI draw
            st.booleans(),  # manual uncapped-HI indicator
            st.integers(-1_000_000, 1_000_000),  # active FICA exclusion
            st.booleans(),  # dependent exclusion
            st.integers(0, 3),  # tax-unit membership
        ),
        min_size=1,
        max_size=12,
    ),
    rates=_RATE_POLICY,
    override_factor=st.sampled_from([0, 0.5, 0.8, 1]),
    include_hi=st.booleans(),
)
@example(
    rows=[
        (400_000, 20_000, 30_000, 5_000, 50_000, 1_234.5, False, 6_000, False, 0),
        (-10_000, -5_000, -3_000, -1_000, 2_000, 9_000, True, 1_000, False, 0),
        (400_000, 0, 0, 0, 50_000, 12_345, False, 0, True, 0),
        (100_000, 0, 0, 0, 8_000, 50_000, True, 2_000, False, 1),
    ],
    rates=(124, 29, 500),
    override_factor=0.8,
    include_hi=True,
)
@example(
    rows=[(0, 0, 0, 0, 0, 0, False, 0, False, 0)],
    rates=(200, 40, 500),
    override_factor=0,
    include_hi=False,
)
def test_generated_disabled_owners_draw_preserves_main_s770(
    rows, rates, override_factor, include_hi
):
    """Inactive draws preserve main's full signed residual and manual hooks."""
    columns = list(zip(*rows))
    (
        total,
        passive,
        already_se,
        overlap,
        manual_gross,
        manual_oasdi,
        manual_hi,
        active_fica,
        dependent,
        tax_unit_index,
    ) = [np.asarray(column) for column in columns]
    policy = _policy_rates(rates)
    q = 1 - policy["employer_share"] * (policy["oasdi_rate"] + policy["hi_rate"])
    # Independent oracle for main fe9ec1270f / #10402: net signed sources,
    # subtract the manual M7 exclusion using main's rate-derived factor, then
    # exclude dependents and aggregate head/spouse amounts within tax units.
    # An owners-draw factor override must have no effect while it is inactive.
    expected_person = np.zeros(len(rows), dtype=float)
    for index, row in enumerate(rows):
        t, p, se, intersection, gross, base, hi, fica, dep, _ = row
        if not dep:
            manual_exclusion = gross if hi else base / q
            expected_person[index] = t - p - se + intersection - manual_exclusion - fica
    expected = np.bincount(tax_unit_index, weights=expected_person, minlength=4)
    values = {
        "partnership_s_corp_income": total,
        "passive_partnership_s_corp_income": passive,
        "partnership_self_employment_net_earnings": already_se,
        "s770_passive_se_income": overlap,
        "s770_draw_gross": manual_gross,
        "s770_draw_oasdi_base": manual_oasdi,
        "s770_draw_hi_in_effect": manual_hi,
        "s770_active_fica_income": active_fica,
        "is_tax_unit_dependent": dependent,
        # This is the actual exclusion for a disabled or pre-start draw. If
        # the bridge accidentally consumes it, the manual hooks disappear.
        "owners_draw_niit_exclusion": np.zeros(len(rows)),
    }

    def person(name, instant):
        return values[name]

    person.simulation = SimpleNamespace(
        tax_benefit_system=SimpleNamespace(variables={})
    )
    tax_unit = SimpleNamespace(
        members=person,
        sum=lambda array: np.bincount(tax_unit_index, weights=array, minlength=4),
    )
    for installed, enabled, start_year in (
        (True, False, 2027),
        (True, True, 2028),
        (False, True, 2027),
    ):
        person.simulation.tax_benefit_system.variables = (
            {"owners_draw_niit_exclusion": object()} if installed else {}
        )
        parameters = _parameters(
            **policy,
            in_effect=enabled,
            start_year=start_year,
            net_earnings_factor=override_factor,
            include_hi=include_hi,
        )
        if not installed:
            # The main-only path must not require the draw parameter subtree.
            del parameters(PERIOD).gov.contrib.ssa.owners_draw
        actual = s770_active_business_income.formula(tax_unit, PERIOD, parameters)
        np.testing.assert_allclose(actual, expected, rtol=1e-12, atol=1e-8)


@pytest.mark.parametrize(
    "installed, enabled, start_year",
    [(True, True, 2027), (True, False, 2027), (True, True, 2028), (False, True, 2027)],
)
def test_s770_rejects_unclassified_passive_inclusive_draw(
    reform_variables, installed, enabled, start_year
):
    """Only the new active joint route needs an active/NII source allocation."""
    inputs = {
        "s_corp_income": [200_000],
        "passive_partnership_s_corp_income": [100_000],
    }
    standalone = _calculate(
        reform_variables,
        _parameters(material_participation_only=False),
        inputs,
        outputs=["owners_draw_active_income"],
    )
    # Passive-inclusive treatment remains available for the standalone draw.
    np.testing.assert_array_equal(standalone["owners_draw_active_income"], [200_000])
    values = {
        "partnership_s_corp_income": 200_000,
        "passive_partnership_s_corp_income": 100_000,
        "partnership_self_employment_net_earnings": 0,
        "s770_passive_se_income": 0,
        "s770_draw_gross": 50_000,
        "s770_draw_oasdi_base": 0,
        "s770_draw_hi_in_effect": True,
        "s770_active_fica_income": 0,
        "is_tax_unit_dependent": False,
        "owners_draw_niit_exclusion": 100_000,
    }

    def person(name, instant):
        return np.asarray(values[name])

    person.simulation = SimpleNamespace(
        tax_benefit_system=SimpleNamespace(
            variables={"owners_draw_niit_exclusion": object()} if installed else {}
        )
    )
    tax_unit = SimpleNamespace(members=person, sum=lambda array: array)
    parameters = _parameters(
        material_participation_only=False,
        in_effect=enabled,
        start_year=start_year,
    )
    if installed and enabled and start_year <= PERIOD.start.year:
        with pytest.raises(ValueError, match="validated active/NII allocation"):
            s770_active_business_income.formula(tax_unit, PERIOD, parameters)
    else:
        np.testing.assert_array_equal(
            s770_active_business_income.formula(tax_unit, PERIOD, parameters),
            50_000,
        )
        # Main rejects a nonpositive standard factor even for a manual HI
        # hook. Inactive and absent draws must preserve that error as well.
        invalid_q = _parameters(
            oasdi_rate=1,
            hi_rate=1,
            employer_share=0.5,
            material_participation_only=False,
            in_effect=enabled,
            start_year=start_year,
        )
        if not installed:
            del invalid_q(PERIOD).gov.contrib.ssa.owners_draw
        with pytest.raises(ValueError, match="netting factor must be positive"):
            s770_active_business_income.formula(tax_unit, PERIOD, invalid_q)
