from policyengine_us.model_api import *


class mi_retirement_benefits_deduction_expanded(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan expanded retirement benefits deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "http://legislature.mi.gov/doc.aspx?mcl-206-30",  # (10)
        "https://www.michigan.gov/taxes/iit/retirement-and-pension-benefits/michigan-standard-deduction",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2023/2023-IIT-Forms/BOOK_MI-1040.pdf#page=22",
    )
    defined_for = "mi_retirement_benefits_deduction_expanded_eligible"

    def formula(tax_unit, period, parameters):
        # Modeled after 2023 MICHIGAN Pension Schedule (Form 4884) Section D
        p = parameters(
            period
        ).gov.states.mi.tax.income.deductions.retirement_benefits.expanded

        filing_status = tax_unit("filing_status", period)
        person = tax_unit.members
        uncapped_pension_income = person("taxable_pension_income", period)
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)

        uncapped_head_or_spouse_pension = tax_unit.sum(
            uncapped_pension_income * is_head_or_spouse
        )
        cap = min_(uncapped_head_or_spouse_pension, p.amount[filing_status])

        # Modeled after Worksheet 3.3 Retirement and Pension Benefits Subtraction for Section D of Form 4884

        # If a filer is recieving military retirement pay, the calculation includes the smaller of
        # a part of tier one or tier three deduction amount
        p2 = parameters(
            period
        ).gov.states.mi.tax.income.deductions.retirement_benefits.tier_one
        tier_one_cap = p2.amount[filing_status]  # Line 1
        military_retirement_pay = (
            person("military_retirement_pay", period) * is_head_or_spouse
        )
        total_military_retirement_pay = tax_unit.sum(
            military_retirement_pay
        )  # Line 2
        military_retirement_pay_eligible = total_military_retirement_pay > 0

        # the cap is reduced by the amount of military retirement pay
        reduced_tier_one_cap = max_(
            tier_one_cap - total_military_retirement_pay, 0
        )  # Line 3
        multiplited_tier_one_cap = reduced_tier_one_cap * p.rate  # Line 4
        smaller_of_cap_or_benefits = min_(
            multiplited_tier_one_cap, uncapped_head_or_spouse_pension
        )  # Line 6

        return where(
            military_retirement_pay_eligible,
            smaller_of_cap_or_benefits,
            cap,
        )  # Line 19
