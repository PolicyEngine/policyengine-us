from policyengine_us.model_api import *


class mi_retirement_benefits_deduction_tier_three_ssa_retired_eligible(
    Variable
):
    value_type = int
    entity = TaxUnit
    label = "Eligible for the Michigan tier three retirement benefits deduction qualifying SSA & retired"
    definition_period = YEAR
    reference = (
        "http://legislature.mi.gov/doc.aspx?mcl-206-30",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf#page=18",
        "https://www.michigan.gov/taxes/iit/retirement-and-pension-benefits",
    )
    defined_for = StateCode.MI

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.mi.tax.income.deductions.retirement_benefits.tier_three.ssa_retired

        person = tax_unit.members

        retirement_eligible = (
            person("year_of_retirement", period) <= p.retirement_year
        ) & (person("year_of_retirement", period) > 0)

        ssa_eligible = (
            person("retirement_benefits_from_ssa_exempt_employment", period)
            > 0
        )

        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)

        eligible_person = (
            ssa_eligible * retirement_eligible * is_head_or_spouse
        )

        return tax_unit.sum(eligible_person)
