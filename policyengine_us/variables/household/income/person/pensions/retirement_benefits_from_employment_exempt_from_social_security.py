from policyengine_us.model_api import *


class retirement_benefits_from_employment_exempt_from_social_security(
    Variable
):
    value_type = float
    entity = Person
    label = "Retirement benefits amount from employment exempt from Social Security"
    unit = USD
    documentation = "Amount of a recipient receive retirement benefits from employment exempt from Social Security"
    reference = "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf#page=17"
    definition_period = YEAR
