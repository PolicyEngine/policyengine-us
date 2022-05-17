from openfisca_us.model_api import *


class unreported_payroll_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Unreported payroll taxes from Form 4137 or 8919"
    unit = USD
    definition_period = YEAR
