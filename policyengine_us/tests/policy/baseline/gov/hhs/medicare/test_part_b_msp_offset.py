import pytest

from policyengine_us import CountryTaxBenefitSystem, Simulation


SYSTEM = CountryTaxBenefitSystem()
PERIOD = "2025"


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
