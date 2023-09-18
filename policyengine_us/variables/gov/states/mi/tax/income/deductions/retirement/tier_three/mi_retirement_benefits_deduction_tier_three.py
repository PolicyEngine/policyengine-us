from policyengine_us.model_api import *


class mi_retirement_benefits_deduction_tier_three(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan retirement benefits deduction for tier three"
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
        ).gov.states.mi.tax.income.deductions.retirement_benefits.tier_three

        rb3_age_eligibility = tax_unit(
            "mi_retirement_benefits_deduction_tier_three_eligible", period
        )
        rb3_amount = p.amount

        person = tax_unit.members
        social_security = (
            person("social_security_exempt_retirement_benefits", period) > 0
        )
        total_eligible = tax_unit.sum(social_security)

        return rb3_age_eligibility * rb3_amount * total_eligible
