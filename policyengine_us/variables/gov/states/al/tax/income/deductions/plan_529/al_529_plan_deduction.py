from policyengine_us.model_api import *


class al_529_plan_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Alabama deduction for contributions to 529 plans"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/alabama/title-16/chapter-33c/section-16-33c-16/",
        "https://collegecounts529.com/tax-benefits/",
    )
    defined_for = StateCode.AL

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.al.tax.income.deductions.plan_529
        contributions = tax_unit("investment_in_529_plan", period)
        filing_status = tax_unit("filing_status", period)
        cap = p.cap[filing_status]
        return min_(contributions, cap)
