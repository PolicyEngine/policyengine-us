from policyengine_us.model_api import *


class meets_additional_senior_deduction_identification_requirements(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = (
        "Person meets additional senior deduction identification requirements"
    )
    reference = "https://www.finance.senate.gov/imo/media/doc/finance_committee_legislative_text_title_vii.pdf#page=3"

    def formula(person, period, parameters):
        ssn_card_type = person("ssn_card_type", period)
        ssn_card_types = ssn_card_type.possible_values
        citizen = ssn_card_type == ssn_card_types.CITIZEN
        non_citizen_valid_ead = (
            ssn_card_type == ssn_card_types.NON_CITIZEN_VALID_EAD
        )
        return citizen | non_citizen_valid_ead
