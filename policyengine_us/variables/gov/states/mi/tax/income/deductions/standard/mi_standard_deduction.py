from policyengine_us.model_api import *


class mi_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan standard deduction"
    unit = USD
    definition_period = YEAR
    documentation = "Michigan standard deduction of qualifying age."
    reference = (
        "http://legislature.mi.gov/doc.aspx?mcl-206-30",
        "https://www.michigan.gov/taxes/iit/retirement-and-pension-benefits/michigan-standard-deduction",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf#page=18",
    )
    defined_for = StateCode.MI

    adds = [
        "mi_standard_deduction_tier_two",
        "mi_standard_deduction_tier_three",
    ]
