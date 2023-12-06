from policyengine_us.model_api import *


class mi_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan taxable income subtractions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/Schedule-1.pdf",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/MI-1040.pdf",
    )
    defined_for = StateCode.MI

    adds = "gov.states.mi.tax.income.subtractions"
