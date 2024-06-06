from policyengine_us.model_api import *


class ca_la_life_program_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for the Los Angeles metro LIFE program"
    definition_period = YEAR
    defined_for = "in_la"

    def formula(person, period, parameters):
        applicable_programs = add(
            person.spm_unit,
            period,
            [
                "snap",
                "social_security",
                "social_security_disability",
                "tanf",
            ],
        )

        return applicable_programs > 0
