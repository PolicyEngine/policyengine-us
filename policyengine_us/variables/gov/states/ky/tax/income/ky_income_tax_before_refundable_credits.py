from policyengine_us.model_api import *


class ky_income_tax_before_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kentucky income tax before refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.KY

    def formula(tax_unit, period, paramters):
        income = tax_unit("ky_taxable_income", period)
        rate = paramters(period).gov.states.ky.tax.income.rate
        return income * rate
