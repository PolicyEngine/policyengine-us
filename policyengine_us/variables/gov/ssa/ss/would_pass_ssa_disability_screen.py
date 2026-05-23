from policyengine_us.model_api import *


class would_pass_ssa_disability_screen(Variable):
    value_type = bool
    entity = Person
    label = "Would pass SSA disability screen"
    definition_period = YEAR
    reference = [
        "https://www.law.cornell.edu/uscode/text/42/423#d_1_A",
        "https://www.law.cornell.edu/uscode/text/42/1382c#a_3_A",
    ]

    def formula(person, period, parameters):
        return person("is_disabled", period)
