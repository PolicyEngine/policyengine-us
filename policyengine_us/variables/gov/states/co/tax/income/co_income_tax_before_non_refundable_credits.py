from policyengine_us.model_api import *


class co_income_tax_before_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado income tax before non-refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CO

    def formula(tax_unit, period, parameters):
        income = tax_unit("co_taxable_income", period)
        rate = parameters(period).gov.states.co.tax.income.rate
        return income * rate
