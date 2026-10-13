from policyengine_us.model_api import *


class de_other_subtractions(Variable):
    value_type = float
    entity = Person
    label = "Delaware other subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DE
    documentation = "Other subtractions from federal adjusted gross income reported on Delaware Form 200-01 / 200-02, Line 15."
    reference = "https://revenuefiles.delaware.gov/2024/PIT-RES_TY24_2024-01_Instructions.pdf#page=7"
