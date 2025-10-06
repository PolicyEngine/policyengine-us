from policyengine_us.model_api import *


class ma_ccfa_fpg(Variable):
    value_type = float
    entity = SPMUnit
    label = "Massachusetts Child Care Financial Assistance (CCFA) federal poverty guideline"
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.MA
    reference = "https://www.mass.gov/doc/parent-fee-chart-fy2025/download"

    def formula(spm_unit, period, parameters):
        size = spm_unit("spm_unit_size", period)
        capped_size = min_(size, 12)
        state_group = spm_unit.household("state_group_str", period.this_year)
        p_fpg = parameters(period).gov.hhs.fpg
        year = period.start.year
        month = period.start.month
        if month >= 10:
            instant_str = f"{year}-10-01"
        else:
            instant_str = f"{year - 1}-10-01"
        p_fpg = parameters(instant_str).gov.hhs.fpg
        p1 = p_fpg.first_person[state_group]
        pn = p_fpg.additional_person[state_group]
        return p1 + pn * (capped_size - 1)
