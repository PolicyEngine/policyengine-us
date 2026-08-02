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
        # deducted. A vehicle used as the principal residence is evaluated
        # as real property.
        assessed_value = add(spm_unit, period, ["assessed_property_value"])
        household = spm_unit.household
        lives_in_vehicle = household("lives_in_vehicle", period)
        vehicle_value = household("household_vehicles_value", period)
        return assessed_value + lives_in_vehicle * vehicle_value
