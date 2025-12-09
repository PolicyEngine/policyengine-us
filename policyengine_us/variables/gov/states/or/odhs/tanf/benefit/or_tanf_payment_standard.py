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
        p = parameters(period).gov.states["or"].odhs.tanf.payment_standard
        size = spm_unit("spm_unit_size", period)
        size_capped = min_(size, 10)
        additional_people = max_(size - 10, 0)
        base_amount = p.amount[size_capped]
        additional_amount = additional_people * p.additional_person
        return base_amount + additional_amount
