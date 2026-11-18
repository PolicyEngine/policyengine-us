from policyengine_us.model_api import *


class has_chronic_breathing_condition(Variable):
    value_type = bool
    entity = Person
    label = "Has a chronic breathing condition"
    documentation = (
        "Whether the person has a chronic breathing condition, such as asthma or "
        "chronic obstructive pulmonary disease (chronic bronchitis or emphysema)."
    )
    definition_period = YEAR
    default_value = False
