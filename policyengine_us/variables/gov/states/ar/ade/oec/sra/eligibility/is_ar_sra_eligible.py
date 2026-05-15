from policyengine_us.model_api import *


class is_ar_sra_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Arkansas School Readiness Assistance"
    definition_period = MONTH
    defined_for = StateCode.AR
    reference = (
        "https://dese.ade.arkansas.gov/Files/FSU-Procedural-Manual-June-2023_UPDATED_20230629075344.pdf#page=13",
        "https://dese.ade.arkansas.gov/Files/R_&_R__Nov_2025_(English)_(1)_OEC.pdf#page=1",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ar.ade.oec.sra
        if not p.in_effect:
            return False
        has_eligible_child = add(spm_unit, period, ["is_ar_sra_child_eligible"]) > 0
        income_ok = spm_unit("is_ar_sra_income_eligible", period)
        asset_ok = spm_unit("is_ar_sra_asset_eligible", period)
        li_active = spm_unit("is_ar_sra_li_activity_eligible", period)
        ess_active = spm_unit("is_ar_sra_ess_eligible", period)
        activity_ok = li_active | ess_active
        return has_eligible_child & income_ok & asset_ok & activity_ok
