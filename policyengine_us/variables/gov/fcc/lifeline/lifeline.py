from policyengine_us.model_api import *


class lifeline(Variable):
    value_type = float
    entity = SPMUnit
    label = "Lifeline"
    documentation = "Amount of Lifeline phone and broadband benefit"
    definition_period = YEAR
    unit = USD
    reference = "https://www.law.cornell.edu/cfr/text/47/54.403"

    def formula(spm_unit, period, parameters):
        # NB: Only one Lifeline benefit is available per SPM unit, per:
        # https://www.law.cornell.edu/cfr/text/47/54.409#c
        amounts = parameters(period).gov.fcc.lifeline.amount
        household = spm_unit.household
        is_rural_tribal = and_(
            household, period, ["is_rural", "is_on_tribal_land"]
        )
        base_amount = amounts.standard
        # CA and OR provide separate maximum lifeline benefit amount
        state_code = spm_unit.household("state_code_str", period)

        p_ca = parameters(period).gov.states.ca.fcc.lifeline
        if p_ca.in_effect:
            ca_amount = p_ca.max_amount
            in_ca = state_code == "CA"
            base_amount = where(in_ca, ca_amount, base_amount)

        p_or = parameters(period).gov.states["or"].fcc.lifeline
        if p_or.in_effect:
            or_amount = p_or.max_amount
            in_or = state_code == "OR"
            base_amount = where(in_or, or_amount, base_amount)

        max_amount = (
            base_amount + is_rural_tribal * amounts.rural_tribal_supplement
        ) * MONTHS_IN_YEAR
        phone_broadband_cost = add(
            spm_unit, period, ["phone_cost", "broadband_cost"]
        )
        amount_if_eligible = min_(phone_broadband_cost, max_amount)
        eligible = spm_unit("is_lifeline_eligible", period)
        return eligible * amount_if_eligible
