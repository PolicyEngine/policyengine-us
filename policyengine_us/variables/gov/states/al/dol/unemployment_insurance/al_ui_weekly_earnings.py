from policyengine_us.model_api import *


class al_ui_weekly_earnings(Variable):
    value_type = float
    entity = Person
    label = "Alabama UI gross weekly earnings during a partial unemployment week"
    unit = USD
    definition_period = YEAR
    default_value = 0
    reference = (
        "https://admincode.legislature.state.al.us/administrative-code/480-4-3-.11",
        "https://oui.doleta.gov/unemploy/pdf/uilawcompar/2023/monetary.pdf#page=20",
    )
    defined_for = StateCode.AL
