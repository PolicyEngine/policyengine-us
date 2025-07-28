from policyengine_us.model_api import *


class tip_income_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tip income deduction"
    unit = USD
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
        ineligible_cardholder_present = (
            ineligible_head_exists | ineligible_spouse_exists
        )

        tip_income = person("tip_income", period)
        agi = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period)
        p = parameters(period).gov.irs.deductions.tip_income_exempt
        start = p.phase_out.start[filing_status]
        agi_excess = max_(agi - start, 0)
        phase_out_amount = agi_excess * p.phase_out.rate
        total_tip_income = tax_unit.sum(tip_income)
        capped_tip_income = min_(p.cap, total_tip_income)
        phased_out_tip_income = max_(
            0, capped_tip_income - phase_out_amount
        )
        return phased_out_tip_income * ~ineligible_cardholder_present
