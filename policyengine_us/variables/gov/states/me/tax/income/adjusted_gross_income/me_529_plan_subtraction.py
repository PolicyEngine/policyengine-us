from policyengine_us.model_api import *


class me_529_plan_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maine subtraction for contributions to 529 plans"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://legislature.maine.gov/legis/bills/getPDF.asp?paper=SP0031&item=5&snum=130",
        "https://www.nextgenforme.com/maine-state-tax-deduction/",
    )
    defined_for = StateCode.ME

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.me.tax.income.agi.subtractions.plan_529
        contributions = tax_unit("investment_in_529_plan", period)
        beneficiaries = add(
            tax_unit,
            period,
            ["count_529_contribution_beneficiaries"],
        )
        cap = p.cap * beneficiaries
        # Income eligibility
        agi = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period)
        agi_limit = p.agi_limit[filing_status]
        eligible = agi < agi_limit
        return eligible * min_(contributions, cap)
