from policyengine_us.model_api import *


class ca_oc_general_relief_countable_vehicle_value(Variable):
    value_type = float
    entity = SPMUnit
    label = "Orange County General Relief countable vehicle value"
    unit = USD
    quantity_type = STOCK
    definition_period = YEAR
    defined_for = "in_oc"
    reference = "https://www.ssa.ocgov.com/sites/ssa/files/2023-04/GR%20Reg%20SECTION%2060%20-%20Approved%20-%20March%202023_0.pdf#page=02"

    def formula(spm_unit, period, parameters):
        # The exclusion amount comes off the vehicle value; the rest counts
        # (Sec 60.4.c). We use total household vehicle value as a proxy for the
        # one-vehicle rule.
        p = parameters(period).gov.local.ca.oc.general_relief.resources
        vehicle_value = spm_unit.household("household_vehicles_value", period)
        return max_(vehicle_value - p.vehicle_exclusion, 0)
