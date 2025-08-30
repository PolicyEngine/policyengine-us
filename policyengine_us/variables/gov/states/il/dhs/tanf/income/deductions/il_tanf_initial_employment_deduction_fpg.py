from policyengine_us.model_api import *


class il_tanf_initial_employment_deduction_fpg(Variable):
    value_type = float
    entity = SPMUnit
    label = "Illinois TANF federal poverty guidelines for the initial employment deduction"
    definition_period = MONTH
    defined_for = StateCode.IL

    def formula(spm_unit, period, parameters):
        n = spm_unit("il_tanf_assistance_unit_size", period)
        state_group = spm_unit.household("state_group_str", period)
        p_fpg = parameters(period).gov.hhs.fpg
        year = period.start.year
        month = period.start.month
        if month >= 3:
            instant_str = f"{year}-03-01"
        else:
            instant_str = f"{year - 1}-03-01"
        p_fpg = parameters(instant_str).gov.hhs.fpg
        p1 = p_fpg.first_person[state_group]
        pn = p_fpg.additional_person[state_group]
        return (p1 + pn * (n - 1)) / MONTHS_IN_YEAR
