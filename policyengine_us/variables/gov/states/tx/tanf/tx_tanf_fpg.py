from policyengine_us.model_api import *


class tx_tanf_fpg(Variable):
    value_type = float
    entity = SPMUnit
    label = "Texas TANF federal poverty guideline"
    unit = USD
    documentation = "The federal poverty guideline used to determine Texas TANF eligibility and benefits."
    definition_period = MONTH
    reference = (
        "https://www.hhs.texas.gov/handbooks/texas-works-handbook/a-1340-income-limits",
    )
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        n = spm_unit("tx_tanf_assistance_unit_size", period)
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
