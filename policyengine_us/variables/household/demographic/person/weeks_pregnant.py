from policyengine_us.model_api import *


class weeks_pregnant(Variable):
    value_type = int
    entity = Person
    definition_period = YEAR
    label = (
        "Number of weeks that the person has been pregnant throughout the year"
    )
