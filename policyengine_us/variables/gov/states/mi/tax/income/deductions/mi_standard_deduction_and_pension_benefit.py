from policyengine_us.model_api import *


class mi_standard_deduction_and_pension_benefit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan standard deduction and pension benefit"
    unit = USD
    definition_period = YEAR
    documentation = "Michigan standard deduction, consist of standard deduction, retirement and pension benefits, and interest, dividends, and capital gains deduction of qualifying age."
    reference = (
        "http://legislature.mi.gov/doc.aspx?mcl-206-30",
        "https://www.michigan.gov/taxes/iit/retirement-and-pension-benefits/michigan-standard-deduction",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf#page=18",
        "https://www.michigan.gov/taxes/iit/retirement-and-pension-benefits",
    )
    defined_for = StateCode.MI

    adds = [
        "mi_standard_deduction_tier_two",
        "mi_standard_deduction_tier_three",
        "mi_retirement_benefits_deduction_tier_one",
        "mi_retirement_benefits_deduction_tier_three",
        "mi_interest_dividends_capital_gains_deduction",
    ]
