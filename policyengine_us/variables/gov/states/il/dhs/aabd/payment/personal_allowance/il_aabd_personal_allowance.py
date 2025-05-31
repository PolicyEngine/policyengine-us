from policyengine_us.model_api import *


class il_aabd_personal_allowance(Variable):
    value_type = float
    entity = Person
    label = (
        "Illinois Aid to the Aged, Blind or Disabled (AABD) personal allowance"
    )
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.IL
    reference = "https://www.dhs.state.il.us/page.aspx?item=15913"

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.il.dhs.aabd.payment.personal_allowance
        size = person.spm_unit("spm_unit_size", period)
        capped_size = clip(size, 1, 8)
        is_bedfast = person("il_aabd_is_bedfast", period)
        return where(is_bedfast, p.bedfast[capped_size], p.active[capped_size])
