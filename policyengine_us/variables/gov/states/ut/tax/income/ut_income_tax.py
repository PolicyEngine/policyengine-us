from policyengine_us.model_api import *


class ut_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah income tax"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        ut_income_tax_before_credits = tax_unit(
            "ut_income_tax_before_credits", period
        )
        ut_taxpayer_credit = tax_unit("ut_taxpayer_credit", period)
        return max_(ut_income_tax_before_credits - ut_taxpayer_credit, 0)
