from policyengine_us.model_api import *


class il_aabd_personal_allowance(Variable):
    value_type = float
    entity = Person
    label = (
        "Illinois Aid to the Aged, Blind or Disabled (AABD) personal allowance"
    )
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.IL  ## defined_for = "il_aabd_eligible_person"
    reference = (
        "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-113.259",
    )

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.il.dhs.aabd.payment.personal_allowance
        size = person.spm_unit("spm_unit_size", period)
        capped_size = min_(size, 8)
        is_bedfast = person("il_aabd_is_bedfast", period)
        return where(is_bedfast, p.bedfast[capped_size], p.active[capped_size])
