from policyengine_us.model_api import *


class oh_ccap_fpg(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    definition_period = MONTH
    label = "Ohio CCAP monthly federal poverty guideline"
    defined_for = StateCode.OH
    reference = "https://dam.assets.ohio.gov/image/upload/childrenandyouth.ohio.gov/For%20Partners/Rules%20and%20Resources/2025/PL_21.pdf#page=1"

    def formula(spm_unit, period, parameters):
        # DCY publishes the income standards each October first from that
        # year's federal poverty guidelines — 5180:6-1-02(F)(1)(b) requires
        # annual publication in a child care manual procedure letter — and
        # they remain in effect until the next annual letter, so months
        # before October use the prior year's guideline (same October-vintage
        # pattern as snap_fpg).
        n = spm_unit("spm_unit_size", period.this_year)
        state_group = spm_unit.household("state_group_str", period.this_year)
        year = period.start.year
        month = period.start.month
        if month >= 10:
            instant_str = f"{year}-10-01"
        else:
            instant_str = f"{year - 1}-10-01"
        p_fpg = parameters(instant_str).gov.hhs.fpg
        p1 = p_fpg.first_person[state_group] / MONTHS_IN_YEAR
        pn = p_fpg.additional_person[state_group] / MONTHS_IN_YEAR
        return p1 + pn * (n - 1)
