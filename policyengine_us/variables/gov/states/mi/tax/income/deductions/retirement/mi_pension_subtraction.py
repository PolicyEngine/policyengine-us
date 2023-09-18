from policyengine_us.model_api import *


class mi_retirement_benefits_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan retirement benefits deduction"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Michigan retirement and pension benefits of qualifying age."
    )
    reference = (
        "http://legislature.mi.gov/doc.aspx?mcl-206-30",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf#page=17",
        "https://www.michigan.gov/taxes/iit/retirement-and-pension-benefits",
    )
    defined_for = StateCode.MI

    def formula(tax_unit, period, parameters):
        # Retirement or pension benefits received from a federal public retirement system
        # Not federal public retirement system or military:
        # capped at $42,240.00 for a single return and $84,480.00 for a joint return.
        # The maximum amounts allowed under this subparagraph shall be reduced by the amount of the deduction for retirement or pension benefits claimed under subparagraph (i) 
        # or subdivision (e) and by the amount of a deduction claimed under subdivision (p)
        # THIS IS A CIRCULAR REFRENCE AS SUBDIVISION (P) IS REDUCED BY THIS AMOUNT



#TODO: limitations of part (9)
