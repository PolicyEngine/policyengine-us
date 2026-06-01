from policyengine_us.model_api import *


class ca_oc_general_relief_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Meets Orange County General Relief resource requirements"
    definition_period = MONTH
    defined_for = "in_oc"
    reference = "https://www.ssa.ocgov.com/sites/ssa/files/2023-04/GR%20Reg%20SECTION%2050%20-%20Approved%20-%20March%202023_0.pdf#page=01"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.local.ca.oc.general_relief.resources
        home_equity = spm_unit("ca_oc_general_relief_home_equity", period.this_year)
        property_value = spm_unit(
            "ca_oc_general_relief_countable_property",
            period.this_year,
        )
        return (home_equity <= p.home_equity_limit) & (
            property_value <= p.property_limit
        )
