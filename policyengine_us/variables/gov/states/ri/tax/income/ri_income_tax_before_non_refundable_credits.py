from policyengine_us.model_api import *


class ri_income_tax_before_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Rhode Island income tax before refundable credits"
    defined_for = StateCode.RI
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        income = tax_unit("ri_taxable_income", period)
        rate = parameters(period).gov.states.ri.tax.income.rate
        return rate.calc(income)
