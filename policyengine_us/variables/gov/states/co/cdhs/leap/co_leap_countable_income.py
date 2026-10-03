from policyengine_us.model_api import *


class co_leap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Colorado LEAP countable household income"
    defined_for = StateCode.CO
    reference = "https://drive.google.com/file/d/1G3XKsXyKoPZmsA5-P6NI6w3svP99xOZd/view#page=46,47,48,49,50,51"
    adds = ["co_leap_countable_income_person", "co_tanf"]
