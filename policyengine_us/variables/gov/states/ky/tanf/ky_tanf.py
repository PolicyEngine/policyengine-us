from policyengine_us.model_api import *


class ky_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "Kentucky Transitional Assistance Program benefit"
    unit = USD
    definition_period = MONTH
    reference = "https://apps.legislature.ky.gov/law/kar/titles/921/002/016/"
    defined_for = "ky_tanf_eligible"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ky.tanf
        need_standard = spm_unit("ky_tanf_need_standard", period)
        countable_income = spm_unit("ky_tanf_countable_income", period)
        payment_standard = spm_unit("ky_tanf_payment_standard", period)
        deficit = max_(need_standard - countable_income, 0)
        reduced_benefit = deficit * p.benefit_rate
        return min_(reduced_benefit, payment_standard)
