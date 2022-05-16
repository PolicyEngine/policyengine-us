from openfisca_us.model_api import *


class excess_payroll_tax_withheld(Variable):
    value_type = float
    entity = TaxUnit
    label = "Excess payroll (FICA/RRTA) tax withheld"
    unit = USD
    definition_period = YEAR
