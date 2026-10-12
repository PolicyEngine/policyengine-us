from policyengine_us.model_api import *


class ks_liheap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Eligible for Kansas LIEAP"
    documentation = "Kansas household that is income eligible, contains at least one citizen or qualified noncitizen, and meets the heating energy vulnerability requirement."
    reference = (
        "https://content.dcf.ks.gov/ees/KEESM/Robo10-24/Robo_10_01_24/keesm13300.htm",
        "https://content.dcf.ks.gov/ees/KEESM/Robo01-26/Robo_01_01_26/keesm13300.htm",
        "https://liheapch.acf.gov/docs/2026/state-plans/KS_Plan_2026.pdf#page=8",
    )
    defined_for = StateCode.KS

    def formula(spm_unit, period, parameters):
        income_eligible = spm_unit("ks_liheap_income_eligible", period)
        has_qualified_member = spm_unit("ks_liheap_household_size", period) > 0
        energy_vulnerable = spm_unit("ks_liheap_energy_vulnerable", period)
        return income_eligible & has_qualified_member & energy_vulnerable
