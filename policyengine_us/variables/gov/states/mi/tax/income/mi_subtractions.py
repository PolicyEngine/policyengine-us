from policyengine_us.model_api import *


class mi_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan subtractions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/Schedule-1.pdf",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf",
        "https://www.michigan.gov/-/media/Project/Websites/taxes/2022RM/UNCAT/2019_Taxpayer_Assistance_Manual.pdf",
    )
    defined_for = StateCode.MI

    adds = "gov.states.mi.tax.income.subtractions"
