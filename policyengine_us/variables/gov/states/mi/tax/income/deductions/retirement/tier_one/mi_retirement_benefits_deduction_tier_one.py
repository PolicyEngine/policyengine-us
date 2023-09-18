from policyengine_us.model_api import *


class mi_retirement_benefits_deduction_tier_one(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan retirement benefits deduction for tier one"
    unit = USD
    definition_period = YEAR
    reference = (
        "http://legislature.mi.gov/doc.aspx?mcl-206-30",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf#page=17",
        "https://www.michigan.gov/taxes/iit/retirement-and-pension-benefits",
    )
    defined_for = StateCode.MI

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.mi.tax.income.deductions.retirement_benefits.tier_one
        # Core deduction based on filing status.
        filing_status = tax_unit("filing_status", period)

        age_eligibility = tax_unit(
            "mi_retirement_benefits_deduction_tier_one_eligible", period
        )
        max_amount = p.amount[filing_status]

        # add all qualifying retirement and pension benefits received from federal or Michigan public sources
        # are uncapped
        public_pension_income = tax_unit(
            "taxable_public_pension_income", period
        )
        # All private penion income is capped at a certain amount
        uncapped_private_pension_income = tax_unit(
            "taxable_private_pension_income", period
        )
        capped_private_pension_income = max_(
            max_amount, uncapped_private_pension_income
        )
        total_pension_income = (
            public_pension_income + capped_private_pension_income
        )
        return age_eligibility * total_pension_income
