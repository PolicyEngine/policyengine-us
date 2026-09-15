from policyengine_us.model_api import *


class ma_ccfa_asset_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Asset eligible for Massachusetts Child Care Financial Assistance (CCFA)"
    defined_for = StateCode.MA
    reference = (
        "https://www.mass.gov/doc/eecs-financial-assistance-policy-guide-february-1-2022/download#page=36",
        "https://www.mass.gov/doc/eec-policy-advisory-field-operations-2023-4-child-care-financial-assistance/download#page=3",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ma.eec.ccfa.assets
        eligible = spm_unit("spm_unit_assets", period.this_year) <= p.limit
        if p.homeless_exemption_in_effect:
            eligible |= spm_unit.household("is_homeless", period.this_year)
        if p.tafdc_exemption_in_effect:
            eligible |= spm_unit("is_tanf_enrolled", period)
        return eligible
