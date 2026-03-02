from policyengine_us.model_api import *


class nd_529_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "North Dakota 529 plan contribution subtraction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/north-dakota/2022/title-57/chapter-57-38/section-57-38-30-3/",
        "https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2025-iit/2025-individual-income-tax-booklet.pdf#page=14",
    )
    defined_for = StateCode.ND

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.nd.tax.income.taxable_income.subtractions.plan_529_contributions
        contributions = tax_unit("investment_in_529_plan", period)
        filing_status = tax_unit("filing_status", period)
        cap = p.cap[filing_status]
        return min_(contributions, cap)
