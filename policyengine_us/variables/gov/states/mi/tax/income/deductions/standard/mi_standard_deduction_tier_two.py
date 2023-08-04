from policyengine_us.model_api import *


class mi_standard_deduction_tier_two(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan standard deduction increase"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Michigan standard deduction increase of qualifying age and condition."
    )
    reference = (
        "http://legislature.mi.gov/doc.aspx?mcl-206-30",
        "https://www.michigan.gov/taxes/iit/retirement-and-pension-benefits/michigan-standard-deduction",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf#page=15",
    )
    defined_for = StateCode.MI

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.mi.tax.income.deductions.standard.tier_two
        # Core deduction based on filing status.
        filing_status = tax_unit("filing_status", period)

        age_older = tax_unit("greater_age_head_spouse", period)
        # Michigan standard deduction increase
        sd2_birth_year = -(age_older - period.start.year)
        sd2_age_eligibility = (sd2_birth_year >= p.min_birth_year) & (
            sd2_birth_year <= p.max_birth_year
        )

        person = tax_unit.members
        social_security = (
            person("social_security_exempt_retirement_benefits", period) > 0
        )
        total_eligible = tax_unit.sum(social_security)

        sd2_amount = where(
            total_eligible == 0,
            p.amount.non_qualifying[filing_status],
            where(
                total_eligible == 1,
                p.amount.single_qualifying[filing_status],
                p.amount.both_qualifying[filing_status],
            ),
        )

        return sd2_age_eligibility * sd2_amount
