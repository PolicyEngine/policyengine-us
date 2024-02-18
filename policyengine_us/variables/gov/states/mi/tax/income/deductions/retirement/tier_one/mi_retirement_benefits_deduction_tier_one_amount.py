from policyengine_us.model_api import *


class mi_retirement_benefits_deduction_tier_one_amount(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan retirement benefits deduction amount for tier one, regardless of eligiblity"
    unit = USD
    definition_period = YEAR
    reference = (
        "http://legislature.mi.gov/doc.aspx?mcl-206-30",  # (1)(f)
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf#page=17",
        "https://www.michigan.gov/taxes/iit/retirement-and-pension-benefits",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/4884.pdf#page=2",
    )
    defined_for = StateCode.MI

    # This file computes the Michigan Tier one retirement benefits deduction, regardless
    # of the eligibility, as the amount will be needed for the computation of the tier three
    # retirement benefits deduction
    def formula(tax_unit, period, parameters):
        # Modeled after 2022 MICHIGAN Pension Schedule (Form 4884) Section A
        p = parameters(
            period
        ).gov.states.mi.tax.income.deductions.retirement_benefits.tier_one
        filing_status = tax_unit("filing_status", period)

        private_cap = p.amount[filing_status]  # Line 9
        person = tax_unit.members
        # "Recipients born before 1946 may subtract all qualifying retirement and
        # pension benefits received from federal or Michigan public sources"
        # all public benefits can be deducted
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        military_retirement_pay = (
            person("military_retirement_pay", period) * is_head_or_spouse
        )  # Line 10

        total_military_retirement_pay = tax_unit.sum(military_retirement_pay)
        # the cap is reduced by the amount of military retirement pay
        reduced_private_cap = max_(
            private_cap - total_military_retirement_pay, 0
        )  # Line 11

        public_benefits = (
            person("taxable_public_pension_income", period) * is_head_or_spouse
        )
        total_public_benefit = tax_unit.sum(public_benefits)  # Line 12

        # If your public retirement benefits are greater than the maximum amount,
        # you are not entitled to claim an additional subtraction for private pensions.
        reduced_private_cap_reduced_by_public_benefits = max_(
            reduced_private_cap - total_public_benefit, 0
        )  # Line 13

        uncapped_private_benefits = (
            person("taxable_private_pension_income", period)
            * is_head_or_spouse
        )
        total_uncapped_private_benefits = tax_unit.sum(
            uncapped_private_benefits
        )  # Line 14

        capped_private_benefits = min_(
            reduced_private_cap_reduced_by_public_benefits,
            total_uncapped_private_benefits,
        )  # Line 15

        return capped_private_benefits + total_public_benefit  # Line 16
