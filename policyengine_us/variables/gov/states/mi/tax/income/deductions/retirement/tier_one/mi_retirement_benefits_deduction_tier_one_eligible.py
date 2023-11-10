from policyengine_us.model_api import *


class mi_retirement_benefits_deduction_tier_one_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Michigan tier one retirement benefits deduction"
    definition_period = YEAR
    reference = (
        "http://legislature.mi.gov/doc.aspx?mcl-206-30",  # (1)(f)
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf#page=17",
        "https://www.michigan.gov/taxes/iit/retirement-and-pension-benefits",
    )
    defined_for = StateCode.MI

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.mi.tax.income.deductions.retirement_benefits.tier_one

        older_spouse_birth_year = tax_unit("older_spouse_birth_year", period)

        return older_spouse_birth_year < p.birth_year
