from policyengine_us.model_api import *


class ca_marin_general_relief_countable_vehicle_value(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    quantity_type = STOCK
    definition_period = YEAR
    label = "Marin County General Relief countable vehicle value"
    defined_for = "in_marin"
    reference = "https://marin.granicus.com/DocumentViewer.php?file=marin_ce4ed1aaf509aaf7176c360d26f8f1c6.pdf#page=11"

    def formula(spm_unit, period, parameters):
        # The Standards exempt one motor vehicle used for transportation
        # regardless of value, and a second if used by the applicant as a
        # home; further vehicles count at market value. We use the
        # household-average vehicle value as a proxy for each vehicle's
        # value.
        p = parameters(period).gov.local.ca.marin.general_relief.eligibility
        household = spm_unit.household
        vehicle_count = household("household_vehicles_owned", period)
        vehicle_value = household("household_vehicles_value", period)
        average_vehicle_value = where(
            vehicle_count > 0,
            vehicle_value / max_(vehicle_count, 1),
            0,
        )
        exempt_vehicles = p.vehicle_exemption + household("lives_in_vehicle", period)
        countable_vehicles = max_(vehicle_count - exempt_vehicles, 0)
        return countable_vehicles * average_vehicle_value
