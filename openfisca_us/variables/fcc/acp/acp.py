from openfisca_us.model_api import *


class acp(Variable):
    value_type = float
    entity = SPMUnit
    label = "Affordable Connectivity Program"
    documentation = "Affordable Connectivity Program amount"
    definition_period = YEAR
    unit = USD
    reference = "https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title47-section1752&edition=prelim"

    def formula(spm_unit, period, parameters):
        eligible = spm_unit("is_acp_eligible", period)
        broadband_cost = spm_unit("broadband_cost_after_lifeline", period)
        tribal = spm_unit.household("is_on_tribal_land", period)
        amounts = parameters(period).fcc.acp.amount
        max_amount = where(tribal, amounts.tribal, amounts.standard) * 12
        amount_if_eligible = min_(max_amount, broadband_cost)
        return where(eligible, amount_if_eligible, 0)
