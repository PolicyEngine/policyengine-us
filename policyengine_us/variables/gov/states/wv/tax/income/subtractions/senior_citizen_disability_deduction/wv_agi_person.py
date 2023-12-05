from policyengine_us.model_api import *


class wv_agi_person(Variable):
    value_type = float
    entity = Person
    label = "West Virginia adjusted gross income for each person"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.WV
