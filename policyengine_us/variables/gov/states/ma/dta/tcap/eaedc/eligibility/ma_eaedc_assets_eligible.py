from policyengine_us.model_api import *


class ma_eaedc_assets_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Assets eligible for Massachusetts EAEDC"
    definition_period = YEAR
    defined_for = StateCode.MA
    reference = (
        "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-110"
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ma.dta.tcap.eaedc.assets
        countable_assets = add(spm_unit, period, ["ma_eaedc_assets"])
        vehicle_value = spm_unit.household("household_vehicles_value", period)
        countable_vehicle_value = max(vehicle_value - p.vehicle_exemption, 0)
        total_assets = countable_assets + countable_vehicle_value
        return total_assets <= p.limit
