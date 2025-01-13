from policyengine_us.model_api import *


class ca_state_supplement_blind_amount(Variable):
    value_type = float
    entity = SPMUnit
    label = "California SSI state supplement blind amount"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.CA
    reference = "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=WIC&sectionNum=12200"

    def formula(spm_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.ca.cdss.state_supplement.payment_standard
        person = spm_unit.members
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        # Blind amount
        blind = person("is_blind", period) * head_or_spouse
        blind_count = spm_unit.sum(blind)
        is_married = spm_unit("spm_unit_is_married", period)
        blind_married_amount = select(
            [blind_count >= 2, blind_count == 1],
            [p.blind.married.two_blind, p.blind.married.one_blind],
            default=0,
        )
        return where(is_married, blind_married_amount, p.blind.single)
