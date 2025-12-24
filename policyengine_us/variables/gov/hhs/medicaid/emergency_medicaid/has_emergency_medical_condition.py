from policyengine_us.model_api import *


class has_emergency_medical_condition(Variable):
    value_type = bool
    entity = Person
    label = "Has emergency medical condition"
    definition_period = YEAR
    default_value = False
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1396b#v_3",
        "https://www.law.cornell.edu/cfr/text/42/440.255#c",
    )
    # Placing the patient's health in serious jeopardy
    # Serious impairment to bodily functions
    # Serious dysfunction of any bodily organ or part
