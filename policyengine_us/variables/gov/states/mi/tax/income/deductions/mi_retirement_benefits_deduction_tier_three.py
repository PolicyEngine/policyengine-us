from policyengine_us.model_api import *


class mi_retirement_benefits_deduction_tier_three(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan standard deduction"
    unit = USD
    definition_period = YEAR
    documentation = "Michigan retirement and pension benefits for age 62-66."
    reference = (
        "http://legislature.mi.gov/doc.aspx?mcl-206-30",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf?rev=86a928564e3f42449c531309673f5da7&hash=7147C48E7C9B1B8171B72DC34A66642A",
        "https://www.michigan.gov/taxes/iit/retirement-and-pension-benefits",
    )
    defined_for = StateCode.MI

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.mi.tax.income.deductions.retirement_benefits.tier_three
        # Core deduction based on filing status.
        filing_status = tax_unit("filing_status", period)

        age_older = tax_unit("greater_age_head_spouse", period)
        # Retirement Benefits Deduction Tier 3
        rb3_age_eligibility = (age_older >= p.min_age) & (
            age_older <= p.max_age
        )
        rb3_amount = p.amount[filing_status]

        return (
            rb3_age_eligibility
            * rb3_amount
            * (
                tax_unit("social_security_exempt_retirement_benefits", period)
                > 0
            )
        )
