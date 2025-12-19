from policyengine_us.model_api import *


class parent_has_less_than_high_school_education(Variable):
    value_type = bool
    entity = Household
    label = "Parent has less than high school education"
    definition_period = YEAR
    documentation = "Whether any parent or guardian in the household has less than a high school diploma or equivalent"
