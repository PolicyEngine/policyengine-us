from policyengine_us.model_api import *


class is_ar_sra_asset_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Asset-eligible for Arkansas SRA"
    definition_period = MONTH
    defined_for = StateCode.AR
    reference = (
        "https://dese.ade.arkansas.gov/Files/2025-2027_CCDF_State_Plan_Final_4.26.24.1REV_OEC.pdf#page=25",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ar.ade.oec.sra.eligibility
        assets = spm_unit("spm_unit_assets", period.this_year)
        return assets <= p.asset_limit
