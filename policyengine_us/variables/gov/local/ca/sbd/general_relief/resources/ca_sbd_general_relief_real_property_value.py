from policyengine_us.model_api import *


class ca_sbd_general_relief_real_property_value(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    quantity_type = STOCK
    definition_period = YEAR
    label = "San Bernardino County General Relief real property value"
    defined_for = "in_sbd"
    reference = "https://sanbernardino.legistar1.com/sanbernardino/attachments/9e5e1b1a-e577-4f84-92c4-86574a9ff0cf.docx"

    def formula(spm_unit, period, parameters):
        # Combined assessed value of real property; no encumbrances are
        # deducted.
        assessed_value = add(spm_unit, period, ["assessed_property_value"])
        household = spm_unit.household
        vehicle_count = household("household_vehicles_owned", period)
        vehicle_value = household("household_vehicles_value", period)
        average_vehicle_value = where(
            vehicle_count > 0,
            vehicle_value / max_(vehicle_count, 1),
            0,
        )
        # A vehicle used as the principal residence is evaluated as real
        # property; the household-average vehicle value proxies that
        # vehicle's value.
        residence_vehicle_value = (
            household("lives_in_vehicle", period) * average_vehicle_value
        )
        return assessed_value + residence_vehicle_value
