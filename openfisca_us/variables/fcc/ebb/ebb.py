from openfisca_us.model_api import *

class ebb(Variable):
    value_type = float
    entity = SPMUnit
    label = "Emergency Broadband Benefit amount"
    description = "Emergency Broadband Benefit amount"
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        eligible = spm_unit("is_ebb_eligible", period)
        broadband_cost = spm_unit("broadband_cost", period)
        tribal = spm_unit.household("is_on_tribal_land", period)
        amount = parameters(period).fcc.ebb.amount[tribal] * 12
        return where(eligible, min_(broadband_cost, amount), 0)
