from policyengine_us.model_api import *


class sd_ssp_care_joint_entry(Variable):
    value_type = bool
    entity = Person
    label = "South Dakota spouses begin long-term care in the same month"
    definition_period = MONTH
    reference = "https://sdlegislature.gov/Rules/Administrative/67:46:05:30"
