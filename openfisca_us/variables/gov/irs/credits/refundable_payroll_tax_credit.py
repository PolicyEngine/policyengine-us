from openfisca_us.model_api import *


class refundable_payroll_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Refundable payroll tax credit"
    unit = USD
