from policyengine_us.model_api import *


class in_tanf_payment_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Indiana TANF payment standard"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://iga.in.gov/laws/2025/ic/titles/12/#12-14-2-5",
        "https://iar.iga.in.gov/code/2026/470/10.3#470-10.3-4-3",
    )
    defined_for = StateCode.IN

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states["in"].fssa.tanf.standard_of_need
        size = spm_unit("spm_unit_size", period.this_year)
        capped_size = min_(size, p.max_unit_size)
        return p.amount[capped_size]
