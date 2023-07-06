from policyengine_us.model_api import *


class children_recieving_tanf_number(Variable):
    value_type = float
    entity = Person
    label = "number of children receiving tanf"
    definition_period = YEAR

    def formula(person, period, parameters):
        children_number = person("children_recieving_tanf_number", period)
        return children_number
