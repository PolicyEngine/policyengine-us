from policyengine_us.model_api import *


class ak_atap_need_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Alaska ATAP need standard"
    unit = USD
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/alaska/7-AAC-45.520"
    defined_for = StateCode.AK

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ak.dpa.atap.income.need_standard
        unit_size = spm_unit("ak_atap_unit_size", period)
        is_child_only = spm_unit("ak_atap_is_child_only_unit", period)
        is_pregnant_only = spm_unit("ak_atap_is_pregnant_woman_only", period)

        # Child-only: use child_only table (sizes 1-4+)
        child_only_capped = min_(unit_size, 4)
        child_only_standard = p.child_only.amount[child_only_capped]

        # Pregnant woman only: single value
        pregnant_standard = p.pregnant_woman.amount

        # Adult-included: use adult_included table (sizes 2-11+)
        adult_capped = clip(unit_size, 2, 11)
        adult_standard = p.adult_included.amount[adult_capped]

        return where(
            is_pregnant_only,
            pregnant_standard,
            where(is_child_only, child_only_standard, adult_standard),
        )
