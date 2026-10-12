from policyengine_us.model_api import *


class head_start_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Head Start countable income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ecfr.gov/current/title-45/section-1302.12#p-1302.12(i)(1)",
        "https://www.federalregister.gov/documents/2024/08/21/2024-18279/supporting-the-head-start-workforce-and-consistent-quality-programming",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.hhs.head_start.housing_cost_adjustment
        gross_income = spm_unit("head_start_gross_income", period)
        # A program may reduce gross income by housing costs exceeding a
        # share of gross income (45 CFR 1302.12(i)(1)(ii), 2024 final rule).
        applies_adjustment = spm_unit(
            "head_start_applies_housing_cost_adjustment", period
        )
        housing_cost = spm_unit("head_start_housing_cost", period)
        excess_housing_cost = max_(
            housing_cost - p.income_share_threshold * gross_income, 0
        )
        return gross_income - where(applies_adjustment, excess_housing_cost, 0)
