from policyengine_us.model_api import *


class in_tanf_payment_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Indiana TANF payment eligible"
    definition_period = MONTH
    reference = (
        "https://iar.iga.in.gov/code/2026/470/10.3#470-10.3-4-3",
        "https://iga.in.gov/laws/2025/ic/titles/12/#12-14-2-5",
    )
    defined_for = StateCode.IN

    def formula(spm_unit, period, parameters):
        countable = spm_unit("in_tanf_countable_income_for_payment", period)
        payment_standard = spm_unit("in_tanf_payment_standard", period)
        return countable < payment_standard
