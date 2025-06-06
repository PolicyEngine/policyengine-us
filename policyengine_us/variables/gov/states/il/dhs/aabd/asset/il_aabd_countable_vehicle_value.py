from policyengine_us.model_api import *


class il_aabd_countable_vehicle_value(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    label = "Illinois Aid to the Aged, Blind or Disabled (AABD) countable vehicles value"
    reference = (
        "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-113.141",
    )
    defined_for = StateCode.IL

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.il.dhs.aabd.asset.vehicle_exemption
        vehicle_count = spm_unit.household("household_vehicles_owned", period)
        total_vehicle_value = (
            spm_unit.household("household_vehicles_value", period)
            * MONTHS_IN_YEAR
        )
        avg_vehicle_value = np.zeros_like(vehicle_count)
        mask = vehicle_count != 0
        avg_vehicle_value[mask] = (
            total_vehicle_value[mask] / vehicle_count[mask]
        )
        vehicle_is_essential = spm_unit("il_aabd_vehicle_is_essential", period)
        # Household can exclude one vehicle completely regardless of value if it has an essential vehicle.
        full_exemption = avg_vehicle_value
        # If household does not meet essential vehicle requirements, exempt one vehicle up to $4500 in household
        partial_exemption = min_(avg_vehicle_value, p.amount)
        vehicle_exemption = where(
            vehicle_is_essential, full_exemption, partial_exemption
        )
        return max_(total_vehicle_value - vehicle_exemption, 0)
