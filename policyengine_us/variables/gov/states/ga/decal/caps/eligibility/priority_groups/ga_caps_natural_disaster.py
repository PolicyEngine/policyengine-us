from policyengine_us.model_api import *


class ga_caps_natural_disaster(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Family was harmed by a declared natural disaster in the previous 24 months, for the Georgia CAPS priority group"
    defined_for = StateCode.GA
    reference = "https://caps.decal.ga.gov/assets/downloads/CAPS/07-CAPS_Policy-Priority%20Groups.pdf#page=6"
