from policyengine_us.model_api import *


class nj_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey taxable income"
    unit = USD
    documentation = "New Jersey taxable income deductions"
    definition_period = YEAR
    reference = ""
    defined_for = StateCode.NJ
