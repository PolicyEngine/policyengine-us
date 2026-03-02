from policyengine_us.model_api import *


class ne_529_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Nebraska 529 plan contribution subtraction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.nebraskalegislature.gov/laws/statutes.php?statute=77-2716",
        "https://revenue.nebraska.gov/sites/default/files/doc/tax-forms/2025/f_Individual_Income_Tax_Booklet.pdf#page=26",
    )
    defined_for = StateCode.NE

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.ne.tax.income.agi.subtractions.plan_529_contributions
        contributions = tax_unit("investment_in_529_plan", period)
        filing_status = tax_unit("filing_status", period)
        cap = p.cap[filing_status]
        return min_(contributions, cap)
