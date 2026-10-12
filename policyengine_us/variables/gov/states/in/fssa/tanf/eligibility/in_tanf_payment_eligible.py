from policyengine_us.model_api import *


class in_tanf_payment_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Indiana TANF payment eligible"
    definition_period = MONTH
    reference = (
        "https://iga.in.gov/laws/2025/ic/titles/12/#12-14-2-5",
        "https://www.in.gov/fssa/dfr/files/3000.pdf#page=7",
    )
    defined_for = StateCode.IN

    def formula(spm_unit, period, parameters):
        countable = spm_unit("in_tanf_countable_income_for_payment", period)
        maximum_benefit = spm_unit("in_tanf_maximum_benefit", period)
        return countable < maximum_benefit
