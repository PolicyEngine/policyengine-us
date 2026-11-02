"""Pure COLA algebra and rounding properties required for benefit levers.

Python is needed for generated ledgers, ordering, and Decimal boundaries.
These tests construct no simulations; public-variable policy examples belong
in YAML, with ingress and migration checked by the separate integration tests.
"""

from math import prod

import pytest
from hypothesis import given, settings, strategies as st

from policyengine_us.tools.social_security_benefit_levers import (
    joint_cola_factor,
    projected_cola_rates,
)


@st.composite
def cola_ledgers(draw):
    first_year = draw(st.integers(min_value=1984, max_value=2050))
    count = draw(st.integers(min_value=1, max_value=12))
    rates = draw(
        st.lists(
            st.integers(min_value=0, max_value=1500),
            min_size=count,
            max_size=count,
        )
    )
    changes = draw(
        st.lists(
            st.integers(min_value=-2000, max_value=2000),
            min_size=count,
            max_size=count,
        )
    )
    withholding = draw(st.lists(st.booleans(), min_size=count, max_size=count))
    events = [
        {
            "payment_year": first_year + offset,
            "payment_month": 1,
            "rate": rate / 10000,
            "rounding_rule": 2,
        }
        for offset, rate in enumerate(rates)
    ]
    first_payment = (
        first_year + draw(st.integers(min_value=-2, max_value=count + 1)),
        draw(st.integers(min_value=1, max_value=12)),
    )
    through_year = first_year + draw(st.integers(min_value=-2, max_value=count + 1))
    pp_changes = {
        first_year + offset: change / 100000 for offset, change in enumerate(changes)
    }
    withheld = {first_year + offset: value for offset, value in enumerate(withholding)}
    return events, first_payment, through_year, pp_changes, withheld


@settings(max_examples=100, deadline=None)
@given(cola_ledgers())
def test_joint_factor_is_nonnegative(ledger):
    assert joint_cola_factor(*ledger) >= 0


@settings(max_examples=100, deadline=None)
@given(
    cola_ledgers(),
    st.integers(min_value=-2000, max_value=2000),
    st.integers(min_value=-2000, max_value=2000),
)
def test_joint_factor_is_monotone_in_cola_change(ledger, delta_a, delta_b):
    events, first_payment, through_year, _, withheld = ledger
    lower, upper = sorted((delta_a / 100000, delta_b / 100000))
    lower_changes = {event["payment_year"]: lower for event in events}
    upper_changes = {event["payment_year"]: upper for event in events}
    lower_factor = joint_cola_factor(
        events, first_payment, through_year, lower_changes, withheld
    )
    upper_factor = joint_cola_factor(
        events, first_payment, through_year, upper_changes, withheld
    )
    assert lower_factor <= upper_factor + 1e-12


@settings(max_examples=100, deadline=None)
@given(cola_ledgers())
def test_unexposed_benefit_has_unit_factor(ledger):
    events, _, through_year, pp_changes, withheld = ledger
    after_last_event = (events[-1]["payment_year"] + 1, 1)
    assert (
        joint_cola_factor(events, after_last_event, through_year, pp_changes, withheld)
        == 1
    )


@settings(max_examples=100, deadline=None)
@given(cola_ledgers(), st.integers(min_value=0, max_value=12))
def test_factor_is_one_before_change_start(ledger, start_offset):
    events, first_payment, _, pp_changes, _ = ledger
    start_year = events[0]["payment_year"] + start_offset
    future_changes = {
        year: change for year, change in pp_changes.items() if year >= start_year
    }
    assert (
        joint_cola_factor(events, first_payment, start_year - 1, future_changes, {})
        == 1
    )


@settings(max_examples=100, deadline=None)
@given(cola_ledgers())
def test_event_factors_multiply_and_event_order_commutes(ledger):
    events, first_payment, through_year, pp_changes, withheld = ledger
    whole = joint_cola_factor(*ledger)
    separate = prod(
        joint_cola_factor([event], first_payment, through_year, pp_changes, withheld)
        for event in events
    )
    reversed_factor = joint_cola_factor(
        list(reversed(events)),
        first_payment,
        through_year,
        pp_changes,
        withheld,
    )
    assert whole == pytest.approx(separate, rel=1e-12)
    assert whole == pytest.approx(reversed_factor, rel=1e-12)


@settings(max_examples=100, deadline=None)
@given(
    cola_ledgers(),
    st.integers(min_value=0, max_value=1000000),
    st.integers(min_value=-1000, max_value=2000),
    st.integers(min_value=0, max_value=1000),
)
def test_independent_factors_commute_and_reported_zero_stays_zero(
    ledger, reported, across_rate_points, payable_points
):
    cola = joint_cola_factor(*ledger)
    across = 1 + across_rate_points / 1000
    payable = payable_points / 1000
    assert across >= 0
    assert payable >= 0
    combined = reported * prod((cola, across, payable))
    assert combined >= 0
    assert combined == pytest.approx((reported * payable) * across * cola, rel=1e-12)
    assert 0 * prod((cola, across, payable)) == 0


def test_projection_uses_high_water_after_decline_and_rounded_zero():
    rates = projected_cola_rates(
        {
            2024: 100,
            2025: 99,
            2026: 100.04,
            2027: 100.05,
            2028: 101.0505,
        }
    )
    assert rates[2025] == 0
    assert rates[2026] == 0
    # 0.05 percent ties round upward to 0.1 percent, rather than to even.
    assert rates[2027] == 0.001
    # Once a positive COLA occurs, its Q3 index becomes the comparison base.
    assert rates[2028] == 0.01


def test_projection_rounds_statutory_rate_instead_of_using_raw_index_ratio():
    rates = projected_cola_rates({2025: 308.729, 2026: 317.265})
    assert rates[2026] == 0.028


@pytest.mark.parametrize("delta", [0.0015, -0.0030])
def test_presets_keep_half_tenth_precision_after_baseline_rounding(delta):
    event = {
        "payment_year": 2027,
        "payment_month": 1,
        "rate": 0.028,
        "rounding_rule": 2,
    }
    factor = joint_cola_factor([event], (2020, 1), 2027, {2027: delta}, {})
    assert factor == pytest.approx((1.028 + delta) / 1.028)


def test_withheld_year_uses_joint_numerator_and_unchanged_denominator():
    event = {
        "payment_year": 2027,
        "payment_month": 1,
        "rate": 0.028,
        "rounding_rule": 2,
    }
    factor = joint_cola_factor([event], (2020, 1), 2027, {2027: 0.0015}, {2027: True})
    assert factor == pytest.approx(1 / 1.028)


def test_changed_cola_is_floored_at_zero():
    event = {
        "payment_year": 2027,
        "payment_month": 1,
        "rate": 0.001,
        "rounding_rule": 2,
    }
    factor = joint_cola_factor([event], (2020, 1), 2027, {2027: -0.0030}, {})
    assert factor == pytest.approx(1 / 1.001)


def test_historical_july_event_respects_first_payment_month():
    event = {
        "payment_year": 1981,
        "payment_month": 7,
        "rate": 0.112,
        "rounding_rule": 1,
    }
    exposed = joint_cola_factor([event], (1981, 7), 1981, {1981: 0.0015}, {})
    assert exposed == pytest.approx(1.1135 / 1.112)
    assert joint_cola_factor([event], (1981, 8), 1981, {1981: 0.0015}, {}) == 1


def test_unsupported_rounding_is_rejected_only_for_exposed_history():
    event = {
        "payment_year": 2027,
        "payment_month": 1,
        "rate": 0.028,
        "rounding_rule": 999,
    }
    with pytest.raises(ValueError, match="rounding"):
        joint_cola_factor([event], (2020, 1), 2027, {}, {})
    assert joint_cola_factor([event], (2028, 1), 2027, {}, {}) == 1


@pytest.mark.parametrize(
    "variable,field,value",
    [
        ("social_security_across_the_board_factor", "rate", -1.01),
        ("social_security_across_the_board_factor", "rate", float("inf")),
        ("social_security_across_the_board_factor", "rate", float("nan")),
        ("social_security_payable_factor", "share", -0.01),
        ("social_security_payable_factor", "share", 1.01),
        ("social_security_payable_factor", "share", float("inf")),
        ("social_security_payable_factor", "share", float("nan")),
    ],
)
def test_invalid_policy_factors_are_rejected(variable, field, value):
    # YAML cannot assert exceptions. Call the authored formula with a minimal
    # parameter view; no additional country model or simulation is built.
    from types import SimpleNamespace
    from policyengine_core.periods import period
    from policyengine_us.system import system

    parameter = SimpleNamespace(**{field: value, "start_year": 2024})
    leaf = "across_the_board" if field == "rate" else "payable"
    tree = SimpleNamespace(
        gov=SimpleNamespace(
            contrib=SimpleNamespace(
                ssa=SimpleNamespace(benefit_levers=SimpleNamespace(**{leaf: parameter}))
            )
        )
    )
    formula = system.variables[variable].get_formula("2024-01-01")
    with pytest.raises(ValueError):
        formula(None, period("2024"), lambda _: tree)


def exposure_parameters(**overrides):
    from policyengine_core.parameters import ParameterNode
    from policyengine_us.system import system

    values = dict(
        start_year=9999,
        effective_year=0,
        effective_month=12,
        end_year=0,
        pp_change=0,
        alternative_rate=-1,
        withholding_enabled=False,
    )
    values.update(overrides)
    cola = {
        name: {"values": value if isinstance(value, dict) else {"0000-01-01": value}}
        for name, value in values.items()
    }
    cola["means_test"] = {"enabled": {"values": {"0000-01-01": False}}}
    params = ParameterNode(
        data={
            "gov": {
                "contrib": {"ssa": {"benefit_levers": {"cola": cola}}},
                "ssa": {
                    "uprating": {
                        "values": {
                            "2026-01-01": 317.265,
                            "2027-01-01": 328.746,
                            "2028-01-01": 332.241,
                        }
                    }
                },
            }
        }
    )
    params.gov.ssa.add_child(
        "cola_history", system.parameters.gov.ssa.cola_history.clone()
    )
    return params


class ExposurePerson:
    ids = ["worker"]

    def __init__(self, age, **inputs):
        self.age = age
        self.inputs = inputs

    def __call__(self, name, year):
        import numpy as np
        from policyengine_us.tools.social_security_benefit_levers import (
            SocialSecurityBenefitSource,
        )

        if name.endswith("_source"):
            return SocialSecurityBenefitSource.encode(np.array(["reported"]))
        if name == "age":
            return np.array([self.age])
        if name.endswith("_worker_id"):
            return np.array([""])
        if name.endswith("_month"):
            return np.array([1])
        value = self.inputs.get(name, 0)
        if isinstance(value, dict):
            value = value.get(int(str(year)[:4]), False)
        return np.array([value])


def test_historical_june_change_exposes_retirement_eligibility_year():
    from policyengine_core.periods import period
    from policyengine_us.tools.social_security_benefit_levers import (
        reported_joint_cola_factor,
    )

    params = exposure_parameters(
        effective_year=1981, effective_month=6, pp_change=0.0015
    )
    factor = reported_joint_cola_factor(
        ExposurePerson(62), period("1981"), params, "retirement"
    )
    assert factor[0] == pytest.approx(1.1135 / 1.112)


def test_prior_withheld_cola_remains_after_withholding_is_disabled():
    from policyengine_core.periods import period
    from policyengine_us.tools.social_security_benefit_levers import (
        reported_joint_cola_factor,
    )

    params = exposure_parameters(
        withholding_enabled={
            "0000-01-01": False,
            "2027-01-01": True,
            "2028-01-01": False,
        }
    )
    person = ExposurePerson(
        70,
        social_security_retirement_first_cola_year=2027,
        social_security_retirement_cola_withheld={2027: True},
    )
    factor = reported_joint_cola_factor(person, period("2028"), params, "retirement")
    assert factor[0] == pytest.approx(1 / 1.036)


def test_mixed_calculated_rows_bypass_population_exposure_validation():
    import numpy as np
    from policyengine_core.periods import period
    from policyengine_us.tools.social_security_benefit_levers import (
        SocialSecurityBenefitSource,
        reported_joint_cola_factor,
    )

    class MixedPerson:
        ids = ["reported", "calculated"]

        def __call__(self, name, year):
            if name.endswith("_source"):
                return SocialSecurityBenefitSource.encode(
                    np.array(["reported", "supplied_pia"])
                )
            if name.endswith("_worker_id"):
                return np.array(["", "irrelevant-missing-record"])
            if name.endswith("_month"):
                return np.array([1, 13])
            if name.endswith("_first_cola_year"):
                return np.array([2027, 2027])
            if name == "age":
                return np.array([70, 70])
            return np.array([0, 0])

    params = exposure_parameters(start_year=2027, pp_change=0.0015)
    factors = reported_joint_cola_factor(
        MixedPerson(), period("2027"), params, "retirement"
    )
    np.testing.assert_allclose(factors, [1.0375 / 1.036, 1])
