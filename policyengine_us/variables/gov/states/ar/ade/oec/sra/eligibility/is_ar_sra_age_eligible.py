from policyengine_us.model_api import *


class is_ar_sra_age_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Age-eligible for Arkansas SRA"
    definition_period = MONTH
    defined_for = StateCode.AR
    reference = (
        "https://dese.ade.arkansas.gov/Files/2025-2027_CCDF_State_Plan_Final_4.26.24.1REV_OEC.pdf#page=18",
        "https://dese.ade.arkansas.gov/Files/FSU-Procedural-Manual-June-2023_UPDATED_20230629075344.pdf#page=32",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ar.ade.oec.sra.eligibility
        age = person("age", period.this_year)
        is_disabled = person("is_disabled", period.this_year)
        age_limit = where(is_disabled, p.child_age_limit_disabled, p.child_age_limit)
        return age < age_limit
