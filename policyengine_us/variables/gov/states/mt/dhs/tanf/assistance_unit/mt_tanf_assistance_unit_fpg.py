from policyengine_us.model_api import *


class mt_tanf_assistance_unit_fpg(Variable):
    value_type = float
    entity = SPMUnit
    label = "Montana TANF assistance unit's federal poverty guideline"
    unit = USD
    reference = "https://dphhs.mt.gov/assets/hcsd/tanfmanual/TANF001.pdf"
    definition_period = MONTH

    def formula(spm_unit, period, parameters):
        n = spm_unit("mt_tanf_assistance_unit_size", period.this_year)
        state_group = spm_unit.household("state_group_str", period.this_year)
        year = period.start.year
        month = period.start.month
        if month >= 7:
            instant_str = f"{year}-7-01"
        else:
            instant_str = f"{year - 1}-7-01"
        p_fpg = parameters(instant_str).gov.hhs.fpg
        p1 = p_fpg.first_person[state_group] / MONTHS_IN_YEAR
        pn = p_fpg.additional_person[state_group] / MONTHS_IN_YEAR
        return p1 + pn * (n - 1)
