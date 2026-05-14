from policyengine_us.model_api import *


class wv_ccap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for West Virginia CCAP based on income"
    definition_period = MONTH
    defined_for = StateCode.WV
    reference = (
        "https://bfa.wv.gov/media/39915/download?inline#page=20",
        "https://bfa.wv.gov/media/6781/download?inline",
    )

    def formula(spm_unit, period, parameters):
        # Per CCDF State Plan §2.2.4 / §2.2.5(a), WV sets its sole income
        # ceiling at 85% of state median income; graduated phase-out is
        # marked "Not applicable" because the threshold already sits at
        # the federal CCDF ceiling.
        p = parameters(period).gov.states.wv.dhhr.ccap.income
        countable_income = spm_unit("wv_ccap_countable_income", period)
        smi = spm_unit("hhs_smi", period)
        smi_eligible = countable_income <= smi * p.smi_rate
        # TANF recipients are categorically income-eligible per Policy
        # Manual §3.2.1. We don't currently distinguish "TANF children-
        # only" cases (§3.2.1.4), which must still meet the income test;
        # the bypass applies to all is_tanf_enrolled units.
        is_tanf = spm_unit("is_tanf_enrolled", period)
        return is_tanf | smi_eligible
