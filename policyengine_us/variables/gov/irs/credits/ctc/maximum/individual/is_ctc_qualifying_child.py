from policyengine_us.model_api import *


class is_ctc_qualifying_child(Variable):
    value_type = bool
    entity = Person
    label = "Is a CTC-qualifying child"
    documentation = "Is a child qualifying for the Child Tax Credit"
    definition_period = YEAR

    def formula(person, period, parameters):
        age = person("age", period)
        return age <= parameters(period).gov.irs.credits.ctc.child.max_age
