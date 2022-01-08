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
        broadband_cost = spm_unit("broadband_cost", period)
        tribal = spm_unit.household("is_on_tribal_land", period)
        max_amount = parameters(period).fcc.ebb.amount[tribal] * 12
        amount_if_eligible = min_(max_amount, broadband_cost)
        return where(eligible, amount_if_eligible, 0)
