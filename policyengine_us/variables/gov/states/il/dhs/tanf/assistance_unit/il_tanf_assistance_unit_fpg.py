from policyengine_us.model_api import *


class il_tanf_assistance_unit_fpg(Variable):
    value_type = float
    entity = SPMUnit
    label = "Illinois TANF assistance unit's federal poverty guideline"
    definition_period = MONTH
    defined_for = StateCode.IL

    def formula(spm_unit, period, parameters):
        n = spm_unit("il_tanf_assistance_unit_size", period)
        state_group = spm_unit.household("state_group_str", period)
        p_fpg = parameters(period).gov.hhs.fpg
        p1 = p_fpg.first_person[state_group] / MONTHS_IN_YEAR
        pn = p_fpg.additional_person[state_group] / MONTHS_IN_YEAR
        return p1 + pn * (n - 1)
