from policyengine_us.model_api import *


class mi_standard_deduction_tier_three_eligible(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan standard deduction age eligibility"
    unit = USD
    definition_period = YEAR
    reference = (
        "http://legislature.mi.gov/doc.aspx?mcl-206-30",
        "https://www.michigan.gov/taxes/iit/retirement-and-pension-benefits/michigan-standard-deduction",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf#page=16",
    )
    defined_for = StateCode.MI

    def formula(tax_unit, period, parameters):
        # Part 9 (c) - a person born in 1946 through 1952 and
        # beginning January 1, 2018 for a person born after 1945 who has retired as of January 1, 2013,
        # the sum of the deductions under subsection (1)(f)(i), (ii), and (iv) is limited to $35,000.00 for a single return
        # and, except as otherwise provided under this subdivision, $55,000.00 for a joint return
        p = parameters(
            period
        ).gov.states.mi.tax.income.deductions.standard.tier_three

        age_older = tax_unit("greater_age_head_spouse", period)
        # Michigan Standard Deduction
        sd3_birth_year = -(age_older - period.start.year)
        return (age_older >= p.min_age) & (sd3_birth_year >= p.birth_year)
