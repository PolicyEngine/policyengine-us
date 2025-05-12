from policyengine_us.model_api import *


class tax_unit_has_valid_ssn_card_type_for_eitc(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "All members in the tax unit have valid SSN card type to be eligible for the EITC"
    reference = "https://www.law.cornell.edu/uscode/text/26/32#c_1_E"

    def formula(tax_unit, period, parameters):
        ssn_card_type = tax_unit.members("ssn_card_type", period)
        ssn_card_types = ssn_card_type.possible_values
        citizen = ssn_card_type == ssn_card_types.CITIZEN
        non_citizen_valid_ead = (
            ssn_card_type == ssn_card_types.NON_CITIZEN_VALID_EAD
        )
        eligible_ssn_card_type = citizen | non_citizen_valid_ead
        return tax_unit.all(eligible_ssn_card_type)
