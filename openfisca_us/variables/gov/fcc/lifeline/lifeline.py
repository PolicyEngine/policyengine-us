from openfisca_us.model_api import *


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
        max_amount = (
            amounts.standard
            + is_rural_tribal * amounts.rural_tribal_supplement
        ) * MONTHS_IN_YEAR
        phone_broadband_cost = add(
            spm_unit, period, ["phone_cost", "broadband_cost"]
        )
        amount_if_eligible = min_(phone_broadband_cost, max_amount)
        eligible = spm_unit("is_lifeline_eligible", period)
        return eligible * amount_if_eligible
