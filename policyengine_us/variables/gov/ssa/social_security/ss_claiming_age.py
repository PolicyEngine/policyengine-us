from policyengine_us.model_api import *


class ss_claiming_age(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Social Security claiming age"
    documentation = (
        "Age at which the person claims Social Security retirement "
        "benefits. Defaults to current age. Set independently to "
        "model a person who claimed at a different age than their "
        "current age (e.g., a 70-year-old who claimed at 62)."
    )
    unit = "year"

    def formula(person, period, parameters):
        return person("age", period)
