from policyengine_us.model_api import *


class ctc_qualifying_child(Variable):
    value_type = bool
    entity = Person
    label = "CTC-qualifying child"
    documentation = "Child qualifies for the Child Tax Credit"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/24#c"

    def formula(person, period, parameters):
        return person("ctc_child_individual_maximum", period) > 0
