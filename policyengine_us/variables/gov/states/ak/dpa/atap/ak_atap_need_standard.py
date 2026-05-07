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
        p = parameters(period).gov.states.ak.dpa.atap.need_standard
        unit_size = spm_unit("spm_unit_size", period)

        # Check for pregnant woman alone (size 1 with pregnant person)
        is_pregnant = add(spm_unit, period, ["is_pregnant"]) > 0
        is_pregnant_woman_alone = (unit_size == 1) & is_pregnant

        # Adult-included standards: sizes 2-8, with additional amount for larger
        max_unit_size = p.max_unit_size
        capped_size = clip(unit_size, 2, max_unit_size)
        base_standard = p.amount[capped_size]

        # Add additional amount for each person beyond max table size
        extra_persons = max_(unit_size - max_unit_size, 0)
        additional = extra_persons * p.additional_person
        adult_included_standard = base_standard + additional

        # Return pregnant woman standard if alone, otherwise adult-included
        return where(
            is_pregnant_woman_alone,
            p.pregnant_woman,
            where(unit_size >= 2, adult_included_standard, 0),
        )
