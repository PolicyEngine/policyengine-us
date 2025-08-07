from policyengine_us.model_api import *


class self_employed_health_insurance_premiums(Variable):
    value_type = float
    entity = Person
    label = "Self-employed health insurance premiums"
    unit = USD
    documentation = "Health insurance premiums for plans covering individuals who are not covered by any employer-sponsored health insurance."
    definition_period = YEAR
    defined_for = "is_self_employed"
    adds = ["health_insurance_premiums"]
