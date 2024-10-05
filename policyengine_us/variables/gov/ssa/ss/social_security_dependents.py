from policyengine_us.model_api import *


class social_security_dependents(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Social Security dependents benefits"
    unit = USD
    # uprating = "gov.ssa.uprating"
