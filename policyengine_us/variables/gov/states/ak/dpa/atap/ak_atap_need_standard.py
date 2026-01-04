from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.ak.dpa.atap.ak_atap_unit_type import (
    AKATAPUnitType,
)


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
        unit_size = spm_unit("spm_unit_size", period)
        unit_type = spm_unit("ak_atap_unit_type", period)

        # Child-only: use child_only table (sizes 1-4+)
        child_only_capped = min_(unit_size, 4)
        child_only_standard = p.child_only.amount[child_only_capped]

        # Pregnant woman only: single value
        pregnant_standard = p.pregnant_woman.amount

        # Adult-included (one-parent or two-parent able): use adult_included table (sizes 2-11+)
        adult_capped = clip(unit_size, 2, 11)
        adult_standard = p.adult_included.amount[adult_capped]

        # Incapacitated parent: use incapacitated_parent table (sizes 3-4+)
        # Minimum size 3 = 2 parents + 1 child
        incap_capped = clip(unit_size, 3, 4)
        incapacitated_standard = p.incapacitated_parent.amount[incap_capped]

        return select(
            [
                unit_type == AKATAPUnitType.PREGNANT_WOMAN,
                unit_type == AKATAPUnitType.CHILD_ONLY,
                unit_type == AKATAPUnitType.TWO_PARENT_INCAPACITATED,
            ],
            [
                pregnant_standard,
                child_only_standard,
                incapacitated_standard,
            ],
            default=adult_standard,
        )
