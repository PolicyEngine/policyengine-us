from policyengine_us.model_api import *


class va_529_plan_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia deduction for contributions to 529 plans"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.tax.virginia.gov/deductions",
        "https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/",
    )
    defined_for = StateCode.VA

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.va.tax.income.subtractions.plan_529
        contributions = tax_unit("investment_in_529_plan", period)
        beneficiaries = add(
            tax_unit,
            period,
            ["count_529_contribution_beneficiaries"],
        )
        cap = p.cap * beneficiaries
        return min_(contributions, cap)
