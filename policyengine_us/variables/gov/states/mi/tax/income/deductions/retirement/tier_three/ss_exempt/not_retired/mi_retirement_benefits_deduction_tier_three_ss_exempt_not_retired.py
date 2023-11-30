from policyengine_us.model_api import *


class mi_retirement_benefits_deduction_tier_three_ss_exempt_not_retired(
    Variable
):
    value_type = float
    entity = TaxUnit
    label = "Michigan non-retired tier three retirement benefits deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "http://legislature.mi.gov/doc.aspx?mcl-206-30",  # (9)(d)
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf#page=17",
        "https://www.michigan.gov/taxes/iit/retirement-and-pension-benefits",
    )
    defined_for = "mi_retirement_benefits_deduction_tier_three_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.mi.tax.income.deductions.retirement_benefits.tier_three.ss_exempt.not_retired
        #  Recipients should receive retirement benefits from employment exempt from Social Security
        eligible_people = tax_unit(
            "mi_retirement_benefits_deduction_tier_three_ss_exempt_not_retired_eligible_people",
            period,
        )

        person = tax_unit.members
        uncapped_pension_income = person("taxable_pension_income", period)
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)

        # Head and spouse both are eligible to receive an equal deduction amount
        cap = p.amount * eligible_people

        return min_(
            tax_unit.sum(uncapped_pension_income * is_head_or_spouse), cap
        )
