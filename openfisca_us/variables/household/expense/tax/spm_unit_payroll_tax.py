from openfisca_us.model_api import *


class spm_unit_payroll_tax(Variable):
    value_type = float
    entity = SPMUnit
    label = "Payroll tax"
    definition_period = YEAR
    unit = USD

    def formula(spm_unit, period, parameters):
        return sum_contained_tax_units(
            "employee_payroll_tax", spm_unit, period
        )
