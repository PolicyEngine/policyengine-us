from policyengine_us.model_api import *


class ca_oc_general_relief_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Meets Orange County General Relief resource requirements"
    definition_period = MONTH
    defined_for = "in_oc"
    reference = "https://www.ssa.ocgov.com/sites/ssa/files/2023-04/GR%20Reg%20SECTION%2060%20-%20Approved%20-%20March%202023_0.pdf#page=01"

    def formula(spm_unit, period, parameters):
        # Countable personal property -- cash plus any non-excluded vehicle --
        # must not exceed the limit (Sec 60.2.a).
        p = parameters(period).gov.local.ca.oc.general_relief.resources
        countable_property = spm_unit(
            "ca_oc_general_relief_countable_property", period.this_year
        )
        return countable_property <= p.property_limit
