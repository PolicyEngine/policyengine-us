from policyengine_us.model_api import *


class ca_riv_general_relief_property_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Meets property limit for Riverside County General Relief"
    definition_period = YEAR
    defined_for = "in_riv"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.local.ca.riv.general_relief.property
        total_property_value = spm_unit(
            "ca_riv_general_relief_countable_property_value", period
        )
        return total_property_value < p.limit
