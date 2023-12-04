from policyengine_us.model_api import *


class mi_retirement_benefits_deduction_tier_three_ss_exempt_retired_eligible_people(
    Variable
):
    value_type = int
    entity = TaxUnit
    label = "Eligible for the Michigan tier three retired retirement benefits deduction"
    definition_period = YEAR
    reference = (
        "http://legislature.mi.gov/doc.aspx?mcl-206-30",  # (9)(c)
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf#page=18",
        "https://www.michigan.gov/taxes/iit/retirement-and-pension-benefits",
    )
    defined_for = StateCode.MI

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.mi.tax.income.deductions.retirement_benefits.tier_three.ss_exempt.retired

        person = tax_unit.members
        # Recipients should received retirement benefits from SSA exempt employment
        # and were retired before qualifying year
        retirement_eligible = (
            person("year_of_retirement", period) <= p.retirement_year
        ) & (person("year_of_retirement", period) > 0)

        has_retirement_benefits_from_ss_exempt_employment = (
            person("retirement_benefits_from_ss_exempt_employment", period) > 0
        )

        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)

        eligible_people = (
            has_retirement_benefits_from_ss_exempt_employment
            * retirement_eligible
            * is_head_or_spouse
        )

        return tax_unit.sum(eligible_people)
