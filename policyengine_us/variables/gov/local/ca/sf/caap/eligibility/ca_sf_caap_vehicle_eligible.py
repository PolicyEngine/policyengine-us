from policyengine_us.model_api import *


class ca_sf_caap_vehicle_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Meets motor vehicle requirements for San Francisco County CAAP"
    definition_period = MONTH
    defined_for = "in_san_francisco"
    reference = "https://www.sfhsa.org/sites/default/files/media/document/2026-07/manual_caap_eligibility_7_6_2026.pdf#page=222"

    def formula(spm_unit, period, parameters):
        # Per Manual 92-26, each client may own at most one vehicle (one per
        # person in couples cases) with equity within the CalWORKs maximum
        # vehicle value under WIC Section 11155(c). We use the
        # household-average vehicle value as a proxy for each vehicle's
        # equity (encumbrances are not modeled).
        p = parameters(period).gov.local.ca.sf.caap.eligibility.vehicle
        p_calworks = parameters(period).gov.states.ca.cdss.tanf.cash.resources.limit
        household = spm_unit.household
        vehicle_count = household("household_vehicles_owned", period.this_year)
        vehicle_value = household("household_vehicles_value", period.this_year)
        average_vehicle_value = where(
            vehicle_count > 0,
            vehicle_value / max_(vehicle_count, 1),
            0,
        )
        # The allowance counts the adults present, not just budget unit
        # members: an SSI/CAPI-excluded spouse's vehicle still appears in
        # household_vehicles_owned but may be owned by that spouse, whom
        # Manual 92-26 also allows one vehicle.
        adult_count = spm_unit("spm_unit_count_adults", period.this_year)
        allowed_vehicles = where(adult_count >= 2, p.limit.couple, p.limit.single)
        return (vehicle_count <= allowed_vehicles) & (
            average_vehicle_value <= p_calworks.vehicle
        )
