from policyengine_us.model_api import *


class basic_health_program_enrolled(Variable):
    value_type = bool
    entity = Person
    label = "Basic Health Program enrolled"
    definition_period = YEAR
    reference = "https://www.medicaid.gov/basic-health-program"
    defined_for = "is_basic_health_program_eligible"
    adds = ["takes_up_basic_health_program_if_eligible"]
