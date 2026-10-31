"""History ingress, complete source export, and future cohort integration.

Pure arithmetic and generated properties live in the history service tests.
These few vector cases exercise the real Simulation boundary and dated policy.
"""

import json
from decimal import Decimal, ROUND_HALF_UP

import numpy as np
import pytest
from policyengine_core.reforms import Reform

from policyengine_us import Simulation


def _history(claim_year):
    return json.dumps(
        {
            "first_year": claim_year - 1,
            "certified_zero_before_first_year": True,
            "certified_zero_years": [],
            "records": [
                {
                    "year": claim_year - 1,
                    "covered_wages": "120000.00",
                    "covered_self_employment": "0.01",
                }
            ],
        }
    )


def _record(identifier, eligibility=2026, claim=2026, source="history"):
    return {
        "ss_calculator_source": source,
        "ss_calculator_worker_id": identifier,
        "ss_calculator_birth_date": f"{eligibility - 62}-01-02",
        "ss_calculator_eligibility_year": eligibility,
        "ss_calculator_entitlement_month": f"{claim}-01",
        "ss_calculator_insured": True,
        "ss_calculator_claiming_factor": "1",
        "ss_calculator_no_special_monthly_test": True,
        "ss_calculator_no_prior_withholding_adjustment": True,
        "ss_calculator_earnings_test_no_trigger": True,
        "ss_calculator_earnings_history": _history(claim),
        "ss_calculator_supplied_aime": 285,
    }


def _situation(people):
    members = list(people)
    return {
        "people": people,
        "tax_units": {"unit": {"members": members}},
        "families": {"unit": {"members": members}},
        "spm_units": {"unit": {"members": members}},
        "households": {"unit": {"members": members}},
    }


def _simulation(situation, reform=None):
    if reform is None:
        return Simulation(situation=situation)
    return Simulation(
        situation=situation,
        tax_benefit_system=Simulation.default_tax_benefit_system_instance,
        reform=reform,
    )


@pytest.fixture(scope="module")
def history_simulation():
    return _simulation(
        _situation(
            {
                "supplied": _record("supplied", source="aime"),
                "history": _record("history"),
                "off": {
                    "ss_calculator_source": "off",
                    "ss_calculator_earnings_history": "{not valid JSON",
                },
            }
        )
    )


def test_history_and_supplied_aime_match_while_off_skips_malformed_source(
    history_simulation,
):
    simulation = history_simulation
    # A single face-value 2025 year gives floor(120000.01 / 420) = 285.
    # The 2026 first factor is .90, so initial PIA is 256.50.
    np.testing.assert_allclose(
        simulation.calculate("ss_calculated_eligibility_pia", "2026-01"),
        [256.5, 256.5, 0],
        rtol=0,
        atol=0.0001,
    )
    np.testing.assert_array_equal(
        simulation.calculate("ss_calculated_payment", "2026-01"), [0, 0, 0]
    )
    np.testing.assert_array_equal(
        simulation.calculate("ss_calculated_payment", "2026-02"), [256, 256, 0]
    )
    np.testing.assert_array_equal(
        simulation.calculate("ss_calculated_annual_payment", 2026),
        [256 * 11, 256 * 11, 0],
    )


def test_complete_json_source_survives_export_extract_and_reload(history_simulation):
    simulation = history_simulation
    expected = simulation.calculate("ss_calculated_annual_payment", 2026).copy()
    inputs = simulation.to_input_dict()
    assert "ss_calculated_annual_payment" not in inputs
    assert inputs["ss_calculator_earnings_history"]["ETERNITY"][1] == _history(2026)
    assert "ss_calculator_earnings_history" in simulation.true_input_variables

    extracted = simulation.extract_person(index=1)
    observed = extracted["people"]["person_2"]["ss_calculator_earnings_history"]
    assert next(iter(observed.values())) == _history(2026)
    reloaded = _simulation(extracted)
    np.testing.assert_array_equal(
        reloaded.calculate("ss_calculated_annual_payment", 2026), expected
    )
    # No float32 conversion, observation carry-forward, or computed output
    # replaces the supplied decimal string when the source is exported again.
    assert reloaded.to_input_dict()["ss_calculator_earnings_history"]["ETERNITY"][
        1
    ] == _history(2026)


def test_future_cohorts_and_2057_2059_claims_apply_each_policy_once():
    cases = ((2036, 2039), (2038, 2043), (2054, 2057), (2054, 2059))
    people = {}
    for eligibility, claim in cases:
        for source in ("history", "aime"):
            identifier = f"{source}_{eligibility}_{claim}"
            people[identifier] = _record(identifier, eligibility, claim, source)
    simulation = _simulation(
        _situation(people),
        reform={
            "gov.contrib.ssa.pia.in_effect": {"2036-01-01": True},
            "gov.contrib.ssa.pia.factors.start_year": {"2036-01-01": 2036},
            "gov.contrib.ssa.pia.factors.first": {
                "2036-01-01": 0.95,
                "2050-01-01": 0.85,
            },
            # An absolute zero baseline plus .10 gives a known 10% COLA,
            # independent of the model's projected CPI-W observations.
            "gov.contrib.ssa.benefit_levers.cola.alternative_rate": {
                "2036-01-01": 0,
            },
            "gov.contrib.ssa.benefit_levers.cola.pp_change": {
                "2036-01-01": 0.10,
            },
            "gov.contrib.ssa.benefit_levers.cola.start_year": {
                "2036-01-01": 2036,
            },
            "gov.contrib.ssa.benefit_levers.across_the_board.rate": {
                "2036-01-01": 0.10,
            },
            "gov.contrib.ssa.benefit_levers.across_the_board.start_year": {
                "2036-01-01": 2036,
            },
            "gov.contrib.ssa.benefit_levers.payable.share": {
                "2036-01-01": 0.80,
            },
        },
    )
    for case_index, (eligibility, claim) in enumerate(cases):
        indices = [case_index * 2, case_index * 2 + 1]
        first_factor = Decimal(".85") if eligibility >= 2050 else Decimal(".95")
        initial = Decimal(int(Decimal(285) * first_factor * 10)) / 10
        np.testing.assert_allclose(
            simulation.calculate("ss_calculated_eligibility_pia", f"{claim}-01")[
                indices
            ],
            [float(initial)] * 2,
            rtol=0,
            atol=0.0001,
        )
        updated = initial
        for _ in range(claim - eligibility):
            updated = Decimal(int(updated * Decimal("1.10") * 10)) / 10
        expected = int(updated * Decimal("1.10") * Decimal(".80"))
        np.testing.assert_array_equal(
            simulation.calculate("ss_calculated_payment", f"{claim}-02")[indices],
            [expected, expected],
        )


def test_all_three_reforms_reconcile_hand_computed_history_in_real_engine():
    """The design fixture reaches real inputs, parameters, and payment outputs."""

    class SyntheticHistoryParameters(Reform):
        def apply(self):
            def modify(parameters):
                ssa = parameters.gov.ssa
                ssa.nawi.update(start="1951-01-01", value=1)
                ssa.social_security.wage_base.update(start="1951-01-01", value=120_000)
                scale = ssa.social_security.pia.formula_factors
                scale.brackets[1].threshold.update(start="2036-01-01", value=1000)
                scale.brackets[2].threshold.update(start="2036-01-01", value=6000)

                draw = parameters.gov.contrib.ssa.owners_draw
                draw.in_effect.update(start="2027-01-01", value=True)
                draw.start_year.update(start="1983-01-01", value=2027)
                draw.phase_in_share.update(start="2027-01-01", value=1)
                draw.current_law_cap.update(start="1951-01-01", value=120_000)

                history = parameters.gov.contrib.ssa.history
                history.mini_pia.in_effect.update(start="1983-01-01", value=True)
                history.donut.oact_2025_e2_13.in_effect.update(
                    start="1983-01-01", value=True
                )
                cola = parameters.gov.contrib.ssa.benefit_levers.cola
                cola.alternative_rate.update(start="1983-01-01", value=0)
                cola.start_year.update(start="1983-01-01", value=1983)
                return parameters

            self.modify_parameters(modify)

    def observed(year, wages=0, gross_draw=0):
        return {
            "year": year,
            "covered_wages": str(wages),
            "covered_self_employment": "0",
            "owners_draw": {
                "s_corp_income": str(gross_draw),
                "partnership_income": "0",
                "passive_income": "0",
                "already_se_income": "0",
                "subsets_are_disjoint": True,
            },
        }

    record = _record("all-three", eligibility=2036, claim=2039)
    # Compute the exact age-65 reduction instead of supplying a factor.
    record.pop("ss_calculator_claiming_factor")
    record["ss_calculator_donut_variant"] = "oact_2025_e2_13"
    record["ss_calculator_earnings_history"] = json.dumps(
        {
            "first_year": 1999,
            "certified_zero_before_first_year": True,
            "certified_zero_years": list(range(1999, 2004)),
            "records": [observed(year, wages=60_000) for year in range(2004, 2037)]
            + [observed(2037, gross_draw=60_000), observed(2038, wages=500_800)],
        }
    )
    simulation = _simulation(
        _situation({"worker": record}), reform=SyntheticHistoryParameters
    )
    np.testing.assert_allclose(
        simulation.calculate("ss_calculated_eligibility_pia", "2039-01"),
        [2088.5],
        rtol=0,
        atol=0.0001,
    )
    np.testing.assert_array_equal(
        simulation.calculate("ss_calculated_payment", "2039-02"), [1810]
    )
    np.testing.assert_array_equal(
        simulation.calculate("ss_calculated_annual_entitlement", 2039), [21_720]
    )
    np.testing.assert_array_equal(
        simulation.calculate("ss_calculated_annual_payment", 2039), [19_910]
    )
    assert simulation.calculate("ss_calculated_history_aime", 2039)[0] == 5131
    assert simulation.calculate("ss_calculated_history_aime_plus", 2039)[0] == 240
    assert simulation.calculate("ss_calculated_history_conventional_pia", 2039)[
        0
    ] == pytest.approx(2221.9)
    assert simulation.calculate("ss_calculated_history_mini_pia", 2039)[
        0
    ] == pytest.approx(float(Decimal("77097.6") / 37))
    ledger = json.loads(simulation.calculate("ss_calculated_history_ledger", 2039)[0])
    assert ledger["eligibility_pia"] == "2088.5"
    assert ledger["mini_pia_exact"] == "385488/185"
    assert ledger["donut_credit_pia_exact"] == "24/5"
    rows = {row["year"]: row for row in ledger["rows"]}
    assert rows[1999]["certified_zero"] is True
    assert Decimal(rows[2037]["e1_credited"]) == 55410
    assert Decimal(rows[2037]["mini_pia"]) == Decimal("2057.6")
    assert Decimal(rows[2038]["donut_taxed"]) == 100800
    assert sum(row["ordinary_top35"] for row in rows.values()) == 35


def test_default_history_accepts_earnings_before_1983_with_disabled_reforms():
    """Earnings-year policy reads must support a modern worker's whole career."""
    record = _record("historical-earnings", eligibility=2026, claim=2029)
    record["ss_calculator_earnings_history"] = json.dumps(
        {
            "first_year": 1980,
            "certified_zero_before_first_year": True,
            "certified_zero_years": list(range(1981, 2029)),
            "records": [
                {
                    "year": 1980,
                    "covered_wages": "18000.00",
                    "covered_self_employment": "0.00",
                }
            ],
        }
    )
    simulation = _simulation(_situation({"worker": record}))
    # SSA published NAWI: 1980 $12,513.46; E-2 = 2024 $69,846.57.
    # The 1980 contribution/benefit base is $25,900, above supplied wages.
    # https://www.ssa.gov/OACT/COLA/AWI.html
    expected_indexed = (
        Decimal("18000.00") * Decimal("69846.57") / Decimal("12513.46")
    ).quantize(Decimal(".01"), rounding=ROUND_HALF_UP)
    expected_aime = int(expected_indexed // 420)
    assert expected_aime == 239
    assert simulation.calculate("ss_calculated_history_aime", 2029)[0] == expected_aime
    assert simulation.calculate("ss_calculated_history_aime_plus", 2029)[0] == 0
    assert simulation.calculate("ss_calculated_history_conventional_pia", 2029)[
        0
    ] == pytest.approx(215.1)
    report = json.loads(simulation.calculate("ss_calculated_history_ledger", 2029)[0])
    first = report["rows"][0]
    assert first["year"] == 1980
    assert Decimal(first["ordinary_cap"]) == 25_900
    assert Decimal(first["ordinary_covered"]) == 18_000
    assert Decimal(first["indexed_ordinary"]) == expected_indexed
    assert Decimal(first["donut_taxed"]) == 0
    assert len(report["rows"]) == 49
