from policyengine_us.model_api import *


class dc_gac_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for DC General Assistance for Children (GAC)"
    definition_period = MONTH
    reference = (
        "https://code.dccouncil.gov/us/dc/council/code/sections/4-205.05a#(c)"
    )
    defined_for = "dc_gac_income_eligible"

    def formula(spm_unit, period, parameters):
        has_eligible_child = (
            add(spm_unit, period, ["dc_gac_eligible_child"]) > 0
        )
        resources_eligible = spm_unit("dc_tanf_resources_eligible", period)

        return has_eligible_child & resources_eligible
