from policyengine_us.model_api import *


class mi_529_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan 529 plan contribution subtraction"
    unit = USD
    definition_period = YEAR
    reference = (
        "http://legislature.mi.gov/doc.aspx?mcl-206-30",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/IIT/TY2024/MI-1040-Instructions.pdf#page=13",
    )
    defined_for = StateCode.MI

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.mi.tax.income.deductions.plan_529_contributions
        contributions = tax_unit("investment_in_529_plan", period)
        filing_status = tax_unit("filing_status", period)
        cap = p.cap[filing_status]
        return min_(contributions, cap)
