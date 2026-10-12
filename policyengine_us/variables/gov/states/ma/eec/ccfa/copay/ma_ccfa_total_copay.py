from policyengine_us.model_api import *


class ma_ccfa_total_copay(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    label = "Massachusetts Child Care Financial Assistance (CCFA) parent total copay"
    defined_for = StateCode.MA
    unit = USD
    reference = (
        "https://www.mass.gov/doc/eecs-financial-assistance-policy-guide-february-1-2022/download#page=76",
        "https://www.mass.gov/doc/eec-policy-advisory-field-operations-2023-4-child-care-financial-assistance/download#page=2",
        "https://www.mass.gov/doc/eec-ccfa-2026-04-income-eligible-consolidated-policies-may-6-2026/download#page=44",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ma.eec.ccfa.copay
        # Reported TANF enrollment is the DTA-related-care proxy, as in
        # other state CCDF models; calculated TAFDC eligibility is insufficient.
        exempt = spm_unit("is_tanf_enrolled", period)
        if p.homeless_exemption_in_effect:
            exempt = exempt | spm_unit.household("is_homeless", period.this_year)
        return where(exempt, 0, add(spm_unit, period, ["ma_ccfa_copay_person"]))
