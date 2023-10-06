from policyengine_us.model_api import *


class snap_fpg(Variable):
    value_type = float
    entity = SPMUnit
    label = "SNAP federal poverty guideline"
    unit = USD
    documentation = (
        "The federal poverty guideline used to determine SNAP eligibility."
    )
    definition_period = MONTH

    def formula(spm_unit, period, parameters):
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
