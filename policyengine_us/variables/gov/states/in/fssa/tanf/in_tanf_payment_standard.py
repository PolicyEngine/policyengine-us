from policyengine_us.model_api import *


class in_tanf_payment_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Indiana TANF payment standard"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.in.gov/fssa/dfr/tanf-cash-assistance/about-tanf/",
        "https://iga.in.gov/laws/2023/ic/titles/12",
    )
    defined_for = StateCode.IN

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states["in"].fssa.tanf
        # Cap at maximum documented family size
        capped_size = min_(spm_unit("spm_unit_size", period), 10)
        return p.payment_standard[capped_size]
