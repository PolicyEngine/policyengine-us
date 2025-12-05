from policyengine_us.model_api import *


class ky_ktap(Variable):
    value_type = float
    entity = SPMUnit
    label = "Kentucky K-TAP benefit"
    unit = USD
    definition_period = MONTH
    reference = "https://apps.legislature.ky.gov/law/kar/titles/921/002/016/"
    defined_for = "ky_ktap_eligible"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ky.dcbs.ktap.benefit
        need_standard = spm_unit("ky_ktap_need_standard", period)
        countable_income = spm_unit("ky_ktap_countable_income", period)
        payment_standard = spm_unit("ky_ktap_payment_standard", period)
        deficit = max_(need_standard - countable_income, 0)
        return min_(deficit * p.rate, payment_standard)
