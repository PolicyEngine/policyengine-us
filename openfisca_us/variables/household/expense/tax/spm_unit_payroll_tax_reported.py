from openfisca_us.model_api import *


class spm_unit_payroll_tax_reported(Variable):
    value_type = float
    entity = SPMUnit
    label = "SPM unit payroll tax (reported)"
    unit = USD
    definition_period = YEAR
