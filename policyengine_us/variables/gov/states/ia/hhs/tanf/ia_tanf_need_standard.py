from policyengine_us.model_api import *


class ia_tanf_need_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Iowa TANF standard of need"
    unit = USD
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/iowa/Iowa-Admin-Code-r-441-41-28"
    defined_for = StateCode.IA

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ia.hhs.tanf
        ns = p.need_standard
        unit_size = spm_unit("spm_unit_size", period)
        base = ns.amount.calc(unit_size)
        additional = (
            max_(unit_size - p.max_unit_size, 0) * ns.additional_person
        )
        return base + additional
