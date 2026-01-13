from policyengine_us.model_api import *


class al_tanf_payment_standard(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Alabama TANF payment standard"
    definition_period = MONTH
    reference = (
        "https://dhr.alabama.gov/wp-content/uploads/2024/09/2024-State-Plan-TANF.pdf#page=23",
    )
    defined_for = StateCode.AL

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.al.dhs.tanf
        unit_size = spm_unit("spm_unit_size", period)
        capped_unit_size = min_(unit_size, p.max_unit_size)
        return p.payment_standard[capped_unit_size]
