from policyengine_us.model_api import *


class meets_wic_income_test(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    documentation = "Meets income test for the Special Supplemental Nutrition Program for Women, Infants and Children (WIC)"
    label = "Meets WIC income test"
    reference = "https://www.law.cornell.edu/uscode/text/42/1786#d_2_A_i"

    def formula(spm_unit, period, parameters):
        income = spm_unit("wic_countable_income", period.this_year)
        limit = spm_unit("wic_income_limit", period.first_month)
        return income <= limit
