from policyengine_us.model_api import *


class or_tanf_payment_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Oregon TANF payment standard"
    unit = USD
    definition_period = MONTH
    reference = "https://oregon.public.law/rules/oar_461-155-0030"
    defined_for = StateCode.OR

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states["or"].odhs.tanf
        size = spm_unit("spm_unit_size", period.this_year)
        max_size = p.maximum_need_group_size
        size_capped = min_(size, max_size)
        additional_people = max_(size - max_size, 0)
        base_amount = p.payment_standard.amount[size_capped]
        additional_amount = (
            additional_people * p.payment_standard.additional_person
        )
        return base_amount + additional_amount
