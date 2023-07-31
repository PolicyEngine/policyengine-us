from policyengine_us.model_api import *


class de_income_tax_before_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Delaware personal income tax before refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DE

    def formula(tax_unit, period, parameters):
        income = tax_unit("de_taxable_income", period)
        return parameters(period).gov.states.de.tax.income.rate.calc(income)
