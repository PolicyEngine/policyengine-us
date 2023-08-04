from policyengine_us.model_api import *


class mi_military_retirement_pay_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan deduction of retirement or pension benefits, received for services in the Armed Forces of the United States"
    unit = USD
    definition_period = YEAR
    reference = (
        "http://legislature.mi.gov/doc.aspx?mcl-206-30", #(e)
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf#page=16",
    )
    defined_for = StateCode.MI

    # Added this variable because it is used as a condition of the Michigan 
    # interest, dividend, and capital gains deduction.

    adds = ["military_retirement_pay"]