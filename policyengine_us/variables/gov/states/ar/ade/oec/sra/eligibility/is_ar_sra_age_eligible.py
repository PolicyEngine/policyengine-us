from policyengine_us.model_api import *


class is_ar_sra_age_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Age-eligible for Arkansas SRA"
    definition_period = MONTH
    defined_for = StateCode.AR
    reference = (
        "https://www.publichealthlawcenter.org/sites/default/files/Arkansas%20Title%20016%20Division%2022%20Rule%208.pdf#page=11",
        "https://dese.ade.arkansas.gov/Files/2025-2027_CCDF_State_Plan_Final_4.26.24.1REV_OEC.pdf#page=18",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ar.ade.oec.sra.eligibility
        age = person("age", period.this_year)
        is_disabled = person("is_disabled", period.this_year)
        # CCDF State Plan §2.2.1: disabled children eligible up to age 18.
        age_limit = where(is_disabled, p.child_age_limit_disabled, p.child_age_limit)
        return age < age_limit
