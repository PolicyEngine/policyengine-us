from policyengine_us.model_api import *


class ms_income_tax_before_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Mississippi income tax before credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MS

    def formula(tax_unit, period, parameters):
        income = tax_unit("ms_taxable_income", period)
        rate = parameters(period).gov.states.ms.tax.income.rate
        return rate.calc(income)
