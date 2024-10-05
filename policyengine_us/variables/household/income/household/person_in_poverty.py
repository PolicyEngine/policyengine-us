from policyengine_us.model_api import *


class person_in_poverty(Variable):
    label = "person in poverty"
    documentation = "Whether person is in poverty"
    entity = Person
    definition_period = YEAR
    value_type = bool

    def formula(person, period, parameters):
        return person.spm_unit("in_poverty", period)
