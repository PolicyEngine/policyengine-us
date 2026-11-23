from policyengine_us.model_api import *
from policyengine_us.tools.general import has_input_for_period


class il_aabd_countable_for_snap(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "Illinois AABD Cash countable as SNAP unearned income"
    unit = USD
    defined_for = StateCode.IL
    reference = "https://www.dhs.state.il.us/page.aspx?item=15627"

    def formula(person, period):
        if has_input_for_period(person.simulation, "il_aabd", period):
            return 0
        return person("il_aabd_person", period)
