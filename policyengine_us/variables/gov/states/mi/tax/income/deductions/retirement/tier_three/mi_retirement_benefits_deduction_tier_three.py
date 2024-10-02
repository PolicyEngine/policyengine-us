from policyengine_us.model_api import *


class mi_retirement_benefits_deduction_tier_three(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan retirement benefits deduction for tier three"
    unit = USD
    definition_period = YEAR
    reference = (
        "http://legislature.mi.gov/doc.aspx?mcl-206-30",  # (9)(c) & (d)
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf#page=17",
        "https://www.michigan.gov/taxes/iit/retirement-and-pension-benefits",
    )
    defined_for = "mi_retirement_benefits_deduction_tier_three_eligible"

    def formula(tax_unit, period, parameters):
        ss_exempt_not_retired_amount = tax_unit(
            "mi_retirement_benefits_deduction_tier_three_ss_exempt_not_retired",
            period,
        )
        ss_exempt_retired_amount = tax_unit(
            "mi_retirement_benefits_deduction_tier_three_ss_exempt_retired",
            period,
        )

        return max_(ss_exempt_not_retired_amount, ss_exempt_retired_amount)
