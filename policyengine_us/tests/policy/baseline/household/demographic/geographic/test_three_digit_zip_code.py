"""Test that three_digit_zip_code is derived from zip_code.

Regression test for https://github.com/PolicyEngine/policyengine-us/pull/7695
which removed the formula, breaking ACA PTC for LA County households.
"""

from policyengine_us import CountryTaxBenefitSystem, Simulation

system = CountryTaxBenefitSystem()


def _make_sim(zip_code):
    return Simulation(
        tax_benefit_system=system,
        situation={
            "people": {"person": {"age": {"2026": 30}}},
            "households": {
                "household": {
                    "members": ["person"],
                    "zip_code": {"2026": zip_code},
                },
            },
            "tax_units": {"tax_unit": {"members": ["person"]}},
            "spm_units": {"spm_unit": {"members": ["person"]}},
            "families": {"family": {"members": ["person"]}},
            "marital_units": {"marital_unit": {"members": ["person"]}},
        },
    )


def test_three_digit_zip_code_derived_from_zip():
    """90019 -> 900"""
    sim = _make_sim("90019")
    result = sim.calculate("three_digit_zip_code", 2026)
    assert result[0] == "900"


def test_three_digit_zip_code_leading_zero():
    """01234 -> 012"""
    sim = _make_sim("01234")
    result = sim.calculate("three_digit_zip_code", 2026)
    assert result[0] == "012"


def test_la_county_aca_ptc_nonzero_with_zip():
    """ACA PTC should be nonzero for an LA County household providing zip_code.

    Integration test from Amplifi bug report: zip 90019 should produce
    a nonzero aca_ptc for an eligible individual.
    """
    sim = Simulation(
        tax_benefit_system=system,
        situation={
            "people": {
                "you": {
                    "age": {"2026": 33},
                    "employment_income": {"2026": 22_222},
                    "is_aca_eshi_eligible": {"2026": False},
                },
            },
            "households": {
                "household": {
                    "members": ["you"],
                    "zip_code": {"2026": "90019"},
                    "state_code_str": {"2026": "CA"},
                    "in_la": {"2026": True},
                },
            },
            "tax_units": {
                "tax_unit": {"members": ["you"]},
            },
            "spm_units": {
                "spm_unit": {"members": ["you"]},
            },
            "families": {
                "family": {"members": ["you"]},
            },
            "marital_units": {
                "marital_unit": {"members": ["you"]},
            },
        },
    )
    aca_ptc = sim.calculate("aca_ptc", 2026)
    assert aca_ptc[0] > 0, (
        f"Expected nonzero ACA PTC for LA County zip 90019, got {aca_ptc[0]}"
    )
