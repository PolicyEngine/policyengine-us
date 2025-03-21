from policyengine_us.model_api import *


class is_ssi_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Is SSI eligible person"
    definition_period = YEAR

    def formula(person, period, parameters):
        meets_resource_test = person("meets_ssi_resource_test", period)
        eligible = person("is_ssi_eligible_individual", period)
        return meets_resource_test & eligible
