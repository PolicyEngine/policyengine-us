from policyengine_us.model_api import *


class ak_ccap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Alaska CCAP based on income"
    definition_period = MONTH
    defined_for = StateCode.AK
    reference = (
        "https://www.akleg.gov/statutesPDF/aac%20Title%207.pdf#page=907",
        "https://health.alaska.gov/media/igiccwuf/child-care-assistance-program-policies-and-procedures.pdf#page=173",
    )

    def formula(spm_unit, period, parameters):
        countable = spm_unit("ak_ccap_countable_income", period)
        # Alaska CCAP "family" (Manual §4070-4 A.1) is parents + minor children — extended-family
        # members co-residing are excluded. PolicyEngine uses spm_unit_size (via hhs_smi), which
        # can include such adults, slightly overstating family size in those households. Accepted
        # simplification.
        smi = spm_unit("hhs_smi", period)
        smi_rate = parameters(period).gov.states.ak.dpa.ccap.income.smi_rate
        return countable <= smi * smi_rate
