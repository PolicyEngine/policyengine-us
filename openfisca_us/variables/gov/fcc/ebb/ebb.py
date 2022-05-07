from openfisca_us.model_api import *


class ebb(Variable):
    value_type = float
    entity = SPMUnit
    label = "Emergency Broadband Benefit amount"
    documentation = "Emergency Broadband Benefit amount"
    definition_period = YEAR
    unit = USD

    def formula(spm_unit, period, parameters):
        eligible = spm_unit("is_ebb_eligible", period)
        broadband_cost = spm_unit("broadband_cost_after_lifeline", period)
        tribal = spm_unit.household("is_on_tribal_land", period)
        amounts = parameters(period).fcc.ebb.amount
        max_amount = (
            where(tribal, amounts.tribal, amounts.standard) * MONTHS_IN_YEAR
        )
        amount_if_eligible = min_(max_amount, broadband_cost)
        return where(eligible, amount_if_eligible, 0)
