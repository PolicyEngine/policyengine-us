from policyengine_us.model_api import *


class tn_ccap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Tennessee CCAP based on income"
    definition_period = MONTH
    defined_for = StateCode.TN
    reference = (
        "https://www.tn.gov/content/dam/tn/human-services/documents/Income%20Eligibility%20Limits%20and%20CoPay%20Chart%2010.1.25.pdf#page=1",
        "https://www.tn.gov/content/dam/tn/human-services/documents/CCDF%20State%20Plan%20FFY%202025-2027%20Tennessee.pdf#page=36",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.tn.dhs.ccap.income.smi_rate
        countable_income = spm_unit("tn_ccap_countable_income", period)
        monthly_smi = spm_unit("tn_ccap_smi", period)
        enrolled = spm_unit("tn_ccap_enrolled", period)
        # New applicants use the 85% SMI limit. Enrolled families use the
        # enrolled limit at redetermination (85% SMI, or 100% SMI from
        # October 1, 2025 under Smart Steps Plus).
        initial_limit = monthly_smi * p.initial
        enrolled_limit = monthly_smi * p.enrolled
        income_limit = where(enrolled, enrolled_limit, initial_limit)
        return countable_income <= income_limit
