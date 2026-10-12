from policyengine_us.model_api import *


class is_ar_sra_child_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for Arkansas SRA"
    definition_period = MONTH
    defined_for = StateCode.AR
    reference = "https://dese.ade.arkansas.gov/Files/2025-2027_CCDF_State_Plan_Final_4.26.24.1REV_OEC.pdf#page=18"

    def formula(person, period, parameters):
        age_eligible = person("is_ar_sra_age_eligible", period)
        immigration_eligible = person(
            "is_ccdf_immigration_eligible_child", period.this_year
        )
        return age_eligible & immigration_eligible
