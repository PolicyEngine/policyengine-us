from policyengine_us.model_api import *


class ak_atap(Variable):
    value_type = float
    entity = SPMUnit
    label = "Alaska ATAP benefit"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/alaska/7-AAC-45.525",
        "https://www.law.cornell.edu/regulations/alaska/7-AAC-45.523",
    )
    defined_for = "ak_atap_eligible"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ak.dpa.atap
        need_standard = spm_unit("ak_atap_need_standard", period)
        countable_income = spm_unit("ak_atap_countable_income", period)
        maximum_payment = spm_unit("ak_atap_maximum_payment", period)

        # Per 7 AAC 45.525: Payment = (Need Standard - Countable Income)
        # * (Max Payment / Need Standard) for the unit's size
        income_deficit = max_(need_standard - countable_income, 0)
        ratable_reduction = maximum_payment / need_standard
        return income_deficit * ratable_reduction
