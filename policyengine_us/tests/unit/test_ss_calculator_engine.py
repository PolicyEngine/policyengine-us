"""Simulation API integration for supplied Social Security records.

The pure services carry the statutory examples/properties. These small model
cases exercise string/object inputs, float32 money restoration, mixed source
vectors, parameter scheduling and annual-versus-monthly output adapters.
Simulation reuses the default runtime system; only parameter reforms detach it.
"""

from copy import deepcopy
from decimal import Decimal, ROUND_FLOOR

import numpy as np
import pytest

from policyengine_us import Simulation
from policyengine_us.tools.social_security.cola import read_parameter_events


def _simulation(*, situation, reform=None):
    """Apply each variant once to the wrapper's isolated runtime clone.

    Passing the processed default system avoids reconstructing the country.
    The US wrapper clones supplied policy when a reform is present, and Core
    then applies the reform. Precloning or preapplying here would duplicate
    that work and keep a second full policy tree alive during construction.
    """
    if reform is None:
        return Simulation(situation=situation)
    return Simulation(
        situation=situation,
        tax_benefit_system=Simulation.default_tax_benefit_system_instance,
        reform=reform,
    )


def _record(worker_id="worker", **overrides):
    values = {
        "ss_calculator_source": "pia",
        "ss_calculator_worker_id": worker_id,
        "ss_calculator_birth_date": "1964-01-02",
        "ss_calculator_entitlement_month": "2026-01",
        "ss_calculator_eligibility_year": 2026,
        "ss_calculator_supplied_pia": 1000,
        "ss_calculator_claiming_factor": "1",
        "ss_calculator_insured": True,
        "ss_calculator_no_special_monthly_test": True,
        "ss_calculator_no_prior_withholding_adjustment": True,
        "ss_calculator_earnings_test_no_trigger": True,
    }
    values.update(overrides)
    return values


def _situation(people):
    members = list(people)
    return {
        "people": people,
        "tax_units": {"tax_unit": {"members": members}},
        "families": {"family": {"members": members}},
        "spm_units": {"spm_unit": {"members": members}},
        "households": {"household": {"members": members}},
    }


def test_source_off_requires_no_record_fields_and_does_not_activate_amount():
    simulation = _simulation(
        situation=_situation(
            {
                "missing": {},
                "unselected": {
                    "ss_calculator_source": "off",
                    "ss_calculator_supplied_aime": 5000,
                    "ss_calculator_supplied_pia": 2000,
                },
            }
        )
    )
    for variable, period in (
        ("ss_calculated_annual_payment", 2026),
        ("ss_calculated_retirement", 2026),
        ("ss_calculated_survivors", 2026),
        ("ss_calculated_benefit", "2026-01"),
        ("ss_calculated_payment", "2026-01"),
    ):
        np.testing.assert_array_equal(simulation.calculate(variable, period), [0, 0])


def test_mixed_aime_pia_sources_preserve_explicit_zero_and_string_inputs():
    people = {}
    for source, amount in (("aime", 0), ("pia", 0), ("aime", 3000), ("pia", 1606.7)):
        name = f"{source}_{amount}"
        people[name] = _record(
            name,
            ss_calculator_source=source,
            ss_calculator_birth_date="1961-01-02",
            ss_calculator_entitlement_month="2023-01",
            ss_calculator_eligibility_year=2023,
            **{"ss_calculator_supplied_" + source: amount},
        )
    simulation = _simulation(situation=_situation(people))
    # SSA Supplement2023 AppendixD's AIME3000->PIA1606.70 also exercises
    # restoration of the supplied float32 PIA to its original dime value.
    np.testing.assert_allclose(
        simulation.calculate("ss_calculated_eligibility_pia", "2023-01"),
        [0, 0, 1606.7, 1606.7],
        atol=0.0001,
    )
    np.testing.assert_array_equal(
        simulation.calculate("ss_calculated_payment", "2023-01"), [0, 0, 0, 0]
    )
    np.testing.assert_array_equal(
        simulation.calculate("ss_calculated_payment", "2023-02"), [0, 0, 1606, 1606]
    )
    np.testing.assert_array_equal(
        simulation.calculate("ss_calculated_retirement", 2023),
        [0, 0, 1606 * 11, 1606 * 11],
    )


@pytest.mark.parametrize("source", ["aime", "pia"])
def test_selected_source_requires_an_amount_distinct_from_supplied_zero(source):
    record = _record(ss_calculator_source=source)
    record.pop("ss_calculator_supplied_" + source, None)
    simulation = _simulation(situation=_situation({"worker": record}))
    with pytest.raises(ValueError, match="Supplied (AIME|eligibility PIA) must"):
        simulation.calculate("ss_calculated_payment", "2026-02")


def test_fractional_aime_reaches_service_validation_without_input_truncation():
    simulation = _simulation(
        situation=_situation(
            {
                "worker": _record(
                    ss_calculator_source="aime",
                    ss_calculator_supplied_aime=3000.5,
                )
            }
        )
    )
    with pytest.raises(ValueError, match="whole monthly dollar"):
        simulation.calculate("ss_calculated_payment", "2026-02")


def test_couple_uses_distinct_own_records_and_keeps_public_inputs_independent():
    people = {
        "first": _record(
            "first-worker",
            ss_calculator_supplied_pia=1000.1,
            ss_calculator_entitlement_month="2026-07",
            social_security_retirement={2026: 9000},
        ),
        "second": _record(
            "second-worker",
            ss_calculator_supplied_pia=2000.2,
            ss_calculator_entitlement_month="2026-07",
            ss_calculator_claiming_factor="0.7",
            social_security_retirement={2026: 12000},
        ),
    }
    situation = _situation(people)
    situation["marital_units"] = {"couple": {"members": list(people)}}
    simulation = _simulation(situation=situation)
    np.testing.assert_allclose(
        simulation.calculate("ss_calculated_eligibility_pia", "2026-07"),
        [1000.1, 2000.2],
        atol=0.0002,
    )
    np.testing.assert_array_equal(
        simulation.calculate("ss_calculated_payment", "2026-08"), [1000, 1400]
    )
    np.testing.assert_array_equal(
        simulation.calculate("ss_calculated_annual_payment", 2026), [5000, 7000]
    )
    np.testing.assert_array_equal(
        simulation.calculate("social_security_retirement", 2026), [9000, 12000]
    )
    np.testing.assert_array_equal(
        simulation.calculate("ss_calculated_survivors", 2026), [0, 0]
    )


def test_exported_couple_checks_compose_with_benefit_tax_thresholds_and_niit():
    # Before the public source-selector integration, the documented one-step
    # wiring exports each own record's checks to the existing public input.
    calculated = _simulation(
        situation=_situation(
            {
                "first": _record("first-worker", ss_calculator_supplied_pia=1000),
                "second": _record("second-worker", ss_calculator_supplied_pia=2000),
            }
        )
    ).calculate("ss_calculated_retirement", 2026)
    np.testing.assert_array_equal(calculated, [11000, 22000])
    people = {
        name: {
            "age": {2026: 62},
            "is_tax_unit_head": {2026: index == 0},
            "is_tax_unit_spouse": {2026: index == 1},
            "social_security_retirement": {2026: float(calculated[index])},
            "taxable_interest_income": {2026: (20000, 10000)[index]},
        }
        for index, name in enumerate(("first", "second"))
    }
    situation = _situation(people)
    situation["tax_units"]["tax_unit"]["filing_status"] = {2026: "JOINT"}
    # This interest-only witness takes the standard deduction in every case.
    # Declare that election so this integration test does not run the model's
    # unrelated state/federal itemization search for each parameter variant.
    situation["tax_units"]["tax_unit"]["tax_unit_itemizes"] = {2026: False}
    situation["marital_units"] = {"couple": {"members": list(people)}}
    benefit_thresholds = {
        "gov.irs.social_security.taxability.threshold.base.main.JOINT": {
            "2026-01-01": 64000
        },
        "gov.irs.social_security.taxability.threshold.adjusted_base.main.JOINT": {
            "2026-01-01": 88000
        },
    }
    investment_threshold = {
        "gov.irs.investment.net_investment_income_tax.threshold.JOINT": {
            "2026-01-01": 35000
        }
    }
    cases = {
        "baseline": ({}, 8125, 38125, 0),
        "benefit_thresholds": (benefit_thresholds, 0, 30000, 0),
        "investment_threshold": (investment_threshold, 8125, 38125, 118.75),
        "combined": ({**benefit_thresholds, **investment_threshold}, 0, 30000, 0),
    }
    income_taxes = {}
    for name, (reform, taxable_benefits, agi, investment_tax) in cases.items():
        simulation = _simulation(situation=deepcopy(situation), reform=reform or None)
        np.testing.assert_array_equal(
            simulation.calculate("social_security_retirement", 2026), calculated
        )
        assert (
            simulation.calculate("tax_unit_social_security_for_taxability", 2026)[0]
            == 33000
        )
        assert (
            simulation.calculate("tax_unit_taxable_social_security", 2026)[0]
            == taxable_benefits
        )
        assert simulation.calculate("adjusted_gross_income", 2026)[0] == agi
        assert simulation.calculate("net_investment_income", 2026)[0] == 30000
        assert simulation.calculate("net_investment_income_tax", 2026)[
            0
        ] == pytest.approx(investment_tax)
        income_taxes[name] = simulation.calculate("income_tax", 2026)[0]
    # Provisional income46500: .85*(46500-44000)+6000=8125 taxable.
    # Lowering existing NIIT's joint threshold gives .038*(38125-35000)
    # =118.75; excluding these benefits from AGI removes that excess too.
    assert income_taxes["benefit_thresholds"] < income_taxes["baseline"]
    assert income_taxes["combined"] < income_taxes["investment_threshold"]


def test_annual_earnings_input_is_allocated_to_entitlement_months_before_checks():
    simulation = _simulation(
        situation=_situation(
            {
                "worker": _record(
                    ss_calculator_earnings_test_no_trigger=False,
                    ss_calculator_annual_earnings={2026: 26480},
                )
            }
        )
    )
    # $2,000 above the 2026 exemption gives a $1,000 annual deduction,
    # allocated to January entitlement (the February check).
    assert (
        simulation.calculate("ss_calculated_earnings_test_reduction", 2026)[0] == 1000
    )
    assert simulation.calculate("ss_calculated_benefit", "2026-01")[0] == 0
    assert simulation.calculate("ss_calculated_payment", "2026-02")[0] == 0
    assert simulation.calculate("ss_calculated_payment", "2026-03")[0] == 1000
    # December entitlement includes the 3.6% COLA first paid January2027;
    # that $36 increase belongs to this entitlement total, not 2026 checks.
    assert simulation.calculate("ss_calculated_annual_entitlement", 2026)[0] == 11036
    assert simulation.calculate("ss_calculated_annual_payment", 2026)[0] == 10000


def test_s770_parameter_schedule_reaches_old_cohort_at_2026():
    simulation = _simulation(
        situation=_situation(
            {
                "worker": _record(
                    ss_calculator_source="aime",
                    ss_calculator_supplied_aime=5000,
                    ss_calculator_birth_date="1958-01-02",
                    ss_calculator_entitlement_month="2020-01",
                    ss_calculator_eligibility_year=2020,
                )
            }
        ),
        reform={"gov.contrib.congress.s770.section_2.in_effect": {"2026-01-01": True}},
    )
    assert simulation.calculate("ss_calculated_eligibility_pia", "2025-01")[
        0
    ] == pytest.approx(2156.8)
    assert simulation.calculate("ss_calculated_eligibility_pia", "2026-01")[
        0
    ] == pytest.approx(2313.6)
    # Section2(c)(1) first changes January2026 entitlement, paid in February.
    # January's check still pays December2025 entitlement at baseline PIA.
    assert simulation.calculate("ss_calculated_payment", "2026-01")[0] == 2734
    assert simulation.calculate("ss_calculated_payment", "2026-02")[0] == 2933


def test_turning_70_releases_deferred_claim_year_credits_in_the_birthday_month():
    simulation = _simulation(
        situation=_situation(
            {
                "worker": _record(
                    ss_calculator_birth_date="1956-04-02",
                    ss_calculator_eligibility_year=2018,
                    ss_calculator_entitlement_month="2026-02",
                    ss_calculator_claiming_factor="",
                )
            }
        )
    )
    # https://secure.ssa.gov/poms.nsf/lnx/0300615690
    # Before70 the claim-year delayed credits wait; attaining70
    # in April releases the final claim-year credit immediately. Sequential
    # eligibility2018 COLAs produce PIA1324 in2026. January credits41months
    # give1324*(1+41/150)->1685; all42credits give1324*1.28->1694.
    assert simulation.calculate("ss_calculated_benefit", "2026-03")[0] == 1685
    assert simulation.calculate("ss_calculated_benefit", "2026-04")[0] == 1694
    assert simulation.calculate("ss_calculated_payment", "2026-04")[0] == 1685
    assert simulation.calculate("ss_calculated_payment", "2026-05")[0] == 1694


def test_next_january_reform_is_included_in_december_entitlement_row():
    simulation = _simulation(
        situation=_situation({"worker": _record()}),
        reform={"gov.contrib.congress.s770.section_2.in_effect": {"2027-01-01": True}},
    )
    assert simulation.calculate("ss_calculated_payment", "2026-12")[0] == 1000
    # PIA1000 implies AIME1000/.9; .95 factor ->1055.5 after dime
    # truncation, then December2026 COLA3.6% ->1093.4 ->1093 check.
    assert simulation.calculate("ss_calculated_benefit", "2026-12")[0] == 1093
    assert simulation.calculate("ss_calculated_payment", "2027-01")[0] == 1093
    assert simulation.calculate("ss_calculated_annual_entitlement", 2026)[0] == 12093
    assert simulation.calculate("ss_calculated_annual_payment", 2026)[0] == 11000


def test_joint_cola_withholding_pp_change_and_payment_factors_apply_once():
    situation = _situation(
        {
            "with_cola": _record("with-cola"),
            "withheld": _record(
                "withheld-cola", ss_calculator_withhold_cola={2027: True}
            ),
        }
    )
    simulation = _simulation(
        situation=situation,
        reform={
            "gov.contrib.ssa.benefit_levers.cola.pp_change": {"2027-01-01": 0.0015},
            "gov.contrib.ssa.benefit_levers.cola.start_year": {"2027-01-01": 2027},
            "gov.contrib.ssa.benefit_levers.cola.withholding_enabled": {
                "2027-01-01": True
            },
            "gov.contrib.ssa.benefit_levers.across_the_board.rate": {"2027-01-01": 0.1},
            "gov.contrib.ssa.benefit_levers.across_the_board.start_year": {
                "2027-01-01": 2027
            },
            "gov.contrib.ssa.benefit_levers.payable.share": {"2027-01-01": 0.8},
        },
    )
    # Joint COLA is3.6%+.15%=3.75% or zero when withheld. Dime-rounded
    # PIA1037.5/1000, then benefit factors1.10*.80 ->913/880 whole dollars.
    np.testing.assert_array_equal(
        simulation.calculate("ss_calculated_payment", "2027-01"), [913, 880]
    )


def test_common_cola_alternative_rate_effective_window_and_withholding_gate():
    people = {
        "worker": _record(ss_calculator_withhold_cola={2027: True}),
    }
    simulation = _simulation(
        situation=_situation(people),
        reform={
            "gov.contrib.ssa.benefit_levers.cola.alternative_rate": {
                "2027-01-01": 0.02
            },
            "gov.contrib.ssa.benefit_levers.cola.pp_change": {"2027-01-01": 0.0015},
            # The effective-date selector overrides the unused start-year
            # selector, and the end year includes this first affected event.
            "gov.contrib.ssa.benefit_levers.cola.effective_year": {"2027-01-01": 2026},
            "gov.contrib.ssa.benefit_levers.cola.effective_month": {"2027-01-01": 12},
            "gov.contrib.ssa.benefit_levers.cola.end_year": {"2027-01-01": 2027},
        },
    )
    # Withholding stays disabled, so the person's decision cannot suppress
    # the alternative2%+.15% COLA: PIA1000 ->1021.5 ->1021 check.
    assert simulation.calculate("ss_calculated_payment", "2027-01")[0] == 1021
    # End-year gating changes no later COLA; the earlier level persists.
    parameters = simulation.tax_benefit_system.parameters
    next_rate = next(
        event.rate
        for event in read_parameter_events(parameters, 2028)
        if event.payment_month == "2028-01"
    )
    expected = int(
        (Decimal("1021.5") * (1 + next_rate)).quantize(
            Decimal(".1"), rounding=ROUND_FLOOR
        )
    )
    assert simulation.calculate("ss_calculated_payment", "2028-01")[0] == expected


def test_absolute_alternative_cola_replaces_1999_original_and_corrected_rate():
    simulation = _simulation(
        situation=_situation(
            {
                "worker": _record(
                    ss_calculator_birth_date="1937-01-02",
                    ss_calculator_eligibility_year=1999,
                    ss_calculator_entitlement_month="1999-01",
                )
            }
        ),
        reform={
            "gov.contrib.ssa.benefit_levers.cola.alternative_rate": {
                "2000-01-01": 0.03
            },
            "gov.contrib.ssa.benefit_levers.cola.start_year": {"2000-01-01": 2000},
            "gov.contrib.ssa.benefit_levers.cola.end_year": {"2000-01-01": 2000},
        },
    )
    assert simulation.calculate("ss_calculated_payment", "2000-01")[0] == 1030
    # The later historical correction must retain the supplied absolute3%
    # rate rather than reconstructing the statutory2.5% COLA for1999.
    assert simulation.calculate("ss_calculated_payment", "2001-08")[0] == 1066


def _survivor():
    return _record(
        "deceased-worker",
        ss_calculator_source="survivor",
        ss_calculator_birth_date="1950-01-02",
        ss_calculator_eligibility_year=0,
        ss_calculator_entitlement_month="2025-09",
        ss_calculator_claiming_factor="",
        ss_calculator_worker_birth_year=1970,
        ss_calculator_worker_birth_date="1970-06-15",
        ss_calculator_death_year=2025,
        ss_calculator_death_date="2025-08-12",
        ss_calculator_basis_provenance="Supplied exact worker birth and death dates",
        ss_calculator_no_prior_disability=True,
        ss_calculator_ordinary_non_windex=True,
        ss_calculator_monthly_amount=2375,
        ss_calculator_valuation_month="2026-01",
        ss_calculator_composite_ratio="1",
        ss_calculator_ratio_description="Supplied composite including survivor reductions",
        ss_calculator_nonbinding_rib_lim=True,
        ss_calculator_nonbinding_family_maximum=True,
        ss_calculator_no_dual_entitlement=True,
        ss_calculator_no_earnings_test_at_valuation=True,
    )


def test_survivor_engine_derives_death_benchmark_and_first_cola():
    simulation = _simulation(situation=_situation({"survivor": _survivor()}))
    # Death-year2025 rather than hypothetical age62 year2032 supplies
    # the benchmark and December2025 COLA first paid January2026.
    assert simulation.calculate("ss_calculated_payment", "2025-12")[0] == 2310
    assert simulation.calculate("ss_calculated_payment", "2026-01")[0] == 2375
    assert simulation.calculate("ss_calculated_retirement", 2026)[0] == 0
    assert simulation.calculate("ss_calculated_survivors", 2026)[0] == 2375 * 12
    assert simulation.calculate("ss_calculated_pia_lower", 2026)[0] == pytest.approx(
        2310.4
    )


def test_survivor_selected_source_requires_a_supplied_monthly_amount():
    record = _survivor()
    record.pop("ss_calculator_monthly_amount")
    simulation = _simulation(situation=_situation({"survivor": record}))
    with pytest.raises(ValueError, match="Supply a nonnegative gross monthly payment"):
        simulation.calculate("ss_calculated_payment", "2026-02")


@pytest.mark.parametrize("increase,expected", [(False, 2371.7), (True, 2510.7)])
def test_survivor_engine_s770_flag_changes_bend_increase_only(increase, expected):
    simulation = _simulation(
        situation=_situation({"survivor": deepcopy(_survivor())}),
        reform={
            "gov.contrib.congress.s770.section_2.in_effect": {"2026-01-01": True},
            "gov.contrib.congress.s770.section_2.recompute_pre2026_death_before_eligibility": {
                "2026-01-01": increase
            },
        },
    )
    # Supplied-dollar inversion recovers lower-endpoint eligibility PIA2310.4.
    # Factor-only gain=.05*1226=61.3; factor+bend gain=.1634*1226=200.3284.
    assert simulation.calculate("ss_calculated_eligibility_pia", "2026-01")[
        0
    ] == pytest.approx(expected)
    assert simulation.calculate("ss_calculated_payment", "2026-01")[0] == 2375
