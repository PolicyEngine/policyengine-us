from policyengine_us.model_api import *


class il_529_plan_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Illinois subtraction for contributions to 529 plans"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.illinois.gov/questionsandanswers/answer.206.html",
        "https://brightstart.com/account/illinois-taxpayer-guide/",
    )
    defined_for = StateCode.IL

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.il.tax.income.subtractions.plan_529
        contributions = tax_unit("investment_in_529_plan", period)
        filing_status = tax_unit("filing_status", period)
        cap = p.cap[filing_status]
        return min_(contributions, cap)
