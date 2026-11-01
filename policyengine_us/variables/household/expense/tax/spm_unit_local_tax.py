from policyengine_us.model_api import *


class spm_unit_local_tax(Variable):
    value_type = float
    entity = SPMUnit
    label = "Local tax"
    documentation = "Local income and occupational taxes net of refundable credits."
    definition_period = YEAR
    unit = USD

    def formula(spm_unit, period, parameters):
        return sum_contained_tax_units("local_tax", spm_unit, period)
