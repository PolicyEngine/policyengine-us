from policyengine_us.model_api import *


class nv_ccdp_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Nevada CCDP"
    definition_period = MONTH
    defined_for = StateCode.NV
    reference = "https://dss.nv.gov/uploadedFiles/dwssnvgov/content/Care/Child%20Care%20Manual%20July%202024.pdf#page=36"

    def formula(spm_unit, period, parameters):
        # MS 218 residency is enforced by defined_for = StateCode.NV.
        has_eligible_child = add(spm_unit, period, ["nv_ccdp_eligible_child"]) > 0
        income_eligible = spm_unit("nv_ccdp_income_eligible", period)
        # MS 320 (Manual p.75) / 45 CFR 98.20: $1,000,000 CCDF asset ceiling.
        asset_eligible = spm_unit("is_ccdf_asset_eligible", period.this_year)
        activity_eligible = spm_unit("nv_ccdp_activity_eligible", period)
        return has_eligible_child & income_eligible & asset_eligible & activity_eligible
