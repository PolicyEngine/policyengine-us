from policyengine_us.model_api import *


class tip_income_deduction_ineligible_cardholder_present(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Ineligible cardholder present for the tip income deduction"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        ssn_card_type = person("ssn_card_type", period)
        ssn_card_str = ssn_card_type.decode_to_str()
        p = parameters(period).gov.irs.deductions.tip_income
        eligible_ssn_card_type = np.isin(
            ssn_card_str, p.eligible_ssn_card_type
        )
        head = person("is_tax_unit_head", period)
        spouse = person("is_tax_unit_spouse", period)
        ineligible_head_exists = tax_unit.any(head & ~eligible_ssn_card_type)
        ineligible_spouse_exists = tax_unit.any(
            spouse & ~eligible_ssn_card_type
        )
        return ineligible_head_exists | ineligible_spouse_exists
