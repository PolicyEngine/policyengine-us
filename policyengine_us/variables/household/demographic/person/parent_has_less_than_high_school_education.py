from policyengine_us.model_api import *


class parent_has_less_than_high_school_education(Variable):
    value_type = bool
    entity = Person
    label = "Parent has less than high school education"
    definition_period = YEAR
