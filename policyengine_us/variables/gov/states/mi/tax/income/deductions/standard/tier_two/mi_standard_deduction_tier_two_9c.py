from policyengine_us.model_api import *


class mi_standard_deduction_tier_two(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan standard deduction increase"
    unit = USD
    definition_period = YEAR
    reference = (
        "http://legislature.mi.gov/doc.aspx?mcl-206-30", # (b)&(c)
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
        # HAVE TO CHECK THIS
        age_older = tax_unit("greater_age_head_spouse", period)
        # Michigan standard deduction increase
        sd2_birth_year = -(age_older - period.start.year)
        sd2_age_eligibility = (sd2_birth_year >= p.min_birth_year) & (
            sd2_birth_year <= p.max_birth_year
        )
        age_threshold = age_older >= p.min_age
        # (9), (b)
        # If the person has not reached the age of 67 (which is mathematically impossible) and is born betwee 1946 and 1952
        # then the person is eligible to a pension benefit deduction of 20,000 or 40,000, based on filing status
        uncapped_pension_income = tax_unit("taxable_pension_income", period)
        #CHECK PARAMETER NAME
        capped_pension_income = max_(uncapped_pension_income, p.non_qualifying) * ~age_threshold
        # If the person has surpassed the age of 67 and was born between 1946 and 1952 (which in 2022 is the only possible outcome)
        # the person is allows a general standard deduction of 20,000 or 40,000, based on income, no matter what income
        # CHECK PARAMETER METADATA
        tier_two_standard_deduction = p.capped_deduction * age_threshold
        return where(sd2_age_eligibility, capped_pension_income + tier_two_standard_deduction, 0)

        # NEED to check whether person received 9 (e) - then uneligible



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
