from policyengine_us.model_api import *


class lifeline(Variable):
    value_type = float
    entity = SPMUnit
    label = "Lifeline"
    documentation = "Amount of Lifeline phone and broadband benefit"
    definition_period = YEAR
    unit = USD
    defined_for = "is_lifeline_eligible"
    reference = "https://www.law.cornell.edu/cfr/text/47/54.403"

    def formula(spm_unit, period, parameters):
        # NB: Only one Lifeline benefit is available per SPM unit, per:
        # https://www.law.cornell.edu/cfr/text/47/54.409#c
        p = parameters(period).gov
        base_amount = p.fcc.lifeline.amount.standard
        household = spm_unit.household
        is_rural_tribal = and_(
            household, period, ["is_rural", "is_on_tribal_land"]
        )
        state_code = household("state_code_str", period)

        # Check for state-specific Lifeline programs
        STATES_WITH_LIFELINE = ["ca", "or"]
        for state in STATES_WITH_LIFELINE:
            state_params = p.states[state].fcc.lifeline
            if hasattr(state_params, "in_effect") and state_params.in_effect:
                base_amount = where(
                    state_code == state.upper(),
                    state_params.max_amount,
                    base_amount,
                )

        max_monthly_amount = (
            base_amount
            + is_rural_tribal * p.fcc.lifeline.amount.rural_tribal_supplement
        )
        max_amount = max_monthly_amount * MONTHS_IN_YEAR
        phone_broadband_cost = add(
            spm_unit, period, ["phone_cost", "broadband_cost"]
        )
        return min_(phone_broadband_cost, max_amount)
