from policyengine_us.model_api import *


class ca_la_life_program_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Los Angeles metro LIFE program eligibility"
    definition_period = YEAR
    defined_for = "in_la"

    def formula(person, period, parameters):
        return (
            add(
                person,
                period,
                [
                    "snap",
                    "social_security",
                    "social_security_disability",
                    "tanf",
                ],
            )
            > 0
        )
