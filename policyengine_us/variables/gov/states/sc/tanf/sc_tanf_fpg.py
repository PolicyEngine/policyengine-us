from policyengine_us.model_api import *


class sc_tanf_fpg(Variable):
    value_type = float
    entity = SPMUnit
    label = "South Carolina TANF federal poverty guideline"
    unit = USD
    defined_for = StateCode.SC
    definition_period = MONTH

    def formula(spm_unit, period, parameters):
        size = spm_unit("spm_unit_size", period.this_year)
        qualifying_child = add(
            spm_unit, period.this_year, ["is_child_dependent"]
        )
        child_count = add(spm_unit, period.this_year, ["is_child"])
        n = size - child_count + qualifying_child
        state_group = spm_unit.household("state_group_str", period.this_year)
        year = period.start.year
        month = period.start.month
        if month >= 10:
            instant_str = f"{year}-10-01"
        else:
            instant_str = f"{year - 1}-10-01"
        p_fpg = parameters(instant_str).gov.hhs.fpg
        p1 = p_fpg.first_person[state_group]
        pn = p_fpg.additional_person[state_group]
        return (p1 + pn * (n - 1)) / MONTHS_IN_YEAR
