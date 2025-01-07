from policyengine_us.model_api import *


class or_liheap_income_threshold(Variable):
    value_type = int
    entity = SPMUnit
    label = "Income range for Oregon LIHEAP eligibility"
    unit = USD
    definition_period = YEAR
    reference = "https://www.oregon.gov/ohcs/energy-weatherization/Documents/2021-Energy-Assistance-Manual.pdf#Pg=55"
    defined_for = StateCode.OR

    def formula(spm_unit, period, parameters):
        income = spm_unit("adjusted_gross_income", period)
        threshold = spm_unit("or_liheap_income_threshold", period)

        range1_upper = 0.25 * threshold
        range2_upper = 0.5 * threshold
        range3_upper = 0.75 * threshold

        if income <= range1_upper:
            return 1
        elif income <= range2_upper:
            return 2
        elif income <= range3_upper:
            return 3
        else:
            return 4
