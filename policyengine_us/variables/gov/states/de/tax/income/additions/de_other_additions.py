from policyengine_us.model_api import *


class de_other_additions(Variable):
    value_type = float
    entity = Person
    label = "Delaware other additions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DE
    documentation = "Other additions to federal adjusted gross income reported on Delaware Form 200-01 / 200-02, Line 3."
    reference = "https://revenuefiles.delaware.gov/2024/PIT-RES_TY24_2024-01_Instructions.pdf#page=6"
