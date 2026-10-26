from policyengine_us.model_api import *


class mi_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan taxable income additions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/IIT/TY2022/Schedule-1.pdf",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/IIT/TY2022/BOOK_MI-1040.pdf",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/IIT/TY2022/MI-1040.pdf",
    )
    defined_for = StateCode.MI

    adds = "gov.states.mi.tax.income.additions"
