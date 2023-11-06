from policyengine_us.model_api import *


class mi_standard_deduction_tier_two(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan tier two standard deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "http://legislature.mi.gov/doc.aspx?mcl-206-30",  # (9)(b) & (c)
        "https://www.michigan.gov/taxes/iit/retirement-and-pension-benefits/michigan-standard-deduction",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf#page=15",
    )
    defined_for = "mi_standard_deduction_tier_two_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.mi.tax.income.deductions.standard.tier_two
        filing_status = tax_unit("filing_status", period)

        ssa_eligible = tax_unit(
            "mi_standard_deduction_tier_two_increase_eligible", period
        )

        person = tax_unit.members
        uncapped_pension_income = person("taxable_pension_income", period)
        military_retirement_pay = person("military_retirement_pay", period)
        military_service_income = person("military_service_income", period)

        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)

        reductions = tax_unit.sum(
            (military_retirement_pay + military_service_income)
            * is_head_or_spouse
        )
        sd2_amount = max_(
            p.amount.capped_deduction[filing_status]
            + p.amount.increase * ssa_eligible
            - reductions,
            0,
        )

        return min_(tax_unit.sum(uncapped_pension_income), sd2_amount)
