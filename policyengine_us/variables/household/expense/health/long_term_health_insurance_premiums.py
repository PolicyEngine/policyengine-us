from policyengine_us.model_api import *


class long_term_health_insurance_premiums(Variable):
    value_type = float
    entity = Person
    label = "Long-term health insurance premiums"
    unit = USD
    definition_period = YEAR
