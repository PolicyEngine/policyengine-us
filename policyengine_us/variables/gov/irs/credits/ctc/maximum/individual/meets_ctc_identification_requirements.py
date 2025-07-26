from policyengine_us.model_api import *


class meets_ctc_identification_requirements(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Person meets CTC identification requirements"
    reference = "https://docs.house.gov/meetings/WM/WM00/20250513/118260/BILLS-119CommitteePrintih.pdf#page=4"

    def formula(person, period, parameters):
        ssn_card_type = person("ssn_card_type", period)
        ssn_card_types = ssn_card_type.possible_values
        citizen = ssn_card_type == ssn_card_types.CITIZEN
        non_citizen_valid_ead = (
            ssn_card_type == ssn_card_types.NON_CITIZEN_VALID_EAD
        )
        return citizen | non_citizen_valid_ead
