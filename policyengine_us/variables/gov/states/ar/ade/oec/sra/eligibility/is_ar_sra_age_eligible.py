from policyengine_us.model_api import *


class is_ar_sra_age_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Age-eligible for Arkansas SRA"
    definition_period = MONTH
    defined_for = StateCode.AR
    reference = (
        "https://www.publichealthlawcenter.org/sites/default/files/Arkansas%20Title%20016%20Division%2022%20Rule%208.pdf#page=11",
        "https://dese.ade.arkansas.gov/Files/FSU-Procedural-Manual-June-2023_UPDATED_20230629075344.pdf#page=13",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ar.ade.oec.sra.eligibility
        age = person("age", period.this_year)
        return age < p.child_age_limit
