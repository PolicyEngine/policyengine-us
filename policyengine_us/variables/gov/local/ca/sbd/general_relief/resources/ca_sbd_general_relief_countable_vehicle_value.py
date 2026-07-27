from policyengine_us.model_api import *


class ca_sbd_general_relief_countable_vehicle_value(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    quantity_type = STOCK
    definition_period = YEAR
    label = "San Bernardino County General Relief countable vehicle value"
    defined_for = "in_sbd"
    reference = (
        "https://sanbernardino.legistar1.com/sanbernardino/attachments/39fc00fa-7256-4849-9f07-7710402996f1.docx",
        "https://sanbernardino.legistar1.com/sanbernardino/attachments/9e5e1b1a-e577-4f84-92c4-86574a9ff0cf.docx",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.local.ca.sbd.general_relief.resources
        household = spm_unit.household
        vehicle_count = household("household_vehicles_owned", period)
        vehicle_value = household("household_vehicles_value", period)
        # The first $3,000 of each vehicle's net market value is exempt and
        # the balance counts toward the personal property limit; the
        # household-average vehicle value proxies each vehicle's value.
        average_vehicle_value = where(
            vehicle_count > 0,
            vehicle_value / max_(vehicle_count, 1),
            0,
        )
        # A vehicle used as the principal residence is evaluated as real
        # property instead of personal property.
        residence_vehicles = household("lives_in_vehicle", period)
        countable_vehicles = max_(vehicle_count - residence_vehicles, 0)
        return max_(average_vehicle_value - p.vehicle_exemption, 0) * (
            countable_vehicles
        )
