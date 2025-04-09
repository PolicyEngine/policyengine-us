from policyengine_us.model_api import *


class il_aabd_asset_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Eligible for Illinois Aid to the Aged, Blind or Disabled (AABD) due to asset"
    reference = (
        "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-113.141",
    )
    defined_for = StateCode.IL

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.il.dhs.aabd.asset
        size = spm_unit("spn_unit_size", period)
        countable_asset = spm_unit(
            "il_aabd_countable_asset", period
        )  # ssi_countable_resources
        p1 = p.asset_disregard.base[size]
        pn = p.asset_disregard.additional
        asset_disregard = p1 + pn * (size - 2)

        # Exempt one vehicle up to $4500 in household
        vehicle_count = spm_unit.household("household_vehicles_owned", period)
        total_vehicle_value = spm_unit.household(
            "household_vehicles_value", period
        )
        avg_vehicle_value = np.zeros_like(vehicle_count)
        mask = vehicle_count != 0
        avg_vehicle_value[mask] = (
            total_vehicle_value[mask] / vehicle_count[mask]
        )
        has_vehicle = vehicle_count >= 1
        exempt_vehicle_value = min_(
            avg_vehicle_value, p.vehicle_exemption.amount
        )
        vehicle_exemption = where(has_vehicle, exempt_vehicle_value, 0)

        non_exempt_asset = max_(countable_asset - vehicle_exemption, 0)
        return non_exempt_asset <= asset_disregard


# TODO: Applicant can exclude one vehicle completely regardless of value under conditions.
