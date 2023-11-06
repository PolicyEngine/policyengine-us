from policyengine_us.model_api import *


class mi_retirement_benefits_deduction_tier_one(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan retirement benefits deduction for tier one"
    unit = USD
    definition_period = YEAR
    reference = (
        "http://legislature.mi.gov/doc.aspx?mcl-206-30",  # (1)(f)
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf#page=17",
        "https://www.michigan.gov/taxes/iit/retirement-and-pension-benefits",
    )
    defined_for = "mi_retirement_benefits_deduction_tier_one_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.mi.tax.income.deductions.retirement_benefits.tier_one
        filing_status = tax_unit("filing_status", period)

        person = tax_unit.members
        uncapped_pension_income = person("taxable_pension_income", period)
        military_retirement_pay = person("military_retirement_pay", period)

        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)

        rbd1_amount = p.amount[filing_status] - tax_unit.sum(
            military_retirement_pay * is_head_or_spouse
        )

        return min_(tax_unit.sum(uncapped_pension_income), rbd1_amount)
