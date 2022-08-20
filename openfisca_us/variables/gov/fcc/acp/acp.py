from openfisca_us.model_api import *


class acp(Variable):
    value_type = float
    entity = SPMUnit
    label = "Affordable Connectivity Program"
    documentation = "Affordable Connectivity Program amount"
    definition_period = YEAR
    unit = USD
    reference = "https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title47-section1752&edition=prelim"
    defined_for = "is_acp_eligible"

    def formula(spm_unit, period, parameters):
        broadband_cost = spm_unit("broadband_cost_after_lifeline", period)
        tribal = spm_unit.household("is_on_tribal_land", period)
        amounts = parameters(period).gov.fcc.acp.amount
        max_amount = (
            where(tribal, amounts.tribal, amounts.standard) * MONTHS_IN_YEAR
        )
        return min_(max_amount, broadband_cost)
