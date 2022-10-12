from policyengine_us.model_api import *


class ut_income_tax_before_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah Income Tax Before Credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.UT

    def formula(tax_unit, period, parameters):
        rate = parameters(period).gov.states.ut.tax.income.rate
        income = tax_unit("ut_taxable_income", period)
        return max_(rate * income, 0)
