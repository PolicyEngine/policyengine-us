from policyengine_us.model_api import *


class ebb(Variable):
    value_type = float
    entity = SPMUnit
    label = "Emergency Broadband Benefit amount"
    documentation = "Emergency Broadband Benefit amount"
    definition_period = YEAR
    unit = USD
    defined_for = "is_ebb_eligible"

    def formula(spm_unit, period, parameters):
        broadband_cost = spm_unit("broadband_cost_after_lifeline", period)
        tribal = spm_unit.household("is_on_tribal_land", period)
        p = parameters(period).gov.fcc.ebb
        max_amount = (
            where(tribal, p.amount.tribal, p.amount.standard) * MONTHS_IN_YEAR
        )
        return min_(max_amount, broadband_cost)
