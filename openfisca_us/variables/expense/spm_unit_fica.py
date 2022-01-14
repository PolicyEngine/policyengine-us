from openfisca_us.model_api import *


class spm_unit_fica(Variable):
    value_type = float
    entity = SPMUnit
    label = "SPM unit total FICA"
    definition_period = YEAR
    unit = USD

    def formula(spm_unit, period, parameters):
        return sum_contained_tax_units("employee_payrolltax", spm_unit, period)
