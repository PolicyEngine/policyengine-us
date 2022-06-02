from openfisca_us.model_api import *


class is_ctc_qualifying_child(Variable):
    value_type = bool
    entity = Person
    label = "Is a CTC-qualifying child"
    documentation = "Is a child qualifying for the Child Tax Credit"
    definition_period = YEAR

    def formula(person, period, parameters):
        ctc = parameters(period).irs.credits.ctc
        age = person("age", period)
        return age <= ctc.child.max_age
