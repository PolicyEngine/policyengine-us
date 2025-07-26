from policyengine_us.model_api import *


class dc_tanf_demographic_eligible_person(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Eligible person for DC Temporary Assistance for Needy Families (TANF) based on demographics"
    reference = (
        "https://code.dccouncil.gov/us/dc/council/code/sections/4-205.18",
        "https://code.dccouncil.gov/us/dc/council/code/sections/4-205.63",
    )
    defined_for = StateCode.DC

    def formula(person, period, parameters):
        pap_eligible_child = person("dc_pap_eligible_child", period)
        related_to_head_or_spouse = person(
            "is_related_to_head_or_spouse", period
        )
        pregnant = person("is_pregnant", period)
        immigration_status_eligible = person(
            "dc_tanf_immigration_status_eligible_person", period
        )

        return (pap_eligible_child & related_to_head_or_spouse) | (
            pregnant & immigration_status_eligible
        )
