from policyengine_us.model_api import *


class mi_retirement_benefits_deduction_tier_one(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan retirement benefits deduction for tier one"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.legislature.mi.gov/Laws/MCL?objectName=mcl-206-30",  # (1)(f)
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/IIT/TY2022/BOOK_MI-1040.pdf#page=17",
        "https://web.archive.org/web/20250202214915/https://www.michigan.gov/taxes/iit/retirement-and-pension-benefits",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/IIT/TY2022/4884.pdf#page=2",
    )
    defined_for = "mi_retirement_benefits_deduction_tier_one_eligible"

    adds = [
        "mi_retirement_benefits_deduction_tier_one_amount",
    ]
