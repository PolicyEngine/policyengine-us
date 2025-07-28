from policyengine_us.model_api import *


class overtime_income_deduction_ineligible_cardholder_present(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Ineligible cardholder present for the overtime income deduction"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        ssn_card_type = person("ssn_card_type", period)
        ssn_card_types = ssn_card_type.possible_values
        citizen = ssn_card_type == ssn_card_types.CITIZEN
        non_citizen_valid_ead = (
            ssn_card_type == ssn_card_types.NON_CITIZEN_VALID_EAD
        )
        eligible_ssn_card_type = citizen | non_citizen_valid_ead
        head = person("is_tax_unit_head", period)
        spouse = person("is_tax_unit_spouse", period)
        ineligible_head_exists = tax_unit.any(head & ~eligible_ssn_card_type)
        ineligible_spouse_exists = tax_unit.any(
            spouse & ~eligible_ssn_card_type
        )
        return ineligible_head_exists | ineligible_spouse_exists
