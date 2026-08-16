"""Reform tests for Head Start income eligibility flexibilities.

45 CFR 1302.12(c)(1)(i) sets the statutory floor (income at or below 100%
of the federal poverty guidelines), which the baseline models. Two
grantee-discretionary flexibilities are exposed as parameters, off by
default, so reforms and screeners can activate them:

- 1302.12(d): programs may fill a share of slots with families between
  100% and 130% of the poverty guidelines
  (``gov.hhs.head_start.income_limit``).
- The 2024 final rule (89 FR, Aug 21, 2024; effective October 2024) lets
  programs deduct housing costs exceeding a share of gross income
  (``gov.hhs.head_start.housing_cost_adjustment``).
"""

from policyengine_core.reforms import Reform

from policyengine_us import CountryTaxBenefitSystem, Simulation

PERIOD = "2025"
FPG = 20_000

BASELINE_SYSTEM = CountryTaxBenefitSystem()

DISCRETIONARY_BAND_REFORM = {
    "gov.hhs.head_start.income_limit": {"2021-01-01.2100-12-31": 1.3},
}
HOUSING_ADJUSTMENT_REFORM = {
    "gov.hhs.head_start.housing_cost_adjustment.in_effect": {
        "2021-01-01.2100-12-31": True
    },
}


def make_system(reform_dict=None):
    if reform_dict is None:
        return BASELINE_SYSTEM
    reform = Reform.from_dict(reform_dict, country_id="us")
    return CountryTaxBenefitSystem(reform=(reform,))


def child_is_income_eligible(system, agi, housing_cost=0):
    members = ["parent", "child"]
    simulation = Simulation(
        tax_benefit_system=system,
        situation={
            "people": {
                "parent": {"age": {PERIOD: 30}},
                "child": {"age": {PERIOD: 4}},
            },
            "tax_units": {
                "tax_unit": {
                    "members": members,
                    "adjusted_gross_income": {PERIOD: agi},
                    "tax_unit_fpg": {PERIOD: FPG},
                }
            },
            "spm_units": {
                "spm_unit": {
                    "members": members,
                    "housing_cost": {PERIOD: housing_cost},
                }
            },
            "households": {
                "household": {
                    "members": members,
                    "state_code": {PERIOD: "TX"},
                }
            },
            "families": {"family": {"members": members}},
            "marital_units": {
                "mu_parent": {"members": ["parent"]},
                "mu_child": {"members": ["child"]},
            },
        },
    )
    eligible = simulation.calculate("is_head_start_income_eligible", PERIOD)
    return bool(eligible[1])


def test_baseline_floor_holds_at_and_just_above_fpg():
    assert child_is_income_eligible(BASELINE_SYSTEM, agi=FPG)
    assert not child_is_income_eligible(BASELINE_SYSTEM, agi=FPG + 1)


def test_baseline_ignores_housing_costs():
    # 120% of FPG with substantial housing costs: the housing adjustment is
    # grantee-discretionary and off by default, so the family stays over.
    assert not child_is_income_eligible(
        BASELINE_SYSTEM, agi=24_000, housing_cost=12_000
    )


def test_discretionary_band_reform_extends_limit_to_130_percent():
    system = make_system(DISCRETIONARY_BAND_REFORM)
    # 120% of FPG falls inside the 1302.12(d) band.
    assert child_is_income_eligible(system, agi=24_000)
    # Exactly 130% of FPG is still within the ceiling.
    assert child_is_income_eligible(system, agi=26_000)
    # 135% of FPG exceeds even the discretionary ceiling.
    assert not child_is_income_eligible(system, agi=27_000)


def test_housing_cost_adjustment_reform_deducts_excess_housing_costs():
    system = make_system(HOUSING_ADJUSTMENT_REFORM)
    # AGI 24,000; threshold = 30% x 24,000 = 7,200.
    # Housing costs 12,000 -> excess 4,800 -> countable 19,200 <= 20,000.
    assert child_is_income_eligible(system, agi=24_000, housing_cost=12_000)
    # Housing costs 8,000 -> excess 800 -> countable 23,200 > 20,000.
    assert not child_is_income_eligible(system, agi=24_000, housing_cost=8_000)
    # No housing costs: the adjustment changes nothing.
    assert not child_is_income_eligible(system, agi=24_000, housing_cost=0)
