from policyengine_us.model_api import *


class ut_income_tax_before_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah income tax before credits"
    unit = USD
    defined_for = StateCode.UT
    documentation = "Form TC-40, line 10"
    definition_period = YEAR
    reference = "https://le.utah.gov/xcode/Title59/Chapter10/59-10-S104.html?v=C59-10-S104_2022050420220504"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ut.tax.income
        ut_taxable_income = tax_unit("ut_taxable_income", period)
        return max_(ut_taxable_income * p.rate, 0)
