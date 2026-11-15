from policyengine_us.model_api import *


class ga_caps_grandparents_raising_grandchildren(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Family participates in the Georgia Grandparents Raising Grandchildren program, for the Georgia CAPS priority group"
    defined_for = StateCode.GA
    reference = "https://caps.decal.ga.gov/assets/downloads/CAPS/07-CAPS_Policy-Priority%20Groups.pdf#page=8"
