from policyengine_us.model_api import *


class ga_caps_pre_k_enrolled(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Child attends Georgia's Pre-K Program, for the Georgia CAPS priority group"
    defined_for = StateCode.GA
    reference = "https://caps.decal.ga.gov/assets/downloads/CAPS/07-CAPS_Policy-Priority%20Groups.pdf#page=5"
