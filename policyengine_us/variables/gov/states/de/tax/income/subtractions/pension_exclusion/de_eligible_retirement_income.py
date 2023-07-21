from policyengine_us.model_api import *


class eligible_retirement_income_for_elderly(Variable):
    value_type = float
    entity = Person
    label = "Delaware eligible retirement income amount for elderly"
    unit = USD
    definition_period = YEAR
    documentation = "Delaware individual income tax instructions for 2022"
    reference = "https://revenuefiles.delaware.gov/2022/PIT-RES_TY22_2022-02_Instructions.pdf#page=6"
