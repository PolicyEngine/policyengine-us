from policyengine_us.model_api import *


class ut_income_tax_before_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah income tax before credits"
    unit = USD
    defined_for = StateCode.UT
    documentation = "Form TC-40, line 10"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        ut_taxable_income = tax_unit("ut_taxable_income", period)
        total_tax = (
            ut_taxable_income
            * parameters(period).gov.states.ut.tax.income.rate
        )
        return max_(total_tax, 0)
