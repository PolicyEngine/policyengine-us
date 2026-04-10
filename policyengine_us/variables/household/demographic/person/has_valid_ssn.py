from policyengine_us.model_api import *


class has_valid_ssn(Variable):
    value_type = bool
    entity = Person
    label = "Has a valid SSN for SSN-gated federal tax rules"
    definition_period = YEAR
    default_value = True

    def formula(person, period, parameters):
        id_holder = person.simulation.get_holder("taxpayer_id_type")
        if period in id_holder.get_known_periods():
            taxpayer_id_type = person("taxpayer_id_type", period)
            return taxpayer_id_type == taxpayer_id_type.possible_values.VALID_SSN

        ssn_card_type = person("ssn_card_type", period)
        ssn_card_types = ssn_card_type.possible_values
        return ssn_card_type == ssn_card_types.CITIZEN
