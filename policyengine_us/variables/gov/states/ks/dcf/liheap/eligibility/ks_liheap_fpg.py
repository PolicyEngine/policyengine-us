from policyengine_us.model_api import *


class ks_liheap_fpg(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "Kansas LIEAP federal poverty guideline"
    documentation = "Federal poverty guideline used for the Kansas LIEAP income limit. The household size counts only U.S. citizens and qualified aliens (KEESM 13330), and the guideline is the prior calendar year's because each season's published income table is 150% of the prior year's HHS poverty guidelines."
    unit = USD
    reference = (
        "https://content.dcf.ks.gov/ees/keesm/current/keesm13300.htm",
        "https://liheapch.acf.gov/docs/2026/state-plans/KS_Plan_2026.pdf#page=8",
        "https://www.dcf.ks.gov/services/ees/pages/energyassistance.aspx",
    )
    defined_for = StateCode.KS

    def formula(spm_unit, period, parameters):
        size = spm_unit("ks_liheap_household_size", period)
        state_group = spm_unit.household("state_group_str", period)
        p_fpg = parameters(period.last_year).gov.hhs.fpg
        first_person = p_fpg.first_person[state_group]
        additional_person = p_fpg.additional_person[state_group]
        return first_person + additional_person * max_(size - 1, 0)
