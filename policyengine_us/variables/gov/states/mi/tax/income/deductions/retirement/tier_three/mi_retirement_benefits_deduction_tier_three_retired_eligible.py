from policyengine_us.model_api import *


class mi_retirement_benefits_deduction_tier_three_retired_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Michigan tier three retirement benefits deduction qualifying both SSA and retirement year"
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
        ).gov.states.mi.tax.income.deductions.standard.tier_two

        person = tax_unit.members

        retirement_eligible = (
            person("year_of_retirement", period) <= p.retirement_age
        ) & (person("year_of_retirement", period) > 0)

        filer_eligible = person("is_tax_unit_head", period)
        spouse_eligible = person("is_tax_unit_spouse", period)
        is_head_or_spouse = filer_eligible | spouse_eligible

        eligible_person = retirement_eligible * is_head_or_spouse

        return tax_unit.sum(eligible_person) > 0
