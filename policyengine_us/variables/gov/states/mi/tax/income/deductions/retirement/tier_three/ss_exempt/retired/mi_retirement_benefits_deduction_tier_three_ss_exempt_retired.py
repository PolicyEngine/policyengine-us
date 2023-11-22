from policyengine_us.model_api import *


class mi_retirement_benefits_deduction_tier_three_ss_exempt_retired(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan retired tier three retirement benefits deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "http://legislature.mi.gov/doc.aspx?mcl-206-30",  # (9)(c)
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf#page=17",
        "https://www.michigan.gov/taxes/iit/retirement-and-pension-benefits",
    )
    defined_for = "mi_retirement_benefits_deduction_tier_three_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.mi.tax.income.deductions.retirement_benefits.tier_three.ss_exempt.retired
        # Recipients should received retirement benefits from SSA exempt employment
        # and were retired before qualifying year
        ss_retired_eligible_person = tax_unit(
            "mi_retirement_benefits_deduction_tier_three_ss_exempt_retired_eligible_count",
            period,
        )

        filing_status = tax_unit("filing_status", period)
        person = tax_unit.members
        uncapped_pension_income = person("taxable_pension_income", period)
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)

        # Where one or two people in the household qualify determines the amount of deduction
        qualified_amount = where(
            ss_retired_eligible_person == 1,
            p.single_qualifying_amount[filing_status],
            p.both_qualifying_amount[filing_status],
        )
        cap = where(
            ss_retired_eligible_person == 0,
            0,
            qualified_amount,
        )

        return min_(
            tax_unit.sum(uncapped_pension_income * is_head_or_spouse), cap
        )
