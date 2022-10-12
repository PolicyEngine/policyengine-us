from policyengine_us.model_api import *


class meets_wic_income_test(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    documentation = "Meets income test for the Special Supplemental Nutrition Program for Women, Infants and Children (WIC)"
    label = "Meets WIC income test"
    reference = "https://www.law.cornell.edu/uscode/text/42/1786#d_2_A_i"

    def formula(spm_unit, period, parameters):
        # Must be below the school meal reduced price tier.
        # We can't use school_meal_tier, because pregnant women have an
        # additional person for defining the poverty line
        # (for WIC but not school meals).
        income = spm_unit("school_meal_countable_income", period)
        adj_fpg = spm_unit("wic_fpg", period)
        limit = parameters(period).gov.usda.school_meals.income.limit.REDUCED
        income_fpg_ratio = income / adj_fpg
        return income_fpg_ratio <= limit
