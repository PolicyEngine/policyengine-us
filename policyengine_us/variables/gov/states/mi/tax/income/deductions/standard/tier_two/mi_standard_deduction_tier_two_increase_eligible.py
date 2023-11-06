from policyengine_us.model_api import *


class mi_standard_deduction_tier_two_increase_eligible(Variable):
    value_type = int
    entity = TaxUnit
    label = "Number of eligible people for the Michigan tier two standard deduction increase"
    definition_period = YEAR
    reference = (
        "http://legislature.mi.gov/doc.aspx?mcl-206-30",  # (9)(c)
        "https://www.michigan.gov/taxes/iit/retirement-and-pension-benefits/michigan-standard-deduction",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf#page=15",
    )
    defined_for = StateCode.MI

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.mi.tax.income.deductions.standard.tier_two

        person = tax_unit.members

        retirement_eligible = (
            person("year_of_retirement", period) <= p.retirement_year
        )

        # Line 23C & 23G from the 2022 tax form
        ssa_eligible = (
            person("retirement_benefits_from_ssa_exempt_employment", period)
            > 0
        )

        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)

        eligible_person = (
            retirement_eligible * ssa_eligible * is_head_or_spouse
        )

        return tax_unit.sum(eligible_person)
