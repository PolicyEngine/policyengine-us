from policyengine_us.model_api import *


class subsidized_housing(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Household lives in subsidized housing"
    definition_period = YEAR
    reference = "https://www.masslegalservices.org/system/files/blog/FY_2022_LIHEAP_Income_Eligibility_and_Benefit_Chart_APRIL_2022_UTILITY_Increase.pdf"

    def formula(spm_unit, period, parameters):
        housing_assistance = spm_unit("housing_assistance", period)
        return housing_assistance > 0
