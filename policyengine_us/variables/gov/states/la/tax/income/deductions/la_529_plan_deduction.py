from policyengine_us.model_api import *


class la_529_plan_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Louisiana deduction for contributions to 529 plans"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.startsaving.la.gov/startfaqs.aspx",
        "https://law.justia.com/codes/louisiana/revised-statutes/title-47/rs-47-293/",
    )
    defined_for = StateCode.LA

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.la.tax.income.deductions.plan_529
        contributions = tax_unit("investment_in_529_plan", period)
        filing_status = tax_unit("filing_status", period)
        beneficiaries = add(
            tax_unit,
            period,
            ["count_529_contribution_beneficiaries"],
        )
        cap = p.cap[filing_status] * beneficiaries
        return min_(contributions, cap)
