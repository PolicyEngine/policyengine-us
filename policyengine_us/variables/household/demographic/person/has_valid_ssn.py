from policyengine_us.model_api import *


class has_valid_ssn(Variable):
    value_type = bool
    entity = Person
    label = "Has a valid SSN for SSN-gated federal tax rules"
    definition_period = YEAR
    default_value = True

    def formula(person, period, parameters):
        taxpayer_id_type = person("taxpayer_id_type", period)
        return taxpayer_id_type == taxpayer_id_type.possible_values.VALID_SSN
