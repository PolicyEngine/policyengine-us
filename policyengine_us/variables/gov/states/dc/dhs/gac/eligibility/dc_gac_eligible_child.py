from policyengine_us.model_api import *


class dc_gac_eligible_child(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Eligible child for DC General Assistance for Children (GAC) based on demographics"
    reference = (
        "https://code.dccouncil.gov/us/dc/council/code/sections/4-205.05a"
    )
    defined_for = "dc_pap_eligible_child"

    def formula(person, period, parameters):
        return ~person("is_related_to_head_or_spouse", period)
