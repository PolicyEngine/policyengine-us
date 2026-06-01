from policyengine_us.model_api import *


class ca_oc_general_relief_countable_vehicle_value(Variable):
    value_type = float
    entity = SPMUnit
    label = "Orange County General Relief countable vehicle value"
    documentation = (
        "Uses total household vehicle equity as a proxy for the net value of one "
        "vehicle per Orange County General Relief economic unit."
    )
    unit = USD
    quantity_type = STOCK
    definition_period = YEAR
    defined_for = "in_oc"
    reference = "https://www.ssa.ocgov.com/sites/ssa/files/2023-04/GR%20Reg%20SECTION%2060%20-%20Approved%20-%20March%202023_0.pdf#page=02"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.local.ca.oc.general_relief.resources
        vehicle_equity = spm_unit.household("household_vehicles_equity", period)
        return where(vehicle_equity <= p.vehicle_exclusion, 0, vehicle_equity)
