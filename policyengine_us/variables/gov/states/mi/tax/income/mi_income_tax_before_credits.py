from policyengine_us.model_api import *


class mi_income_tax_before_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan income tax before credits"
    defined_for = StateCode.MI
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        taxable_income = tax_unit("mi_taxable_income", period)
        rate = parameters(period).gov.states.mi.tax.income.rate
        return taxable_income * rate
