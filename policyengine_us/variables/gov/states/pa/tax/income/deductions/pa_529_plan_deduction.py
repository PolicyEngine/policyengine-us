from policyengine_us.model_api import *


class pa_529_plan_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Pennsylvania deduction for contributions to 529 plans"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenue-pa.custhelp.com/app/answers/detail/a_id/2208/~/what-is-the-limit-on-a-deduction-to-a-529-plan",
        "https://www.pa529.com/faqs/",
    )
    defined_for = StateCode.PA

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.pa.tax.income.deductions.plan_529
        contributions = tax_unit("investment_in_529_plan", period)
        beneficiaries = add(
            tax_unit,
            period,
            ["count_529_contribution_beneficiaries"],
        )
        cap = p.cap * beneficiaries
        return min_(contributions, cap)
