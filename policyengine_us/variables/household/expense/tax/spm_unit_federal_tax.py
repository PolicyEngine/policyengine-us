from policyengine_us.model_api import *


class spm_unit_federal_tax(Variable):
    value_type = float
    entity = SPMUnit
    label = "Federal income tax"
    definition_period = YEAR
    unit = USD

    def formula(spm_unit, period, parameters):
        return sum_contained_tax_units("income_tax", spm_unit, period)
