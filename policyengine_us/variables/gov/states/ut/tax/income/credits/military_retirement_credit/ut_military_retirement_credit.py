from policyengine_us.model_api import *


class ut_military_retirement_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah military retirement credit"
    unit = USD
    definition_period = YEAR
    reference = "https://le.utah.gov/xcode/Title59/Chapter10/59-10-S1043.html"
    defined_for = "ut_military_retirement_credit_eligible"

    def formula(tax_unit, period, parameters):
        military_retirement_pay = add(
            tax_unit, period, ["military_retirement_pay"]
        )
        p = parameters(
            period
        ).gov.states.ut.tax.income.credits.military_retirement
        return military_retirement_pay * p.rate
