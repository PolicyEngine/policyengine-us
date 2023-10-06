from policyengine_us.model_api import *


class mi_retirement_benefits_deduction_tier_three_retired(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan retirement benefits deduction for tier three qualifying both SSA and retirement year"
    unit = USD
    definition_period = YEAR
    reference = (
        "http://legislature.mi.gov/doc.aspx?mcl-206-30",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf#page=17",
        "https://www.michigan.gov/taxes/iit/retirement-and-pension-benefits",
    )
    defined_for = "mi_retirement_benefits_deduction_tier_three_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.mi.tax.income.deductions.retirement_benefits.tier_three

        ssa_eligible = tax_unit(
            "mi_retirement_benefits_deduction_tier_three_ssa_eligible", period
        )
        retired_eligible = tax_unit(
            "mi_retirement_benefits_deduction_tier_three_retired_eligible",
            period,
        )

        filing_status = tax_unit("filing_status", period)
        person = tax_unit.members
        uncapped_pension_income = person("taxable_pension_income", period)

        rbd3_retired_amount = retired_eligible * (
            p.retired_amount[filing_status]
            + p.amount * min_(ssa_eligible, retired_eligible)
        )

        return min_(tax_unit.sum(uncapped_pension_income), rbd3_retired_amount)
