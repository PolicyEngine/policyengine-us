from policyengine_us.model_api import *


class dc_gac_eligible_child(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Eligible child for DC General Assistance for Children (GAC) based on demographics"
    reference = (
        "https://code.dccouncil.gov/us/dc/council/code/sections/4-205.05a"
    )
    defined_for = StateCode.DC

    def formula(person, period, parameters):
        eligible_child = person("dc_pap_eligible_child", period)
        related_to_head_or_spouse = person(
            "is_dc_tanf_related_to_head_or_spouse", period
        )
        return ~related_to_head_or_spouse & eligible_child
