from policyengine_us.model_api import *


class medical_out_of_pocket_expenses(Variable):
    value_type = float
    entity = Person
    label = "Medical out of pocket expenses"
    unit = USD
    definition_period = YEAR
    adds = [
        "health_insurance_premiums",
        "over_the_counter_health_expenses",
        "other_medical_expenses",
    ]
