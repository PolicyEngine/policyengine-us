from policyengine_us.model_api import *


class mi_retirement_benefits_deduction_tier_three_ss_exempt_not_retired_eligible_people(
    Variable
):
    value_type = int
    entity = TaxUnit
    label = "Number of eligible people for the Michigan non-retired tier three retirement benefits deduction"
    definition_period = YEAR
    reference = (
        "http://legislature.mi.gov/doc.aspx?mcl-206-30",  # (9)(d)
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf#page=17",
        "https://www.michigan.gov/taxes/iit/retirement-and-pension-benefits",
    )
    defined_for = StateCode.MI

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        #  Recipients should receive retirement benefits from employment exempt from Social Security
        has_retirement_benefits_from_ss_exempt_employment = (
            person(
                "retirement_benefits_from_ss_exempt_employment",
                period,
            )
            > 0
        )

        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)

        eligible_people = (
            has_retirement_benefits_from_ss_exempt_employment
            * is_head_or_spouse
        )

        return tax_unit.sum(eligible_people)
