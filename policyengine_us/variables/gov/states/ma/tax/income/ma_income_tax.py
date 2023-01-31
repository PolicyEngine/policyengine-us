from policyengine_us.model_api import *


class ma_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA income tax"
    unit = USD
    documentation = "Massachusetts State income tax."
    definition_period = YEAR
    reference = "https://www.mass.gov/doc/2021-form-1-massachusetts-resident-income-tax-return/download"
    defined_for = StateCode.MA
    adds = ["ma_income_tax_before_refundable_credits"]
    subtracts = ["ma_refundable_credits"]
