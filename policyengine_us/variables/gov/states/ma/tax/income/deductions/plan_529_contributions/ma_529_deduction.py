from policyengine_us.model_api import *


class ma_529_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Massachusetts 529 plan contribution deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://malegislature.gov/Laws/GeneralLaws/PartI/TitleIX/Chapter62/Section3",
        "https://www.mass.gov/info-details/529-plan-deduction",
    )
    defined_for = StateCode.MA

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.ma.tax.income.deductions.plan_529_contributions
        contributions = tax_unit("investment_in_529_plan", period)
        filing_status = tax_unit("filing_status", period)
        cap = p.cap[filing_status]
        return min_(contributions, cap)
