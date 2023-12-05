from policyengine_us.model_api import *


class mi_pension_benefit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan pension benefit"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Michigan retirement and pension benefits of qualifying age."
    )
    reference = (
        "http://legislature.mi.gov/doc.aspx?mcl-206-30",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf#page=18",
        "https://www.michigan.gov/taxes/iit/retirement-and-pension-benefits",
    )
    defined_for = StateCode.MI

    adds = [
        "mi_retirement_benefits_deduction_tier_one",
        "mi_retirement_benefits_deduction_tier_three",
    ]
