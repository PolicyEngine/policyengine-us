from policyengine_us.model_api import *


class tip_income_deduction_ssn_requirement_met(Variable):
    value_type = bool
    entity = TaxUnit
    label = "SSN requirement met for the tip income deduction"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        ssn_card_type = person("ssn_card_type", period)
        ssn_card_str = ssn_card_type.decode_to_str()
        p = parameters(period).gov.irs.deductions.tip_income
        eligible_ssn_card_type = np.isin(
            ssn_card_str, p.eligible_ssn_card_type
        )
        joint = tax_unit("tax_unit_is_joint", period)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        eligible_head_or_spouse = eligible_ssn_card_type & head_or_spouse
        return where(
            joint,
            tax_unit.sum(eligible_head_or_spouse) == 2,
            tax_unit.any(eligible_head_or_spouse),
        )
