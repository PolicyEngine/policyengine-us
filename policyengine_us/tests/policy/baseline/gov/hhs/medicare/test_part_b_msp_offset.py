from types import SimpleNamespace

import numpy as np
import pytest
from policyengine_core import periods

from policyengine_us import CountryTaxBenefitSystem, Simulation
import policyengine_us.variables.household.expense.health.medicare_part_b_premiums as part_b_module
from policyengine_us.variables.household.expense.health.medicare_part_b_premiums import (
    _get_explicit_legacy_part_b_inputs,
    medicare_part_b_premiums,
)


SYSTEM = CountryTaxBenefitSystem()
PERIOD = "2025"


class FakePartBPerson:
    ids = ["person"]
    count = 1

    def __init__(self, situation_input=None):
        self.simulation = SimpleNamespace(situation_input=situation_input)
        self.values = {
            "medicare_enrolled": np.array([True]),
            "income_adjusted_part_b_premium": np.array([123.0]),
            "msp_part_b_premium_coverage": np.array([0.0]),
        }

    def __call__(self, variable, period):
        return self.values[variable]


def make_simulation(
    *,
    medicare_enrolled: bool,
    gross_part_b_premium: float,
    base_part_b_premium: float,
    msp_income_eligible: bool,
    msp_asset_eligible: bool,
) -> Simulation:
    return Simulation(
        tax_benefit_system=SYSTEM,
        situation={
            "people": {
                "person": {
                    "age": {PERIOD: 65},
                    "medicare_enrolled": {PERIOD: medicare_enrolled},
                    "income_adjusted_part_b_premium": {PERIOD: gross_part_b_premium},
                    "base_part_b_premium": {PERIOD: base_part_b_premium},
                    "msp_income_eligible": {f"{PERIOD}-01": msp_income_eligible},
                    "msp_asset_eligible": {f"{PERIOD}-01": msp_asset_eligible},
                }
            },
            "households": {"household": {"members": ["person"]}},
            "tax_units": {"tax_unit": {"members": ["person"]}},
            "spm_units": {"spm_unit": {"members": ["person"]}},
            "families": {"family": {"members": ["person"]}},
            "marital_units": {"marital_unit": {"members": ["person"]}},
        },
    )


def test_msp_part_b_premium_coverage_pays_standard_premium():
    sim = make_simulation(
        medicare_enrolled=True,
        gross_part_b_premium=4_440,
        base_part_b_premium=2_220,
        msp_income_eligible=True,
        msp_asset_eligible=True,
    )

    assert sim.calculate("msp_part_b_premium_coverage", PERIOD)[0] == pytest.approx(
        2_220
    )


def test_medicare_part_b_premiums_preserve_only_irmaa_above_msp_support():
    sim = make_simulation(
        medicare_enrolled=True,
        gross_part_b_premium=4_440,
        base_part_b_premium=2_220,
        msp_income_eligible=True,
        msp_asset_eligible=True,
    )

    assert sim.calculate("medicare_part_b_premiums", PERIOD)[0] == pytest.approx(2_220)


def test_medicare_part_b_premiums_are_zero_when_msp_covers_standard_premium():
    sim = make_simulation(
        medicare_enrolled=True,
        gross_part_b_premium=2_220,
        base_part_b_premium=2_220,
        msp_income_eligible=True,
        msp_asset_eligible=True,
    )

    assert sim.calculate("medicare_part_b_premiums", PERIOD)[0] == pytest.approx(0)


def test_medicare_cost_uses_gross_part_b_before_msp_offset():
    sim = Simulation(
        tax_benefit_system=SYSTEM,
        situation={
            "people": {
                "person": {
                    "age": {PERIOD: 65},
                    "medicare_enrolled": {PERIOD: True},
                    "base_part_a_premium": {PERIOD: 0},
                    "income_adjusted_part_b_premium": {PERIOD: 2_220},
                    "base_part_b_premium": {PERIOD: 2_220},
                    "msp_income_eligible": {f"{PERIOD}-01": True},
                    "msp_asset_eligible": {f"{PERIOD}-01": True},
                }
            },
            "households": {"household": {"members": ["person"]}},
            "tax_units": {"tax_unit": {"members": ["person"]}},
            "spm_units": {"spm_unit": {"members": ["person"]}},
            "families": {"family": {"members": ["person"]}},
            "marital_units": {"marital_unit": {"members": ["person"]}},
        },
    )

    assert sim.calculate("medicare_part_b_premiums", PERIOD)[0] == pytest.approx(0)
    assert sim.calculate("medicare_cost", PERIOD)[0] == pytest.approx(12_280)


def test_medicare_part_b_premiums_are_zero_when_not_enrolled():
    sim = make_simulation(
        medicare_enrolled=False,
        gross_part_b_premium=2_220,
        base_part_b_premium=2_220,
        msp_income_eligible=True,
        msp_asset_eligible=True,
    )

    assert sim.calculate("msp_part_b_premium_coverage", PERIOD)[0] == pytest.approx(0)
    assert sim.calculate("medicare_part_b_premiums", PERIOD)[0] == pytest.approx(0)


def test_legacy_medicare_part_b_input_uprates_forward():
    sim = Simulation(
        tax_benefit_system=SYSTEM,
        situation={
            "people": {
                "person": {
                    "age": {"2024": 65},
                    "medicare_part_b_premiums": {"2024": 1_000},
                }
            },
            "households": {"household": {"members": ["person"]}},
            "tax_units": {"tax_unit": {"members": ["person"]}},
            "spm_units": {"spm_unit": {"members": ["person"]}},
            "families": {"family": {"members": ["person"]}},
            "marital_units": {"marital_unit": {"members": ["person"]}},
        },
    )

    assert sim.calculate("medicare_part_b_premiums", "2025")[0] == pytest.approx(
        1_030.8833,
        abs=1e-3,
    )


def test_legacy_part_b_helper_handles_missing_situation_input():
    person = SimpleNamespace(simulation=SimpleNamespace(situation_input=None))

    assert _get_explicit_legacy_part_b_inputs(person) == {}


def test_legacy_part_b_helper_handles_missing_people_input():
    person = SimpleNamespace(simulation=SimpleNamespace(situation_input={}))

    assert _get_explicit_legacy_part_b_inputs(person) == {}


def test_legacy_part_b_helper_skips_non_dict_person_input():
    person = SimpleNamespace(
        ids=["person"],
        count=1,
        simulation=SimpleNamespace(
            situation_input={"people": {"person": "not a dict"}}
        ),
    )

    assert _get_explicit_legacy_part_b_inputs(person) == {}


def test_legacy_part_b_formula_uses_current_direct_input():
    situation_input = {
        "people": {"person": {"medicare_part_b_premiums": {PERIOD: 1_000}}}
    }
    person = FakePartBPerson(situation_input)

    result = medicare_part_b_premiums.formula(
        person, periods.period(PERIOD), parameters=None
    )

    assert result[0] == pytest.approx(1_000)


def test_legacy_part_b_formula_uses_modeled_value_when_prior_input_is_missing(
    monkeypatch,
):
    monkeypatch.setattr(
        part_b_module,
        "_get_explicit_legacy_part_b_inputs",
        lambda person: {periods.period("2024"): np.array([np.nan])},
    )
    person = FakePartBPerson()

    result = medicare_part_b_premiums.formula(
        person, periods.period(PERIOD), parameters=None
    )

    assert result[0] == pytest.approx(123)


def test_msp_part_b_premium_coverage_scales_with_eligible_months():
    monthly_eligibility = {
        f"{PERIOD}-{month:02d}": month <= 3 for month in range(1, 13)
    }
    sim = Simulation(
        tax_benefit_system=SYSTEM,
        situation={
            "people": {
                "person": {
                    "age": {PERIOD: 65},
                    "medicare_enrolled": {PERIOD: True},
                    "base_part_b_premium": {PERIOD: 2_220},
                    "msp_income_eligible": monthly_eligibility,
                    "msp_asset_eligible": monthly_eligibility,
                }
            },
            "households": {"household": {"members": ["person"]}},
            "tax_units": {"tax_unit": {"members": ["person"]}},
            "spm_units": {"spm_unit": {"members": ["person"]}},
            "families": {"family": {"members": ["person"]}},
            "marital_units": {"marital_unit": {"members": ["person"]}},
        },
    )

    assert sim.calculate("msp_part_b_premium_coverage", PERIOD)[0] == pytest.approx(
        555,
        abs=1e-6,
    )


def test_medicare_part_b_premiums_do_not_depend_on_calculation_order():
    no_msp_eligibility = {
        f"{year}-{month:02d}": False
        for year in ("2025", "2026")
        for month in range(1, 13)
    }
    situation = {
        "people": {
            "person": {
                "age": {"2025": 65, "2026": 66},
                "medicare_enrolled": {"2025": True, "2026": True},
                "income_adjusted_part_b_premium": {"2025": 2_220, "2026": 2_220},
                "base_part_b_premium": {"2025": 2_220, "2026": 2_220},
                "msp_income_eligible": no_msp_eligibility,
                "msp_asset_eligible": no_msp_eligibility,
            }
        },
        "households": {"household": {"members": ["person"]}},
        "tax_units": {"tax_unit": {"members": ["person"]}},
        "spm_units": {"spm_unit": {"members": ["person"]}},
        "families": {"family": {"members": ["person"]}},
        "marital_units": {"marital_unit": {"members": ["person"]}},
    }

    ordered_sim = Simulation(tax_benefit_system=SYSTEM, situation=situation)
    ordered_sim.calculate("medicare_part_b_premiums", "2025")
    ordered_result = ordered_sim.calculate("medicare_part_b_premiums", "2026")[0]

    fresh_sim = Simulation(tax_benefit_system=SYSTEM, situation=situation)
    fresh_result = fresh_sim.calculate("medicare_part_b_premiums", "2026")[0]

    assert ordered_result == pytest.approx(fresh_result)
    assert ordered_result == pytest.approx(2_220)


def test_income_adjusted_part_b_premium_handles_direct_filing_status_inputs():
    sim = Simulation(
        tax_benefit_system=SYSTEM,
        situation={
            "people": {
                "person_1": {
                    "age": {PERIOD: 65},
                    "base_part_b_premium": {PERIOD: 2_220},
                    "is_medicare_eligible": {PERIOD: True},
                    "tax_exempt_interest_income": {"2023": 0},
                },
                "person_2": {
                    "age": {PERIOD: 65},
                    "base_part_b_premium": {PERIOD: 2_220},
                    "is_medicare_eligible": {PERIOD: True},
                    "tax_exempt_interest_income": {"2023": 0},
                },
                "person_3": {
                    "age": {PERIOD: 65},
                    "base_part_b_premium": {PERIOD: 2_220},
                    "is_medicare_eligible": {PERIOD: True},
                    "tax_exempt_interest_income": {"2023": 0},
                },
            },
            "households": {
                "household": {"members": ["person_1", "person_2", "person_3"]}
            },
            "tax_units": {
                "joint_tax_unit": {
                    "members": ["person_1", "person_2"],
                    "filing_status": {PERIOD: "JOINT"},
                    "adjusted_gross_income": {"2023": 1_000_000},
                },
                "single_tax_unit": {
                    "members": ["person_3"],
                    "filing_status": {PERIOD: "SINGLE"},
                    "adjusted_gross_income": {"2023": 50_000},
                },
            },
            "spm_units": {
                "spm_unit": {"members": ["person_1", "person_2", "person_3"]}
            },
            "families": {"family": {"members": ["person_1", "person_2", "person_3"]}},
            "marital_units": {
                "marital_unit_1": {"members": ["person_1", "person_2"]},
                "marital_unit_2": {"members": ["person_3"]},
            },
        },
    )

    result = sim.calculate("income_adjusted_part_b_premium", PERIOD)
    assert result[0] == pytest.approx(7_546.8)
    assert result[1] == pytest.approx(7_546.8)
    assert result[2] == pytest.approx(2_220)
