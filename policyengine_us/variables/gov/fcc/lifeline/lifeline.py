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
        # We have to set a variable to a raw parameter value because
        # we conditionally overwrite it with state-specific logic later.
        base_amount = p.fcc.lifeline.amount.standard
        household = spm_unit.household
        is_rural_tribal = and_(
            household, period, ["is_rural", "is_on_tribal_land"]
        )
        # CA and OR provide separate maximum lifeline benefit amount
        state_code = household("state_code_str", period)

        # State-specific maximum amounts
        if p.states.ca.fcc.lifeline.in_effect:
            base_amount = where(
                state_code == "CA",
                p.states.ca.fcc.lifeline.max_amount,
                base_amount,
            )

        if p.states["or"].fcc.lifeline.in_effect:
            base_amount = where(
                state_code == "OR",
                p.states["or"].fcc.lifeline.max_amount,
                base_amount,
            )

        max_monthly_amount = (
            base_amount,
            is_rural_tribal * p.amount.rural_tribal_supplement,
        )
        max_amount = max_monthly_amount * MONTHS_IN_YEAR
        phone_broadband_cost = add(
            spm_unit, period, ["phone_cost", "broadband_cost"]
        )
        return min_(phone_broadband_cost, max_amount)
