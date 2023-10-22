from policyengine_us.model_api import *


class retirement_benefits_from_ssa_exempt_employment(Variable):
    value_type = float
    entity = Person
    label = "Retirement benefits amount from SSA exempt employment"
    unit = USD
    documentation = "Amount of a recipient receive retirement benefits from SSA exempt employment"
    reference = "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf#page=18"
    definition_period = YEAR
