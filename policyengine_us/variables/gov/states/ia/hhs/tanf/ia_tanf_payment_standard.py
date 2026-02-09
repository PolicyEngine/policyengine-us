from policyengine_us.model_api import *


class ia_tanf_payment_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Iowa TANF payment standard"
    unit = USD
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/iowa/Iowa-Admin-Code-r-441-41-28"
    defined_for = StateCode.IA

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ia.hhs.tanf
        ps = p.payment_standard
        unit_size = spm_unit("spm_unit_size", period)
        base = ps.amount.calc(unit_size)
        additional = (
            max_(unit_size - p.max_unit_size, 0) * ps.additional_person
        )
        return base + additional
