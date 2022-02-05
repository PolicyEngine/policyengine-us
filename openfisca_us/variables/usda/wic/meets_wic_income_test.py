from openfisca_us.model_api import *


class meets_wic_income_test(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    documentation = "Meets income test for the Special Supplemental Nutrition Program for Women, Infants and Children (WIC)"
    label = "Meets WIC income test"
    reference = "https://www.law.cornell.edu/uscode/text/42/1786#d_2_A_i"

    def formula(spm_unit, period, parameters):
        # Free or reduced are eligible.
        school_meal_tier = spm_unit("school_meal_tier", period)
        school_meal_tiers = school_meal_tier.possible_values
        return school_meal_tier != school_meal_tiers.PAID
