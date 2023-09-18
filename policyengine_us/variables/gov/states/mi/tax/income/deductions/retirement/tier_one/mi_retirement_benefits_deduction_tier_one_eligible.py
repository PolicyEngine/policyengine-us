from policyengine_us.model_api import *


class mi_retirement_benefits_deduction_tier_one_eligible(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan retirement benefits deduction for tier one"
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
        ).gov.states.mi.tax.income.deductions.retirement_benefits.tier_one

        age_older = tax_unit("greater_age_head_spouse", period)
        birth_year = -(age_older - period.start.year)
        return birth_year < p.birth_year
