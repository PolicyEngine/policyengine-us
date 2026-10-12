from policyengine_us.model_api import *


class ca_tanf_countable_vehicle_value(Variable):
    value_type = float
    entity = SPMUnit
    label = "California CalWORKs countable vehicle value"
    unit = USD
    definition_period = YEAR
    quantity_type = STOCK
    defined_for = StateCode.CA
    reference = (
        "https://www.cdss.ca.gov/Portals/9/Additional-Resources/Letters-and-Notices/ACLs/2026/26-38.pdf#page=3",
        "https://www.cdss.ca.gov/Portals/9/Additional-Resources/Letters-and-Notices/ACLs/2025/25-37.pdf#page=3",
    )

    def formula(spm_unit, period, parameters):
        # NOTE: The ACL applies the limit to each vehicle's equity value
        # (market value less encumbrances) and fully exempts certain vehicles;
        # we apply it once to the household-level total vehicle market value.
        vehicle_value = spm_unit.household("household_vehicles_value", period)
        p = parameters(period).gov.states.ca.cdss.tanf.cash.resources.limit
        return max_(vehicle_value - p.vehicle, 0)
