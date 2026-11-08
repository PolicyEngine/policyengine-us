from policyengine_us.model_api import *


class deceased_spouse_age(Variable):
    value_type = float
    entity = Person
    label = "Age the deceased spouse would have reached"
    documentation = (
        "For a surviving spouse, the age the deceased spouse would have "
        "reached by the end of the year had they lived. Without an input, "
        "this takes the person's own age."
    )
    unit = "year"
    definition_period = YEAR

    def formula(person, period, parameters):
        return person("age", period)
