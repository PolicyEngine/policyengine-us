from policyengine_us.model_api import *


class meets_wic_income_test(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    documentation = "Meets income test for the Special Supplemental Nutrition Program for Women, Infants and Children (WIC)"
    label = "Meets WIC income test"
    reference = "https://www.law.cornell.edu/uscode/text/42/1786#d_2_A_i"

    def formula(spm_unit, period, parameters):
        # WIC uses the reduced-price school meal income limit, with a
        # WIC-specific countable income definition and pregnancy adjustment.
        income = spm_unit("wic_countable_income", period)
        adj_fpg = spm_unit("wic_fpg", period)
        limit = parameters(period).gov.usda.school_meals.income.limit.REDUCED
        income_fpg_ratio = income / adj_fpg
        return income_fpg_ratio <= limit
