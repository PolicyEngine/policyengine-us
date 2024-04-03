from policyengine_us.model_api import *


class mi_expanded_retirement_benefits_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan expanded retirement benefits deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "http://legislature.mi.gov/doc.aspx?mcl-206-30",  # (10)
        "https://www.michigan.gov/taxes/iit/retirement-and-pension-benefits/michigan-standard-deduction",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2023/2023-IIT-Forms/BOOK_MI-1040.pdf#page=25",
    )
    defined_for = "mi_expanded_retirement_benefits_deduction_eligible"

    def formula(tax_unit, period, parameters):
        # Modeled after 2023 MICHIGAN Pension Schedule (Form 4884) Section D
        p = parameters(
            period
        ).gov.states.mi.tax.income.deductions.retirement_benefits

        filing_status = tax_unit("filing_status", period)
        person = tax_unit.members
        uncapped_pension_income = person("taxable_pension_income", period)
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        uncapped_head_or_spouse_pension = tax_unit.sum(
            uncapped_pension_income * is_head_or_spouse
        )

        # Modeled after Worksheet 3.3 Retirement and Pension Benefits Subtraction for Section D of Form 4884

        # If a filer is recieving military retirement pay, the calculation includes the smaller of
        # a part of tier one or expanded deduction amount
        # Line 1
        tier_one_cap = p.tier_one.amount[filing_status]
        head_or_spouse_military_retirement_pay = (
            person("military_retirement_pay", period) * is_head_or_spouse
        )
        # Line 2
        total_military_retirement_pay = tax_unit.sum(
            head_or_spouse_military_retirement_pay
        )
        received_military_retirement_pay = total_military_retirement_pay > 0
        # the cap is reduced by the amount of military retirement pay
        # Line 3
        reduced_tier_one_cap = max_(
            tier_one_cap - total_military_retirement_pay, 0
        )
        # Line 4
        applicable_tier_one_cap = reduced_tier_one_cap * p.expanded.rate
        # Line 6
        capped_benefit_amount = min_(
            applicable_tier_one_cap, uncapped_head_or_spouse_pension
        )

        # Expanded deduction amount
        capped_head_or_spouse_pension_income = min_(
            uncapped_head_or_spouse_pension, tier_one_cap * p.expanded.rate
        )

        # Line 19
        return where(
            received_military_retirement_pay,
            capped_benefit_amount,
            capped_head_or_spouse_pension_income,
        )
