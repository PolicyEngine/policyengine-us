from policyengine_us.model_api import *


class or_529_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Oregon 529 plan contribution credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.oregon.gov/dor/programs/individuals/pages/credits.aspx",
        "https://oregon.public.law/statutes/ors_315.643",
    )
    defined_for = StateCode.OR

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states["or"].tax.income.credits.plan_529
        contributions = tax_unit("investment_in_529_plan", period)
        filing_status = tax_unit("filing_status", period)
        max_credit = p.max_credit[filing_status]
        return min_(contributions, max_credit)
