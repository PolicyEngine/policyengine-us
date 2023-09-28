from policyengine_us.model_api import *


class snap_fpg(Variable):
    value_type = float
    entity = SPMUnit
    label = "SNAP federal poverty guideline"
    unit = USD
    documentation = (
        "The federal poverty guideline used to determine SNAP eligibility."
    )
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        n = spm_unit("spm_unit_size", period)
        state_group = spm_unit.household("state_group_str", period)
        year = period.start.year
        instant_str = f"{year - 1}-10-01"
        p_fpg = parameters(instant_str).gov.hhs.fpg
        p1 = p_fpg.first_person[state_group]
        pn = p_fpg.additional_person[state_group]
        return p1 + pn * (n - 1)
