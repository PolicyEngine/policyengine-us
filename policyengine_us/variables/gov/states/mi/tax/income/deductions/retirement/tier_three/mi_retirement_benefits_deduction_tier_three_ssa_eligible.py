from policyengine_us.model_api import *


class mi_retirement_benefits_deduction_tier_three_ssa_eligible(Variable):
    value_type = int
    entity = TaxUnit
    label = "Number of eligible people for the Michigan tier three retirement benefits deduction increase"
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

        ssa_eligible = (
            person("social_security_exempt_retirement_benefits", period) > 0
        )

        filer_eligible = person("is_tax_unit_head", period)
        spouse_eligible = person("is_tax_unit_spouse", period)
        is_head_or_spouse = filer_eligible | spouse_eligible

        eligible_person = ssa_eligible * is_head_or_spouse

        return tax_unit.sum(eligible_person)
