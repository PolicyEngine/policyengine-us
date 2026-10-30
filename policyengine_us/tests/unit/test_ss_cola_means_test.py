"""COLA means-test acceptance, historical inputs and joint-event invariants.

Synthetic thresholds are examples, never contributed package settings. The
payment-year convention means December2026's COLA first changes January2027.
Country systems are reused; pure schedule properties do not clone the model.
"""

from copy import deepcopy
from decimal import Decimal, ROUND_DOWN
from math import prod

import numpy as np
import pytest
from hypothesis import given, settings, strategies as st
from policyengine_core.parameters import ParameterNode

from policyengine_us import Simulation
from policyengine_us.reforms.ssa.cola_means_test import a9
from policyengine_us.tools.social_security.means_test import (
    chained_cola_rates,
    indexed_threshold,
)
from policyengine_us.tools.social_security_benefit_levers import (
    cola_event_multiplier,
    cola_events,
    joint_cola_factor,
)


MEANS_TEST = "gov.contrib.ssa.benefit_levers.cola.means_test"
COMPONENTS = ("retirement", "disability", "survivors", "dependents")


def _reform(**overrides):
    values = {
        "enabled": True,
        "scope": "first_eligible_cohorts",
        "first_eligible_year": 2026,
        "effective_year": 2026,
        "effective_month": 12,
        "below_threshold_cola_index": "statutory",
        "thresholds.base_year": 2026,
        "thresholds.single": 100_000,
        "thresholds.joint": 200_000,
        "thresholds.index_lag": 1,
        "thresholds.rounding": 100,
    }
    values.update(overrides)
    enum_values = {
        "scope": {"first_eligible_cohorts": 0, "all_beneficiaries": 1},
        "below_threshold_cola_index": {"statutory": 0, "chained_cpi_u": 1},
        "pre_receipt_cola_index": {
            "follow_below_threshold": -1,
            "statutory": 0,
            "chained_cpi_u": 1,
        },
        "income_sensitivity": {
            "prior_year": 0,
            "never_withheld": 1,
            "always_withheld": 2,
        },
    }
    for name, value in tuple(values.items()):
        mapping = (
            {"single": 0, "joint": 1}
            if name.startswith("filing_groups.")
            else enum_values.get(name, {})
        )
        values[name] = mapping.get(value, value)
    return {
        f"{MEANS_TEST}.{name}": {"2020-01-01": value} for name, value in values.items()
    }


def _record(eligibility=2026, **overrides):
    record = {"age": {2027: 63}, "is_tax_unit_head": True}
    for component in COMPONENTS:
        prefix = f"social_security_{component}"
        record[f"{prefix}_reported"] = {2027: 12_000}
        record[f"{prefix}_worker_eligibility_year"] = eligibility
        record[f"{prefix}_first_cola_year"] = 2027
    record.update(overrides)
    return record


def _situation(records=None, incomes=None, statuses=None):
    records = records or {"worker": _record()}
    incomes = incomes or {}
    statuses = statuses or {}
    situation = {
        "people": deepcopy(records),
        "tax_units": {},
        "families": {},
        "spm_units": {},
        "households": {},
    }
    for person in records:
        unit = {"members": [person]}
        if person in incomes:
            income = incomes[person]
            unit["social_security_cola_means_test_magi"] = (
                income if isinstance(income, dict) else {2026: income}
            )
        if person in statuses:
            status = statuses[person]
            unit["filing_status"] = (
                status if isinstance(status, dict) else {2026: status}
            )
        unit["tax_unit_itemizes"] = {year: False for year in range(2025, 2031)}
        situation["tax_units"][person] = unit
        for entity in ("families", "spm_units", "households"):
            situation[entity][person] = {"members": [person]}
    return situation


def _simulation(situation, reform=None, system=None):
    return Simulation(
        situation=deepcopy(situation),
        tax_benefit_system=(system or Simulation.default_tax_benefit_system_instance),
        **({"reform": reform} if reform is not None else {}),
    )


@pytest.fixture(scope="module")
def means_test_system():
    return _simulation(_situation(), _reform()).tax_benefit_system


@pytest.fixture(scope="module")
def disabled_means_test_system():
    return _simulation(
        _situation(),
        _reform(
            enabled=False,
            scope="all_beneficiaries",
            below_threshold_cola_index="chained_cpi_u",
        ),
    ).tax_benefit_system


def _event(year, rate):
    return {
        "payment_year": year,
        "payment_month": 1,
        "rate": rate,
        "rounding_rule": 2,
    }


def test_neutral_defaults_require_explicit_threshold_package():
    p = Simulation.default_tax_benefit_system_instance.parameters("2027-01-01")
    means_test = p.gov.contrib.ssa.benefit_levers.cola.means_test
    assert not means_test.enabled
    assert means_test.scope == 0
    assert means_test.first_eligible_year == 2026
    assert means_test.below_threshold_cola_index == 0
    assert means_test.pre_receipt_cola_index == -1
    assert means_test.thresholds.single == means_test.thresholds.joint == 0


@pytest.mark.parametrize(
    "amount,base,current,rounding,expected",
    [
        (85_000, 100, 120, 100, 102_000),
        (170_000, 100, 120, 100, 204_000),
        (85_000, 100, 138, 100, 117_300),
        (170_000, 100, 138, 100, 234_600),
        (100, 100, 100.5, 1, 101),
        (100_000, 100, 100.05, 100, 100_100),
    ],
)
def test_cpi_u_threshold_indexing_and_decimal_half_up(
    amount, base, current, rounding, expected
):
    assert indexed_threshold(amount, base, current, rounding) == expected


def _chained_parameters(levels):
    return ParameterNode(
        data={
            "gov": {
                "bls": {
                    "cpi": {
                        "c_cpi_u": {
                            "values": {
                                f"{year}-07-01": value for year, value in levels.items()
                            }
                        }
                    }
                }
            }
        }
    )


def test_chained_index_uses_q3_high_water_and_half_up():
    parameters = _chained_parameters({2000: 100, 2001: 99, 2002: 100.04, 2003: 101})
    rates = chained_cola_rates(parameters, 2004)
    assert [rates[year] for year in (2002, 2003, 2004)] == [0, 0, 0.01]
    half_up = chained_cola_rates(_chained_parameters({2000: 100, 2001: 100.05}), 2002)
    assert half_up[2002] == 0.001


def test_chained_index_reads_all_three_q3_months():
    parameters = _chained_parameters({2000: 100, 2001: 101})
    index = parameters.gov.bls.cpi.c_cpi_u
    index.update(start="2001-08-01", value=102)
    index.update(start="2001-09-01", value=103)
    # Q3 means100 and102 give2%; September alone would give3%.
    assert chained_cola_rates(parameters, 2002)[2002] == 0.02


@pytest.mark.parametrize("index", ["statutory", "chained_cpi_u"])
@pytest.mark.parametrize("scope", ["first_eligible_cohorts", "all_beneficiaries"])
def test_each_index_scope_combination_and_first_eligible_boundary(index, scope):
    records = {
        "old_low": _record(2025),
        "old_high": _record(2025),
        "new_low": _record(2026),
        "new_high": _record(2026),
    }
    incomes = {name: (200_000 if name.endswith("high") else 0) for name in records}
    simulation = _simulation(
        _situation(records, incomes),
        _reform(below_threshold_cola_index=index, scope=scope),
    )
    parameters = simulation.tax_benefit_system.parameters
    baseline_rate = next(
        event["rate"]
        for event in cola_events(parameters, 2027)
        if event["payment_year"] == 2027
    )
    below_rate = (
        baseline_rate
        if index == "statutory"
        else chained_cola_rates(parameters, 2027)[2027]
    )
    below_factor = (1 + below_rate) / (1 + baseline_rate)
    withheld_factor = 1 / (1 + baseline_rate)
    expected_withholding = (
        [False, False, False, True]
        if scope == "first_eligible_cohorts"
        else [False, True, False, True]
    )
    expected_factors = (
        [1, 1, below_factor, withheld_factor]
        if scope == "first_eligible_cohorts"
        else [below_factor, withheld_factor, below_factor, withheld_factor]
    )
    for component in COMPONENTS:
        np.testing.assert_array_equal(
            simulation.calculate(
                f"social_security_{component}_cola_means_test_withheld", 2027
            ),
            expected_withholding,
        )
        np.testing.assert_allclose(
            simulation.calculate(
                f"social_security_{component}_joint_cola_factor", 2027
            ),
            expected_factors,
        )


def test_equality_is_paid_and_each_filing_status_has_an_explicit_group(
    means_test_system,
):
    statuses = ["SINGLE", "HEAD_OF_HOUSEHOLD", "SEPARATE", "JOINT", "SURVIVING_SPOUSE"]
    records = {name: _record() for name in statuses}
    records["equality"] = _record()
    simulation = _simulation(
        _situation(
            records,
            {**{name: 100_001 for name in statuses}, "equality": 100_000},
            {**{name: name for name in statuses}, "equality": "SINGLE"},
        ),
        system=means_test_system,
    )
    np.testing.assert_array_equal(
        simulation.calculate(
            "social_security_retirement_cola_means_test_withheld", 2027
        ),
        [True, True, True, False, False, False],
    )


def test_surviving_spouse_mapping_is_a_parameter():
    simulation = _simulation(
        _situation(
            incomes={"worker": 100_001}, statuses={"worker": "SURVIVING_SPOUSE"}
        ),
        _reform(**{"filing_groups.SURVIVING_SPOUSE": "single"}),
    )
    assert simulation.calculate(
        "social_security_retirement_cola_means_test_withheld", 2027
    )[0]


def test_static_cohort_proxy_is_reconstructed_within_each_score_year(means_test_system):
    record = _record(age={2026: 70, 2035: 70})
    for component in COMPONENTS:
        record.pop(f"social_security_{component}_worker_eligibility_year")
        record.pop(f"social_security_{component}_first_cola_year")
    simulation = _simulation(
        _situation(
            {"worker": record},
            {"worker": {year: 1_000_000 for year in range(2025, 2035)}},
        ),
        system=means_test_system,
    )
    # Fixed-age static cross-sections infer E2018 in2026 and E2027 in2035.
    # Within the2035 score, all exposed events use E2027 rather than re-aging
    # the row separately at each historical payment event.
    assert (
        simulation.calculate("social_security_retirement_joint_cola_factor", 2026)[0]
        == 1
    )
    events = cola_events(simulation.tax_benefit_system.parameters, 2035)
    expected = prod(
        1 / (1 + event["rate"]) for event in events if event["payment_year"] >= 2028
    )
    assert simulation.calculate("social_security_retirement_joint_cola_factor", 2035)[
        0
    ] == pytest.approx(expected)


def test_only_prior_tax_year_income_and_filing_status_make_the_decision(
    means_test_system,
):
    simulation = _simulation(
        _situation(
            incomes={"worker": {2026: 150_000, 2027: 0}},
            statuses={"worker": {2026: "SINGLE", 2027: "JOINT"}},
        ),
        system=means_test_system,
    )
    assert simulation.calculate(
        "social_security_retirement_cola_means_test_withheld", 2027
    )[0]


def test_magi_excludes_social_security_and_retains_irmaa_addbacks():
    situation = _situation()
    situation["people"]["worker"].update(
        tax_exempt_interest_income={2026: 2_000},
        us_bonds_for_higher_ed={2026: 300},
    )
    situation["people"]["spouse"] = {
        "age": {2026: 63},
        "is_tax_unit_spouse": True,
        "tax_exempt_interest_income": {2026: 500},
    }
    situation["people"]["dependent"] = {
        "age": {2026: 19},
        "is_tax_unit_dependent": True,
        "tax_exempt_interest_income": {2026: 100_000},
        # The parent's education-bond exclusion can be recorded on the child.
        "us_bonds_for_higher_ed": {2026: 700},
    }
    members = list(situation["people"])
    unit = situation["tax_units"]["worker"]
    unit.update(
        members=members,
        adjusted_gross_income={2026: 100_000},
        tax_unit_taxable_social_security={2026: 10_000},
        section_911_excluded_income={2026: 4_000},
        specified_possession_income={2026: 5_000},
        puerto_rico_income={2026: 6_000},
    )
    for entity in ("families", "spm_units", "households"):
        situation[entity]["worker"]["members"] = members
    situation["marital_units"] = {
        "couple": {"members": ["worker", "spouse"]},
        "dependent": {"members": ["dependent"]},
    }
    simulation = _simulation(situation)
    # 100000-10000+2500+1000+4000+5000+6000; the dependent's own interest
    # is on a separate return and never enters the parents' income measure.
    assert (
        simulation.calculate("social_security_cola_means_test_magi", 2026)[0] == 108_500
    )


def test_supplied_income_history_overrides_the_extended_record_proxy(
    means_test_system,
):
    # Core stores one complete array per input/period. A partially supplied
    # TaxUnit input would fill other units with its default zero, so compare
    # the supplied-history and calculated-income situations independently.
    decisions = []
    for histories in ({"worker": {2026: 90_000}}, {}):
        simulation = _simulation(
            _situation(
                {"worker": _record(employment_income={2026: 200_000})}, histories
            ),
            system=means_test_system,
        )
        decisions.append(
            bool(
                simulation.calculate(
                    "social_security_retirement_cola_means_test_withheld", 2027
                )[0]
            )
        )
    assert decisions == [False, True]


@pytest.mark.parametrize(
    "sensitivity,income,expected",
    [("never_withheld", 1_000_000, False), ("always_withheld", 0, True)],
)
def test_static_cross_section_proxy_sensitivities(sensitivity, income, expected):
    simulation = _simulation(
        _situation(incomes={"worker": income}),
        _reform(income_sensitivity=sensitivity),
    )
    assert (
        bool(
            simulation.calculate(
                "social_security_retirement_cola_means_test_withheld", 2027
            )[0]
        )
        is expected
    )


def test_explicit_withholding_input_remains_a_final_decision(means_test_system):
    simulation = _simulation(
        _situation(
            {"worker": _record(social_security_retirement_cola_override={2027: 1})},
            {"worker": 0},
        ),
        system=means_test_system,
    )
    assert simulation.calculate(
        "social_security_retirement_cola_means_test_withheld", 2027
    )[0]
    assert simulation.calculate("social_security_retirement", 2027)[0] < 12_000


def test_disabled_means_test_preserves_manual_input_carry_over():
    simulation = _simulation(
        _situation(
            {"worker": _record(social_security_retirement_cola_withheld={2026: True})}
        )
    )
    assert simulation.calculate(
        "social_security_retirement_cola_means_test_withheld", 2027
    )[0]


def test_zero_cola_and_downward_adjustment_floor():
    assert cola_event_multiplier(0, 0.0015, True) == 1
    assert cola_event_multiplier(0, -0.003, False) == 1
    assert cola_event_multiplier(0.002, -0.003, False) == pytest.approx(1 / 1.002)
    assert cola_event_multiplier(0.002, -0.003, True) == pytest.approx(1 / 1.002)


def test_two_year_cpi_e_and_withholding_use_one_joint_numerator():
    events = [_event(2029, 0.03), _event(2030, 0.04)]
    factor = joint_cola_factor(
        events, (2029, 1), 2030, {2029: 0.0015, 2030: 0.0015}, {2029: True}
    )
    # Baseline1000*1.03*1.04=1071.20. First COLA is withheld, so the
    # reformed path is1000*1*1.0415=1041.50, rather than retaining CPI-E.
    assert factor == pytest.approx(1041.50 / 1071.20)
    assert 1071.20 * factor == pytest.approx(1041.50)
    separate_factors = (
        joint_cola_factor(events, (2029, 1), 2030, {2029: 0.0015, 2030: 0.0015}, {})
        / 1.03
    )
    assert factor != pytest.approx(separate_factors)


@pytest.mark.parametrize(
    "below,pre_receipt,use_chained_before_receipt",
    [
        ("chained_cpi_u", "follow_below_threshold", True),
        ("chained_cpi_u", "statutory", False),
        ("statutory", "chained_cpi_u", True),
    ],
)
def test_pre_receipt_index_is_separate_and_has_no_income_withholding(
    below, pre_receipt, use_chained_before_receipt
):
    simulation = _simulation(
        _situation(
            {
                "worker": _record(
                    social_security_retirement_entitlement_year=2029,
                    social_security_retirement_entitlement_month=12,
                    social_security_retirement_reported={2030: 12_000},
                )
            },
            {"worker": {year: 1_000_000 for year in range(2026, 2030)}},
        ),
        _reform(
            below_threshold_cola_index=below,
            pre_receipt_cola_index=pre_receipt,
        ),
    )
    parameters = simulation.tax_benefit_system.parameters
    chained = chained_cola_rates(parameters, 2030)
    baseline = {
        event["payment_year"]: event["rate"] for event in cola_events(parameters, 2030)
    }
    expected = prod(
        (1 + chained[year]) / (1 + baseline[year]) if use_chained_before_receipt else 1
        for year in (2027, 2028, 2029)
    ) / (1 + baseline[2030])
    assert not simulation.calculate(
        "social_security_retirement_cola_means_test_withheld", 2029
    )[0]
    assert simulation.calculate(
        "social_security_retirement_cola_means_test_withheld", 2030
    )[0]
    assert simulation.calculate("social_security_retirement_joint_cola_factor", 2030)[
        0
    ] == pytest.approx(expected)


def _calculator_record(name):
    record = _record()
    record.update(
        social_security_retirement_source="supplied_pia",
        ss_calculator_source="pia",
        ss_calculator_worker_id=name,
        ss_calculator_birth_date="1964-01-02",
        ss_calculator_entitlement_month="2026-01",
        ss_calculator_eligibility_year=2026,
        ss_calculator_supplied_pia=1000,
        ss_calculator_claiming_factor="1",
        ss_calculator_insured=True,
        ss_calculator_no_special_monthly_test=True,
        ss_calculator_no_prior_withholding_adjustment=True,
        ss_calculator_earnings_test_no_trigger=True,
    )
    return record


@pytest.mark.parametrize("calculator", [False, True])
def test_partial_paid_override_preserves_other_persons_automatic_decision(
    means_test_system, calculator
):
    # Core stores a complete array for each supplied variable/year. The -1
    # default must keep A automatic when only B supplies a paid decision.
    records = {
        name: _calculator_record(name) if calculator else _record()
        for name in ("A", "B")
    }
    override = (
        "ss_calculator_cola_override"
        if calculator
        else "social_security_retirement_cola_override"
    )
    records["B"][override] = {2027: 0}
    simulation = _simulation(
        _situation(records, {"A": 1_000_000, "B": 1_000_000}),
        system=means_test_system,
    )
    variable, period, expected = (
        ("ss_calculated_payment", "2027-01", [1000, 1036])
        if calculator
        else ("social_security_retirement", 2027, [11583.01, 12000])
    )
    np.testing.assert_allclose(
        simulation.calculate(variable, period), expected, rtol=0, atol=0.01
    )


def test_calculator_override_precedence_and_exact_year_expiry(means_test_system):
    # Exercise Core's separate input arrays: component decisions reach the
    # calculator, and its own non-auto input takes precedence for that person.
    records = {name: _calculator_record(name) for name in ("A", "B", "C")}
    records["A"]["social_security_retirement_cola_override"] = {2027: 0}
    records["B"].update(
        social_security_retirement_cola_override={2027: 1},
        ss_calculator_cola_override={2027: 0},
    )
    records["C"].update(
        social_security_retirement_cola_override={2027: 0},
        ss_calculator_cola_override={2027: 1},
    )
    simulation = _simulation(
        _situation(
            records,
            {name: {2026: 1_000_000, 2027: 1_000_000} for name in records},
        ),
        system=means_test_system,
    )
    np.testing.assert_array_equal(
        simulation.calculate("ss_calculated_payment", "2027-01"),
        [1036, 1036, 1000],
    )
    # All overrides expire after 2027. High prior-year income withholds the
    # next COLA for all three; paid 2027 COLAs remain in A and B's check levels.
    np.testing.assert_array_equal(
        simulation.calculate("ss_calculated_payment", "2028-01"),
        [1036, 1036, 1000],
    )


def test_disabled_means_test_calculator_ignores_component_withholding():
    # Literal checks captured from main 37dd5099ed7fad694419fb652eb3ba7bd14122ba.
    # A5's calculator channel is exact-year ss_calculator_withhold_cola only.
    record = _calculator_record("worker")
    record["ss_calculator_supplied_pia"] = 1000.1
    record["social_security_retirement_cola_withheld"] = {2027: True}
    simulation = _simulation(
        _situation({"worker": record}),
        reform={
            "gov.contrib.ssa.benefit_levers.cola.withholding_enabled": {
                "2020-01-01": True
            }
        },
    )
    for year, expected in zip(range(2027, 2031), (1036, 1062, 1086, 1111)):
        assert (
            simulation.calculate("ss_calculated_payment", f"{year}-01")[0] == expected
        )


def test_disabled_means_test_calculator_manual_decision_is_exact_year():
    records = {name: _calculator_record(name) for name in ("A", "B")}
    for record in records.values():
        record["ss_calculator_supplied_pia"] = 1000.1
    records["B"]["ss_calculator_withhold_cola"] = {2027: True}
    # New E3 inputs have no effect when E3 is off.
    records["A"]["ss_calculator_cola_override"] = {2027: 1}
    simulation = _simulation(
        _situation(records),
        reform={
            "gov.contrib.ssa.benefit_levers.cola.withholding_enabled": {
                "2020-01-01": True
            }
        },
    )
    np.testing.assert_array_equal(
        simulation.calculate("ss_calculated_payment", "2027-01"), [1036, 1000]
    )
    np.testing.assert_array_equal(
        simulation.calculate("ss_calculated_payment", "2028-01"), [1062, 1025]
    )


@pytest.mark.parametrize("other_payment_factors", [False, True])
def test_calculated_source_applies_withholding_and_cpi_e_once(other_payment_factors):
    reform = _reform()
    reform.update(
        {
            "gov.contrib.ssa.benefit_levers.cola.start_year": {"2020-01-01": 2027},
            "gov.contrib.ssa.benefit_levers.cola.pp_change": {"2020-01-01": 0.0015},
        }
    )
    if other_payment_factors:
        reform.update(
            {
                "gov.contrib.ssa.benefit_levers.across_the_board.start_year": {
                    "2020-01-01": 2027
                },
                "gov.contrib.ssa.benefit_levers.across_the_board.rate": {
                    "2020-01-01": 0.08
                },
                "gov.contrib.ssa.benefit_levers.payable.share": {"2020-01-01": 0.8},
            }
        )
    simulation = _simulation(
        _situation(
            {name: _calculator_record(name) for name in ("paid", "withheld")},
            {"paid": {2026: 0}, "withheld": {2026: 1_000_000}},
        ),
        reform,
    )
    # Baseline3.6%+.15pp produces PIA1037.5 ->1037 checks. Above the
    # line, the single joint numerator produces PIA1000 ->1000 checks.
    np.testing.assert_array_equal(
        simulation.calculate("ss_calculated_payment", "2027-01"),
        [896, 864] if other_payment_factors else [1037, 1000],
    )
    np.testing.assert_array_equal(
        simulation.calculate("social_security_retirement_joint_cola_factor", 2027),
        [1, 1],
    )
    np.testing.assert_array_equal(
        simulation.calculate("social_security_retirement", 2027),
        simulation.calculate("ss_calculated_retirement", 2027),
    )
    np.testing.assert_array_equal(
        simulation.calculate("social_security_retirement", 2027),
        [10_752, 10_368] if other_payment_factors else [12_444, 12_000],
    )


def test_midyear_first_check_retains_the_pre_receipt_index():
    records = {
        "reported": _record(),
        "calculated": _calculator_record("calculated"),
    }
    for record in records.values():
        record.update(
            social_security_retirement_entitlement_year=2028,
            social_security_retirement_entitlement_month=6,
        )
    records["calculated"]["ss_calculator_entitlement_month"] = "2028-06"
    simulation = _simulation(
        _situation(
            records,
            {name: {year: 1_000_000 for year in range(2026, 2029)} for name in records},
        ),
        _reform(pre_receipt_cola_index="chained_cpi_u"),
    )
    # First receipt is July2028. January2028's COLA therefore uses the
    # pre-receipt index regardless of income; January2029 is income-tested.
    np.testing.assert_array_equal(
        simulation.calculate(
            "social_security_retirement_cola_means_test_withheld", 2028
        ),
        [False, False],
    )
    np.testing.assert_array_equal(
        simulation.calculate(
            "social_security_retirement_cola_means_test_withheld", 2029
        ),
        [True, True],
    )
    parameters = simulation.tax_benefit_system.parameters
    chained = chained_cola_rates(parameters, 2028)
    baseline = {
        event["payment_year"]: event["rate"] for event in cola_events(parameters, 2028)
    }
    expected = prod((1 + chained[year]) / (1 + baseline[year]) for year in (2027, 2028))
    assert simulation.calculate("social_security_retirement_joint_cola_factor", 2028)[
        0
    ] == pytest.approx(expected)
    pia = Decimal(1000)
    for year in (2027, 2028):
        pia = (pia * (1 + Decimal(str(chained[year])))).quantize(
            Decimal("0.1"), rounding=ROUND_DOWN
        )
    assert simulation.calculate("ss_calculated_payment", "2028-07")[1] == int(pia)


def test_named_withholding_uses_selected_calculator_cohort_and_receipt(
    means_test_system, disabled_means_test_system
):
    records = {}
    for name, birth, eligibility in (
        ("old", "1955-01-02", 2017),
        ("new", "1964-01-02", 2026),
    ):
        # Only calculator dates identify these records; ordinary population
        # age, worker-cohort and entitlement inputs are deliberately absent.
        records[name] = {
            field: value
            for field, value in _calculator_record(name).items()
            if field.startswith("ss_calculator_")
            or field in ("social_security_retirement_source", "is_tax_unit_head")
        }
        records[name].update(
            ss_calculator_birth_date=birth,
            ss_calculator_eligibility_year=eligibility,
            ss_calculator_entitlement_month="2028-06",
        )
    situation = _situation(
        records,
        {name: {year: 1_000_000 for year in range(2026, 2029)} for name in records},
    )
    simulation = _simulation(situation, system=means_test_system)
    baseline = _simulation(situation, system=disabled_means_test_system)
    np.testing.assert_array_equal(
        simulation.calculate(
            "social_security_retirement_cola_means_test_withheld", 2028
        ),
        [False, False],
    )
    np.testing.assert_array_equal(
        simulation.calculate(
            "social_security_retirement_cola_means_test_withheld", 2029
        ),
        [False, True],
    )
    np.testing.assert_array_equal(
        simulation.calculate("ss_calculated_payment", "2028-07"),
        baseline.calculate("ss_calculated_payment", "2028-07"),
    )
    payments = simulation.calculate("ss_calculated_payment", "2029-01")
    baseline_payments = baseline.calculate("ss_calculated_payment", "2029-01")
    assert payments[0] == baseline_payments[0]
    assert payments[1] < baseline_payments[1]


def test_a9_preset_reproduces_captured_description():
    # Literal line boundaries pin the model's projection path independently
    # of indexed_threshold's implementation. Equality is paid in both groups.
    names = (
        "below",
        "above",
        "single_equal",
        "single_above",
        "joint_equal",
        "joint_above",
    )
    simulation = _simulation(
        _situation(
            {
                name: _record(
                    2025,
                    age={2028: 70, 2029: 70},
                    social_security_retirement_first_cola_year=2029,
                )
                for name in names
            },
            {
                "below": {2027: 0, 2028: 0},
                "above": {2027: 1_000_000, 2028: 1_000_000},
                "single_equal": {2028: 117_800},
                "single_above": {2028: 117_801},
                "joint_equal": {2028: 235_700},
                "joint_above": {2028: 235_701},
            },
            {
                "single_equal": {2028: "SINGLE"},
                "single_above": {2028: "SINGLE"},
                "joint_equal": {2028: "JOINT"},
                "joint_above": {2028: "JOINT"},
            },
        ),
        a9,
    )
    p = simulation.tax_benefit_system.parameters("2029-01-01")
    means_test = p.gov.contrib.ssa.benefit_levers.cola.means_test
    assert means_test.enabled
    assert means_test.scope == 1
    assert means_test.effective_year == 2028
    assert means_test.effective_month == 12
    assert means_test.below_threshold_cola_index == 1
    assert means_test.pre_receipt_cola_index == 1
    assert means_test.thresholds.base_year == 2018
    assert means_test.thresholds.single == 85_000
    assert means_test.thresholds.joint == 170_000
    parameters = simulation.tax_benefit_system.parameters
    index = parameters.gov.bls.cpi.cpi_u
    assert index("2026-12-01") == 332.568  # Latest BLS value: June 2026.
    assert index("2028-12-01") == 348.3  # CBO value authored February 2028.
    np.testing.assert_array_equal(
        simulation.calculate(
            "social_security_retirement_cola_means_test_withheld", 2028
        ),
        [False] * len(names),
    )
    np.testing.assert_array_equal(
        simulation.calculate(
            "social_security_retirement_cola_means_test_withheld", 2029
        ),
        [False, True, False, True, False, True],
    )
    baseline = next(
        event["rate"]
        for event in cola_events(parameters, 2029)
        if event["payment_year"] == 2029
    )
    chained = chained_cola_rates(parameters, 2029)[2029]
    np.testing.assert_allclose(
        simulation.calculate("social_security_retirement_joint_cola_factor", 2029),
        [(1 + chained) / (1 + baseline), 1 / (1 + baseline)] * 3,
    )


def test_disabled_later_policy_retains_an_earlier_withheld_event():
    reform = _reform()
    reform[f"{MEANS_TEST}.enabled"]["2028-01-01"] = False
    simulation = _simulation(
        _situation(incomes={"worker": {2026: 1_000_000, 2027: 1_000_000}}), reform
    )
    baseline = next(
        event["rate"]
        for event in cola_events(simulation.tax_benefit_system.parameters, 2027)
        if event["payment_year"] == 2027
    )
    assert not simulation.calculate(
        "social_security_retirement_cola_means_test_withheld", 2028
    )[0]
    assert simulation.calculate("social_security_retirement_joint_cola_factor", 2028)[
        0
    ] == pytest.approx(1 / (1 + baseline))


@pytest.mark.parametrize("calculated", [False, True], ids=["reported", "calculator"])
def test_multi_year_income_dependency_graph_is_acyclic(means_test_system, calculated):
    years = range(2025, 2031)
    record = _record(
        age={year: year - 1964 for year in years},
        employment_income={year: 120_000 for year in years},
        traditional_ira_contributions={year: 1_000 for year in years},
        social_security_retirement_reported={year: 12_000 for year in years},
    )
    if calculated:
        record.update(_calculator_record("worker"))
        record["age"] = {year: year - 1964 for year in years}
        record["employment_income"] = {year: 10_000 for year in years}
        record["taxable_interest_income"] = {year: 120_000 for year in years}
    simulation = _simulation(_situation({"worker": record}), system=means_test_system)
    simulation.trace = True
    for year in (2028, 2029, 2030):
        benefit = simulation.calculate("social_security_retirement", year)
        assert np.isfinite(benefit).all()
        assert (benefit > 0).all()
    edges = {}

    def key(node):
        return node.name, str(node.period), getattr(node, "branch_name", None)

    def visit(node):
        parent = key(node)
        edges.setdefault(parent, set())
        for child in node.children:
            edges[parent].add(key(child))
            visit(child)

    for tree in simulation.tracer.trees:
        visit(tree)
    active, complete = set(), set()

    def assert_dag(node):
        assert node not in active, f"Dependency cycle at {node}"
        if node in complete:
            return
        active.add(node)
        for child in edges[node]:
            assert_dag(child)
        active.remove(node)
        complete.add(node)

    for node in edges:
        assert_dag(node)
    income_periods = {
        int(period[:4])
        for name, period, _ in edges
        if name == "social_security_cola_means_test_magi"
    }
    assert {2027, 2028, 2029} <= income_periods
    income_edges = []
    for parent, children in edges.items():
        if parent[0] != "social_security_cola_means_test_withheld":
            continue
        for child in children:
            if child[0] == "social_security_cola_means_test_magi":
                income_edges.append((parent, child))
                assert int(child[1][:4]) == int(parent[1][:4]) - 1
    assert income_edges, "The graph must exercise the actual prior-year income read"


@settings(max_examples=12, deadline=None)
@given(lower=st.integers(0, 250_000), increase=st.integers(0, 250_000))
def test_property_withholding_is_monotone_in_income(means_test_system, lower, increase):
    simulation = _simulation(
        _situation(
            {"lower": _record(), "higher": _record()},
            {"lower": lower, "higher": lower + increase},
        ),
        system=means_test_system,
    )
    decisions = simulation.calculate(
        "social_security_retirement_cola_means_test_withheld", 2027
    )
    assert int(decisions[0]) <= int(decisions[1])


@settings(max_examples=60, deadline=None)
@given(
    rate=st.integers(0, 100).map(lambda value: value / 1000),
    delta=st.integers(-100, 100).map(lambda value: value / 10000),
)
def test_property_a_withheld_year_never_raises_the_benefit(rate, delta):
    withheld = float(cola_event_multiplier(rate, delta, True))
    paid = float(cola_event_multiplier(rate, delta, False))
    assert withheld <= 1
    assert withheld <= paid


@pytest.mark.parametrize(
    "reported,prior_income,expected_components,expected_total",
    [
        (0, 0, [0, 0, 0, 0], 0),
        (12_000, 1_000_000, [12_000, 12_000, 12_000, 12_000], 48_000),
        (100_000, 100_000, [100_000, 100_000, 100_000, 100_000], 400_000),
    ],
)
def test_means_test_off_matches_main_stacked_base_outputs(
    disabled_means_test_system,
    reported,
    prior_income,
    expected_components,
    expected_total,
):
    # Literal outputs from main 37dd5099ed7fad694419fb652eb3ba7bd14122ba.
    # Both public ingress modes must match main, even if both change together.
    record = _record()
    for component in COMPONENTS:
        record[f"social_security_{component}"] = {2027: reported}
        record.pop(f"social_security_{component}_reported")
    situation = _situation({"worker": record}, {"worker": prior_income})
    for system in (None, disabled_means_test_system):
        simulation = _simulation(situation, system=system)
        for component, expected in zip(COMPONENTS, expected_components):
            np.testing.assert_array_equal(
                simulation.calculate(f"social_security_{component}", 2027),
                [expected],
            )
            np.testing.assert_array_equal(
                simulation.calculate(
                    f"social_security_{component}_joint_cola_factor", 2027
                ),
                [1],
            )
        np.testing.assert_array_equal(
            simulation.calculate("social_security", 2027), [expected_total]
        )


def test_a5_only_joint_factor_ignores_calculator_population_dates():
    """Core must not validate irrelevant population dates on calculator rows."""
    calculated = _calculator_record("calculated")
    calculated.update(
        social_security_retirement_entitlement_year=2026,
        social_security_retirement_entitlement_month=13,
    )
    simulation = _simulation(
        _situation(
            {
                "reported": _record(
                    social_security_retirement_cola_withheld={2027: True}
                ),
                "calculated": calculated,
            }
        ),
        {
            "gov.contrib.ssa.benefit_levers.cola.start_year": {"2020-01-01": 2027},
            "gov.contrib.ssa.benefit_levers.cola.withholding_enabled": {
                "2020-01-01": True
            },
        },
    )
    # The calculator's own dates are complete and valid. Its unused population
    # month must not enter the A5 reported-route dependency graph when E3 is off.
    np.testing.assert_allclose(
        simulation.calculate("social_security_retirement_joint_cola_factor", 2027),
        [0.9652509652509652, 1],
    )


def _assert_cached_outputs_equal(reference, actual):
    for population in reference.populations.values():
        for name, holder in population._holders.items():
            for period in holder.get_known_periods():
                expected = holder.get_array(period)
                if expected is not None:
                    np.testing.assert_array_equal(
                        actual.calculate(name, period),
                        expected,
                        err_msg=f"{name} at {period}",
                    )


@pytest.mark.parametrize("calculated", [False, True], ids=["reported", "calculator"])
def test_means_test_off_preserves_downstream_dependency_closure(
    disabled_means_test_system, calculated
):
    # Main 37dd5099ed7fad694419fb652eb3ba7bd14122ba supplies these literals.
    # Main cannot select the calculator as its public source, so the calculated
    # case checks its direct calculator channel against main below and retains
    # public downstream equality as supplemental disabled-policy coverage.
    main_reported = {
        "social_security": 24_000,
        "taxable_social_security": 11_300,
        "adjusted_gross_income": 41_300,
        "income_tax": 2_715,
        "net_investment_income_tax": 0,
        "medicare_part_b_premium": 0,
        "household_net_income": 49_442.6015625,
    }
    record = _calculator_record("worker") if calculated else _record()
    if not calculated:
        # Differential ingress uses legacy public inputs, as M9 requires.
        for component in COMPONENTS:
            record[f"social_security_{component}"] = {2027: 6_000}
            record.pop(f"social_security_{component}_reported")
    record.update(
        employment_income={2027: 10_000},
        taxable_interest_income={2027: 20_000},
    )
    situation = _situation({"worker": record})
    situation["households"]["worker"]["state_code"] = {2027: "NY"}
    baseline = _simulation(situation)
    disabled = _simulation(situation, system=disabled_means_test_system)
    for name in (
        "social_security",
        "taxable_social_security",
        "adjusted_gross_income",
        "income_tax",
        "net_investment_income_tax",
        "medicare_part_b_premium",
        "household_net_income",
    ):
        np.testing.assert_array_equal(
            disabled.calculate(name, 2027), baseline.calculate(name, 2027), err_msg=name
        )
        if not calculated:
            for simulation in (baseline, disabled):
                np.testing.assert_array_equal(
                    simulation.calculate(name, 2027),
                    [main_reported[name]],
                    err_msg=f"main: {name}",
                )
    if calculated:
        for name, period, expected in (
            ("ss_calculated_payment", "2027-01", 1_036),
            ("ss_calculated_annual_entitlement", 2027, 12_457),
            ("ss_calculated_retirement", 2027, 12_432),
        ):
            for simulation in (baseline, disabled):
                np.testing.assert_array_equal(
                    simulation.calculate(name, period),
                    [expected],
                    err_msg=f"main: {name}",
                )
    _assert_cached_outputs_equal(baseline, disabled)
