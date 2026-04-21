from policyengine_us.model_api import *


class in_529_plan_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Indiana tax credit for contributions to CollegeChoice 529 plans"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/indiana/title-6/article-3/chapter-3/section-6-3-3-12/",
        "https://www.in.gov/dor/files/ib98.pdf",
    )
    defined_for = StateCode.IN

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states["in"].tax.income.credits.plan_529
        contributions = tax_unit("investment_in_529_plan", period)
        credit = contributions * p.rate
        filing_status = tax_unit("filing_status", period)
        cap = p.cap[filing_status]
        return min_(credit, cap)
