from policyengine_us.model_api import *


class never_eligible_for_social_security_benefits(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Never eligible for Social Security"
    default_value = False
