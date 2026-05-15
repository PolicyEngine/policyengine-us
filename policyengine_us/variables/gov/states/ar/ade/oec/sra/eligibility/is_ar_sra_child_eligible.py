from policyengine_us.model_api import *


class is_ar_sra_child_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for Arkansas SRA"
    definition_period = MONTH
    defined_for = StateCode.AR
    reference = (
        "https://dese.ade.arkansas.gov/Files/FSU-Procedural-Manual-June-2023_UPDATED_20230629075344.pdf#page=14",
        "https://www.publichealthlawcenter.org/sites/default/files/Arkansas%20Title%20016%20Division%2022%20Rule%208.pdf#page=11",
    )

    def formula(person, period, parameters):
        age_eligible = person("is_ar_sra_age_eligible", period)
        immigration_eligible = person(
            "is_ccdf_immigration_eligible_child", period.this_year
        )
        return age_eligible & immigration_eligible
