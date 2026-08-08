from policyengine_us.model_api import *


class il_ccap_royalty_income(Variable):
    value_type = float
    entity = Person
    unit = USD
    definition_period = YEAR
    default_value = 0
    label = "Illinois CCAP royalty income"
    documentation = (
        "Royalty income counted by the Illinois Child Care Assistance Program."
    )
    defined_for = StateCode.IL
    reference = "https://www.dhs.state.il.us/page.aspx?item=10163"
