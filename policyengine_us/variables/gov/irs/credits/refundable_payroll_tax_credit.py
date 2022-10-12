from policyengine_us.model_api import *


class refundable_payroll_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Refundable Payroll Tax Credit"
    unit = USD


rptc = variable_alias("rptc", refundable_payroll_tax_credit)
