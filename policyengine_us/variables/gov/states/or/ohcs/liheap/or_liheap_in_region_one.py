from policyengine_us.model_api import *


class or_liheap_in_region_one(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    defined_for = StateCode.OR
    label = (
        "Whether the househld located in region one under the Oregon LIHEAP"
    )
    reference = "https://www.oregon.gov/ohcs/energy-weatherization/Documents/2021-Energy-Assistance-Manual.pdf#page=55"

    def formula(spm_unit, period, parameters):
        county = spm_unit.household("county_str", period)
        p = parameters(period).gov.states["or"].ohcs.liheap
        return county in p.region_one_counties
