from policyengine_us.model_api import *


class ca_riv_general_relief_property_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Meets property limit for Riverside County General Relief"
    definition_period = YEAR
    defined_for = "in_riv"
    reference = "https://web.archive.org/web/20210713051521/http://dpss.co.riverside.ca.us/files/pdf/dpss-general-assistance.pdf#page=1"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.local.ca.riv.general_relief.property
        total_property_value = spm_unit(
            "ca_riv_general_relief_countable_property_value", period
        )
        # The fact sheet's property bullet says the total cannot exceed the
        # limit, so a unit holding exactly the limit is eligible.
        # Inputs are stored as float32, so compare whole cents with the limit.
        return np.round(total_property_value, 2) <= p.limit
